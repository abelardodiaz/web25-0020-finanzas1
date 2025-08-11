# <!-- file: core/models.py -->
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from uuid import uuid4
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, F, Case, When
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import path
from django.core.exceptions import ValidationError

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.db.models import Q
from django.core.paginator import Paginator
from django.template.loader import render_to_string


class Moneda(models.TextChoices):
    MXN = "MXN", _("Peso MXN")
    USD = "USD", _("Dólar USD")


class TipoCuenta(models.Model):
    codigo  = models.CharField(max_length=10, unique=True)
    nombre  = models.CharField(max_length=50)
    GRUPOS  = [
        ("DEB", "Debito"),
        ("SER", "Servicios/gastos/proveedores"),
        ("CRE", "Creditos"),
        ("ING", "Ingresos"),
    ]
    grupo   = models.CharField(max_length=3, choices=GRUPOS, default="DEB",)

    class Meta:
        verbose_name = "tipo de cuenta"
        verbose_name_plural = "tipos de cuenta"

    def __str__(self):
        return self.nombre  # Return only the name without grupo code

class CuentaManager(models.Manager):
    def medios_pago(self):
        return self.filter(tipo__grupo__in=["DEB", "CRE", "EFE"])

    def servicios(self):
        return self.filter(tipo__codigo__in=["SERV", "SID"])

    def transferibles(self):
        return self.medios_pago()

    def proveedores(self):
        return self.filter(tipo__codigo="PROV")


class Cuenta(models.Model):
    nombre            = models.CharField(max_length=100, unique=True)
    tipo              = models.ForeignKey(TipoCuenta, on_delete=models.RESTRICT,
                                          related_name="cuentas")
    moneda            = models.CharField(max_length=3, choices=Moneda.choices,
                                          default=Moneda.MXN)
    # REMOVED: activo field

    # 🔸 campos que aparecen en «SALDOS - Cuentas.csv»
    referencia        = models.CharField(max_length=50, blank=True)
    ref_comentario    = models.CharField(max_length=120, blank=True)
    no_cliente        = models.CharField(max_length=30,  blank=True)
    fecha_apertura    = models.DateField(null=True, blank=True)
    no_contrato       = models.CharField(max_length=40,  blank=True)
    # REMOVED: dia_corte field

    # Naturaleza contable de la cuenta
    NATURALEZA = [
        ("DEUDORA", "Deudora"),
        ("ACREEDORA", "Acreedora"),
    ]
    naturaleza = models.CharField(
        max_length=10, 
        choices=NATURALEZA, 
        default="DEUDORA",
        help_text="Naturaleza contable de la cuenta"
    )

    saldo_inicial = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        verbose_name="Saldo Inicial"
    )

    # Campos adicionales identificados en el análisis
    propietario = models.CharField(
        max_length=50,
        blank=True,
        help_text="Propietario de la cuenta (ej: ADS, empresa, etc.)"
    )
    
    medio_pago = models.BooleanField(
        default=False,
        help_text="Indica si esta cuenta puede usarse como medio de pago"
    )

    objects = CuentaManager()

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.tipo.nombre})"

    # Saldo "al vuelo" - v0.7.0 usando partidas contables
    def saldo(self, as_of_date=None):
        """
        Calcula el saldo usando las partidas contables (doble partida).
        Más preciso que el método anterior basado en transacciones unificadas.
        """
        qs = self.partidas_contables.all()
        if as_of_date:
            qs = qs.filter(asiento__fecha__lte=as_of_date)
        
        # Calcular balance según naturaleza contable
        balance = qs.aggregate(
            balance=Sum(
                Case(
                    When(debito__isnull=False, then=F('debito')),
                    default=F('credito') * -1,
                    output_field=models.DecimalField()
                )
            )
        )['balance'] or Decimal('0.00')
        
        # Para cuentas deudoras: débitos positivos, créditos negativos
        # Para cuentas acreedoras: invertir el signo 
        if self.naturaleza == "ACREEDORA":
            balance = -balance
            
        return self.saldo_inicial + balance

    # Método legacy mantenido por compatibilidad
    def saldo_legacy(self):
        """Método anterior basado en transacciones unificadas
        
        IMPORTANTE - Lógica contable:
        - Para cuentas DEUDORAS (como cuentas de débito):
          * entradas (cuenta_destino) = CARGOS contables → aumentan saldo
          * salidas (cuenta_origen) = ABONOS contables → disminuyen saldo
        - Para cuentas ACREEDORAS (como tarjetas de crédito):
          * entradas (cuenta_destino) = ABONOS contables → aumentan saldo
          * salidas (cuenta_origen) = CARGOS contables → disminuyen saldo
        """
        salidas = self.transacciones_origen.aggregate(
            total=models.Sum("monto"))["total"] or Decimal("0.00")
        entradas = self.transacciones_destino.aggregate(
            total=models.Sum("monto"))["total"] or Decimal("0.00")
        
        if self.naturaleza == "DEUDORA":
            # entradas son CARGOS (aumentan), salidas son ABONOS (disminuyen)
            return self.saldo_inicial + entradas - salidas
        else:  # ACREEDORA
            # salidas son CARGOS (disminuyen), entradas son ABONOS (aumentan)
            return self.saldo_inicial + salidas - entradas

    def aplicar_cargo(self, monto):
        """
        Aplica un CARGO contable según la naturaleza de la cuenta.
        
        CARGO contable:
        - En cuentas DEUDORAS (débito, activos): AUMENTA el saldo (+)
        - En cuentas ACREEDORAS (crédito, pasivos): DISMINUYE el saldo (-)
        
        Ejemplos:
        - CARGO a cuenta débito BBVA: +$100 (aumenta el activo)
        - CARGO a tarjeta de crédito: -$100 (disminuye la deuda)
        """
        return monto if self.naturaleza == "DEUDORA" else -monto

    def aplicar_abono(self, monto):
        """
        Aplica un ABONO contable según la naturaleza de la cuenta.
        
        ABONO contable:
        - En cuentas DEUDORAS (débito, activos): DISMINUYE el saldo (-)
        - En cuentas ACREEDORAS (crédito, pasivos): AUMENTA el saldo (+)
        
        Ejemplos:
        - ABONO a cuenta débito BBVA: -$100 (disminuye el activo)
        - ABONO a tarjeta de crédito: +$100 (aumenta la deuda)
        """
        return -monto if self.naturaleza == "DEUDORA" else monto
        

class CategoriaTipo(models.TextChoices):
    PERSONAL = "PERSONAL", _("Personal")
    NEGOCIO  = "NEGOCIO", _("Negocio")
    MIXTO  = "MIXTO", _("Mixto")
    TERCEROS  = "TERCEROS", _("Terceros")

class Categoria(models.Model):
    nombre       = models.CharField(max_length=100)
    tipo         = models.CharField(
        max_length=10,
        choices=CategoriaTipo.choices,
        default=CategoriaTipo.PERSONAL,
    )
    padre        = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        related_name="subcategorias",
    )
    descripcion  = models.TextField(
        max_length=200,
        blank=True,
        help_text="Descripción detallada de la categoría"
    )

    class Meta:
        unique_together = ("nombre", "padre")      # evita duplicados en jerarquía
        ordering        = ["nombre"]

    def __str__(self):
        base = self.nombre if not self.padre else f"{self.padre} › {self.nombre}"
        return f"{base} ({self.get_tipo_display()})"


# === MODELO ANTERIOR (RESPALDO) - ELIMINAR EN v0.7.0 ===
class TransaccionLegacy(models.Model):
    """Modelo anterior - mantener temporalmente para migración"""
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    tipo = models.CharField(max_length=13, blank=True)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255, blank=True)
    cuenta_servicio = models.ForeignKey(Cuenta, null=True, blank=True, on_delete=models.RESTRICT, related_name="legacy_servicios")
    categoria = models.ForeignKey(Categoria, on_delete=models.RESTRICT, related_name="legacy_transacciones")
    medio_pago = models.ForeignKey(Cuenta, on_delete=models.RESTRICT, related_name="legacy_pagos")
    grupo_uuid = models.UUIDField(default=uuid4, editable=False)
    ajuste = models.BooleanField(default=False)
    moneda = models.CharField(max_length=3, choices=Moneda.choices, default=Moneda.MXN)
    periodo = models.ForeignKey("Periodo", null=True, blank=True, on_delete=models.SET_NULL, related_name="legacy_transacciones")
    conciliado = models.BooleanField(default=False)

    class Meta:
        db_table = 'core_transaccion_legacy'


# === NUEVO MODELO SIMPLIFICADO ===
class TransaccionTipo(models.TextChoices):
    INGRESO = "INGRESO", _("Ingreso")
    GASTO = "GASTO", _("Gasto")
    TRANSFERENCIA = "TRANSFERENCIA", _("Transferencia")


class TransaccionEstado(models.TextChoices):
    """Estados del ciclo de vida de las transacciones"""
    PENDIENTE = 'pending', _('Pendiente')
    LIQUIDADA = 'cleared', _('Liquidada') 
    CONCILIADA = 'reconciled', _('Conciliada')
    VERIFICADA = 'verified', _('Verificada')


class Transaccion(models.Model):
    """Modelo simplificado v0.6.0 - Un registro por transacción"""
    monto = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Monto de la transacción (siempre positivo)"
    )
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255)
    
    # Cuentas involucradas
    cuenta_origen = models.ForeignKey(
        Cuenta,
        null=True,  # Temporal para migración
        blank=True,
        on_delete=models.RESTRICT,
        related_name="transacciones_origen",
        help_text="Cuenta de donde sale el dinero"
    )
    cuenta_destino = models.ForeignKey(
        Cuenta,
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        related_name="transacciones_destino",
        help_text="Cuenta hacia donde va el dinero (solo transferencias)"
    )
    
    categoria = models.ForeignKey(
        Categoria,
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        related_name="transacciones",
        help_text="Categoría del gasto/ingreso"
    )
    
    # Tipo inferido automáticamente
    tipo = models.CharField(
        max_length=13,
        choices=TransaccionTipo.choices,
        default=TransaccionTipo.GASTO,  # Valor por defecto
        editable=False,  # Se calcula automáticamente
    )
    
    moneda = models.CharField(
        max_length=3,
        choices=Moneda.choices,
        default=Moneda.MXN,
    )
    
    periodo = models.ForeignKey(
        "Periodo",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transacciones",
    )
    
    conciliado = models.BooleanField(default=False)
    
    # Campo para ajustes (operaciones de 1 solo movimiento)
    ajuste = models.BooleanField(
        default=False,
        help_text="Si es True, crea solo 1 asiento contable sin contrapartida automática"
    )
    
    # Nuevo campo de estado
    estado = models.CharField(
        max_length=12,
        choices=TransaccionEstado.choices,
        default=TransaccionEstado.PENDIENTE,
        help_text="Estado del ciclo de vida de la transacción"
    )
    
    # Campos de conciliación bancaria
    fecha_conciliacion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha cuando se concilió la transacción"
    )
    
    referencia_bancaria = models.CharField(
        max_length=100,
        blank=True,
        help_text="Referencia/ID del banco para matching automático"
    )
    
    saldo_posterior = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Saldo de la cuenta después de esta transacción"
    )
    
    # Campos específicos para importación BBVA
    importacion_bbva = models.ForeignKey(
        'ImportacionBBVA',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='transacciones_creadas',
        help_text="Importación BBVA que creó esta transacción"
    )
    
    referencia_bbva = models.TextField(
        blank=True,
        help_text="Descripción original del estado de cuenta BBVA"
    )
    
    saldo_posterior_bbva = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Saldo reportado por BBVA después de esta transacción"
    )

    class Meta:
        indexes = [
            models.Index(fields=["fecha"]),
            models.Index(fields=["categoria"]),
            models.Index(fields=["cuenta_origen"]),
            models.Index(fields=["tipo"]),
            models.Index(fields=["estado"]),
        ]
        ordering = ["-fecha"]

    def clean(self):
        """Validaciones del modelo"""
        if self.cuenta_destino and self.categoria:
            raise models.ValidationError("Una transacción no puede tener cuenta_destino Y categoría")
        
        if not self.cuenta_destino and not self.categoria:
            raise models.ValidationError("Debe especificar cuenta_destino O categoría")
            
        if self.cuenta_origen == self.cuenta_destino:
            raise models.ValidationError("Las cuentas origen y destino deben ser diferentes")

    def save(self, *args, **kwargs):
        """Inferir tipo y generar asientos contables automáticamente"""
        # Inferir tipo automáticamente basado en el tipo de cuenta_origen
        if self.cuenta_origen and self.cuenta_origen.tipo.codigo == 'ING':
            # Si viene de una cuenta de ingresos, es un INGRESO
            self.tipo = TransaccionTipo.INGRESO
        elif self.cuenta_origen and self.cuenta_destino:
            # Si hay ambas cuentas, verificar si es transferencia o pago
            origen_es_banco = self.cuenta_origen.tipo.codigo in ['DEB', 'CRE']
            destino_es_banco = self.cuenta_destino.tipo.codigo in ['DEB', 'CRE']
            
            if origen_es_banco and destino_es_banco:
                self.tipo = TransaccionTipo.TRANSFERENCIA
            elif origen_es_banco and self.cuenta_destino.tipo.codigo in ['CRE', 'SER']:
                self.tipo = TransaccionTipo.GASTO  # Pago de tarjeta/servicio
            else:
                self.tipo = TransaccionTipo.TRANSFERENCIA
        elif self.categoria:
            # Fallback a categoría
            if self.categoria.tipo in ['PERSONAL', 'NEGOCIO']:
                self.tipo = TransaccionTipo.GASTO
            else:
                self.tipo = TransaccionTipo.INGRESO
        
        # Asegurar monto positivo
        self.monto = abs(self.monto)
        
        # Guardar la transacción principal
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Generar asiento contable automáticamente (solo para transacciones nuevas)
        if is_new:
            self._crear_asiento_contable()

    def _crear_asiento_contable(self):
        """Crea automáticamente el asiento contable de doble partida o ajuste simple"""
        with transaction.atomic():
            # Crear el asiento principal
            asiento = AsientoContable.objects.create(
                fecha=self.fecha,
                descripcion=self.descripcion + (" - AJUSTE" if self.ajuste else ""),
                transaccion_origen=self,
                estado=self.estado
            )
            
            if self.ajuste:
                # AJUSTE: Crear solo 1 partida sin contrapartida
                self._crear_partida_ajuste(asiento)
            else:
                # DOBLE PARTIDA NORMAL
                if self.tipo == TransaccionTipo.TRANSFERENCIA:
                    self._crear_partidas_transferencia(asiento)
                elif self.tipo == TransaccionTipo.GASTO:
                    self._crear_partidas_gasto(asiento)
                elif self.tipo == TransaccionTipo.INGRESO:
                    self._crear_partidas_ingreso(asiento)

    def _crear_partidas_transferencia(self, asiento):
        """Crear partidas para transferencia entre cuentas"""
        # Debitar cuenta destino (dinero que entra)
        PartidaContable.objects.create(
            asiento=asiento,
            cuenta=self.cuenta_destino,
            debito=self.monto,
            descripcion=f"Transferencia de {self.cuenta_origen.nombre}",
            transaccion_referencia=self
        )
        
        # Acreditar cuenta origen (dinero que sale)
        PartidaContable.objects.create(
            asiento=asiento,
            cuenta=self.cuenta_origen,
            credito=self.monto,
            descripcion=f"Transferencia a {self.cuenta_destino.nombre}",
            transaccion_referencia=self
        )

    def _crear_partidas_gasto(self, asiento):
        """Crear partidas para gasto"""
        # Necesitamos una cuenta de gastos - crear si no existe
        cuenta_gastos = self._obtener_cuenta_gastos()
        
        # Debitar cuenta de gastos (aumenta el gasto)
        PartidaContable.objects.create(
            asiento=asiento,
            cuenta=cuenta_gastos,
            debito=self.monto,
            descripcion=f"Gasto: {self.categoria.nombre}",
            transaccion_referencia=self
        )
        
        # Acreditar cuenta origen (dinero que sale)
        PartidaContable.objects.create(
            asiento=asiento,
            cuenta=self.cuenta_origen,
            credito=self.monto,
            descripcion=f"Pago: {self.descripcion}",
            transaccion_referencia=self
        )

    def _crear_partidas_ingreso(self, asiento):
        """Crear partidas para ingreso"""
        # Necesitamos una cuenta de ingresos - crear si no existe
        cuenta_ingresos = self._obtener_cuenta_ingresos()
        
        # Debitar cuenta destino (dinero que entra)  
        PartidaContable.objects.create(
            asiento=asiento,
            cuenta=self.cuenta_destino,
            debito=self.monto,
            descripcion=f"Ingreso: {self.categoria.nombre}",
            transaccion_referencia=self
        )
        
        # Acreditar cuenta de ingresos (aumenta el ingreso)
        PartidaContable.objects.create(
            asiento=asiento,
            cuenta=cuenta_ingresos,
            credito=self.monto,
            descripcion=f"Ingreso: {self.descripcion}",
            transaccion_referencia=self
        )

    def _crear_partida_ajuste(self, asiento):
        """Crear una sola partida para ajustes (sin contrapartida)"""
        # Para ajustes, usar la cuenta_destino como la cuenta a ajustar
        cuenta_ajuste = self.cuenta_destino or self.cuenta_origen
        
        if not cuenta_ajuste:
            raise models.ValidationError("Para ajustes debe especificar cuenta_destino o cuenta_origen")
        
        # Determinar si es débito o crédito según la naturaleza de la cuenta
        # y si el tipo de transacción es GASTO (débito) o INGRESO (crédito)
        if self.tipo == TransaccionTipo.GASTO:
            # Ajuste de gasto - siempre débito
            PartidaContable.objects.create(
                asiento=asiento,
                cuenta=cuenta_ajuste,
                debito=self.monto,
                descripcion=f"Ajuste: {self.descripcion}",
                transaccion_referencia=self
            )
        else:
            # Ajuste de ingreso - siempre crédito
            PartidaContable.objects.create(
                asiento=asiento,
                cuenta=cuenta_ajuste,
                credito=self.monto,
                descripcion=f"Ajuste: {self.descripcion}",
                transaccion_referencia=self
            )

    def _obtener_cuenta_gastos(self):
        """Obtiene o crea cuenta de gastos para la categoría"""
        # Buscar tipo de cuenta de gastos
        tipo_gastos, _ = TipoCuenta.objects.get_or_create(
            codigo="GAST",
            defaults={
                'nombre': 'Gastos',
                'grupo': 'SER'
            }
        )
        
        # Buscar o crear cuenta específica para esta categoría
        nombre_cuenta = f"Gastos - {self.categoria.nombre}"
        cuenta_gastos, _ = Cuenta.objects.get_or_create(
            nombre=nombre_cuenta,
            defaults={
                'tipo': tipo_gastos,
                'naturaleza': 'DEUDORA',  # Los gastos son deudores
                'moneda': self.moneda
            }
        )
        return cuenta_gastos

    def _obtener_cuenta_ingresos(self):
        """Obtiene o crea cuenta de ingresos para la categoría"""
        # Buscar tipo de cuenta de ingresos  
        tipo_ingresos, _ = TipoCuenta.objects.get_or_create(
            codigo="ING",
            defaults={
                'nombre': 'Ingresos',
                'grupo': 'ING'
            }
        )
        
        # Buscar o crear cuenta específica para esta categoría
        nombre_cuenta = f"Ingresos - {self.categoria.nombre}"
        cuenta_ingresos, _ = Cuenta.objects.get_or_create(
            nombre=nombre_cuenta,
            defaults={
                'tipo': tipo_ingresos,
                'naturaleza': 'ACREEDORA',  # Los ingresos son acreedores
                'moneda': self.moneda
            }
        )
        return cuenta_ingresos

    def __str__(self):
        if self.tipo == TransaccionTipo.TRANSFERENCIA:
            return f"{self.fecha}: ${self.monto} {self.cuenta_origen.nombre} → {self.cuenta_destino.nombre}"
        else:
            signo = "+" if self.tipo == TransaccionTipo.INGRESO else "-"
            destino = self.categoria.nombre if self.categoria else "Sin categoría"
            return f"{self.fecha}: {signo}${self.monto} {destino}"

    @property
    def es_transferencia(self):
        return self.tipo == TransaccionTipo.TRANSFERENCIA

    @property  
    def es_gasto(self):
        return self.tipo == TransaccionTipo.GASTO

    @property
    def es_ingreso(self):
        return self.tipo == TransaccionTipo.INGRESO

    # Métodos para manejo de estados
    def marcar_liquidada(self, referencia_bancaria="", saldo_posterior=None):
        """Marca la transacción como liquidada (procesada por el banco)"""
        if self.estado == TransaccionEstado.PENDIENTE:
            self.estado = TransaccionEstado.LIQUIDADA
            self.referencia_bancaria = referencia_bancaria
            if saldo_posterior is not None:
                self.saldo_posterior = saldo_posterior
            self.save(update_fields=['estado', 'referencia_bancaria', 'saldo_posterior'])
            
            # Actualizar el asiento contable asociado
            if hasattr(self, 'asiento_contable'):
                self.asiento_contable.estado = TransaccionEstado.LIQUIDADA
                self.asiento_contable.save(update_fields=['estado'])

    def marcar_conciliada(self, usuario=None):
        """Marca la transacción como conciliada"""
        if self.estado in [TransaccionEstado.LIQUIDADA, TransaccionEstado.PENDIENTE]:
            self.estado = TransaccionEstado.CONCILIADA
            self.conciliado = True
            self.fecha_conciliacion = timezone.now()
            self.save(update_fields=['estado', 'conciliado', 'fecha_conciliacion'])
            
            # Actualizar el asiento contable asociado
            if hasattr(self, 'asiento_contable'):
                self.asiento_contable.estado = TransaccionEstado.CONCILIADA
                self.asiento_contable.save(update_fields=['estado'])

    def marcar_verificada(self, usuario=None):
        """Marca la transacción como verificada (revisión final)"""
        if self.estado == TransaccionEstado.CONCILIADA:
            self.estado = TransaccionEstado.VERIFICADA
            self.save(update_fields=['estado'])
            
            # Actualizar el asiento contable asociado
            if hasattr(self, 'asiento_contable'):
                self.asiento_contable.estado = TransaccionEstado.VERIFICADA
                self.asiento_contable.save(update_fields=['estado'])

    def revertir_estado(self):
        """Revierte la transacción al estado anterior"""
        estado_anterior = {
            TransaccionEstado.LIQUIDADA: TransaccionEstado.PENDIENTE,
            TransaccionEstado.CONCILIADA: TransaccionEstado.LIQUIDADA,
            TransaccionEstado.VERIFICADA: TransaccionEstado.CONCILIADA,
        }
        
        if self.estado in estado_anterior:
            nuevo_estado = estado_anterior[self.estado]
            self.estado = nuevo_estado
            
            # Limpiar campos según el estado
            if nuevo_estado == TransaccionEstado.PENDIENTE:
                self.conciliado = False
                self.fecha_conciliacion = None
            
            self.save()
            
            # Actualizar asiento contable
            if hasattr(self, 'asiento_contable'):
                self.asiento_contable.estado = nuevo_estado
                self.asiento_contable.save(update_fields=['estado'])

    @property
    def puede_conciliarse(self):
        """Indica si la transacción puede ser conciliada"""
        return self.estado in [TransaccionEstado.PENDIENTE, TransaccionEstado.LIQUIDADA]

    @property
    def requiere_atencion(self):
        """Indica si la transacción requiere atención (pendiente por mucho tiempo)"""
        if self.estado == TransaccionEstado.PENDIENTE:
            days_pending = (timezone.now().date() - self.fecha).days
            return days_pending > 5  # Más de 5 días pendiente
        return False



class Transferencia(models.Model):
    """Modelo temporal - mantener para compatibilidad con migraciones existentes"""
    origen = models.OneToOneField(
        'Transaccion',
        on_delete=models.CASCADE,
        related_name="transferencia_saliente",
    )
    destino = models.OneToOneField(
        'Transaccion', 
        on_delete=models.CASCADE,
        related_name="transferencia_entrante",
    )

    class Meta:
        db_table = 'core_transferencia'  # Mantener tabla existente

    def __str__(self):
        return f"Transferencia legacy"


class Recurrencia(models.Model):
    cuenta_servicio = models.ForeignKey(
        Cuenta,
        on_delete=models.RESTRICT,
        limit_choices_to={
            "tipo__codigo": "SERV"
        },
    )
    monto_estimado  = models.DecimalField(max_digits=12, decimal_places=2)
    periodicidad    = models.CharField(
        max_length=100,
        help_text="RRULE iCal (ej. FREQ=MONTHLY;BYMONTHDAY=10)",
    )
    proxima_fecha   = models.DateField()
    activo          = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.cuenta_servicio} cada {self.periodicidad}"


def generar_movs_recibo(
    cuenta_servicio: Cuenta,
    monto: Decimal,
    categoria: "Categoria",
    fecha_recibo,
    *,
    registrar_pago=False,
    cuenta_pago: Cuenta | None = None,
    fecha_pago=None,
    descripcion="Recibo"
):
    """
    Devuelve (cargo_serv, abono_serv | None, cargo_pago | None)
    """
    with transaction.atomic():
        # Cargo (aumenta) al servicio/proveedor
        cargo_serv = Transaccion.objects.create(
            monto=monto,
            tipo=TransaccionTipo.INGRESO,   # Produce CARGO en cuenta de servicio
            fecha=fecha_recibo,
            descripcion=descripcion,
            cuenta_servicio=cuenta_servicio,
            medio_pago=cuenta_servicio,
            categoria=categoria,
        )

        abono_serv = cargo_pago = None
        if registrar_pago:
            if not (cuenta_pago and fecha_pago):
                raise ValueError("Pago inmediato requiere cuenta_pago y fecha_pago")
            # Abono (disminuye) al servicio/proveedor al registrar el pago
            abono_serv = Transaccion.objects.create(
                monto=monto,
                tipo=TransaccionTipo.GASTO,  # Produce ABONO en cuenta de servicio
                fecha=fecha_pago,
                descripcion=f"Pago {descripcion}",
                cuenta_servicio=cuenta_servicio,
                medio_pago=cuenta_servicio,
                categoria=categoria,

            )
            # Cargo (dinero sale) en la cuenta de pago
            cargo_pago = Transaccion.objects.create(
                monto=monto,
                tipo=TransaccionTipo.GASTO,  # ABONO en cuenta de pago según lógica en save()
                fecha=fecha_pago,
                descripcion=f"Pago {descripcion}",
                medio_pago=cuenta_pago,
                categoria=categoria,

            )
        return cargo_serv, abono_serv, cargo_pago


# --- MODELO ÚNICO FLEXIBLE PARA PERÍODOS ------------------------------
class Periodo(models.Model):
    TIPO_CHOICES = (
        ('TDC',  'Tarjeta de Crédito'),
        ('SERV', 'Servicio'),
        ('DEB',  'Débito'),
        ('EFE',  'Efectivo'),
    )

    cuenta = models.ForeignKey("Cuenta", on_delete=models.RESTRICT, related_name="periodos")
    tipo = models.CharField(
        max_length=10, 
        choices=TIPO_CHOICES, 
        blank=True,  # Permite vacío
        null=True,   # Permite NULL en BD
        default=None
    )
    fecha_corte = models.DateField(null=True, blank=True)
    fecha_limite_pago = models.DateField(null=True, blank=True)
    monto_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        null=True,  # Permitir NULL en BD
        blank=True  # Permitir vacío en formularios
    )

    # Campos específicos para tarjetas de crédito (opcionales)
    pago_minimo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    pago_no_intereses = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Campos específicos para servicios (opcionales)
    monto_pronto_pago = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fecha_pronto_pago = models.DateField(null=True, blank=True)

    descripcion = models.CharField(max_length=120, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)

    # Nuevo: fin real del periodo (puede coincidir con fecha_corte)
    fecha_fin_periodo = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha de fin del periodo (generalmente igual a fecha_corte)"
    )

    # Gestión de verificación (abierto/cerrado)
    cerrado = models.BooleanField(default=False)
    cerrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="periodos_cerrados"
    )
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("PAGADO",    "Pagado"),
        ("CANCELADO", "Cancelado"),
    ]
    estado = models.CharField(
        max_length=10,
        choices=ESTADOS,
        default="PENDIENTE",  # Valor por defecto
        blank=True            # Permite blanco en formularios
    )

    generado = models.BooleanField(
        default=False,
        verbose_name="Estado de cuenta generado"
    )

    # Permite decidir si se arrastra o no el saldo previo al iniciar el periodo
    usar_saldo_prev = models.BooleanField(
        default=True,
        verbose_name="Usar saldo anterior como saldo inicial"
    )

    # Saldo inicial editable manualmente (opcional)
    saldo_inicial_manual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Saldo inicial manual"
    )

    # Enlace al periodo inmediatamente anterior de la MISMA cuenta
    periodo_anterior = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='periodo_siguiente'
    )

    class Meta:
        ordering = ["-fecha_corte"]

    def __str__(self):
        return f"{self.cuenta} {self.fecha_corte:%b %Y}"

    # --- Propiedades dinámicas -----------------------------------------
    @property
    def total_cargos(self):
        # v0.6.0: Actualizar para usar cuenta_origen y cuenta_destino
        if self.cuenta.naturaleza == "ACREEDORA":
            # Para tarjetas (pasivo): cargos = pagos hacia esta cuenta (disminuye deuda)
            base_pagos = self.transacciones.filter(cuenta_destino=self.cuenta)
            return base_pagos.aggregate(Sum("monto"))["monto__sum"] or 0
        else:
            # Para cuentas deudoras (activo): cargos = dinero que sale de esta cuenta
            base_salidas = self.transacciones.filter(cuenta_origen=self.cuenta)
            return base_salidas.aggregate(Sum("monto"))["monto__sum"] or 0

    @property
    def total_abonos(self):
        # v0.6.0: Actualizar para usar cuenta_origen y cuenta_destino
        if self.cuenta.naturaleza == "ACREEDORA":
            # Para tarjetas: abonos = dinero que sale de esta cuenta (aumenta deuda)
            base_compras = self.transacciones.filter(cuenta_origen=self.cuenta)
            return base_compras.aggregate(Sum("monto"))["monto__sum"] or 0
        else:
            # Para cuentas deudoras: abonos = dinero que entra a esta cuenta
            base_entradas = self.transacciones.filter(cuenta_destino=self.cuenta)
            return base_entradas.aggregate(Sum("monto"))["monto__sum"] or 0

    @property
    def saldo(self):
        # El saldo final debe ser: saldo_inicial + (total_abonos - total_cargos) para acreedoras
        # o saldo_inicial + (total_cargos - total_abonos) para deudoras
        if self.cuenta.naturaleza == "ACREEDORA":
            return self.saldo_inicial + (self.total_abonos - self.total_cargos)
        else:
            return self.saldo_inicial + (self.total_cargos - self.total_abonos)


    @property
    def saldo_inicial(self):
        """Devuelve el saldo inicial del periodo."""
        # 1) Valor manual prevalece
        if self.saldo_inicial_manual is not None:
            return self.saldo_inicial_manual

        # 2) Si se decidió no usar saldo previo → 0
        if not self.usar_saldo_prev:
            return 0

        # 3) Tomar saldo final del periodo anterior, si existe
        if self.periodo_anterior_id:
            return self.periodo_anterior.saldo_final

        # 4) Primer periodo → calcula histórico v0.6.0
        from django.db.models import Q
        return (
            Transaccion.objects
            .filter(Q(cuenta_origen=self.cuenta) | Q(cuenta_destino=self.cuenta), fecha__lt=self.fecha_corte)
            .aggregate(total=Sum("monto"))["total"] or 0
        )

    @property
    def saldo_final(self):
        """Saldo al cierre del periodo."""
        if self.cuenta.naturaleza == "ACREEDORA":
            return self.saldo_inicial + (self.total_abonos - self.total_cargos)
        else:
            return self.saldo_inicial + (self.total_cargos - self.total_abonos)

    def save(self, *args, **kwargs):
        # Fecha_inicio siempre = fecha_corte
        self.fecha_inicio = self.fecha_corte
        super().save(*args, **kwargs)


# === MODELOS DE DOBLE PARTIDA (CAPA SUBYACENTE) ======================

class AsientoContable(models.Model):
    """
    Asiento contable que agrupa las partidas de doble entrada.
    Transparente al usuario - generado automáticamente.
    """
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255)
    
    # Referencia a la transacción unificada del usuario
    transaccion_origen = models.OneToOneField(
        'Transaccion',
        on_delete=models.CASCADE,
        related_name='asiento_contable',
        null=True,
        blank=True
    )
    
    estado = models.CharField(
        max_length=12,
        choices=TransaccionEstado.choices,
        default=TransaccionEstado.PENDIENTE
    )
    
    # Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asientos_creados'
    )

    class Meta:
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['estado']),
            models.Index(fields=['transaccion_origen']),
        ]
        ordering = ['-fecha', '-creado_en']

    def clean(self):
        """Validar que el asiento esté balanceado"""
        if self.pk:
            total_debitos = self.partidas.aggregate(
                total=Sum('debito'))['total'] or Decimal('0.00')
            total_creditos = self.partidas.aggregate(
                total=Sum('credito'))['total'] or Decimal('0.00')
            
            if total_debitos != total_creditos:
                raise ValidationError(
                    f"Asiento no balanceado: Débitos={total_debitos}, Créditos={total_creditos}"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Asiento {self.fecha}: {self.descripcion[:50]}"

    @property
    def total_debitos(self):
        return self.partidas.aggregate(Sum('debito'))['debito__sum'] or Decimal('0.00')
    
    @property
    def total_creditos(self):
        return self.partidas.aggregate(Sum('credito'))['credito__sum'] or Decimal('0.00')
    
    @property
    def esta_balanceado(self):
        return self.total_debitos == self.total_creditos


class PartidaContable(models.Model):
    """
    Partida individual de doble entrada (debe/haber).
    Cada asiento tiene múltiples partidas que suman cero.
    """
    asiento = models.ForeignKey(
        AsientoContable,
        on_delete=models.CASCADE,
        related_name='partidas'
    )
    cuenta = models.ForeignKey(
        'Cuenta',
        on_delete=models.RESTRICT,
        related_name='partidas_contables'
    )
    
    # Importes de debe y haber - solo uno puede tener valor
    debito = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Importe del debe"
    )
    credito = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Importe del haber"
    )
    
    descripcion = models.CharField(max_length=255, blank=True)
    
    # Referencia opcional a la transacción para trazabilidad
    transaccion_referencia = models.ForeignKey(
        'Transaccion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partidas_generadas'
    )

    class Meta:
        indexes = [
            models.Index(fields=['cuenta', 'asiento']),
            models.Index(fields=['asiento', 'debito']),
            models.Index(fields=['asiento', 'credito']),
        ]

    def clean(self):
        """Validar que solo uno de débito o crédito tenga valor"""
        if self.debito and self.credito:
            raise ValidationError("Una partida no puede tener débito Y crédito")
        
        if not self.debito and not self.credito:
            raise ValidationError("Una partida debe tener débito O crédito")
            
        if self.debito and self.debito <= 0:
            raise ValidationError("El débito debe ser mayor a cero")
            
        if self.credito and self.credito <= 0:
            raise ValidationError("El crédito debe ser mayor a cero")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        importe = self.debito if self.debito else self.credito
        tipo = "Débito" if self.debito else "Crédito"
        return f"{self.cuenta.nombre} - {tipo}: ${importe}"

    @property
    def importe(self):
        """Devuelve el importe de la partida (positivo para débito, negativo para crédito)"""
        return self.debito if self.debito else -self.credito

    @property
    def importe_absoluto(self):
        """Devuelve el valor absoluto del importe"""
        return self.debito if self.debito else self.credito


# === MODELOS PARA CONCILIACIÓN AUTOMÁTICA =============================

class ImportacionBancaria(models.Model):
    """Registro de importaciones de estados de cuenta bancarios"""
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='importaciones')
    archivo_nombre = models.CharField(max_length=255)
    fecha_importacion = models.DateTimeField(auto_now_add=True)
    periodo_inicio = models.DateField()
    periodo_fin = models.DateField()
    total_registros = models.IntegerField(default=0)
    registros_procesados = models.IntegerField(default=0)
    registros_conciliados = models.IntegerField(default=0)
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='importaciones_realizadas'
    )
    
    class Meta:
        ordering = ['-fecha_importacion']
        
    def __str__(self):
        return f"Importación {self.cuenta.nombre} - {self.fecha_importacion:%d/%m/%Y}"


class MovimientoBancario(models.Model):
    """Movimientos importados del estado de cuenta bancario"""
    importacion = models.ForeignKey(
        ImportacionBancaria, 
        on_delete=models.CASCADE, 
        related_name='movimientos'
    )
    
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255)
    referencia = models.CharField(max_length=100, blank=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_posterior = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Matching con transacciones internas
    transaccion_conciliada = models.ForeignKey(
        Transaccion,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='movimiento_bancario_match'
    )
    
    CONFIANZA_MATCH = [
        ('EXACTA', 'Coincidencia Exacta (99%)'),
        ('ALTA', 'Alta Confianza (95%)'),
        ('MEDIA', 'Media Confianza (90%)'),
        ('BAJA', 'Baja Confianza (85%)'),
        ('MANUAL', 'Revisión Manual'),
    ]
    
    confianza_match = models.CharField(
        max_length=10,
        choices=CONFIANZA_MATCH,
        default='MANUAL'
    )
    
    conciliado = models.BooleanField(default=False)
    fecha_conciliacion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['fecha', 'monto']),
            models.Index(fields=['referencia']),
            models.Index(fields=['conciliado']),
        ]
        ordering = ['-fecha']
    
    def __str__(self):
        signo = "+" if self.monto >= 0 else ""
        return f"{self.fecha}: {signo}${self.monto} - {self.descripcion[:50]}"
    
    def buscar_coincidencias(self):
        """Busca transacciones internas que coincidan con este movimiento bancario"""
        cuenta = self.importacion.cuenta
        
        # Criterios de búsqueda con diferentes niveles de confianza
        candidatos = []
        
        # 1. Coincidencia EXACTA: fecha, monto y cuenta
        exactas = Transaccion.objects.filter(
            fecha=self.fecha,
            monto=abs(self.monto),
            cuenta_origen=cuenta,
            estado=TransaccionEstado.PENDIENTE
        )
        
        for t in exactas:
            candidatos.append({
                'transaccion': t,
                'confianza': 'EXACTA',
                'score': 99,
                'criterios': ['fecha_exacta', 'monto_exacto', 'cuenta_correcta']
            })
        
        # 2. Coincidencia ALTA: ±1 día, monto exacto
        if not candidatos:
            rango_fechas = Transaccion.objects.filter(
                fecha__range=[
                    self.fecha - timedelta(days=1),
                    self.fecha + timedelta(days=1)
                ],
                monto=abs(self.monto),
                cuenta_origen=cuenta,
                estado=TransaccionEstado.PENDIENTE
            )
            
            for t in rango_fechas:
                candidatos.append({
                    'transaccion': t,
                    'confianza': 'ALTA',
                    'score': 95,
                    'criterios': ['fecha_cercana', 'monto_exacto', 'cuenta_correcta']
                })
        
        # 3. Coincidencia MEDIA: ±3 días, monto similar (±5%)
        if not candidatos:
            tolerancia_monto = abs(self.monto) * Decimal('0.05')  # 5% tolerancia
            monto_min = abs(self.monto) - tolerancia_monto
            monto_max = abs(self.monto) + tolerancia_monto
            
            similares = Transaccion.objects.filter(
                fecha__range=[
                    self.fecha - timedelta(days=3),
                    self.fecha + timedelta(days=3)
                ],
                monto__range=[monto_min, monto_max],
                cuenta_origen=cuenta,
                estado=TransaccionEstado.PENDIENTE
            )
            
            for t in similares:
                candidatos.append({
                    'transaccion': t,
                    'confianza': 'MEDIA',
                    'score': 90,
                    'criterios': ['fecha_aproximada', 'monto_similar', 'cuenta_correcta']
                })
        
        return candidatos
    
    def aplicar_match_automatico(self, umbral_confianza=95):
        """Aplica matching automático si la confianza es suficiente"""
        candidatos = self.buscar_coincidencias()
        
        if candidatos:
            mejor_candidato = max(candidatos, key=lambda x: x['score'])
            
            if mejor_candidato['score'] >= umbral_confianza:
                transaccion = mejor_candidato['transaccion']
                
                # Marcar transacción como liquidada
                transaccion.marcar_liquidada(
                    referencia_bancaria=self.referencia,
                    saldo_posterior=self.saldo_posterior
                )
                
                # Vincular movimiento bancario con transacción
                self.transaccion_conciliada = transaccion
                self.confianza_match = mejor_candidato['confianza']
                self.conciliado = True
                self.fecha_conciliacion = timezone.now()
                self.save()
                
                return True, f"Match automático con {mejor_candidato['confianza']} confianza"
        
        return False, "No se encontraron coincidencias suficientes"


# --- Historial de cambios de estado (abrir/cerrar) ---------------------

class PeriodoEstadoLog(models.Model):
    periodo = models.ForeignKey(
        'Periodo',
        on_delete=models.CASCADE,
        related_name='logs'
    )
    ACCIONES = [
        ("ABRIR", "Abrir"),
        ("CERRAR", "Cerrar"),
        ("ACTUALIZAR", "Actualizar")
    ]
    
    accion = models.CharField(
        max_length=10,
        choices=ACCIONES
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,  # Permitir valores nulos
        blank=True  # Permitir en formularios
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        periodo_str = str(self.periodo) if self.periodo else "Periodo desconocido"
        return f"{periodo_str} – {self.get_accion_display()} ({self.timestamp:%d/%m/%Y %H:%M})"


class PeriodoPDFView(LoginRequiredMixin, View):
    def get(self, request, pk):
        periodo = get_object_or_404(Periodo, pk=pk)
        movs = periodo.transacciones.order_by("fecha")
        
        # Crear respuesta HTTP con PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="estado_cuenta_{periodo.id}.pdf"'
        
        # Crear PDF
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter
        
        # Encabezado
        p.setFont("Helvetica-Bold", 16)
        p.drawString(1*inch, height-1*inch, f"Estado de Cuenta: {periodo.cuenta.nombre}")
        p.setFont("Helvetica", 12)
        p.drawString(1*inch, height-1.2*inch, f"Periodo: {periodo.fecha_corte} - {periodo.fecha_fin_periodo}")
        p.drawString(1*inch, height-1.4*inch, f"Saldo inicial: ${periodo.saldo_inicial}")
        
        # Tabla de movimientos
        p.setFont("Helvetica-Bold", 10)
        p.drawString(1*inch, height-1.6*inch, "Fecha")
        p.drawString(2.5*inch, height-1.6*inch, "Descripción")
        p.drawString(5*inch, height-1.6*inch, "Monto")
        
        y_position = height - 1.8*inch
        p.setFont("Helvetica", 10)
        
        for mov in movs:
            p.drawString(1*inch, y_position, str(mov.fecha))
            p.drawString(2.5*inch, y_position, mov.descripcion[:50])  # Limitar a 50 caracteres
            p.drawString(5*inch, y_position, f"${mov.monto}")
            y_position -= 0.2*inch
            
            # Nueva página si se acaba el espacio
            if y_position < 1*inch:
                p.showPage()
                y_position = height - 1*inch
        
        # Totales
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1*inch, y_position - 0.4*inch, f"Total Cargos: ${periodo.total_cargos}")
        p.drawString(1*inch, y_position - 0.6*inch, f"Total Abonos: ${periodo.total_abonos}")
        p.drawString(1*inch, y_position - 0.8*inch, f"Saldo Final: ${periodo.saldo}")
        
        p.showPage()
        p.save()
        return response


# ===================================================================
# MODELOS PARA IMPORTACIÓN BBVA ASISTIDA
# ===================================================================

class EstadoCuentaBBVA(models.TextChoices):
    """Estados del proceso de importación BBVA"""
    SUBIDO = 'SUBIDO', 'Archivo subido'
    ANALIZADO = 'ANALIZADO', 'Análisis completado'
    VALIDANDO = 'VALIDANDO', 'Validando con usuario'
    PROCESANDO = 'PROCESANDO', 'Creando transacciones'
    COMPLETADO = 'COMPLETADO', 'Importación completada'
    ERROR = 'ERROR', 'Error en proceso'
    CANCELADO = 'CANCELADO', 'Cancelado por usuario'


class ImportacionBBVA(models.Model):
    """Registro maestro de cada importación BBVA"""
    
    # Archivos y usuario
    archivo = models.FileField(upload_to='importaciones/bbva/%Y/%m/')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    
    # Cuenta objetivo
    cuenta_bbva = models.ForeignKey(
        Cuenta, 
        on_delete=models.CASCADE,
        help_text="Cuenta BBVA 5019 de tipo DÉBITO"
    )
    numero_cuenta_detectado = models.CharField(max_length=20, blank=True)
    
    # Control del proceso
    estado = models.CharField(
        max_length=12,
        choices=EstadoCuentaBBVA.choices,
        default=EstadoCuentaBBVA.SUBIDO
    )
    paso_actual = models.IntegerField(default=1)
    total_pasos = models.IntegerField(default=6)
    
    # Datos del archivo
    fecha_primer_movimiento = models.DateField(null=True)
    fecha_ultimo_movimiento = models.DateField(null=True)
    total_movimientos_archivo = models.IntegerField(default=0)
    saldo_inicial_archivo = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    saldo_final_archivo = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    
    # Resultados del procesamiento
    movimientos_nuevos = models.IntegerField(default=0)
    movimientos_duplicados = models.IntegerField(default=0)
    cuentas_creadas = models.IntegerField(default=0)
    categorias_creadas = models.IntegerField(default=0)
    
    # Metadatos
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    log_proceso = models.JSONField(default=dict, blank=True)
    notas_usuario = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = "Importación BBVA"
        verbose_name_plural = "Importaciones BBVA"

    def __str__(self):
        return f"BBVA Import {self.id} - {self.estado} ({self.fecha_inicio.strftime('%d/%m/%Y')})"


class MovimientoBBVATemporal(models.Model):
    """Almacén temporal de movimientos durante el proceso de importación"""
    
    importacion = models.ForeignKey(
        ImportacionBBVA, 
        on_delete=models.CASCADE, 
        related_name='movimientos_temporales'
    )
    
    # Datos originales del archivo BBVA
    fila_excel = models.IntegerField()
    fecha_original = models.DateField()
    descripcion_original = models.TextField()
    cargo_original = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    abono_original = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_original = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Análisis automático
    es_gasto = models.BooleanField()  # True si cargo > 0
    monto_calculado = models.DecimalField(max_digits=12, decimal_places=2)
    tipo_detectado = models.CharField(max_length=50, blank=True)
    categoria_sugerida = models.CharField(max_length=100, blank=True)
    
    # Validaciones del usuario
    descripcion_limpia = models.CharField(max_length=255, blank=True)
    categoria_confirmada = models.ForeignKey(
        Categoria, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )
    cuenta_destino_sugerida = models.CharField(max_length=100, blank=True)
    cuenta_destino_confirmada = models.ForeignKey(
        Cuenta,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='movimientos_bbva_destino'
    )
    
    # Estado de procesamiento
    validado_por_usuario = models.BooleanField(default=False)
    es_duplicado = models.BooleanField(default=False)
    transaccion_existente = models.ForeignKey(
        Transaccion,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='duplicados_bbva'
    )
    transaccion_creada = models.ForeignKey(
        Transaccion,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='origen_bbva'
    )
    
    ignorar = models.BooleanField(default=False)
    notas_usuario = models.TextField(blank=True)
    
    class Meta:
        ordering = ['fila_excel']
        unique_together = ['importacion', 'fila_excel']

    def __str__(self):
        return f"Mov #{self.fila_excel}: {self.descripcion_original[:50]}..."

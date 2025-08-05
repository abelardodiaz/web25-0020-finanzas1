# <!-- file: core/models.py -->
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from uuid import uuid4
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import path

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

    objects = CuentaManager()

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.tipo.nombre})"

    # Saldo "al vuelo" - actualizado para v0.6.0
    def saldo(self):
        # Sumar transacciones donde esta cuenta es origen (salidas)
        salidas = self.transacciones_origen.aggregate(
            total=models.Sum("monto"))["total"] or Decimal("0.00")
        
        # Sumar transacciones donde esta cuenta es destino (entradas) 
        entradas = self.transacciones_destino.aggregate(
            total=models.Sum("monto"))["total"] or Decimal("0.00")
        
        # Para cuentas deudoras: saldo inicial + entradas - salidas
        # Para cuentas acreedoras: saldo inicial + salidas - entradas (deuda)
        if self.naturaleza == "DEUDORA":
            return self.saldo_inicial + entradas - salidas
        else:  # ACREEDORA
            return self.saldo_inicial + salidas - entradas

    def aplicar_cargo(self, monto):
        """
        Devuelve el monto con el signo correcto según naturaleza.
        Cargo ➜ + en deudoras / - en acreedoras
        """
        return monto if self.naturaleza == "DEUDORA" else -monto

    def aplicar_abono(self, monto):
        """
        Abono ➜ - en deudoras / + en acreedoras
        """
        return -monto if self.naturaleza == "DEUDORA" else monto    #Helpers para saber si un movimiento es cargo o abono
        

class CategoriaTipo(models.TextChoices):
    PERSONAL = "PERSONAL", _("Personal")
    NEGOCIO  = "NEGOCIO", _("Negocio")
    MIXTO  = "MIXTO", _("Mixto")
    TERCEROS  = "TERCEROS", _("Terceros")

class Categoria(models.Model):
    nombre    = models.CharField(max_length=100)
    tipo      = models.CharField(
        max_length=10,
        choices=CategoriaTipo.choices,
        default=CategoriaTipo.PERSONAL,
    )
    padre     = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        related_name="subcategorias",
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

    class Meta:
        indexes = [
            models.Index(fields=["fecha"]),
            models.Index(fields=["categoria"]),
            models.Index(fields=["cuenta_origen"]),
            models.Index(fields=["tipo"]),
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
        """Inferir tipo automáticamente antes de guardar"""
        if self.cuenta_destino:
            # Es transferencia entre cuentas
            self.tipo = TransaccionTipo.TRANSFERENCIA
        elif self.categoria:
            # Determinar si es gasto o ingreso por la categoría
            if self.categoria.tipo in ['PERSONAL', 'NEGOCIO']:
                # La mayoría de gastos personales/negocio son gastos
                # TODO: Mejorar lógica según categorías específicas
                self.tipo = TransaccionTipo.GASTO
            else:
                self.tipo = TransaccionTipo.INGRESO
        
        # Asegurar monto positivo
        self.monto = abs(self.monto)
        
        super().save(*args, **kwargs)

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

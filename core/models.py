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

    NATURALEZA = [
        ("DEUDORA", "Deudora"),
        ("ACREEDORA", "Acreedora"),
    ]
    naturaleza = models.CharField(max_length=10, choices=NATURALEZA, default="DEUDORA")


    class Meta:
        verbose_name = "tipo de cuenta"
        verbose_name_plural = "tipos de cuenta"

    def __str__(self):
        return f"{self.nombre} ({self.grupo})"

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

    # Saldo “al vuelo”
    def saldo(self):
        return self.transacciones_pago.aggregate(
            total=models.Sum("monto"))["total"] or Decimal("0.00")

    def aplicar_cargo(self, monto):
        """
        Devuelve el monto con el signo correcto según naturaleza.
        Cargo ➜ + en deudoras / - en acreedoras
        """
        return  monto if self.tipo.naturaleza == "DEUDORA" else -monto

    def aplicar_abono(self, monto):
        """
        Abono ➜ - en deudoras / + en acreedoras
        """
        return -monto if self.tipo.naturaleza == "DEUDORA" else monto    #Helpers para saber si un movimiento es cargo o abono
        

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


class TransaccionTipo(models.TextChoices):
    INGRESO       = "INGRESO", _("Ingreso")
    GASTO         = "GASTO", _("Gasto")
    TRANSFERENCIA = "TRANSFERENCIA", _("Transferencia interna")


class Transaccion(models.Model):
    monto               = models.DecimalField(max_digits=12, decimal_places=2)
    tipo                = models.CharField(
        max_length=13,
        choices=TransaccionTipo.choices,
        default=TransaccionTipo.GASTO,
    )
    fecha               = models.DateField()
    descripcion         = models.CharField(max_length=255, blank=True)
    cuenta_servicio     = models.ForeignKey(
        Cuenta,
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        related_name="transacciones_servicio",
        help_text="Proveedor o servicio (Telcel, CFE…) si aplica",
    )
    categoria           = models.ForeignKey(
        Categoria,
        on_delete=models.RESTRICT,
        related_name="transacciones",
    )
    medio_pago          = models.ForeignKey(
        Cuenta,
        on_delete=models.RESTRICT,
        related_name="transacciones_pago",
    )

    # === Nuevos campos para partida doble ===
    grupo_uuid = models.UUIDField(default=uuid4, editable=False)
    ajuste = models.BooleanField(
        default=False,
        help_text="Marca este movimiento como ajuste para evitar la creación automática del segundo asiento."
    )

    moneda              = models.CharField(
        max_length=3,
        choices=Moneda.choices,
        default=Moneda.MXN,
    )
    periodo      = models.ForeignKey(
        "Periodo",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transacciones",
    )
    conciliado          = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["fecha"]),
            models.Index(fields=["categoria",]),
            models.Index(fields=["medio_pago"]),
        ]
        ordering = ["-fecha"]

    def __str__(self):
        signo = "-" if self.tipo == TransaccionTipo.GASTO else "+"
        return f"{self.fecha}: {signo}${self.monto} {self.categoria}"


    def save(self, *args, **kwargs):
        # Solo aplicar lógica de signo si no es ajuste
        if not self.ajuste:
            # Obtener naturaleza de la cuenta de pago
            naturaleza = self.medio_pago.tipo.naturaleza if self.medio_pago and self.medio_pago.tipo else None
            
            if self.tipo == TransaccionTipo.INGRESO:
                # Lógica para INGRESOS
                if naturaleza == "DEUDORA":
                    # Activos: entra dinero → CARGO (positivo)
                    self.monto = abs(self.monto)
                elif naturaleza == "ACREEDORA":
                    # Pasivos: entra dinero (pago de deuda) → CARGO (negativo)
                    self.monto = -abs(self.monto)
            
            elif self.tipo == TransaccionTipo.GASTO:
                # Lógica para GASTOS
                if naturaleza == "DEUDORA":
                    # Activos: gastos disminuyen (abono) -> monto negativo
                    self.monto = -abs(self.monto)
                elif naturaleza == "ACREEDORA":
                    # Pasivos: gastos aumentan (abono) -> monto positivo
                    self.monto = abs(self.monto)
        
        super().save(*args, **kwargs)
       



class Transferencia(models.Model):
    origen  = models.OneToOneField(
        Transaccion,
        on_delete=models.CASCADE,
        related_name="transferencia_saliente",
        limit_choices_to={"tipo": TransaccionTipo.TRANSFERENCIA},
    )
    destino = models.OneToOneField(
        Transaccion,
        on_delete=models.CASCADE,
        related_name="transferencia_entrante",
        limit_choices_to={"tipo": TransaccionTipo.TRANSFERENCIA},
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(origen=models.F("destino")),
                name="origen_destino_distintos",
            )
        ]

    def __str__(self):
        return f"{self.origen.medio_pago} ➜ {self.destino.medio_pago} (${self.origen.monto})"


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
        if self.cuenta.tipo.naturaleza == "ACREEDORA":
            # Para tarjetas (pasivo): cargos = pagos registrados en esta cuenta (montos < 0)
            base_neg = self.transacciones.filter(medio_pago=self.cuenta, monto__lt=0)
            return -(base_neg.aggregate(Sum("monto"))["monto__sum"] or 0)
        else:
            # Para cuentas deudoras (activo): cargos = salidas de dinero de la cuenta (montos > 0 en esta cuenta)
            base_pos = self.transacciones.filter(medio_pago=self.cuenta, monto__gt=0)
            return base_pos.aggregate(Sum("monto"))["monto__sum"] or 0

    @property
    def total_abonos(self):
        if self.cuenta.tipo.naturaleza == "ACREEDORA":
            # Para tarjetas: abonos = compras registradas en esta cuenta (montos > 0)
            base_pos = self.transacciones.filter(medio_pago=self.cuenta, monto__gt=0)
            return base_pos.aggregate(Sum("monto"))["monto__sum"] or 0
        else:
            # Para cuentas deudoras: abonos = retiros registrados en esta cuenta (montos < 0)
            base_neg = self.transacciones.filter(medio_pago=self.cuenta, monto__lt=0)
            return -(base_neg.aggregate(Sum("monto"))["monto__sum"] or 0)

    @property
    def saldo(self):
        # El saldo final debe ser: saldo_inicial + (total_abonos - total_cargos) para acreedoras
        # o saldo_inicial + (total_cargos - total_abonos) para deudoras
        if self.cuenta.tipo.naturaleza == "ACREEDORA":
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

        # 4) Primer periodo → calcula histórico
        return (
            Transaccion.objects
            .filter(medio_pago=self.cuenta, fecha__lt=self.fecha_corte)
            .aggregate(total=Sum("monto"))["total"] or 0
        )

    @property
    def saldo_final(self):
        """Saldo al cierre del periodo."""
        if self.cuenta.tipo.naturaleza == "ACREEDORA":
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

# <!-- file: core/models.py -->
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class Moneda(models.TextChoices):
    MXN = "MXN", _("Peso MXN")
    USD = "USD", _("Dólar USD")


class TipoCuenta(models.Model):
    codigo  = models.CharField(max_length=10, unique=True)
    nombre  = models.CharField(max_length=50)
    GRUPOS  = [
        ("DEB", "Debito"),
        ("SER", "Servicios"),
        ("CRE", "Creditos"),
    ]
    grupo   = models.CharField(max_length=3, choices=GRUPOS, default="DEB",)

    class Meta:
        verbose_name = "tipo de cuenta"
        verbose_name_plural = "tipos de cuenta"

    def __str__(self):
        return f"{self.nombre} ({self.grupo})"

class Cuenta(models.Model):
    nombre            = models.CharField(max_length=100, unique=True)
    tipo              = models.ForeignKey(TipoCuenta, on_delete=models.RESTRICT,
                                          related_name="cuentas")
    moneda            = models.CharField(max_length=3, choices=Moneda.choices,
                                          default=Moneda.MXN)
    activo            = models.BooleanField(default=True)

    # 🔸 campos que aparecen en «SALDOS - Cuentas.csv»
    referencia        = models.CharField(max_length=50, blank=True)
    ref_comentario    = models.CharField(max_length=120, blank=True)
    no_cliente        = models.CharField(max_length=30,  blank=True)
    fecha_apertura    = models.DateField(null=True, blank=True)
    no_contrato       = models.CharField(max_length=40,  blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.tipo.nombre})"

    # Saldo “al vuelo”
    def saldo(self):
        return self.transacciones_pago.aggregate(
            total=models.Sum("monto"))["total"] or Decimal("0.00")


class CategoriaTipo(models.TextChoices):
    PERSONAL = "PERSONAL", _("Personal")
    NEGOCIO  = "NEGOCIO", _("Negocio")


class Categoria(models.Model):
    nombre    = models.CharField(max_length=100)
    tipo      = models.CharField(
        max_length=10,
        choices=CategoriaTipo.choices,
        default=CategoriaTipo.PERSONAL,
    )
    padre     = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        related_name="subcategorias",
    )

    class Meta:
        unique_together = ("nombre", "padre")      # evita duplicados en jerarquía
        ordering        = ["nombre"]

    def __str__(self):
        return self.nombre if not self.padre else f"{self.padre} › {self.nombre}"


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
    
    moneda              = models.CharField(
        max_length=3,
        choices=Moneda.choices,
        default=Moneda.MXN,
    )
    # periodo      = models.ForeignKey( 
    #     "Periodo",
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name="transacciones",
    # )
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
        """
        Garantiza que:
          • GASTO   → monto negativo
          • INGRESO → monto positivo
        """
        if self.tipo == TransaccionTipo.GASTO  and self.monto > 0:
            self.monto = -self.monto
        elif self.tipo == TransaccionTipo.INGRESO and self.monto < 0:
            self.monto = -self.monto

        if self.monto == 0:
            raise ValueError("El monto no puede ser cero")

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
        cargo_serv = Transaccion.objects.create(
            monto=-monto,
            tipo=TransaccionTipo.GASTO,
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
            abono_serv = Transaccion.objects.create(
                monto=monto,
                tipo=TransaccionTipo.INGRESO,
                fecha=fecha_pago,
                descripcion=f"Pago {descripcion}",
                cuenta_servicio=cuenta_servicio,
                medio_pago=cuenta_servicio,
                categoria=categoria,

            )
            cargo_pago = Transaccion.objects.create(
                monto=-monto,
                tipo=TransaccionTipo.GASTO,
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
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    fecha_corte = models.DateField(null=True, blank=True)
    fecha_limite_pago = models.DateField(null=True, blank=True)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Campos específicos para tarjetas de crédito (opcionales)
    pago_minimo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    pago_no_intereses = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Campos específicos para servicios (opcionales)
    monto_pronto_pago = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fecha_pronto_pago = models.DateField(null=True, blank=True)

    descripcion = models.CharField(max_length=120, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)

    descripcion        = models.CharField(max_length=120, blank=True)

    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("PAGADO",    "Pagado"),
        ("CANCELADO", "Cancelado"),
    ]
    estado = models.CharField(max_length=10,
                                         choices=ESTADOS,
                                         default="PENDIENTE")
    
    class Meta:
        ordering = ["-fecha_corte"]
    
    def __str__(self):
        return f"{self.cuenta} {self.fecha_corte:%b %Y}"

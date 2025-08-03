# ---------- BLOQUE MEJORADO ------------------------------------------
import django_filters
from django import forms
from .models import (
    Transaccion, Cuenta, Categoria, TipoCuenta            # ← importamos TipoCuenta
)

class TransaccionFilter(django_filters.FilterSet):
    fecha_desde = django_filters.DateFilter(
        field_name="fecha", lookup_expr="gte",
        label="Desde",
        widget=forms.DateInput(attrs={"type": "date"})
    )
    fecha_hasta = django_filters.DateFilter(
        field_name="fecha", lookup_expr="lte",
        label="Hasta",
        widget=forms.DateInput(attrs={"type": "date"})
    )

    # --- declaramos vacíos para evitar consultas tempranas -------------
    medio_pago = django_filters.ModelChoiceFilter(
        queryset=Cuenta.objects.none(),
        label="Cuenta / Medio de pago"
    )
    categoria = django_filters.ModelChoiceFilter(
        queryset=Categoria.objects.none(),
        label="Categoría"
    )

    # Nuevo filtro: Cuenta de servicio / proveedor
    cuenta_servicio = django_filters.ModelChoiceFilter(
        queryset=Cuenta.objects.none(),
        label="Cuenta servicio"
    )

    class Meta:
        model  = Transaccion
        fields = ["fecha_desde", "fecha_hasta", "medio_pago", "cuenta_servicio", "categoria"]

    # ------------ rellenamos los queryset en tiempo de ejecución -------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            tipo_serv = TipoCuenta.objects.get(codigo="SERV")
            self.filters["medio_pago"].queryset = Cuenta.objects.exclude(tipo=tipo_serv)
        except TipoCuenta.DoesNotExist:
            self.filters["medio_pago"].queryset = Cuenta.objects.all()

        # Cuentas de servicio (grupo SER)
        self.filters["cuenta_servicio"].queryset = Cuenta.objects.filter(tipo__grupo="SER")

        # todas las categorías son seguras una vez la tabla existe
        self.filters["categoria"].queryset = Categoria.objects.all()


# ------------------------------------------------------------------
# Filtro para listado de cuentas
# ------------------------------------------------------------------
class CuentaFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Nombre'
    )
    tipo = django_filters.ModelChoiceFilter(
        queryset=TipoCuenta.objects.all(),
        label='Tipo de cuenta'
    )

    class Meta:
        model = Cuenta
        fields = ['nombre', 'tipo']

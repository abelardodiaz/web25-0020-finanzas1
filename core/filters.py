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

    # --- Filtro por cuenta (busca en origen O destino) -------------
    cuenta = django_filters.ModelChoiceFilter(
        queryset=Cuenta.objects.none(),
        label="Cuenta",
        method='filter_by_cuenta'
    )
    
    categoria = django_filters.ModelChoiceFilter(
        queryset=Categoria.objects.none(),
        label="Categoría"
    )

    class Meta:
        model  = Transaccion
        fields = ["fecha_desde", "fecha_hasta", "categoria"]
    
    def filter_by_cuenta(self, queryset, name, value):
        """Filtra transacciones donde la cuenta aparece como origen O destino"""
        if value:
            from django.db.models import Q
            return queryset.filter(Q(cuenta_origen=value) | Q(cuenta_destino=value))
        return queryset

    # ------------ rellenamos los queryset en tiempo de ejecución -------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Todas las cuentas para el filtro
        self.filters["cuenta"].queryset = Cuenta.objects.all().order_by("nombre")
        
        # Todas las categorías
        self.filters["categoria"].queryset = Categoria.objects.all().order_by("nombre")


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

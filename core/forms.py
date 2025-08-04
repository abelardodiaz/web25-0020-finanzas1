from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from django import forms

from .models import (
    Categoria, Cuenta, Periodo, TipoCuenta, Transaccion, TransaccionTipo,
    generar_movs_recibo
)


class CuentaForm(forms.ModelForm):
    # Agregar campo para editar el grupo
    grupo = forms.ChoiceField(
        choices=TipoCuenta.GRUPOS,
        required=True,
        label="Grupo de cuenta"
    )
    naturaleza = forms.ChoiceField(
        choices=Cuenta.NATURALEZA,
        required=True,
        label="Naturaleza contable"
    )
    
    class Meta:
        model = Cuenta
        fields = ["nombre", "tipo", "grupo", "naturaleza"]
        
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        
        # Cambiar esta condición para evitar el error en cuentas nuevas
        if self.instance and self.instance.pk:
            # Si la cuenta ya existe, usar sus valores
            if self.instance.tipo_id:
                self.fields['grupo'].initial = self.instance.tipo.grupo
            if hasattr(self.instance, 'naturaleza'):
                self.fields['naturaleza'].initial = self.instance.naturaleza
            
    def save(self, commit: bool = True) -> Cuenta:
        cuenta = super().save(commit=False)
        grupo = self.cleaned_data['grupo']
        naturaleza = self.cleaned_data['naturaleza']
        
        # Actualizar solo el grupo del tipo de cuenta
        if cuenta.tipo:
            cuenta.tipo.grupo = grupo
            cuenta.tipo.save()
        
        # La naturaleza ahora se guarda directamente en la cuenta
        cuenta.naturaleza = naturaleza
        
        if commit:
            cuenta.save()
        return cuenta


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'tipo']


class TransaccionForm(forms.ModelForm):
    class Meta:
        model  = Transaccion
        fields = [
            "monto", "tipo", "fecha", "descripcion",
            "cuenta_servicio", "categoria", "medio_pago",
            "ajuste",
        ]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}, format='%Y-%m-%d'),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Etiquetas más descriptivas
        self.fields["medio_pago"].label = "Cuenta de pago"
        self.fields["cuenta_servicio"].label = "Servicio / Proveedor"
        self.fields["ajuste"].label = "Es ajuste (un solo movimiento)"
        # Mostrar sólo cuentas de pago (DEB, CRE, EFE) para medio_pago
        self.fields["medio_pago"].queryset = (
            Cuenta.objects.medios_pago().order_by("nombre") 
        )

        # -- Ajustes dinámicos para transferencias --
        tipo_value = self.data.get('tipo') if self.data else self.initial.get('tipo')
        if str(tipo_value) == str(TransaccionTipo.TRANSFERENCIA):
            self.fields["medio_pago"].label = "Cuenta origen"
            self.fields["cuenta_servicio"].label = "Cuenta destino"
            self.fields['cuenta_servicio'].queryset = Cuenta.objects.medios_pago().order_by("nombre")

        # Fuerza formato ISO para el campo fecha (requerido por input[type=date])
        if self.instance and self.instance.pk:
            self.initial['fecha'] = self.instance.fecha.isoformat()

        # Si no es transferencia, mantener filtro de servicio + SID
        if str(tipo_value) != str(TransaccionTipo.TRANSFERENCIA):
            self.fields['cuenta_servicio'].queryset = Cuenta.objects.filter(tipo__grupo="SER").order_by("nombre")

    def clean(self) -> dict[str, Any]:
        cleaned = super().clean()
        tipo = cleaned.get("tipo")
        if tipo == TransaccionTipo.TRANSFERENCIA:
            origen = cleaned.get("medio_pago")
            destino = cleaned.get("cuenta_servicio")
            if not origen or not destino:
                raise forms.ValidationError("Debe seleccionar cuenta origen y destino para una transferencia.")
            if origen == destino:
                raise forms.ValidationError("Las cuentas origen y destino deben ser distintas.")
        return cleaned

    def clean_monto(self) -> Decimal:
        monto = self.cleaned_data["monto"]
        if monto == 0:
            raise forms.ValidationError("El monto no puede ser cero.")
        return monto

class TransferenciaForm(forms.Form):
    cuenta_origen   = forms.ModelChoiceField(queryset=Cuenta.objects.all())
    cuenta_destino = forms.ModelChoiceField(
        label="Cuenta que recibe el dinero",
        queryset=Cuenta.objects.none(),    # ← inicio vacío
    )
    monto           = forms.DecimalField(min_value=Decimal("0.01"), max_digits=12, decimal_places=2)
    fecha           = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    descripcion     = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))

    def clean(self) -> dict[str, Any]:
        cleaned = super().clean()
        origen  = cleaned.get("cuenta_origen")
        destino = cleaned.get("cuenta_destino")

        if origen and destino and origen == destino:
            raise forms.ValidationError("La cuenta origen y destino deben ser distintas.")
        return cleaned
    
class EstadoCuentaForm(forms.Form):
    cuenta = forms.ModelChoiceField(queryset=Cuenta.objects.all(), label="Cuenta")
    desde  = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), initial=date.today().replace(day=1))
    hasta  = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), initial=date.today())


# Archivo: core/forms.py
class PeriodoForm(forms.ModelForm):
    # Add hidden fields for account type groups
    grupo = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Periodo
        fields = '__all__'
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_corte': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin_periodo': forms.DateInput(attrs={'type': 'date'}),
            'fecha_limite_pago': forms.DateInput(attrs={'type': 'date'}),
            'fecha_pronto_pago': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.cuenta = kwargs.pop('cuenta', None)
        super().__init__(*args, **kwargs)
        
        if not self.cuenta:
            self.fields['cuenta'].queryset = Cuenta.objects.filter(
                tipo__codigo__in=('TDC', 'SERV', 'DEB', 'EFE')
            )
        else:
            # Set grupo based on account type
            self.fields['grupo'].initial = self.cuenta.tipo.grupo
        
        # Hacer campos no obligatorios inicialmente
        self.fields['monto_total'].required = False
        self.fields['pago_minimo'].required = False
        self.fields['pago_no_intereses'].required = False
        
        # Configurar formatos ISO para todos los campos de fecha
        date_fields = [
            'fecha_corte', 
            'fecha_fin_periodo',
            'fecha_limite_pago',
            'fecha_pronto_pago'
        ]
        
        for field_name in date_fields:
            if field_name in self.fields:
                self.fields[field_name].widget = forms.DateInput(
                    attrs={'type': 'date'},
                    format='%Y-%m-%d'
                )
                self.fields[field_name].input_formats = ['%Y-%m-%d']

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        cuenta = cleaned_data.get('cuenta', self.cuenta)
        
        if not cuenta:
            self.add_error('cuenta', 'Debe seleccionar una cuenta')
            return cleaned_data
        
        # Get account group directly
        grupo = cuenta.tipo.grupo
        cleaned_data['grupo'] = grupo  # Store group for template
        
        # Group-specific validations except fecha_limite_pago which is always required below
        if grupo == 'CRE':          # --- Créditos -------------------------------
            if cleaned_data.get('pago_minimo') is None:
                self.add_error('pago_minimo', 'Requerido para tarjetas de crédito')
            if cleaned_data.get('pago_no_intereses') is None:
                self.add_error('pago_no_intereses', 'Requerido: pago sin intereses')

        elif grupo == 'SER':        # --- Servicios ------------------------------
            if cleaned_data.get('pago_no_intereses') is None:   # se usa como “pago total”
                self.add_error('pago_no_intereses', 'Indique el pago total del recibo')
            # pronto-pago sigue opcional:
            if cleaned_data.get('monto_pronto_pago') and not cleaned_data.get('fecha_pronto_pago'):
                self.add_error('fecha_pronto_pago', 'Si das monto de pronto pago, incluye la fecha')

        elif grupo in ['DEB', 'EFE']:  # Débito/Efectivo
            cleaned_data['pago_minimo'] = None
            cleaned_data['pago_no_intereses'] = None
            cleaned_data['monto_pronto_pago'] = None
            cleaned_data['fecha_pronto_pago'] = None
            
        # Validación siempre requerida para fecha_limite_pago
        if not cleaned_data.get('fecha_limite_pago'):
            self.add_error('fecha_limite_pago', 'Requerido: último día para pagar')

        # Validación condicional para servicios
        if grupo == 'SER' and not cleaned_data.get('monto_total'):
            self.add_error('monto_total', "Requerido para servicios")

        # Validación condicional para créditos la arriba ya manejó
        
        if 'monto_total' not in cleaned_data:
            cleaned_data['monto_total'] = 0.00

        return cleaned_data
    
class IngresoForm(forms.ModelForm):
    """
    Form para registrar ingresos (cobro de servicios, ventas, etc.).
    Solo pide los datos indispensables y fija tipo=INGRESO.
    """
    cuenta_destino = forms.ModelChoiceField(
        label="Cuenta que recibe el dinero",
        queryset=Cuenta.objects.none(),          # ← vacío hasta __init__
    )

    class Meta:
        model   = Transaccion
        fields  = ["monto", "fecha", "descripcion", "categoria", "cuenta_destino"]
        widgets = {"fecha": forms.DateInput(attrs={"type": "date"})}

    # --------- PUNTO CLAVE: movemos la lógica aquí ----------
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        try:
            tipo_serv = TipoCuenta.objects.get(codigo="SERV")
            self.fields["cuenta_destino"].queryset = (
                Cuenta.objects.exclude(tipo=tipo_serv)
            )
        except TipoCuenta.DoesNotExist:
            # Aún no se ha cargado el fixture; deja la lista vacía
            self.fields["cuenta_destino"].queryset = Cuenta.objects.none()

    def save(self, commit: bool = True) -> Transaccion:
        obj = super().save(commit=False)
        obj.tipo            = TransaccionTipo.INGRESO
        obj.medio_pago      = self.cleaned_data["cuenta_destino"]
        obj.cuenta_servicio = None
        
        if commit:
            obj.save()
        return obj

class TipoCuentaForm(forms.ModelForm):
    class Meta:
        model = TipoCuenta
        fields = ['codigo', 'nombre', 'grupo']  # Eliminar naturaleza
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'text-lg py-2 px-3 w-full rounded border border-gray-300 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'nombre': forms.TextInput(attrs={'class': 'text-lg py-2 px-3 w-full rounded border border-gray-300 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'grupo': forms.Select(attrs={'class': 'text-lg py-2 px-3 w-full rounded border border-gray-300 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
        }

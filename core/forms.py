# <!-- file: core/forms.py -->
from django import forms
from .models import (Cuenta, Categoria, Transaccion,
                      generar_movs_recibo,
                    Periodo, TransaccionTipo, TipoCuenta)
from decimal import Decimal
from datetime import date


class CuentaForm(forms.ModelForm):
    # Agregar campo para editar el grupo
    grupo = forms.ChoiceField(
        choices=TipoCuenta.GRUPOS,
        required=True,
        label="Grupo de cuenta"
    )
    
    class Meta:
        model = Cuenta
        fields = ["nombre", "tipo", "dia_corte", "grupo"]  # Agregar grupo
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cambiar esta condición para evitar el error en cuentas nuevas
        if self.instance and self.instance.pk and self.instance.tipo_id:
            # Solo si la cuenta ya existe y tiene un tipo asociado
            self.fields['grupo'].initial = self.instance.tipo.grupo
            
    def save(self, commit=True):
        cuenta = super().save(commit=False)
        grupo = self.cleaned_data['grupo']
        
        # Actualizar el grupo del tipo de cuenta
        if cuenta.tipo:
            cuenta.tipo.grupo = grupo
            cuenta.tipo.save()
        
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Etiquetas más descriptivas
        self.fields["medio_pago"].label = "Cuenta de pago"
        self.fields["cuenta_servicio"].label = "Servicio / Proveedor"
        self.fields["ajuste"].label = "Es ajuste (un solo movimiento)"
        # Mostrar sólo cuentas de pago (DEB, CRE, EFE) para medio_pago
        self.fields["medio_pago"].queryset = (
            Cuenta.objects.filter(tipo__grupo__in=["DEB", "CRE", "EFE"]).order_by("nombre")
        )

        # Fuerza formato ISO para el campo fecha (requerido por input[type=date])
        if self.instance and self.instance.pk:
            self.initial['fecha'] = self.instance.fecha.isoformat()

        # Modificar este filtro para incluir SID
        self.fields['cuenta_servicio'].queryset = Cuenta.objects.filter(
            tipo__codigo__in=["SERV", "SID"]  # Agregar "SID" aquí
        )

def clean_monto(self):
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

    def clean(self):
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
    
    def __init__(self, *args, **kwargs):
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

    def clean(self):
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            tipo_serv = TipoCuenta.objects.get(codigo="SERV")
            self.fields["cuenta_destino"].queryset = (
                Cuenta.objects.exclude(tipo=tipo_serv)
            )
        except TipoCuenta.DoesNotExist:
            # Aún no se ha cargado el fixture; deja la lista vacía
            self.fields["cuenta_destino"].queryset = Cuenta.objects.none()

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.tipo            = TransaccionTipo.INGRESO
        obj.medio_pago      = self.cleaned_data["cuenta_destino"]
        obj.cuenta_servicio = None
        
        if commit:
            obj.save()
        return obj

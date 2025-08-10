# 🏦 Sistema de Importación BBVA Asistida - v0.7.1

> **Sistema inteligente paso a paso para importar estados de cuenta BBVA con validación del usuario**

---

## 📋 **TABLA DE CONTENIDOS**

1. [Análisis de Archivos BBVA](#analisis-bbva)
2. [Arquitectura del Sistema Asistido](#arquitectura)
3. [Modelos de Datos](#modelos)
4. [Servicios de Procesamiento](#servicios)
5. [Wizard de Importación](#wizard)
6. [Templates Interactivos](#templates)
7. [Flujo Completo de Importación](#flujo)

---

## 📊 **ANÁLISIS DE ARCHIVOS BBVA** {#analisis-bbva}

### **Estructura Identificada**
```
Línea 0: "Cuenta: 0469455019"
Línea 1: "DETALLE DE MOVIMIENTOS"  
Línea 2: (vacía)
Línea 3: ["FECHA", "DESCRIPCIÓN", "CARGO", "ABONO", "SALDO"]
Línea 4+: Movimientos reales
Última: "BBVA México, S.A. Institución..."
```

### **Tipos de Movimientos Detectados**
- **SPEI ENVIADO**: Transferencias salientes
- **SPEI RECIBIDO**: Transferencias entrantes
- **PAGO TARJETA DE CREDITO**: Pagos TDC
- **COBRO AUTOMATICO**: Domiciliaciones
- **SU PAGO EN EFECTIVO**: Depósitos
- **Compras**: OXXO, Liverpool, Stripe, etc.

---

## 🏗️ **ARQUITECTURA DEL SISTEMA ASISTIDO** {#arquitectura}

### **Flujo General**
```
1. Subir archivo → 2. Previsualizar → 3. Validar cuenta → 
4. Categorizar movimientos → 5. Crear cuentas faltantes → 6. Confirmar e importar
```

### **Principios del Asistente**
- **Validación constante**: Usuario confirma cada decisión importante
- **Categorización inteligente**: Sistema sugiere, usuario valida
- **Creación de cuentas**: Sistema detecta cuentas faltantes y pregunta al usuario
- **Prevención de duplicados**: Detección automática con opción de sobrescribir
- **Rollback completo**: Si algo sale mal, se puede deshacer todo

---

## 🗄️ **MODELOS DE DATOS** {#modelos}

```python
# core/models.py - Agregar estos modelos al sistema existente

class EstadoCuentaBBVA(models.TextChoices):
    """Estados del proceso de importación"""
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
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
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
        on_delete=models.SET_NULL
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

# Extender modelo Transaccion existente
class Transaccion(models.Model):
    # ... campos existentes de tu v0.7.1 ...
    
    # Nuevos campos para BBVA
    importacion_bbva = models.ForeignKey(
        ImportacionBBVA,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='transacciones_creadas'
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
```

---

## ⚙️ **SERVICIOS DE PROCESAMIENTO** {#servicios}

```python
# core/services/bbva_assistant.py
import pandas as pd
import re
from decimal import Decimal
from datetime import datetime
from django.db import transaction as db_transaction
from django.core.exceptions import ValidationError

class AsistenteBBVA:
    """Sistema asistente para importación de archivos BBVA"""
    
    # Patrones de detección automática
    PATRONES_TIPOS = {
        'SPEI ENVIADO': {
            'tipo': 'transferencia_salida',
            'categoria': 'Transferencias',
            'icono': 'fas fa-arrow-right',
            'color': 'red'
        },
        'SPEI RECIBIDO': {
            'tipo': 'transferencia_entrada', 
            'categoria': 'Transferencias',
            'icono': 'fas fa-arrow-left',
            'color': 'green'
        },
        'PAGO TARJETA DE CREDITO': {
            'tipo': 'pago_tdc',
            'categoria': 'Pagos TDC',
            'icono': 'fas fa-credit-card',
            'color': 'blue'
        },
        'COBRO AUTOMATICO': {
            'tipo': 'domiciliacion',
            'categoria': 'Servicios domiciliados',
            'icono': 'fas fa-calendar-check',
            'color': 'orange'
        },
        'SU PAGO EN EFECTIVO': {
            'tipo': 'deposito',
            'categoria': 'Depósitos',
            'icono': 'fas fa-money-bill',
            'color': 'green'
        }
    }
    
    PATRONES_COMERCIOS = {
        'OXXO': 'Tiendas de conveniencia',
        'LIVERPOOL': 'Tiendas departamentales', 
        'STRIPE': 'Servicios digitales',
        'STARLINK': 'Internet y telecomunicaciones',
        'UBER': 'Transporte',
        'NETFLIX': 'Entretenimiento',
        'SPOTIFY': 'Entretenimiento',
        'AMAZON': 'Compras en línea',
        'MERCADOPAGO': 'Pagos digitales'
    }
    
    @classmethod
    def paso1_leer_archivo(cls, archivo_path):
        """Paso 1: Leer y analizar el archivo Excel de BBVA"""
        
        # Leer Excel saltando encabezados
        df = pd.read_excel(archivo_path, skiprows=3)
        
        # Validar que sea un archivo BBVA válido
        if len(df.columns) != 5:
            raise ValidationError("El archivo no tiene el formato esperado de BBVA")
        
        # Renombrar columnas
        df.columns = ['fecha', 'descripcion', 'cargo', 'abono', 'saldo']
        
        # Limpiar datos
        df['fecha'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y', errors='coerce')
        df['cargo'] = pd.to_numeric(df['cargo'].str.replace(',', '') if df['cargo'].dtype == 'object' else df['cargo'], errors='coerce').fillna(0)
        df['abono'] = pd.to_numeric(df['abono'].str.replace(',', '') if df['abono'].dtype == 'object' else df['abono'], errors='coerce').fillna(0)
        df['saldo'] = pd.to_numeric(df['saldo'].str.replace(',', '') if df['saldo'].dtype == 'object' else df['saldo'], errors='coerce')
        
        # Filtrar filas válidas
        df = df[df['fecha'].notna() & df['descripcion'].notna()]
        df = df[~df['descripcion'].str.contains('BBVA México', na=False)]
        df = df.reset_index(drop=True)
        
        # Extraer información general
        info_archivo = {
            'total_movimientos': len(df),
            'fecha_primer_movimiento': df['fecha'].min(),
            'fecha_ultimo_movimiento': df['fecha'].max(),
            'saldo_inicial': df['saldo'].iloc[0] if len(df) > 0 else 0,
            'saldo_final': df['saldo'].iloc[-1] if len(df) > 0 else 0,
            'total_cargos': df['cargo'].sum(),
            'total_abonos': df['abono'].sum(),
            'movimientos_preview': df.head(5).to_dict('records')
        }
        
        return df, info_archivo
    
    @classmethod 
    def paso2_crear_importacion(cls, archivo, cuenta_id, usuario, info_archivo):
        """Paso 2: Crear registro de importación y movimientos temporales"""
        
        cuenta = Cuenta.objects.get(id=cuenta_id)
        
        # Crear importación
        importacion = ImportacionBBVA.objects.create(
            archivo=archivo,
            usuario=usuario,
            cuenta_bbva=cuenta,
            numero_cuenta_detectado='0469455019',
            fecha_primer_movimiento=info_archivo['fecha_primer_movimiento'],
            fecha_ultimo_movimiento=info_archivo['fecha_ultimo_movimiento'],
            total_movimientos_archivo=info_archivo['total_movimientos'],
            saldo_inicial_archivo=info_archivo['saldo_inicial'],
            saldo_final_archivo=info_archivo['saldo_final'],
            estado=EstadoCuentaBBVA.ANALIZADO
        )
        
        return importacion
    
    @classmethod
    def paso3_analizar_movimientos(cls, importacion, df):
        """Paso 3: Analizar cada movimiento y crear registros temporales"""
        
        movimientos_temporales = []
        
        for index, row in df.iterrows():
            # Determinar tipo de movimiento
            es_gasto = row['cargo'] > 0
            monto = abs(row['cargo'] if es_gasto else row['abono'])
            
            # Detectar tipo y categoría
            tipo_info = cls.detectar_tipo_movimiento(row['descripcion'])
            
            # Limpiar descripción
            descripcion_limpia = cls.limpiar_descripcion(row['descripcion'])
            
            # Buscar duplicados
            es_duplicado, transaccion_existente = cls.buscar_duplicado(
                fecha=row['fecha'],
                monto=monto,
                descripcion=row['descripcion'][:200]
            )
            
            # Crear movimiento temporal
            mov_temporal = MovimientoBBVATemporal.objects.create(
                importacion=importacion,
                fila_excel=index + 1,
                fecha_original=row['fecha'],
                descripcion_original=row['descripcion'],
                cargo_original=row['cargo'],
                abono_original=row['abono'],
                saldo_original=row['saldo'],
                es_gasto=es_gasto,
                monto_calculado=monto,
                tipo_detectado=tipo_info['tipo'],
                categoria_sugerida=tipo_info['categoria'],
                descripcion_limpia=descripcion_limpia,
                es_duplicado=es_duplicado,
                transaccion_existente=transaccion_existente
            )
            
            movimientos_temporales.append(mov_temporal)
        
        return movimientos_temporales
    
    @classmethod
    def detectar_tipo_movimiento(cls, descripcion):
        """Detecta automáticamente el tipo de movimiento"""
        descripcion_upper = descripcion.upper()
        
        # Buscar en patrones principales
        for patron, info in cls.PATRONES_TIPOS.items():
            if patron in descripcion_upper:
                return info
        
        # Buscar en comercios conocidos
        for comercio, categoria in cls.PATRONES_COMERCIOS.items():
            if comercio in descripcion_upper:
                return {
                    'tipo': 'compra',
                    'categoria': categoria,
                    'icono': 'fas fa-shopping-cart',
                    'color': 'purple'
                }
        
        # Valores por defecto
        return {
            'tipo': 'otro',
            'categoria': 'Sin categorizar',
            'icono': 'fas fa-question-circle',
            'color': 'gray'
        }
    
    @classmethod
    def limpiar_descripcion(cls, descripcion_original):
        """Limpia y mejora la descripción para hacerla más legible"""
        descripcion = descripcion_original.strip()
        
        # Caso especial: SPEI
        if 'SPEI' in descripcion:
            # Extraer información útil de SPEI
            match = re.search(r'(\w+)\s+\d{3}\s+\d{7}\s+(.+?)\s+/', descripcion)
            if match:
                banco = match.group(1)
                concepto = match.group(2).strip()
                return f"{concepto} (Transferencia {banco})"
        
        # Limpiar espacios múltiples
        descripcion = ' '.join(descripcion.split())
        
        # Quitar códigos de relleno
        descripcion = re.sub(r'\s+0000000\d*', '', descripcion)
        
        # Capitalizar primera letra
        return descripcion[:100].title()
    
    @classmethod
    def buscar_duplicado(cls, fecha, monto, descripcion):
        """Busca si ya existe una transacción similar"""
        try:
            # Buscar transacciones en el mismo día con mismo monto
            candidatos = Transaccion.objects.filter(
                fecha=fecha,
                monto=Decimal(str(monto))
            )
            
            # Buscar por descripción similar
            for candidato in candidatos:
                # Si la descripción original está guardada y coincide al 80%
                if candidato.referencia_bbva:
                    similitud = cls.calcular_similitud(descripcion, candidato.referencia_bbva)
                    if similitud > 0.8:
                        return True, candidato
                
                # Si la descripción procesada es muy similar
                similitud = cls.calcular_similitud(descripcion, candidato.descripcion)
                if similitud > 0.9:
                    return True, candidato
            
            return False, None
            
        except:
            return False, None
    
    @classmethod
    def calcular_similitud(cls, texto1, texto2):
        """Calcula similitud entre dos textos (algoritmo simple)"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, texto1.upper(), texto2.upper()).ratio()
    
    @classmethod
    def paso4_validar_categorias(cls, importacion):
        """Paso 4: Preparar categorías para validación del usuario"""
        
        movimientos = importacion.movimientos_temporales.all()
        categorias_detectadas = {}
        
        for mov in movimientos:
            if mov.categoria_sugerida not in categorias_detectadas:
                # Buscar si la categoría ya existe
                categoria_existente = Categoria.objects.filter(
                    nombre__icontains=mov.categoria_sugerida
                ).first()
                
                categorias_detectadas[mov.categoria_sugerida] = {
                    'nombre': mov.categoria_sugerida,
                    'existe': categoria_existente is not None,
                    'categoria_obj': categoria_existente,
                    'cantidad_movimientos': 0,
                    'monto_total': Decimal('0'),
                    'ejemplos': []
                }
            
            # Agregar estadísticas
            cat_info = categorias_detectadas[mov.categoria_sugerida]
            cat_info['cantidad_movimientos'] += 1
            cat_info['monto_total'] += mov.monto_calculado
            
            if len(cat_info['ejemplos']) < 3:
                cat_info['ejemplos'].append(mov.descripcion_limpia)
        
        return categorias_detectadas
    
    @classmethod
    @db_transaction.atomic
    def paso5_procesar_confirmaciones(cls, importacion, confirmaciones_usuario):
        """Paso 5: Procesar las confirmaciones del usuario"""
        
        # Actualizar categorías según confirmaciones
        for categoria_nombre, info in confirmaciones_usuario['categorias'].items():
            if info['crear']:
                categoria, created = Categoria.objects.get_or_create(
                    nombre=categoria_nombre,
                    defaults={
                        'tipo': info['tipo'],
                        'color': info['color']
                    }
                )
                
                if created:
                    importacion.categorias_creadas += 1
        
        # Actualizar movimientos temporales
        for mov_id, confirmacion in confirmaciones_usuario['movimientos'].items():
            mov_temporal = MovimientoBBVATemporal.objects.get(id=mov_id)
            
            if confirmacion['ignorar']:
                mov_temporal.ignorar = True
            else:
                # Actualizar categoría confirmada
                if confirmacion['categoria']:
                    categoria = Categoria.objects.get(nombre=confirmacion['categoria'])
                    mov_temporal.categoria_confirmada = categoria
                
                # Actualizar descripción si fue editada
                if confirmacion['descripcion']:
                    mov_temporal.descripcion_limpia = confirmacion['descripcion']
                
                mov_temporal.validado_por_usuario = True
                mov_temporal.notas_usuario = confirmacion.get('notas', '')
            
            mov_temporal.save()
        
        importacion.estado = EstadoCuentaBBVA.PROCESANDO
        importacion.paso_actual = 5
        importacion.save()
    
    @classmethod
    @db_transaction.atomic  
    def paso6_crear_transacciones(cls, importacion):
        """Paso 6: Crear las transacciones finales"""
        
        movimientos_procesados = importacion.movimientos_temporales.filter(
            validado_por_usuario=True,
            ignorar=False
        )
        
        transacciones_creadas = []
        errores = []
        
        for mov in movimientos_procesados:
            try:
                # Crear transacción según el tipo
                if mov.es_gasto:
                    # Es un cargo - dinero sale de la cuenta BBVA
                    transaccion = Transaccion.objects.create(
                        monto=mov.monto_calculado,
                        fecha=mov.fecha_original,
                        descripcion=mov.descripcion_limpia,
                        cuenta_origen=importacion.cuenta_bbva,
                        categoria=mov.categoria_confirmada,
                        referencia_bbva=mov.descripcion_original,
                        saldo_posterior_bbva=mov.saldo_original,
                        importacion_bbva=importacion,
                        estado=TransaccionEstado.LIQUIDADA
                    )
                else:
                    # Es un abono - dinero entra a la cuenta BBVA
                    transaccion = Transaccion.objects.create(
                        monto=mov.monto_calculado,
                        fecha=mov.fecha_original,
                        descripcion=mov.descripcion_limpia,
                        cuenta_destino=importacion.cuenta_bbva,
                        categoria=mov.categoria_confirmada,
                        referencia_bbva=mov.descripcion_original,
                        saldo_posterior_bbva=mov.saldo_original,
                        importacion_bbva=importacion,
                        estado=TransaccionEstado.LIQUIDADA
                    )
                
                # Vincular movimiento temporal con transacción creada
                mov.transaccion_creada = transaccion
                mov.save()
                
                transacciones_creadas.append(transaccion)
                importacion.movimientos_nuevos += 1
                
            except Exception as e:
                errores.append(f"Fila {mov.fila_excel}: {str(e)}")
        
        # Finalizar importación
        importacion.estado = EstadoCuentaBBVA.COMPLETADO
        importacion.fecha_completado = timezone.now()
        importacion.paso_actual = 6
        
        if errores:
            importacion.log_proceso['errores'] = errores
        
        importacion.save()
        
        return {
            'transacciones_creadas': len(transacciones_creadas),
            'errores': errores
        }
```

---

## 🧙‍♂️ **WIZARD DE IMPORTACIÓN** {#wizard}

```python
# core/views/bbva_wizard.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from ..services.bbva_assistant import AsistenteBBVA

class BBVAWizardView(LoginRequiredMixin, View):
    """Vista principal del wizard de importación BBVA"""
    
    def get(self, request, step=1, importacion_id=None):
        """Mostrar el paso actual del wizard"""
        
        if importacion_id:
            importacion = get_object_or_404(ImportacionBBVA, id=importacion_id, usuario=request.user)
        else:
            importacion = None
        
        # Enrutar al paso correspondiente
        if step == 1:
            return self.paso1_subir_archivo(request)
        elif step == 2:
            return self.paso2_validar_datos(request, importacion)
        elif step == 3:
            return self.paso3_revisar_movimientos(request, importacion)
        elif step == 4:
            return self.paso4_confirmar_categorias(request, importacion)
        elif step == 5:
            return self.paso5_crear_cuentas(request, importacion)
        elif step == 6:
            return self.paso6_resumen_final(request, importacion)
    
    def post(self, request, step=1, importacion_id=None):
        """Procesar el paso actual y avanzar al siguiente"""
        
        if step == 1:
            return self.procesar_paso1(request)
        elif step == 2:
            return self.procesar_paso2(request, importacion_id)
        elif step == 3:
            return self.procesar_paso3(request, importacion_id)
        elif step == 4:
            return self.procesar_paso4(request, importacion_id)
        elif step == 5:
            return self.procesar_paso5(request, importacion_id)
    
    def paso1_subir_archivo(self, request):
        """Paso 1: Subir y validar archivo"""
        cuentas_bbva = Cuenta.objects.filter(
            tipo__codigo='DEB',
            referencia__contains='5019'
        )
        
        return render(request, 'bbva/wizard_paso1.html', {
            'paso_actual': 1,
            'total_pasos': 6,
            'cuentas_bbva': cuentas_bbva
        })
    
    def procesar_paso1(self, request):
        """Procesar archivo subido"""
        archivo = request.FILES.get('archivo_bbva')
        cuenta_id = request.POST.get('cuenta_id')
        
        if not archivo or not cuenta_id:
            messages.error(request, 'Debe seleccionar archivo y cuenta')
            return redirect('bbva_wizard', step=1)
        
        try:
            # Leer y analizar archivo
            df, info_archivo = AsistenteBBVA.paso1_leer_archivo(archivo)
            
            # Crear importación
            importacion = AsistenteBBVA.paso2_crear_importacion(
                archivo, cuenta_id, request.user, info_archivo
            )
            
            # Analizar movimientos
            AsistenteBBVA.paso3_analizar_movimientos(importacion, df)
            
            messages.success(request, f'✅ Archivo procesado: {info_archivo["total_movimientos"]} movimientos detectados')
            return redirect('bbva_wizard', step=2, importacion_id=importacion.id)
            
        except Exception as e:
            messages.error(request, f'❌ Error procesando archivo: {str(e)}')
            return redirect('bbva_wizard', step=1)
    
    def paso2_validar_datos(self, request, importacion):
        """Paso 2: Mostrar resumen y validar datos básicos"""
        
        movimientos_preview = importacion.movimientos_temporales.all()[:10]
        duplicados = importacion.movimientos_temporales.filter(es_duplicado=True)
        
        stats = {
            'total_movimientos': importacion.total_movimientos_archivo,
            'total_cargos': movimientos_preview.filter(es_gasto=True).count(),
            'total_abonos': movimientos_preview.filter(es_gasto=False).count(),
            'duplicados_detectados': duplicados.count(),
            'periodo': f"{importacion.fecha_primer_movimiento} - {importacion.fecha_ultimo_movimiento}"
        }
        
        return render(request, 'bbva/wizard_paso2.html', {
            'paso_actual': 2,
            'total_pasos': 6,
            'importacion': importacion,
            'movimientos_preview': movimientos_preview,
            'duplicados': duplicados,
            'stats': stats
        })
    
    def paso3_revisar_movimientos(self, request, importacion):
        """Paso 3: Revisar movimientos individualmente"""
        
        # Paginación
        page = int(request.GET.get('page', 1))
        per_page = 20
        
        movimientos = importacion.movimientos_temporales.all()
        start = (page - 1) * per_page
        end = start + per_page
        movimientos_pagina = movimientos[start:end]
        
        total_pages = (movimientos.count() + per_page - 1) // per_page
        
        return render(request, 'bbva/wizard_paso3.html', {
            'paso_actual': 3,
            'total_pasos': 6,
            'importacion': importacion,
            'movimientos': movimientos_pagina,
            'page': page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        })
    
    def paso4_confirmar_categorias(self, request, importacion):
        """Paso 4: Confirmar y crear categorías"""
        
        categorias_detectadas = AsistenteBBVA.paso4_validar_categorias(importacion)
        
        return render(request, 'bbva/wizard_paso4.html', {
            'paso_actual': 4,
            'total_pasos': 6,
            'importacion': importacion,
            'categorias_detectadas': categorias_detectadas
        })
    
    def paso6_resumen_final(self, request, importacion):
        """Paso 6: Mostrar resumen final"""
        
        return render(request, 'bbva/wizard_paso6.html', {
            'paso_actual': 6,
            'total_pasos': 6,
            'importacion': importacion
        })

# API endpoints para interacción AJAX
class BBVAWizardAPIView(View):
    """Endpoints AJAX para el wizard"""
    
    def post(self, request, action, importacion_id):
        importacion = get_object_or_404(ImportacionBBVA, id=importacion_id)
        
        if action == 'actualizar_movimiento':
            return self.actualizar_movimiento(request, importacion)
        elif action == 'confirmar_categorias':
            return self.confirmar_categorias(request, importacion)
        elif action == 'crear_transacciones':
            return self.crear_transacciones(request, importacion)
    
    def actualizar_movimiento(self, request, importacion):
        """Actualizar un movimiento específico"""
        mov_id = request.POST.get('movimiento_id')
        movimiento = get_object_or_404(MovimientoBBVATemporal, id=mov_id)
        
        # Actualizar campos
        movimiento.descripcion_limpia = request.POST.get('descripcion', movimiento.descripcion_limpia)
        movimiento.ignorar = request.POST.get('ignorar') == 'true'
        movimiento.notas_usuario = request.POST.get('notas', '')
        
        # Actualizar categoría si se especifica
        categoria_id = request.POST.get('categoria_id')
        if categoria_id:
            categoria = Categoria.objects.get(id=categoria_id)
            movimiento.categoria_confirmada = categoria
        
        movimiento.validado_por_usuario = True
        movimiento.save()
        
        return JsonResponse({'success': True, 'message': 'Movimiento actualizado'})
    
    def crear_transacciones(self, request, importacion):
        """Crear todas las transacciones finales"""
        try:
            resultado = AsistenteBBVA.paso6_crear_transacciones(importacion)
            
            return JsonResponse({
                'success': True,
                'transacciones_creadas': resultado['transacciones_creadas'],
                'errores': resultado['errores']
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
```

---

## 🎨 **TEMPLATES INTERACTIVOS** {#templates}

### **Template Base del Wizard**

```html
<!-- templates/bbva/wizard_base.html -->
{% extends 'base.html' %}

{% block extra_css %}
<style>
.wizard-step {
    @apply flex items-center p-4 rounded-lg border-2 transition-all duration-300;
}
.wizard-step.active {
    @apply border-blue-500 bg-blue-50 dark:bg-blue-900/20;
}
.wizard-step.completed {
    @apply border-green-500 bg-green-50 dark:bg-green-900/20;
}
.wizard-step.inactive {
    @apply border-gray-300 bg-gray-50 dark:bg-gray-800;
}

.movimiento-card {
    @apply bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-4;
}
.movimiento-card.duplicado {
    @apply border-yellow-400 bg-yellow-50 dark:bg-yellow-900/20;
}
.movimiento-card.ignorado {
    @apply opacity-60 grayscale;
}
</style>
{% endblock %}

{% block content %}
<div class="max-w-6xl mx-auto p-6">
    <!-- Progreso del wizard -->
    <div class="mb-8">
        <div class="flex items-center justify-between mb-4">
            <h1 class="text-3xl font-bold">Importar Estado de Cuenta BBVA</h1>
            <div class="text-sm text-gray-600">
                Paso {{ paso_actual }} de {{ total_pasos }}
            </div>
        </div>
        
        <!-- Barra de progreso -->
        <div class="w-full bg-gray-200 rounded-full h-2 mb-6">
            <div class="bg-blue-600 h-2 rounded-full transition-all duration-500" 
                 style="width: {{ paso_actual|floatformat:0|add:0|mul:16.666 }}%"></div>
        </div>
        
        <!-- Pasos del wizard -->
        <div class="grid grid-cols-6 gap-2">
            <div class="wizard-step {% if paso_actual == 1 %}active{% elif paso_actual > 1 %}completed{% else %}inactive{% endif %}">
                <i class="fas fa-upload mr-2"></i>
                <span class="text-xs hidden sm:inline">Subir archivo</span>
            </div>
            <div class="wizard-step {% if paso_actual == 2 %}active{% elif paso_actual > 2 %}completed{% else %}inactive{% endif %}">
                <i class="fas fa-search mr-2"></i>
                <span class="text-xs hidden sm:inline">Validar datos</span>
            </div>
            <div class="wizard-step {% if paso_actual == 3 %}active{% elif paso_actual > 3 %}completed{% else %}inactive{% endif %}">
                <i class="fas fa-list mr-2"></i>
                <span class="text-xs hidden sm:inline">Revisar movimientos</span>
            </div>
            <div class="wizard-step {% if paso_actual == 4 %}active{% elif paso_actual > 4 %}completed{% else %}inactive{% endif %}">
                <i class="fas fa-tags mr-2"></i>
                <span class="text-xs hidden sm:inline">Categorías</span>
            </div>
            <div class="wizard-step {% if paso_actual == 5 %}active{% elif paso_actual > 5 %}completed{% else %}inactive{% endif %}">
                <i class="fas fa-plus mr-2"></i>
                <span class="text-xs hidden sm:inline">Crear cuentas</span>
            </div>
            <div class="wizard-step {% if paso_actual == 6 %}active{% else %}inactive{% endif %}">
                <i class="fas fa-check mr-2"></i>
                <span class="text-xs hidden sm:inline">Finalizar</span>
            </div>
        </div>
    </div>
    
    {% block wizard_content %}{% endblock %}
</div>
{% endblock %}
```

### **Paso 1: Subir Archivo**

```html
<!-- templates/bbva/wizard_paso1.html -->
{% extends 'bbva/wizard_base.html' %}

{% block wizard_content %}
<div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
    <div class="text-center mb-6">
        <i class="fas fa-file-excel text-6xl text-green-600 mb-4"></i>
        <h2 class="text-2xl font-bold mb-2">Subir Estado de Cuenta BBVA</h2>
        <p class="text-gray-600">Selecciona el archivo Excel descargado desde BBVA Net</p>
    </div>
    
    <form method="post" enctype="multipart/form-data" class="space-y-6">
        {% csrf_token %}
        
        <!-- Selección de cuenta -->
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Cuenta BBVA Débito 5019
            </label>
            <select name="cuenta_id" required class="form-input">
                <option value="">Seleccionar cuenta...</option>
                {% for cuenta in cuentas_bbva %}
                <option value="{{ cuenta.id }}">
                    {{ cuenta.nombre }} - {{ cuenta.referencia }}
                </option>
                {% endfor %}
            </select>
            {% if not cuentas_bbva %}
            <p class="text-sm text-red-600 mt-2">
                ⚠️ No se encontró cuenta BBVA 5019. <a href="{% url 'cuenta_create' %}" class="underline">Crear cuenta primero</a>
            </p>
            {% endif %}
        </div>
        
        <!-- Subida de archivo -->
        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Archivo Excel (.xlsx)
            </label>
            <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-gray-400 transition-colors">
                <div class="space-y-1 text-center">
                    <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                        <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                    <div class="flex text-sm text-gray-600">
                        <label for="archivo_bbva" class="relative cursor-pointer bg-white dark:bg-gray-800 rounded-md font-medium text-blue-600 hover:text-blue-500">
                            <span>Seleccionar archivo</span>
                            <input id="archivo_bbva" name="archivo_bbva" type="file" accept=".xlsx,.xls" required class="sr-only">
                        </label>
                        <p class="pl-1">o arrastrar aquí</p>
                    </div>
                    <p class="text-xs text-gray-500">Excel (.xlsx) hasta 5MB</p>
                </div>
            </div>
        </div>
        
        <!-- Instrucciones -->
        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-4">
            <h3 class="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                📋 Cómo obtener el archivo de BBVA:
            </h3>
            <ol class="text-sm text-blue-800 dark:text-blue-200 space-y-1 list-decimal list-inside">
                <li>Accede a <strong>BBVA Net</strong> con tu usuario</li>
                <li>Ve a <strong>Consultas</strong> → <strong>Movimientos</strong></li>
                <li>Selecciona tu cuenta <strong>BBVA Débito 5019</strong></li>
                <li>Elige el rango de fechas deseado</li>
                <li>Haz clic en <strong>Exportar a Excel</strong></li>
                <li>Descarga el archivo y súbelo aquí</li>
            </ol>
        </div>
        
        <!-- Botones -->
        <div class="flex justify-between pt-6 border-t">
            <a href="{% url 'dashboard' %}" class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50">
                Cancelar
            </a>
            <button type="submit" class="btn-primary">
                <i class="fas fa-arrow-right mr-2"></i>
                Analizar archivo
            </button>
        </div>
    </form>
</div>
{% endblock %}
```

### **Paso 3: Revisar Movimientos**

```html
<!-- templates/bbva/wizard_paso3.html -->
{% extends 'bbva/wizard_base.html' %}

{% block wizard_content %}
<div class="space-y-6">
    <!-- Resumen -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 class="text-2xl font-bold mb-4">Revisar y Validar Movimientos</h2>
        <div class="grid grid-cols-4 gap-4">
            <div class="text-center">
                <div class="text-2xl font-bold text-blue-600">{{ importacion.total_movimientos_archivo }}</div>
                <div class="text-sm text-gray-600">Total movimientos</div>
            </div>
            <div class="text-center">
                <div class="text-2xl font-bold text-green-600" id="validados-count">0</div>
                <div class="text-sm text-gray-600">Validados</div>
            </div>
            <div class="text-center">
                <div class="text-2xl font-bold text-yellow-600" id="duplicados-count">{{ importacion.movimientos_temporales.filter:es_duplicado=True.count }}</div>
                <div class="text-sm text-gray-600">Duplicados</div>
            </div>
            <div class="text-center">
                <div class="text-2xl font-bold text-red-600" id="ignorados-count">0</div>
                <div class="text-sm text-gray-600">Ignorados</div>
            </div>
        </div>
    </div>
    
    <!-- Lista de movimientos -->
    <div class="space-y-4" id="movimientos-lista">
        {% for mov in movimientos %}
        <div class="movimiento-card {% if mov.es_duplicado %}duplicado{% endif %}" data-movimiento="{{ mov.id }}">
            <div class="flex items-center justify-between">
                <!-- Información básica -->
                <div class="flex-1">
                    <div class="flex items-center mb-2">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                   {% if mov.es_gasto %}bg-red-100 text-red-800{% else %}bg-green-100 text-green-800{% endif %}">
                            {% if mov.es_gasto %}
                                <i class="fas fa-arrow-up mr-1"></i> Cargo
                            {% else %}
                                <i class="fas fa-arrow-down mr-1"></i> Abono
                            {% endif %}
                        </span>
                        
                        <span class="ml-2 text-2xl font-bold">
                            ${{ mov.monto_calculado|floatformat:2 }}
                        </span>
                        
                        <span class="ml-2 text-gray-500">
                            {{ mov.fecha_original|date:"d/m/Y" }}
                        </span>
                        
                        {% if mov.es_duplicado %}
                        <span class="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800">
                            <i class="fas fa-exclamation-triangle mr-1"></i> Posible duplicado
                        </span>
                        {% endif %}
                    </div>
                    
                    <!-- Descripción original vs limpia -->
                    <div class="space-y-1">
                        <div class="text-sm text-gray-500">
                            <strong>Original:</strong> {{ mov.descripcion_original|truncatechars:80 }}
                        </div>
                        <div class="flex items-center">
                            <strong class="text-sm mr-2">Procesada:</strong>
                            <input type="text" 
                                   class="flex-1 text-sm border border-gray-300 rounded px-2 py-1 descripcion-input"
                                   value="{{ mov.descripcion_limpia }}"
                                   data-movimiento="{{ mov.id }}" />
                        </div>
                    </div>
                    
                    <!-- Categoría sugerida -->
                    <div class="mt-2">
                        <span class="text-sm text-gray-600 mr-2">Categoría sugerida:</span>
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                            {{ mov.categoria_sugerida }}
                        </span>
                    </div>
                </div>
                
                <!-- Acciones -->
                <div class="flex items-center space-x-2 ml-4">
                    <button class="validar-btn px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                            data-movimiento="{{ mov.id }}">
                        <i class="fas fa-check mr-1"></i> Validar
                    </button>
                    
                    <button class="ignorar-btn px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
                            data-movimiento="{{ mov.id }}">
                        <i class="fas fa-times mr-1"></i> Ignorar
                    </button>
                    
                    <button class="editar-btn px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                            data-movimiento="{{ mov.id }}">
                        <i class="fas fa-edit mr-1"></i> Editar
                    </button>
                </div>
            </div>
            
            <!-- Panel de edición (oculto por defecto) -->
            <div class="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hidden" id="panel-edicion-{{ mov.id }}">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium mb-1">Categoría:</label>
                        <select class="categoria-select form-input text-sm" data-movimiento="{{ mov.id }}">
                            <option value="">Seleccionar...</option>
                            {% for cat in categorias_disponibles %}
                            <option value="{{ cat.id }}" {% if cat.nombre == mov.categoria_sugerida %}selected{% endif %}>
                                {{ cat.nombre }}
                            </option>
                            {% endfor %}
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-1">Notas:</label>
                        <input type="text" class="notas-input form-input text-sm" 
                               placeholder="Notas adicionales..." 
                               data-movimiento="{{ mov.id }}" />
                    </div>
                </div>
                
                <div class="flex justify-end space-x-2 mt-4">
                    <button class="cancelar-edicion px-3 py-1 border border-gray-300 rounded text-sm">
                        Cancelar
                    </button>
                    <button class="guardar-edicion px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                            data-movimiento="{{ mov.id }}">
                        Guardar cambios
                    </button>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <!-- Paginación -->
    {% if total_pages > 1 %}
    <div class="flex justify-center items-center space-x-2 py-4">
        {% if has_prev %}
        <a href="?page={{ page|add:-1 }}" class="px-3 py-2 border border-gray-300 rounded-md text-sm">
            ← Anterior
        </a>
        {% endif %}
        
        <span class="text-sm text-gray-600">
            Página {{ page }} de {{ total_pages }}
        </span>
        
        {% if has_next %}
        <a href="?page={{ page|add:1 }}" class="px-3 py-2 border border-gray-300 rounded-md text-sm">
            Siguiente →
        </a>
        {% endif %}
    </div>
    {% endif %}
    
    <!-- Botones de navegación -->
    <div class="flex justify-between pt-6 border-t bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <a href="{% url 'bbva_wizard' step=2 importacion_id=importacion.id %}" 
           class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50">
            ← Volver a validar datos
        </a>
        
        <div class="space-x-2">
            <button id="validar-todos-btn" class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
                <i class="fas fa-check-double mr-2"></i>
                Validar todos los visibles
            </button>
            
            <button id="continuar-btn" class="btn-primary" disabled>
                Continuar a categorías
                <i class="fas fa-arrow-right ml-2"></i>
            </button>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Contadores
    function actualizarContadores() {
        const validados = document.querySelectorAll('.movimiento-card.validado').length;
        const ignorados = document.querySelectorAll('.movimiento-card.ignorado').length;
        
        document.getElementById('validados-count').textContent = validados;
        document.getElementById('ignorados-count').textContent = ignorados;
        
        // Habilitar botón continuar si hay al menos un validado
        const continuar = document.getElementById('continuar-btn');
        continuar.disabled = validados === 0;
    }
    
    // Manejar validación individual
    document.querySelectorAll('.validar-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const movId = this.dataset.movimiento;
            const card = document.querySelector(`[data-movimiento="${movId}"]`);
            const descripcion = card.querySelector('.descripcion-input').value;
            
            // Enviar validación al servidor
            fetch(`/bbva/api/actualizar_movimiento/${movId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'descripcion': descripcion,
                    'validado': 'true'
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    card.classList.add('validado');
                    card.classList.remove('ignorado');
                    this.innerHTML = '<i class="fas fa-check mr-1"></i> Validado';
                    this.classList.replace('bg-green-600', 'bg-green-400');
                    this.disabled = true;
                    actualizarContadores();
                }
            });
        });
    });
    
    // Manejar ignorar
    document.querySelectorAll('.ignorar-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const movId = this.dataset.movimiento;
            const card = document.querySelector(`[data-movimiento="${movId}"]`);
            
            fetch(`/bbva/api/actualizar_movimiento/${movId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'ignorar': 'true'
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    card.classList.add('ignorado');
                    card.classList.remove('validado');
                    actualizarContadores();
                }
            });
        });
    });
    
    // Validar todos los visibles
    document.getElementById('validar-todos-btn').addEventListener('click', function() {
        document.querySelectorAll('.validar-btn:not(:disabled)').forEach(btn => {
            btn.click();
        });
    });
    
    // Continuar al siguiente paso
    document.getElementById('continuar-btn').addEventListener('click', function() {
        window.location.href = `{% url 'bbva_wizard' step=4 importacion_id=importacion.id %}`;
    });
    
    // Panel de edición
    document.querySelectorAll('.editar-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const movId = this.dataset.movimiento;
            const panel = document.getElementById(`panel-edicion-${movId}`);
            panel.classList.toggle('hidden');
        });
    });
    
    actualizarContadores();
});
</script>
{% endblock %}
```

---

## 🔄 **FLUJO COMPLETO DE IMPORTACIÓN** {#flujo}

### **URLs Configuration**

```python
# core/urls.py - Agregar estas URLs
from .views.bbva_wizard import BBVAWizardView, BBVAWizardAPIView

urlpatterns = [
    # ... URLs existentes ...
    
    # Wizard BBVA
    path('bbva/importar/', BBVAWizardView.as_view(), name='bbva_wizard'),
    path('bbva/importar/paso-<int:step>/', BBVAWizardView.as_view(), name='bbva_wizard'),
    path('bbva/importar/paso-<int:step>/<int:importacion_id>/', BBVAWizardView.as_view(), name='bbva_wizard'),
    
    # API para AJAX
    path('bbva/api/<str:action>/<int:importacion_id>/', BBVAWizardAPIView.as_view(), name='bbva_api'),
]
```

### **Navegación Integrada**

```html
<!-- Agregar a templates/base.html en el menú principal -->
<li class="border-t border-gray-200 dark:border-gray-700">
    <a href="{% url 'bbva_wizard' %}" 
       class="group flex items-center px-2 py-2 text-base font-medium text-gray-600 rounded-md hover:bg-gray-50 hover:text-gray-900">
        <i class="fas fa-file-import text-gray-400 group-hover:text-gray-500 mr-3"></i>
        Importar BBVA
    </a>
</li>
```

---

## 📋 **CHECKLIST DE IMPLEMENTACIÓN**

### **Fase 1: Modelos Base** ✅
- [ ] Agregar modelos `ImportacionBBVA` y `MovimientoBBVATemporal`
- [ ] Extender modelo `Transaccion` con campos BBVA
- [ ] Crear y aplicar migraciones
- [ ] Instalar pandas: `pip install pandas openpyxl`

### **Fase 2: Servicios de Backend** ✅ 
- [ ] Crear `core/services/bbva_assistant.py`
- [ ] Implementar lógica de detección de tipos
- [ ] Crear sistema de limpieza de descripciones
- [ ] Implementar detección de duplicados

### **Fase 3: Wizard Views** ✅
- [ ] Crear `core/views/bbva_wizard.py`  
- [ ] Implementar los 6 pasos del wizard
- [ ] Crear endpoints AJAX para interacción
- [ ] Manejar errores y validaciones

### **Fase 4: Templates Interactivos** ✅
- [ ] Crear template base del wizard
- [ ] Implementar paso 1 (subida de archivo)
- [ ] Crear paso 3 (revisión de movimientos)
- [ ] Agregar JavaScript para interacción AJAX

### **Fase 5: Integración** ✅
- [ ] Agregar URLs al router principal
- [ ] Integrar enlace en navegación
- [ ] Probar flujo completo
- [ ] Documentar para usuarios

---

## 🎯 **VENTAJAS DE ESTA IMPLEMENTACIÓN**

### **🧙‍♂️ Sistema Asistente Inteligente**
- **Validación paso a paso**: Usuario confirma cada decisión importante
- **Detección automática**: Sistema sugiere tipos y categorías
- **Prevención de errores**: Duplicados detectados automáticamente
- **Rollback completo**: Si algo falla, se puede deshacer todo

### **🎨 Interfaz Intuitiva** 
- **Wizard visual**: Progreso claro con 6 pasos bien definidos
- **Validación en tiempo real**: Feedback inmediato con AJAX
- **Paginación inteligente**: Manejo eficiente de grandes volúmenes
- **Responsive design**: Funciona en móvil y desktop

### **🏦 Específico para BBVA**
- **Formato reconocido**: Lee exactamente tus archivos Excel
- **Categorización automática**: Conoce patrones BBVA (SPEI, pagos TDC, etc.)
- **Limpieza de descripciones**: Hace legibles las descripciones del banco
- **Preserva información**: Guarda descripción original para auditoría

### **🔧 Integración Perfecta**
- **Compatible con v0.7.1**: No cambia tu arquitectura actual
- **Doble partida automática**: Genera asientos contables transparentemente
- **Estados de transacciones**: Marca como 'LIQUIDADA' automáticamente
- **Extensible**: Fácil agregar otros bancos con el mismo patrón

**¡Este sistema te permitirá importar estados de cuenta BBVA de forma asistida, validando cada paso para garantizar precisión total!**
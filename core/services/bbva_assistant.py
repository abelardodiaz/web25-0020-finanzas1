"""
Servicio AsistenteBBVA para importación inteligente de estados de cuenta BBVA
"""
import pandas as pd
import re
from decimal import Decimal
from datetime import datetime
from django.db import transaction as db_transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from difflib import SequenceMatcher

from ..models import (
    ImportacionBBVA, MovimientoBBVATemporal, Transaccion, Categoria,
    EstadoCuentaBBVA, TransaccionEstado, Cuenta
)


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
        },
        'PAGO CUENTA DE TERCERO': {
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
        'MERCADOPAGO': 'Pagos digitales',
        'PAYPAL': 'Pagos digitales',
        'GOOGLE': 'Servicios digitales',
        'MICROSOFT': 'Software',
        'ADOBE': 'Software',
        'CFE': 'Servicios básicos',
        'TELMEX': 'Telecomunicaciones',
        'TOTALPLAY': 'Telecomunicaciones'
    }
    
    @classmethod
    def paso1_leer_archivo(cls, archivo_path):
        """Paso 1: Leer y analizar el archivo Excel de BBVA"""
        
        try:
            # Leer Excel saltando encabezados
            df = pd.read_excel(archivo_path, skiprows=3)
            
            # Validar que sea un archivo BBVA válido
            if len(df.columns) != 5:
                raise ValidationError(f"El archivo no tiene el formato esperado de BBVA (tiene {len(df.columns)} columnas, esperaba 5)")
            
            # Renombrar columnas
            df.columns = ['fecha', 'descripcion', 'cargo', 'abono', 'saldo']
            
            # Limpiar datos
            df['fecha'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y', errors='coerce')
            
            # Limpiar columnas numéricas (manejar comas, negativos y strings)
            def limpiar_numero(serie):
                if serie.dtype == 'object':
                    # Convertir a string y limpiar
                    serie_str = serie.astype(str)
                    # Remover espacios, comas (separador de miles) y símbolo de pesos
                    serie_limpia = serie_str.str.replace(',', '').str.replace('$', '').str.strip()
                    # Manejar el signo negativo correctamente
                    serie_limpia = serie_limpia.str.replace('−', '-')  # Por si viene un signo menos unicode
                    return pd.to_numeric(serie_limpia, errors='coerce')
                return pd.to_numeric(serie, errors='coerce')
            
            # IMPORTANTE: Los cargos en BBVA vienen como negativos
            df['cargo'] = limpiar_numero(df['cargo']).fillna(0)
            df['abono'] = limpiar_numero(df['abono']).fillna(0)
            df['saldo'] = limpiar_numero(df['saldo'])
            
            # Convertir cargos negativos a positivos (son montos que salen)
            df['cargo'] = df['cargo'].abs()
            
            # Filtrar filas válidas
            df = df[df['fecha'].notna() & df['descripcion'].notna()]
            df = df[~df['descripcion'].astype(str).str.contains('BBVA México', na=False)]
            df = df.reset_index(drop=True)
            
            if len(df) == 0:
                raise ValidationError("No se encontraron movimientos válidos en el archivo")
            
            # Extraer información general
            info_archivo = {
                'total_movimientos': len(df),
                'fecha_primer_movimiento': df['fecha'].min().date(),
                'fecha_ultimo_movimiento': df['fecha'].max().date(),
                'saldo_inicial': float(df['saldo'].iloc[0]) if len(df) > 0 else 0,
                'saldo_final': float(df['saldo'].iloc[-1]) if len(df) > 0 else 0,
                'total_cargos': float(df['cargo'].sum()),
                'total_abonos': float(df['abono'].sum()),
                'movimientos_preview': df.head(5).to_dict('records')
            }
            
            return df, info_archivo
            
        except Exception as e:
            raise ValidationError(f"Error leyendo archivo BBVA: {str(e)}")
    
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
            saldo_inicial_archivo=Decimal(str(info_archivo['saldo_inicial'])),
            saldo_final_archivo=Decimal(str(info_archivo['saldo_final'])),
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
                fecha=row['fecha'].date(),
                monto=monto,
                descripcion=str(row['descripcion'])[:200]
            )
            
            # Crear movimiento temporal
            mov_temporal = MovimientoBBVATemporal.objects.create(
                importacion=importacion,
                fila_excel=index + 1,
                fecha_original=row['fecha'].date(),
                descripcion_original=str(row['descripcion']),
                cargo_original=Decimal(str(row['cargo'])),
                abono_original=Decimal(str(row['abono'])),
                saldo_original=Decimal(str(row['saldo'])),
                es_gasto=es_gasto,
                monto_calculado=Decimal(str(monto)),
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
        descripcion_upper = str(descripcion).upper()
        
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
        descripcion = str(descripcion_original).strip()
        
        # Caso especial: SPEI
        if 'SPEI' in descripcion:
            # Extraer información útil de SPEI
            match = re.search(r'(\w+)\s+\d{3}\s+\d{7}\s+(.+?)\s+/', descripcion)
            if match:
                banco = match.group(1)
                concepto = match.group(2).strip()
                return f"{concepto} (Transferencia {banco})"[:100]
        
        # Limpiar espacios múltiples
        descripcion = ' '.join(descripcion.split())
        
        # Quitar códigos de relleno
        descripcion = re.sub(r'\s+0000000\d*', '', descripcion)
        
        # Capitalizar primera letra de cada palabra importante
        palabras = descripcion.split()
        palabras_limpias = []
        for palabra in palabras:
            if len(palabra) > 3 and palabra.isupper():
                palabras_limpias.append(palabra.title())
            else:
                palabras_limpias.append(palabra)
        
        return ' '.join(palabras_limpias)[:100]
    
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
            
        except Exception:
            return False, None
    
    @classmethod
    def calcular_similitud(cls, texto1, texto2):
        """Calcula similitud entre dos textos (algoritmo simple)"""
        if not texto1 or not texto2:
            return 0.0
        return SequenceMatcher(None, str(texto1).upper(), str(texto2).upper()).ratio()
    
    @classmethod
    def obtener_o_crear_cuenta_relacionada(cls, movimiento):
        """Obtiene o crea la cuenta relacionada basándose en la descripción"""
        from ..models import Cuenta, TipoCuenta
        
        descripcion = movimiento.descripcion_original.upper()
        
        # Extraer información del banco/entidad
        banco = None
        numero_cuenta = None
        nombre_cuenta = None
        
        # Patrones para detectar banco y cuenta
        if 'SPEI' in descripcion:
            # Extraer banco de SPEI
            patrones_banco = {
                'SANTANDER': 'Santander',
                'BANORTE': 'Banorte', 
                'BANAMEX': 'Banamex',
                'BANCOMER': 'Bancomer',
                'BBVA': 'BBVA',
                'HSBC': 'HSBC',
                'SCOTIABANK': 'Scotiabank',
                'INBURSA': 'Inbursa',
                'AZTECA': 'Banco Azteca',
                'STP': 'STP',
                'MERCADO PAGO': 'Mercado Pago',
                'NU MEXICO': 'Nu Bank',
                'CONSUBANCO': 'Consubanco'
            }
            
            for patron, nombre in patrones_banco.items():
                if patron in descripcion:
                    banco = nombre
                    break
            
            # Extraer número de cuenta (primeros dígitos después del banco)
            import re
            match = re.search(r'(\d{10,})', descripcion)
            if match:
                numero_cuenta = match.group(1)[:10]  # Primeros 10 dígitos
            
            # Crear nombre descriptivo
            if banco:
                if 'ENVIADO' in descripcion:
                    nombre_cuenta = f"{banco} - Cuenta Externa"
                else:
                    nombre_cuenta = f"{banco} - Origen"
        
        elif 'PAGO CUENTA DE TERCERO' in descripcion:
            # Es un depósito/pago de tercero
            nombre_cuenta = "Cuenta Tercero - Depósito"
            banco = "Externo"
            
            # Buscar número de referencia
            match = re.search(r'(\d{10,})', descripcion)
            if match:
                numero_cuenta = match.group(1)[:10]
        
        elif 'PAGO TARJETA' in descripcion:
            nombre_cuenta = "Tarjeta de Crédito"
            banco = "TDC"
        
        else:
            # Genérico
            nombre_cuenta = "Cuenta Externa"
            banco = "Desconocido"
        
        # Si no se pudo determinar un nombre, usar genérico
        if not nombre_cuenta:
            nombre_cuenta = f"Cuenta Externa {movimiento.id}"
        
        # Buscar si ya existe una cuenta con estas características
        cuenta_existente = None
        
        if numero_cuenta:
            # Buscar por número/referencia
            cuenta_existente = Cuenta.objects.filter(
                referencia__contains=numero_cuenta
            ).first()
        
        if not cuenta_existente and banco and banco != "Desconocido":
            # Buscar por nombre del banco
            cuenta_existente = Cuenta.objects.filter(
                nombre__icontains=banco
            ).first()
        
        # Si existe, devolverla
        if cuenta_existente:
            return cuenta_existente
        
        # Si no existe, crear una nueva
        # Determinar tipo de cuenta
        if 'TARJETA' in descripcion or 'TDC' in descripcion:
            tipo = TipoCuenta.objects.filter(codigo='TDC').first()
        elif 'MERCADO PAGO' in descripcion or 'PAYPAL' in descripcion:
            tipo = TipoCuenta.objects.filter(codigo='DIG').first()  # Digital/Virtual
        else:
            tipo = TipoCuenta.objects.filter(codigo='DEB').first()  # Débito por defecto
        
        if not tipo:
            # Si no hay tipo, usar el primero disponible
            tipo = TipoCuenta.objects.first()
        
        # Crear la cuenta nueva
        nueva_cuenta = Cuenta.objects.create(
            nombre=nombre_cuenta,
            referencia=numero_cuenta or f"AUTO-{movimiento.id}",
            moneda='MXN',
            tipo=tipo,
            naturaleza='DEUDORA' if tipo and tipo.grupo in ['DEB', 'EFE'] else 'ACREEDORA',
            saldo_inicial=0,
            activa=True,
            descripcion=f"Cuenta creada automáticamente desde: {movimiento.descripcion_original[:100]}"
        )
        
        return nueva_cuenta
    
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
        for categoria_nombre, info in confirmaciones_usuario.get('categorias', {}).items():
            if info.get('crear', False):
                categoria, created = Categoria.objects.get_or_create(
                    nombre=categoria_nombre,
                    defaults={
                        'tipo': info.get('tipo', 'PERSONAL'),
                        'color': info.get('color', '#3b82f6')
                    }
                )
                
                if created:
                    importacion.categorias_creadas += 1
        
        # Actualizar movimientos temporales
        for mov_id, confirmacion in confirmaciones_usuario.get('movimientos', {}).items():
            try:
                mov_temporal = MovimientoBBVATemporal.objects.get(id=mov_id)
                
                if confirmacion.get('ignorar', False):
                    mov_temporal.ignorar = True
                else:
                    # Actualizar categoría confirmada
                    categoria_nombre = confirmacion.get('categoria')
                    if categoria_nombre:
                        categoria = Categoria.objects.filter(nombre=categoria_nombre).first()
                        if categoria:
                            mov_temporal.categoria_confirmada = categoria
                    
                    # Actualizar descripción si fue editada
                    if confirmacion.get('descripcion'):
                        mov_temporal.descripcion_limpia = confirmacion['descripcion'][:255]
                    
                    mov_temporal.validado_por_usuario = True
                    mov_temporal.notas_usuario = confirmacion.get('notas', '')
                
                mov_temporal.save()
                
            except MovimientoBBVATemporal.DoesNotExist:
                continue
        
        importacion.estado = EstadoCuentaBBVA.PROCESANDO
        importacion.paso_actual = 5
        importacion.save()
    
    @classmethod
    @db_transaction.atomic  
    def paso6_crear_transacciones(cls, importacion):
        """Paso 6: Crear las transacciones finales con doble entrada"""
        
        movimientos_procesados = importacion.movimientos_temporales.filter(
            validado_por_usuario=True,
            ignorar=False
        )
        
        transacciones_creadas = []
        errores = []
        cuentas_creadas = 0
        
        for mov in movimientos_procesados:
            try:
                # Determinar cuenta relacionada (origen o destino según el caso)
                cuenta_relacionada = mov.cuenta_destino_confirmada
                
                # Si no hay cuenta relacionada confirmada, crear una automáticamente
                if not cuenta_relacionada:
                    cuenta_relacionada = cls.obtener_o_crear_cuenta_relacionada(mov)
                    if cuenta_relacionada and cuenta_relacionada.pk is None:
                        # Es una cuenta nueva
                        cuentas_creadas += 1
                
                # Crear transacción con doble entrada
                if mov.es_gasto:
                    # ABONO contable: Sale dinero de BBVA (disminuye cuenta DEUDORA)
                    # Nota: El banco lo llama "CARGO" pero contablemente es ABONO
                    transaccion = Transaccion.objects.create(
                        monto=mov.monto_calculado,
                        fecha=mov.fecha_original,
                        descripcion=mov.descripcion_limpia,
                        cuenta_origen=importacion.cuenta_bbva,  # Sale de BBVA
                        cuenta_destino=cuenta_relacionada,      # Llega a otra cuenta
                        categoria=mov.categoria_confirmada,
                        referencia_bbva=mov.descripcion_original,
                        saldo_posterior_bbva=mov.saldo_original,
                        importacion_bbva=importacion,
                        estado=TransaccionEstado.LIQUIDADA
                    )
                else:
                    # CARGO contable: Entra dinero a BBVA (aumenta cuenta DEUDORA)
                    # Nota: El banco lo llama "ABONO" pero contablemente es CARGO
                    transaccion = Transaccion.objects.create(
                        monto=mov.monto_calculado,
                        fecha=mov.fecha_original,
                        descripcion=mov.descripcion_limpia,
                        cuenta_origen=cuenta_relacionada,       # Sale de otra cuenta
                        cuenta_destino=importacion.cuenta_bbva, # Llega a BBVA
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

    @classmethod
    def obtener_resumen_importacion(cls, importacion):
        """Obtiene resumen completo de una importación"""
        movimientos = importacion.movimientos_temporales.all()
        
        return {
            'total_movimientos': movimientos.count(),
            'validados': movimientos.filter(validado_por_usuario=True).count(),
            'ignorados': movimientos.filter(ignorar=True).count(),
            'duplicados': movimientos.filter(es_duplicado=True).count(),
            'gastos': movimientos.filter(es_gasto=True).count(),
            'ingresos': movimientos.filter(es_gasto=False).count(),
            'monto_total_gastos': sum(m.monto_calculado for m in movimientos.filter(es_gasto=True)),
            'monto_total_ingresos': sum(m.monto_calculado for m in movimientos.filter(es_gasto=False)),
            'categorias_detectadas': len(set(m.categoria_sugerida for m in movimientos if m.categoria_sugerida)),
            'periodo': f"{importacion.fecha_primer_movimiento} - {importacion.fecha_ultimo_movimiento}",
            'estado': importacion.estado,
            'paso_actual': importacion.paso_actual
        }
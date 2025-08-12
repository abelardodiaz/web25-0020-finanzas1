#!/usr/bin/env python3
"""
Script CLI para importar movimientos bancarios BBVA desde JSON
Versión 0.8.3 - Sistema de importación interactiva
"""
import os
import sys
import json
import logging
import glob
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Agregar el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

# Imports de Django
from django.db import transaction
from core.models import Cuenta, Transaccion, Categoria, TipoCuenta, TransaccionTipo, TransaccionEstado

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('importacion_bbva.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ImportadorBBVA:
    """Clase principal para importar movimientos desde JSON"""
    
    def __init__(self, test_mode=False):
        self.test_mode = test_mode
        self.cuenta_bbva = None
        self.movimientos = []
        self.procesados = 0
        self.errores = 0
        self.duplicados = 0
        self.omitidos = 0
        self.log_operaciones = []
        self.memoria_sistema = None  # Se inicializará después
        self.modo_duplicados = None  # 'omitir', 'sobrescribir', 'preguntar'
        
    def iniciar(self):
        """Flujo principal del importador"""
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}IMPORTADOR DE MOVIMIENTOS BANCARIOS BBVA v0.8.5{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        if self.test_mode:
            print(f"{Colors.WARNING}⚠️  MODO TEST ACTIVADO - No se guardarán cambios{Colors.ENDC}\n")
        
        # Inicializar sistema de memoria para aprendizaje
        try:
            from sistema_memoria import MemoriaPatrones
            self.memoria_sistema = MemoriaPatrones()
            print(f"{Colors.OKGREEN}✓ Sistema de memoria inicializado{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.WARNING}⚠️  Sistema de memoria no disponible: {e}{Colors.ENDC}")
        
        # Verificar cuenta BBVA
        if not self.verificar_cuenta_bbva():
            return
        
        # Cargar archivo JSON
        if not self.cargar_datos():
            return
        
        # Mostrar resumen
        self.mostrar_resumen_inicial()
        
        # Verificar duplicados
        self.verificar_duplicados_iniciales()
        
        # Preguntar por procesamiento masivo
        modo_masivo = self.preguntar_modo_masivo()
        
        # Procesar movimientos
        self.procesar_movimientos(modo_masivo)
        
        # Mostrar estadísticas finales
        self.mostrar_estadisticas_finales()
        
        # Exportar log
        self.exportar_log()
        
    def verificar_cuenta_bbva(self):
        """Verifica que existe la cuenta TDB BBVA 5019"""
        print(f"{Colors.OKBLUE}Verificando cuenta bancaria...{Colors.ENDC}")
        
        try:
            self.cuenta_bbva = Cuenta.objects.get(nombre="TDB BBVA 5019")
            print(f"{Colors.OKGREEN}✓ Trabajando con Cuenta: {self.cuenta_bbva.nombre}{Colors.ENDC}")
            # El saldo es un método en el modelo, no una propiedad
            saldo = self.cuenta_bbva.saldo() if hasattr(self.cuenta_bbva.saldo, '__call__') else self.cuenta_bbva.saldo
            saldo = float(saldo) if saldo else 0.0
            print(f"  Saldo actual: ${saldo:,.2f}")
            print(f"  Naturaleza: {self.cuenta_bbva.naturaleza}")
            print()
            return True
        except Cuenta.DoesNotExist:
            print(f"{Colors.FAIL}✗ Error: No se encontró la cuenta 'TDB BBVA 5019'{Colors.ENDC}")
            crear = input("¿Desea crearla ahora? (s/n): ").lower()
            if crear == 's':
                return self.crear_cuenta_bbva()
            return False
        
    def crear_cuenta_bbva(self):
        """Crea la cuenta BBVA si no existe"""
        try:
            tipo_deb = TipoCuenta.objects.get(codigo='DEB')
            self.cuenta_bbva = Cuenta.objects.create(
                nombre="TDB BBVA 5019",
                tipo=tipo_deb,
                naturaleza='DEUDORA',
                es_medio_pago=True,
                moneda='MXN',
                saldo_inicial=0
            )
            print(f"{Colors.OKGREEN}✓ Cuenta creada exitosamente{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"{Colors.FAIL}✗ Error al crear cuenta: {e}{Colors.ENDC}")
            return False
    
    def cargar_datos(self):
        """Carga el archivo JSON con los movimientos"""
        # Buscar archivos JSON disponibles
        json_files = []
        
        # Buscar en directorio actual
        for file in glob.glob("*.json"):
            json_files.append(file)
        
        # Buscar en scripts_cli/output/
        output_dir = "scripts_cli/output"
        if os.path.exists(output_dir):
            for file in glob.glob(f"{output_dir}/*.json"):
                json_files.append(file)
        
        if not json_files:
            print(f"{Colors.FAIL}No se encontraron archivos JSON{Colors.ENDC}")
            return False
        
        # Ordenar por fecha de modificación (más reciente primero)
        json_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        print(f"{Colors.HEADER}📁 Archivos JSON disponibles:{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        for i, file in enumerate(json_files, 1):
            file_time = datetime.fromtimestamp(os.path.getmtime(file))
            file_size = os.path.getsize(file) / 1024  # KB
            
            if i == 1:  # Más reciente
                print(f"{Colors.OKGREEN}[{i}] {file}{Colors.ENDC} {Colors.BOLD}← MÁS RECIENTE{Colors.ENDC}")
                print(f"    📅 {file_time.strftime('%d/%m/%Y %H:%M:%S')} | 📦 {file_size:.1f} KB")
            else:
                print(f"{Colors.OKCYAN}[{i}] {file}{Colors.ENDC}")
                print(f"    📅 {file_time.strftime('%d/%m/%Y %H:%M:%S')} | 📦 {file_size:.1f} KB")
        
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        while True:
            try:
                opcion = input(f"\n{Colors.OKCYAN}Seleccione archivo [1-{len(json_files)}] o ruta absoluta: {Colors.ENDC}").strip()
                
                if not opcion:  # Enter = usar el más reciente
                    archivo_path = json_files[0]
                    break
                elif opcion.isdigit():
                    idx = int(opcion) - 1
                    if 0 <= idx < len(json_files):
                        archivo_path = json_files[idx]
                        break
                    else:
                        print(f"{Colors.WARNING}Número fuera de rango{Colors.ENDC}")
                elif os.path.exists(opcion):
                    archivo_path = opcion
                    break
                else:
                    print(f"{Colors.WARNING}Archivo no encontrado: {opcion}{Colors.ENDC}")
            except (ValueError, KeyboardInterrupt):
                print(f"{Colors.WARNING}Opción inválida{Colors.ENDC}")
                continue
        
        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.movimientos = data.get('movimientos', [])
            self.metadata = data.get('metadata', {})
            
            print(f"{Colors.OKGREEN}✓ Archivo cargado correctamente{Colors.ENDC}")
            print(f"{Colors.OKCYAN}Se detectaron {len(self.movimientos)} movimientos{Colors.ENDC}\n")
            
            logger.info(f"Archivo cargado: {archivo_path}, {len(self.movimientos)} movimientos")
            return True
            
        except FileNotFoundError:
            print(f"{Colors.FAIL}✗ Error: Archivo no encontrado{Colors.ENDC}")
            logger.error(f"Archivo no encontrado: {archivo_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"{Colors.FAIL}✗ Error: JSON inválido - {e}{Colors.ENDC}")
            logger.error(f"JSON inválido: {e}")
            return False
        except Exception as e:
            print(f"{Colors.FAIL}✗ Error inesperado: {e}{Colors.ENDC}")
            logger.error(f"Error inesperado: {e}")
            return False
    
    def verificar_duplicados_iniciales(self):
        """Verifica si hay transacciones duplicadas en la BD"""
        duplicados_encontrados = []
        
        print(f"\n{Colors.OKBLUE}🔍 Verificando duplicados...{Colors.ENDC}")
        
        for mov in self.movimientos:
            fecha = mov.get('fecha')
            monto = mov.get('monto')
            ref_bancaria = mov.get('referencia_bancaria', '')
            descripcion = mov.get('descripcion', '')[:50]
            
            # Buscar duplicados por fecha + monto + referencia
            query = Transaccion.objects.filter(
                fecha=fecha,
                monto=Decimal(str(monto))
            )
            
            if ref_bancaria:
                query = query.filter(referencia_bancaria=ref_bancaria)
            
            if query.exists():
                duplicados_encontrados.append({
                    'fecha': fecha,
                    'monto': monto,
                    'referencia': ref_bancaria,
                    'descripcion': descripcion,
                    'transaccion_id': query.first().id
                })
        
        if duplicados_encontrados:
            print(f"\n{Colors.WARNING}⚠️  Se encontraron {len(duplicados_encontrados)} posibles duplicados{Colors.ENDC}")
            print(f"\n{Colors.OKCYAN}Primeros 5 duplicados:{Colors.ENDC}")
            for dup in duplicados_encontrados[:5]:
                print(f"  • {dup['fecha']} | ${dup['monto']:,.2f} | {dup['descripcion']}")
            
            print(f"\n{Colors.WARNING}¿Cómo manejar duplicados?{Colors.ENDC}")
            print("1) Omitir duplicados (no importar)")
            print("2) Sobrescribir duplicados (actualizar existentes)")
            print("3) Preguntar para cada uno")
            print("4) Importar de todos modos (puede crear duplicados)")
            
            while True:
                opcion = input(f"\n{Colors.OKCYAN}Seleccione opción (1/2/3/4): {Colors.ENDC}").strip()
                if opcion == '1':
                    self.modo_duplicados = 'omitir'
                    print(f"{Colors.OKGREEN}✓ Se omitirán los duplicados{Colors.ENDC}")
                    break
                elif opcion == '2':
                    self.modo_duplicados = 'sobrescribir'
                    print(f"{Colors.WARNING}⚠️  Se sobrescribirán los duplicados{Colors.ENDC}")
                    break
                elif opcion == '3':
                    self.modo_duplicados = 'preguntar'
                    print(f"{Colors.OKGREEN}✓ Se preguntará para cada duplicado{Colors.ENDC}")
                    break
                elif opcion == '4':
                    self.modo_duplicados = None
                    print(f"{Colors.WARNING}⚠️  Se importarán todos (puede crear duplicados){Colors.ENDC}")
                    break
                else:
                    print(f"{Colors.FAIL}Opción inválida{Colors.ENDC}")
        else:
            print(f"{Colors.OKGREEN}✓ No se encontraron duplicados{Colors.ENDC}")
            self.modo_duplicados = None
    
    def verificar_duplicado_individual(self, movimiento):
        """Verifica si un movimiento específico es duplicado"""
        fecha = movimiento.get('fecha')
        monto = movimiento.get('monto')
        ref_bancaria = movimiento.get('referencia_bancaria', '')
        
        query = Transaccion.objects.filter(
            fecha=fecha,
            monto=Decimal(str(monto))
        )
        
        if ref_bancaria:
            query = query.filter(referencia_bancaria=ref_bancaria)
        
        return query.first() if query.exists() else None
    
    def mostrar_resumen_inicial(self):
        """Muestra resumen de los movimientos cargados"""
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}RESUMEN DE MOVIMIENTOS A IMPORTAR{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        # Contar por tipo
        tipos = {}
        for mov in self.movimientos:
            tipo = mov.get('tipo', 'DESCONOCIDO')
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        for tipo, count in tipos.items():
            print(f"  {tipo}: {count} movimientos")
        
        print(f"\n  Total: {len(self.movimientos)} movimientos")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    def preguntar_modo_masivo(self):
        """Pregunta si procesar todos los movimientos automáticamente"""
        print(f"{Colors.WARNING}OPCIONES DE PROCESAMIENTO:{Colors.ENDC}")
        print("1. Revisar cada movimiento individualmente (recomendado)")
        print("2. Importar todos automáticamente (confirmación masiva)")
        print("3. Salir")
        
        opcion = input("\nSeleccione opción (1/2/3): ").strip()
        
        if opcion == '3':
            print(f"{Colors.WARNING}Proceso cancelado por el usuario{Colors.ENDC}")
            sys.exit(0)
        
        return opcion == '2'
    
    def procesar_movimientos(self, modo_masivo):
        """Procesa cada movimiento según el modo seleccionado"""
        total = len(self.movimientos)
        
        for idx, movimiento in enumerate(self.movimientos, 1):
            print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
            print(f"{Colors.BOLD}Movimiento {idx}/{total}{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
            
            if modo_masivo:
                # Procesamiento automático
                self.procesar_movimiento_automatico(movimiento, idx)
            else:
                # Procesamiento interactivo
                resultado = self.procesar_movimiento_interactivo(movimiento, idx)
                if resultado == 'exit':
                    print(f"\n{Colors.WARNING}Proceso interrumpido por el usuario{Colors.ENDC}")
                    break
    
    def procesar_movimiento_automatico(self, movimiento, numero):
        """Procesa un movimiento automáticamente"""
        try:
            # Aplicar reglas contables y guardar
            transaccion = self.aplicar_reglas_contables(movimiento)
            
            if not self.test_mode:
                self.guardar_movimiento(transaccion)
            
            self.procesados += 1
            print(f"{Colors.OKGREEN}✓ Movimiento {numero} procesado{Colors.ENDC}")
            
        except Exception as e:
            self.errores += 1
            print(f"{Colors.FAIL}✗ Error en movimiento {numero}: {e}{Colors.ENDC}")
            logger.error(f"Error en movimiento {numero}: {e}")
    
    def procesar_movimiento_interactivo(self, movimiento, numero):
        """Procesa un movimiento de forma interactiva"""
        # Verificar si es duplicado
        transaccion_existente = self.verificar_duplicado_individual(movimiento)
        
        if transaccion_existente and self.modo_duplicados:
            if self.modo_duplicados == 'omitir':
                print(f"\n{Colors.WARNING}⏭️  Movimiento {numero} omitido (duplicado){Colors.ENDC}")
                self.omitidos += 1
                self.log_operaciones.append({
                    'numero': numero,
                    'fecha': movimiento.get('fecha'),
                    'monto': movimiento.get('monto'),
                    'estado': 'OMITIDO_DUPLICADO'
                })
                return 'omitido'
            
            elif self.modo_duplicados == 'preguntar':
                print(f"\n{Colors.WARNING}⚠️  POSIBLE DUPLICADO DETECTADO{Colors.ENDC}")
                print(f"ID existente: {transaccion_existente.id}")
                print(f"Fecha: {transaccion_existente.fecha}")
                print(f"Monto: ${transaccion_existente.monto:,.2f}")
                print(f"Descripción: {transaccion_existente.descripcion[:50]}")
                
                print(f"\n{Colors.WARNING}¿Qué hacer con este duplicado?{Colors.ENDC}")
                print("1) Omitir (no importar)")
                print("2) Sobrescribir (actualizar existente)")
                print("3) Importar de todos modos (crear duplicado)")
                
                while True:
                    opcion_dup = input(f"{Colors.OKCYAN}Seleccione (1/2/3): {Colors.ENDC}").strip()
                    if opcion_dup == '1':
                        self.omitidos += 1
                        print(f"{Colors.WARNING}⏭️  Movimiento omitido{Colors.ENDC}")
                        return 'omitido'
                    elif opcion_dup == '2':
                        movimiento['transaccion_id_actualizar'] = transaccion_existente.id
                        print(f"{Colors.WARNING}🔄 Se actualizará transacción existente{Colors.ENDC}")
                        break
                    elif opcion_dup == '3':
                        print(f"{Colors.WARNING}⚠️  Se creará duplicado{Colors.ENDC}")
                        break
                    else:
                        print(f"{Colors.FAIL}Opción inválida{Colors.ENDC}")
            
            elif self.modo_duplicados == 'sobrescribir':
                movimiento['transaccion_id_actualizar'] = transaccion_existente.id
                print(f"\n{Colors.WARNING}🔄 Actualizando transacción existente ID: {transaccion_existente.id}{Colors.ENDC}")
        
        # Mostrar datos actuales
        self.mostrar_movimiento_tabla(movimiento)
        
        # NUEVA FUNCIÓN: Mostrar y revisar clasificación IA si existe
        feedback_clasificacion = None
        if 'decision_ia' in movimiento and movimiento['decision_ia']:
            feedback_clasificacion = self.revisar_clasificacion_ia(movimiento)
        
        # Opción de ver JSON completo
        if input(f"\n{Colors.OKCYAN}¿Ver JSON completo? (s/n): {Colors.ENDC}").strip().lower() == 's':
            print(f"\n{Colors.HEADER}JSON del movimiento:{Colors.ENDC}")
            print(json.dumps(movimiento, indent=2, ensure_ascii=False))
        
        # Permitir edición
        movimiento_editado = self.editar_movimiento(movimiento)
        
        # Si hubo feedback sobre clasificación IA, aplicarlo
        if feedback_clasificacion and feedback_clasificacion.get('accion') == 'correccion':
            movimiento_editado['tipo'] = feedback_clasificacion['clasificacion_correcta']['tipo']
            movimiento_editado['categoria'] = feedback_clasificacion['clasificacion_correcta']['categoria']
        
        # Aplicar reglas contables
        try:
            transaccion = self.aplicar_reglas_contables(movimiento_editado)
            
            # Mostrar vista previa contable
            self.mostrar_vista_previa_contable(transaccion)
            
            # Confirmar
            while True:
                confirmacion = input(f"\n{Colors.WARNING}¿Confirmar este movimiento? (s/n/exit): {Colors.ENDC}").lower()
                
                if confirmacion == 's':
                    # Propagar ID de actualización si existe
                    if 'transaccion_id_actualizar' in movimiento:
                        transaccion['transaccion_id_actualizar'] = movimiento['transaccion_id_actualizar']
                    
                    if not self.test_mode:
                        self.guardar_movimiento(transaccion)
                    self.procesados += 1
                    
                    # Registrar feedback en memoria si hubo revisión de IA
                    if feedback_clasificacion and self.memoria_sistema:
                        self.registrar_feedback_memoria(movimiento_editado, feedback_clasificacion)
                    
                    print(f"{Colors.OKGREEN}✓ Movimiento guardado{Colors.ENDC}")
                    return 'ok'
                    
                elif confirmacion == 'n':
                    print(f"{Colors.WARNING}Re-editando movimiento...{Colors.ENDC}")
                    return self.procesar_movimiento_interactivo(movimiento, numero)
                    
                elif confirmacion == 'exit':
                    return 'exit'
                    
        except Exception as e:
            self.errores += 1
            print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
            logger.error(f"Error en movimiento {numero}: {e}")
            return 'error'
    
    def mostrar_movimiento_tabla(self, movimiento):
        """Muestra el movimiento en formato tabla"""
        # Usar formato simple sin PrettyTable para evitar dependencias
        print(f"\n{Colors.OKCYAN}Datos del movimiento:{Colors.ENDC}")
        print("+" + "-"*20 + "+" + "-"*35 + "+")
        print(f"| {'Campo':<18} | {'Valor':<33} |")
        print("+" + "-"*20 + "+" + "-"*35 + "+")
        
        # Solo mostrar campos que coinciden con el modelo de BD
        # Manejar campos que podrían ser None
        descripcion = movimiento.get('descripcion', '') or ''
        cuenta_origen = movimiento.get('cuenta_origen', '') or ''
        cuenta_destino = movimiento.get('cuenta_destino', '') or ''
        categoria = movimiento.get('categoria', '') or ''
        ref_bancaria = movimiento.get('referencia_bancaria', '') or ''
        
        campos = [
            ('Fecha', movimiento.get('fecha', '')),
            ('Descripción', descripcion[:33]),
            ('Tipo', movimiento.get('tipo', '')),
            ('Monto', f"${movimiento.get('monto', 0):,.2f}"),
            ('Cuenta Origen', cuenta_origen[:33]),
            ('Cuenta Destino', cuenta_destino[:33]),
            ('Categoría', categoria[:33]),
            ('Ref. Bancaria', ref_bancaria[:33])
        ]
        
        for campo, valor in campos:
            print(f"| {campo:<18} | {valor:<33} |")
        
        print("+" + "-"*20 + "+" + "-"*35 + "+")
    
    def editar_movimiento(self, movimiento):
        """Permite editar campos del movimiento"""
        print(f"\n{Colors.WARNING}Editar campos (Enter para mantener valor actual):{Colors.ENDC}")
        
        movimiento_editado = movimiento.copy()
        
        # Editar cada campo
        campos_editables = [
            ('descripcion', 'Descripción'),
            ('monto', 'Monto'),
            ('cuenta_origen', 'Cuenta Origen'),
            ('cuenta_destino', 'Cuenta Destino'),
            ('categoria', 'Categoría')
        ]
        
        for campo, nombre in campos_editables:
            valor_actual = movimiento_editado.get(campo, '')
            nuevo_valor = input(f"{nombre} [{valor_actual}]: ").strip()
            
            if nuevo_valor:
                if campo == 'monto':
                    try:
                        movimiento_editado[campo] = float(nuevo_valor.replace(',', '').replace('$', ''))
                    except ValueError:
                        print(f"{Colors.FAIL}Monto inválido, manteniendo valor original{Colors.ENDC}")
                else:
                    movimiento_editado[campo] = nuevo_valor
                    
                    # Verificar si necesita crear nueva cuenta/categoría
                    if campo in ['cuenta_origen', 'cuenta_destino']:
                        self.verificar_crear_cuenta(nuevo_valor)
                    elif campo == 'categoria':
                        self.verificar_crear_categoria(nuevo_valor)
        
        return movimiento_editado
    
    def verificar_crear_cuenta(self, nombre_cuenta):
        """Verifica si existe la cuenta y la crea si es necesario"""
        if not nombre_cuenta or nombre_cuenta == '-':
            return None
            
        try:
            cuenta = Cuenta.objects.get(nombre=nombre_cuenta)
            return cuenta
        except Cuenta.DoesNotExist:
            # Intentar crear nueva cuenta
            return self.crear_nueva_cuenta(nombre_cuenta)
    
    def crear_nueva_cuenta(self, nombre):
        """Crea una nueva cuenta con asistente interactivo"""
        try:
            print(f"\n{Colors.WARNING}⚠️  Cuenta '{nombre}' no existe{Colors.ENDC}")
            confirmar = input(f"¿Crear nueva cuenta? (1=Sí, 2=No): ").strip()
            
            if confirmar != '1':
                print(f"{Colors.WARNING}Cuenta no creada{Colors.ENDC}")
                return None
            
            print(f"\n{Colors.OKCYAN}═══ Configuración: {nombre} ═══{Colors.ENDC}")
            
            # Determinar defaults inteligentes
            nombre_upper = nombre.upper()
            
            # Default de naturaleza y tipo basado en el nombre
            if 'TDC' in nombre_upper:
                naturaleza_default = 'ACREEDORA'
                tipo_default = 'CRE'
            elif 'TDB' in nombre_upper or 'BANCO' in nombre_upper:
                naturaleza_default = 'DEUDORA'
                tipo_default = 'DEB'
            elif 'INGRESO' in nombre_upper or 'RENTA' in nombre_upper:
                naturaleza_default = 'ACREEDORA'
                tipo_default = 'ING'
            elif any(serv in nombre_upper for serv in ['CFE', 'TELMEX', 'IZZI', 'TOTALPLAY', 'GAS']):
                naturaleza_default = 'ACREEDORA'
                tipo_default = 'SER'
            else:
                naturaleza_default = 'DEUDORA'
                tipo_default = 'DEB'
            
            # Naturaleza simplificada
            print(f"\nNaturaleza (default: {naturaleza_default}):")
            print("1) DEUDORA")
            print("2) ACREEDORA")
            nat_opcion = input("Seleccione 1/2 [Enter=default]: ").strip()
            if nat_opcion == '2':
                naturaleza = 'ACREEDORA'
            elif nat_opcion == '1':
                naturaleza = 'DEUDORA'
            else:
                naturaleza = naturaleza_default
            
            # Tipo de cuenta simplificado
            print(f"\nTipo (default: {tipo_default}):")
            print("1) DEB - Débito")
            print("2) CRE - Crédito")
            print("3) SER - Servicios")
            print("4) ING - Ingresos")
            tipo_opcion = input("Seleccione 1-4 [Enter=default]: ").strip()
            tipo_map = {'1': 'DEB', '2': 'CRE', '3': 'SER', '4': 'ING'}
            tipo_codigo = tipo_map.get(tipo_opcion, tipo_default) if tipo_opcion else tipo_default
            
            try:
                tipo = TipoCuenta.objects.get(codigo=tipo_codigo)
            except TipoCuenta.DoesNotExist:
                print(f"{Colors.WARNING}Tipo no encontrado, usando DEB{Colors.ENDC}")
                tipo = TipoCuenta.objects.get(codigo='DEB')
            
            # Medio de pago (default inteligente según tipo)
            default_medio_pago = '1' if tipo_codigo in ['DEB', 'CRE'] else '2'
            print(f"\n¿Es medio de pago? (default: {'Sí' if default_medio_pago == '1' else 'No'}):")
            print("1) Sí")
            print("2) No")
            medio_opcion = input("Seleccione 1/2 [Enter=default]: ").strip()
            if medio_opcion == '':
                es_medio_pago = (default_medio_pago == '1')
            else:
                es_medio_pago = (medio_opcion == '1')
            
            # Referencia/Número de cuenta (opcional, simplificado)
            referencia = input("\nReferencia bancaria [Enter=omitir]: ").strip()
            
            # Crear la cuenta
            cuenta = Cuenta.objects.create(
                nombre=nombre,
                tipo=tipo,
                naturaleza=naturaleza,
                es_medio_pago=es_medio_pago,
                moneda='MXN',
                saldo_inicial=0,
                referencia=referencia if referencia else None
            )
            
            print(f"{Colors.OKGREEN}✓ Nueva cuenta creada exitosamente!{Colors.ENDC}")
            print(f"  Nombre: {cuenta.nombre}")
            print(f"  Tipo: {tipo.nombre} ({tipo.codigo})")
            print(f"  Naturaleza: {naturaleza}")
            print(f"  Medio de pago: {'Sí' if es_medio_pago else 'No'}")
            if referencia:
                print(f"  Referencia: {referencia}")
            
            logger.info(f"Cuenta creada: {nombre} - Tipo: {tipo.codigo} - Naturaleza: {naturaleza}")
            return cuenta
            
        except Exception as e:
            print(f"{Colors.FAIL}Error al crear cuenta: {e}{Colors.ENDC}")
            logger.error(f"Error al crear cuenta {nombre}: {e}")
            return None
    
    def verificar_crear_categoria(self, nombre_categoria):
        """Verifica si existe la categoría y la crea si es necesario"""
        if not nombre_categoria:
            return None
            
        try:
            categoria = Categoria.objects.get(nombre=nombre_categoria)
            return categoria
        except Categoria.DoesNotExist:
            print(f"{Colors.WARNING}¡Esa categoría se va a crear, confírmala!: {nombre_categoria}{Colors.ENDC}")
            confirmar = input("¿Crear categoría? (s/n): ").lower()
            
            if confirmar == 's':
                return self.crear_nueva_categoria(nombre_categoria)
            return None
    
    def crear_nueva_categoria(self, nombre):
        """Crea una nueva categoría"""
        try:
            categoria = Categoria.objects.create(
                nombre=nombre,
                tipo='personal'
            )
            
            print(f"{Colors.OKGREEN}¡Nueva categoría creada!: {nombre}{Colors.ENDC}")
            logger.info(f"Categoría creada: {nombre}")
            return categoria
            
        except Exception as e:
            print(f"{Colors.FAIL}Error al crear categoría: {e}{Colors.ENDC}")
            logger.error(f"Error al crear categoría {nombre}: {e}")
            return None
    
    def aplicar_reglas_contables(self, movimiento):
        """Aplica las reglas contables para generar la transacción"""
        # Determinar tipo de transacción
        tipo_mov = movimiento.get('tipo', 'GASTO')
        
        # Obtener o crear cuentas
        cuenta_origen_nombre = movimiento.get('cuenta_origen')
        cuenta_destino_nombre = movimiento.get('cuenta_destino')
        
        cuenta_origen = None
        cuenta_destino = None
        
        if cuenta_origen_nombre and cuenta_origen_nombre != '-':
            cuenta_origen = self.verificar_crear_cuenta(cuenta_origen_nombre)
        
        if cuenta_destino_nombre and cuenta_destino_nombre != '-':
            cuenta_destino = self.verificar_crear_cuenta(cuenta_destino_nombre)
        
        # Obtener o crear categoría
        categoria_nombre = movimiento.get('categoria')
        categoria = None
        if categoria_nombre and categoria_nombre != 'SIN CLASIFICAR':
            categoria = self.verificar_crear_categoria(categoria_nombre)
        
        # Crear objeto transacción con campos que coinciden con el modelo
        transaccion_data = {
            'fecha': datetime.strptime(movimiento.get('fecha', '2025-01-01'), '%Y-%m-%d').date(),
            'descripcion': movimiento.get('descripcion', 'Importado desde BBVA')[:255],  # Limitar a 255 chars
            'monto': Decimal(str(movimiento.get('monto', 0))),
            'tipo': self.mapear_tipo_transaccion(tipo_mov),
            'cuenta_origen': cuenta_origen or self.cuenta_bbva,
            'cuenta_destino': cuenta_destino if cuenta_destino else None,
            'categoria': categoria,
            'estado': TransaccionEstado.LIQUIDADA,  # Usar el enum correcto
            'referencia_bancaria': movimiento.get('referencia_bancaria', '')[:100],  # Limitar a 100 chars
            'moneda': 'MXN',
            'conciliado': False,
            'ajuste': False
        }
        
        # Para transferencias, asegurar que ambas cuentas existan
        if tipo_mov == 'TRANSFERENCIA' and not cuenta_destino:
            transaccion_data['cuenta_destino'] = self.cuenta_bbva
        
        return transaccion_data
    
    def mapear_tipo_transaccion(self, tipo_str):
        """Mapea el tipo de string a TransaccionTipo"""
        mapeo = {
            'INGRESO': TransaccionTipo.INGRESO,
            'GASTO': TransaccionTipo.GASTO,
            'TRANSFERENCIA': TransaccionTipo.TRANSFERENCIA
        }
        return mapeo.get(tipo_str, TransaccionTipo.GASTO)
    
    def mostrar_vista_previa_contable(self, transaccion_data):
        """Muestra la vista previa del asiento contable"""
        print(f"\n{Colors.OKCYAN}Vista previa contable:{Colors.ENDC}")
        
        tipo = transaccion_data['tipo']
        monto = transaccion_data['monto']
        cuenta_origen = transaccion_data['cuenta_origen']
        cuenta_destino = transaccion_data['cuenta_destino']
        
        if tipo == TransaccionTipo.GASTO:
            print(f"  DEBE:  {cuenta_destino.nombre if cuenta_destino else 'Gasto'} ${monto:,.2f}")
            print(f"  HABER: {cuenta_origen.nombre} ${monto:,.2f}")
        elif tipo == TransaccionTipo.INGRESO:
            print(f"  DEBE:  {cuenta_destino.nombre} ${monto:,.2f}")
            print(f"  HABER: {cuenta_origen.nombre if cuenta_origen else 'Ingreso'} ${monto:,.2f}")
        else:  # TRANSFERENCIA
            print(f"  DEBE:  {cuenta_destino.nombre} ${monto:,.2f}")
            print(f"  HABER: {cuenta_origen.nombre} ${monto:,.2f}")
    
    @transaction.atomic
    def guardar_movimiento(self, transaccion_data):
        """Guarda o actualiza el movimiento en la base de datos"""
        try:
            # Verificar si es actualización
            if 'transaccion_id_actualizar' in transaccion_data:
                transaccion_id = transaccion_data.pop('transaccion_id_actualizar')
                transaccion = Transaccion.objects.get(id=transaccion_id)
                
                # Actualizar campos
                for key, value in transaccion_data.items():
                    setattr(transaccion, key, value)
                transaccion.save()
                
                self.log_operaciones.append({
                    'fecha': str(transaccion_data['fecha']),
                    'descripcion': transaccion_data['descripcion'],
                    'monto': float(transaccion_data['monto']),
                    'tipo': str(transaccion_data['tipo']),
                    'id_actualizado': transaccion.id,
                    'estado': 'ACTUALIZADO'
                })
                
                logger.info(f"Transacción actualizada: ID {transaccion.id}")
                self.duplicados += 1
                
            else:
                # Crear nueva transacción
                transaccion = Transaccion.objects.create(**transaccion_data)
                
                self.log_operaciones.append({
                    'fecha': str(transaccion_data['fecha']),
                    'descripcion': transaccion_data['descripcion'],
                    'monto': float(transaccion_data['monto']),
                    'tipo': str(transaccion_data['tipo']),
                    'id_generado': transaccion.id,
                    'estado': 'CREADO'
                })
                
                logger.info(f"Transacción guardada: ID {transaccion.id}")
            
        except Exception as e:
            logger.error(f"Error al guardar transacción: {e}")
            raise
    
    def mostrar_estadisticas_finales(self):
        """Muestra estadísticas finales del proceso"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}RESUMEN FINAL{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        print(f"  ✅ Movimientos procesados: {self.procesados}/{len(self.movimientos)}")
        if self.duplicados > 0:
            print(f"  🔄 Duplicados actualizados: {self.duplicados}")
        if self.omitidos > 0:
            print(f"  ⏭️  Duplicados omitidos: {self.omitidos}")
        if self.errores > 0:
            print(f"  ❌ Errores: {self.errores}")
        
        # Calcular totales
        total_exitosos = self.procesados
        total_no_procesados = self.errores + self.omitidos
        
        print(f"\n  📊 Total exitosos: {total_exitosos}")
        if total_no_procesados > 0:
            print(f"  📊 Total no procesados: {total_no_procesados}")
        
        if self.test_mode:
            print(f"\n{Colors.WARNING}MODO TEST - No se guardaron cambios{Colors.ENDC}")
        
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    
    def revisar_clasificacion_ia(self, movimiento):
        """Muestra y permite revisar la clasificación sugerida por IA"""
        decision_ia = movimiento.get('decision_ia', {})
        
        if not decision_ia:
            return None
        
        print(f"\n{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}🤖 CLASIFICACIÓN SUGERIDA POR IA{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
        
        # Mostrar detalles de clasificación
        # Buscar los campos en decision_ia o en el movimiento directamente
        tipo = decision_ia.get('tipo') or movimiento.get('tipo', 'N/A')
        categoria = decision_ia.get('categoria') or movimiento.get('categoria', 'N/A')
        cuenta_vinculada = decision_ia.get('cuenta_vinculada') or movimiento.get('cuenta_destino', 'N/A')
        nota_ia = decision_ia.get('nota_ia', 'N/A')
        confianza = decision_ia.get('confianza', 0)
        
        print(f"\n📊 Tipo detectado: {Colors.BOLD}{tipo}{Colors.ENDC}")
        print(f"📁 Categoría: {Colors.BOLD}{categoria}{Colors.ENDC}")
        print(f"🏦 Cuenta vinculada: {Colors.BOLD}{cuenta_vinculada}{Colors.ENDC}")
        print(f"📝 Nota IA: {nota_ia}")
        print(f"🎯 Confianza: {Colors.BOLD}{confianza*100:.0f}%{Colors.ENDC}")
        
        # Mostrar reglas aplicadas si existen
        reglas = decision_ia.get('reglas_aplicadas', [])
        if reglas:
            print(f"⚙️  Reglas aplicadas: {', '.join(reglas)}")
        
        # Preguntar al usuario
        print(f"\n{Colors.WARNING}¿La clasificación de la IA es correcta?{Colors.ENDC}")
        print("1) ✅ Sí, es correcta")
        print("2) ❌ No, necesita corrección")
        print("3) ⏭️  Omitir (usar clasificación manual)")
        
        while True:
            opcion = input(f"\n{Colors.OKCYAN}Seleccione opción (1/2/3): {Colors.ENDC}").strip()
            
            if opcion == '1':
                # Confirmación
                print(f"{Colors.OKGREEN}✓ Clasificación IA confirmada{Colors.ENDC}")
                return {
                    'accion': 'confirmacion',
                    'clasificacion_correcta': {
                        'tipo': decision_ia.get('tipo'),
                        'categoria': decision_ia.get('categoria')
                    }
                }
                
            elif opcion == '2':
                # Corrección
                print(f"\n{Colors.WARNING}Ingrese la clasificación correcta:{Colors.ENDC}")
                
                # Seleccionar tipo correcto
                print("\nTipo de transacción:")
                print("1) GASTO")
                print("2) INGRESO")
                print("3) TRANSFERENCIA")
                
                tipo_opcion = input(f"{Colors.OKCYAN}Seleccione tipo (1/2/3): {Colors.ENDC}").strip()
                tipo_map = {'1': 'GASTO', '2': 'INGRESO', '3': 'TRANSFERENCIA'}
                tipo_correcto = tipo_map.get(tipo_opcion, decision_ia.get('tipo'))
                
                # Ingresar categoría correcta
                categoria_correcta = input(f"{Colors.OKCYAN}Categoría correcta (Enter para mantener '{decision_ia.get('categoria')}'): {Colors.ENDC}").strip()
                if not categoria_correcta:
                    categoria_correcta = decision_ia.get('categoria')
                
                print(f"{Colors.OKGREEN}✓ Corrección registrada{Colors.ENDC}")
                return {
                    'accion': 'correccion',
                    'clasificacion_original': {
                        'tipo': decision_ia.get('tipo'),
                        'categoria': decision_ia.get('categoria')
                    },
                    'clasificacion_correcta': {
                        'tipo': tipo_correcto,
                        'categoria': categoria_correcta
                    },
                    'nota': f"Corregido por usuario"
                }
                
            elif opcion == '3':
                # Omitir
                print(f"{Colors.WARNING}⏭️  Clasificación IA omitida{Colors.ENDC}")
                return None
            else:
                print(f"{Colors.FAIL}Opción inválida{Colors.ENDC}")
    
    def registrar_feedback_memoria(self, movimiento, feedback):
        """Registra el feedback del usuario en el sistema de memoria"""
        if not self.memoria_sistema or not feedback:
            return
        
        try:
            # Buscar si hay un patrón asociado
            ref_bancaria = movimiento.get('referencia_bancaria', '')
            
            if ref_bancaria:
                # Registrar feedback para patrón de referencia bancaria
                self.memoria_sistema.registrar_feedback_humano(
                    tipo_patron='referencia_bancaria',
                    patron_id=ref_bancaria,
                    feedback=feedback
                )
                print(f"{Colors.OKGREEN}✓ Feedback registrado en memoria{Colors.ENDC}")
            
            # También actualizar por monto si aplica
            monto = abs(float(movimiento.get('monto', 0)))
            monto_str = f"{monto:.2f}"
            
            if monto_str in self.memoria_sistema.memoria['patrones_detectados']['montos_exactos']:
                self.memoria_sistema.registrar_feedback_humano(
                    tipo_patron='monto_exacto',
                    patron_id=monto_str,
                    feedback=feedback
                )
            
            # Guardar memoria actualizada
            self.memoria_sistema.guardar_memoria()
            
        except Exception as e:
            logger.warning(f"No se pudo registrar feedback en memoria: {e}")
    
    def exportar_log(self):
        """Exporta el log de operaciones a CSV"""
        if not self.log_operaciones:
            return
        
        import csv
        from datetime import datetime
        
        nombre_archivo = f"importacion_bbva_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            with open(nombre_archivo, 'w', newline='', encoding='utf-8') as f:
                if self.log_operaciones:
                    writer = csv.DictWriter(f, fieldnames=self.log_operaciones[0].keys())
                    writer.writeheader()
                    writer.writerows(self.log_operaciones)
            
            print(f"\n{Colors.OKGREEN}Log exportado: {nombre_archivo}{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.FAIL}Error al exportar log: {e}{Colors.ENDC}")
            logger.error(f"Error al exportar log: {e}")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Importador de movimientos BBVA')
    parser.add_argument('--test', action='store_true', help='Modo test (no guarda en BD)')
    
    args = parser.parse_args()
    
    importador = ImportadorBBVA(test_mode=args.test)
    
    try:
        importador.iniciar()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Proceso interrumpido por el usuario{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Error crítico: {e}{Colors.ENDC}")
        logger.critical(f"Error crítico: {e}", exc_info=True)


if __name__ == '__main__':
    main()
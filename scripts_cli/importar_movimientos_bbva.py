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
            
            # Buscar duplicados por fecha + monto ABSOLUTO + referencia
            # Comparamos valores absolutos porque el signo puede variar según el contexto
            from django.db.models import Q
            monto_abs = abs(Decimal(str(monto)))
            
            query = Transaccion.objects.filter(
                fecha=fecha
            ).filter(
                Q(monto=monto_abs) | Q(monto=-monto_abs)
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
        
        # Usar la misma lógica que en verificar_duplicados_iniciales
        # Comparar valores absolutos porque el signo puede variar
        from django.db.models import Q
        monto_abs = abs(Decimal(str(monto)))
        
        query = Transaccion.objects.filter(
            fecha=fecha
        ).filter(
            Q(monto=monto_abs) | Q(monto=-monto_abs)
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
    
    def revisar_editar_movimientos(self):
        """Permite revisar y editar movimientos antes de importar"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}👁️  REVISAR Y EDITAR MOVIMIENTOS{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        while True:
            # Mostrar lista de movimientos con formato mejorado
            print(f"\n{Colors.OKCYAN}Movimientos disponibles para revisar:{Colors.ENDC}\n")
            
            for i, mov in enumerate(self.movimientos[:15], 1):  # Mostrar primeros 15 con espaciado
                self._mostrar_movimiento_resumido(i, mov)
            
            if len(self.movimientos) > 15:
                print(f"\n{Colors.WARNING}... y {len(self.movimientos) - 15} movimientos más{Colors.ENDC}")
            
            print(f"\n{Colors.BOLD}OPCIONES:{Colors.ENDC}")
            print("• Escribe el NÚMERO del movimiento para editarlo (1-" + str(len(self.movimientos)) + ")")
            print("• Escribe 'todos' para ver todos los movimientos")
            print("• Escribe 'listo' o Enter para terminar y volver al menú")
            
            seleccion = input(f"\n{Colors.OKCYAN}Tu elección: {Colors.ENDC}").strip().lower()
            
            if seleccion == '' or seleccion == 'listo':
                print(f"{Colors.OKGREEN}✓ Revisión completada{Colors.ENDC}")
                break
            elif seleccion == 'todos':
                # Mostrar todos los movimientos paginados
                self.mostrar_todos_movimientos_paginados()
                continue
            elif seleccion.isdigit():
                num = int(seleccion)
                if 1 <= num <= len(self.movimientos):
                    # Editar el movimiento seleccionado
                    movimiento = self.movimientos[num - 1]
                    print(f"\n{Colors.HEADER}Editando movimiento #{num}{Colors.ENDC}")
                    self.mostrar_movimiento_tabla(movimiento)
                    
                    # Usar la función de editar campos existente
                    movimiento_editado = self.editar_campos(movimiento)
                    if movimiento_editado:
                        # Actualizar el movimiento en la lista
                        self.movimientos[num - 1].update(movimiento_editado)
                        print(f"{Colors.OKGREEN}✓ Movimiento #{num} actualizado{Colors.ENDC}")
                else:
                    print(f"{Colors.FAIL}Número fuera de rango{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}Opción no válida{Colors.ENDC}")
    
    def _mostrar_movimiento_resumido(self, num, mov):
        """Helper para mostrar un movimiento en formato resumido con espaciado"""
        fecha = mov.get('fecha', 'Sin fecha')
        tipo = mov.get('tipo', 'SIN TIPO')[:10]
        categoria = mov.get('categoria', 'Sin categoría')[:20]
        monto = float(mov.get('monto', 0))
        
        # Obtener cuenta vinculada de forma segura
        cuenta_vinculada = mov.get('cuenta_destino')
        if not cuenta_vinculada or cuenta_vinculada == '-':
            if tipo == 'TRANSFERENCIA':
                cuenta_vinculada = mov.get('cuenta_origen', '-')
            else:
                cuenta_vinculada = '-'
        
        # Asegurar que cuenta_vinculada sea string
        if cuenta_vinculada is None:
            cuenta_vinculada = '-'
        elif not isinstance(cuenta_vinculada, str):
            # Si es un objeto Cuenta, obtener su nombre
            cuenta_vinculada = getattr(cuenta_vinculada, 'nombre', str(cuenta_vinculada))
        
        # Truncar strings de forma segura
        cuenta_vinculada_display = (cuenta_vinculada[:15] if len(cuenta_vinculada) > 15 else cuenta_vinculada)
        desc = mov.get('descripcion', 'Sin descripción')[:20]
        
        # Color según el tipo
        if tipo == 'GASTO':
            color_tipo = Colors.FAIL
        elif tipo == 'INGRESO':
            color_tipo = Colors.OKGREEN
        else:
            color_tipo = Colors.OKCYAN
        
        # Color para el monto
        color_monto = Colors.FAIL if monto < 0 else Colors.OKGREEN
        
        # Primera línea: ID, Fecha, Tipo, Categoría
        print(f"{Colors.BOLD}[{num:3}]{Colors.ENDC} {fecha} | {color_tipo}{tipo:<10}{Colors.ENDC} | {categoria:<20}")
        # Segunda línea: Monto, Cuenta vinculada, Descripción
        print(f"     {color_monto}${abs(monto):>12,.2f}{Colors.ENDC} | Cta: {cuenta_vinculada_display:<15} | {desc}")
        # Línea vacía para separación
        print()
    
    def mostrar_todos_movimientos_paginados(self):
        """Muestra todos los movimientos de forma paginada"""
        page_size = 10  # Reducido porque ahora cada movimiento ocupa 3 líneas
        total_pages = (len(self.movimientos) + page_size - 1) // page_size
        current_page = 1
        
        while True:
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, len(self.movimientos))
            
            print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
            print(f"{Colors.HEADER}Página {current_page}/{total_pages} - Movimientos {start_idx+1} a {end_idx} de {len(self.movimientos)}{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
            
            for i in range(start_idx, end_idx):
                self._mostrar_movimiento_resumido(i + 1, self.movimientos[i])
            
            print(f"\n[Enter=siguiente página, 'a'=anterior, 'q'=salir, o número de página]")
            opcion = input(f"Página ({current_page}/{total_pages}): ").strip().lower()
            
            if opcion == '' and current_page < total_pages:
                current_page += 1
            elif opcion == 'a' and current_page > 1:
                current_page -= 1
            elif opcion == 'q':
                break
            elif opcion.isdigit():
                new_page = int(opcion)
                if 1 <= new_page <= total_pages:
                    current_page = new_page
                else:
                    print(f"{Colors.FAIL}Página fuera de rango{Colors.ENDC}")
            else:
                if opcion == '' and current_page == total_pages:
                    break  # En la última página, Enter sale
                else:
                    print(f"{Colors.FAIL}Opción no válida{Colors.ENDC}")
    
    def preguntar_modo_masivo(self):
        """Pregunta si procesar todos los movimientos automáticamente"""
        while True:
            print(f"{Colors.WARNING}OPCIONES DE PROCESAMIENTO:{Colors.ENDC}")
            print("1. Revisar cada movimiento individualmente (recomendado)")
            print("2. Importar todos automáticamente (confirmación masiva)")
            print("3. 👁️  Revisar/editar movimientos antes de importar")
            print("4. Salir")
            
            opcion = input("\nSeleccione opción (1/2/3/4): ").strip()
            
            if opcion == '4':
                print(f"{Colors.WARNING}Proceso cancelado por el usuario{Colors.ENDC}")
                sys.exit(0)
            elif opcion == '3':
                # Revisar y editar movimientos
                self.revisar_editar_movimientos()
                # Después de revisar, volver a mostrar el menú
                continue
            elif opcion in ['1', '2']:
                return opcion == '2'
            else:
                print(f"{Colors.FAIL}Opción no válida{Colors.ENDC}")
                continue
    
    def procesar_movimientos(self, modo_masivo):
        """Procesa cada movimiento según el modo seleccionado"""
        total = len(self.movimientos)
        
        for idx, movimiento in enumerate(self.movimientos, 1):
            if modo_masivo:
                # En modo masivo, siempre mostrar encabezado
                print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
                print(f"{Colors.BOLD}Movimiento {idx}/{total}{Colors.ENDC}")
                print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
                # Procesamiento automático
                self.procesar_movimiento_automatico(movimiento, idx)
            else:
                # En modo interactivo, el encabezado se muestra dentro de la función
                # solo si el movimiento no es omitido
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
        # Verificar si es duplicado ANTES de mostrar cualquier cosa
        transaccion_existente = self.verificar_duplicado_individual(movimiento)
        
        if transaccion_existente and self.modo_duplicados:
            if self.modo_duplicados == 'omitir':
                # No mostrar el encabezado del movimiento, solo el mensaje de omisión
                print(f"\n{Colors.WARNING}⏭️  Movimiento {numero}/{len(self.movimientos)} omitido (duplicado){Colors.ENDC}")
                print(f"    Fecha: {movimiento.get('fecha')} | Monto: ${movimiento.get('monto'):,.2f}")
                print(f"    Descripción: {movimiento.get('descripcion', '')[:50]}")
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
        
        # Mostrar encabezado del movimiento (solo si no fue omitido antes)
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}Movimiento {numero}/{len(self.movimientos)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        # Mostrar datos actuales
        self.mostrar_movimiento_tabla(movimiento)
        
        # PASO 1: Revisar clasificación IA si existe
        feedback_clasificacion = None
        if 'decision_ia' in movimiento and movimiento['decision_ia']:
            feedback_clasificacion = self.revisar_clasificacion_ia(movimiento)
            
            # Si el usuario eligió salir desde la clasificación IA
            if feedback_clasificacion == 'exit':
                return 'exit'
        
        # Si hubo feedback sobre clasificación IA, aplicarlo
        if feedback_clasificacion and isinstance(feedback_clasificacion, dict) and feedback_clasificacion.get('accion') == 'correccion':
            movimiento['tipo'] = feedback_clasificacion['clasificacion_correcta']['tipo']
            movimiento['categoria'] = feedback_clasificacion['clasificacion_correcta']['categoria']
            # Si se corrigió la cuenta vinculada (para transferencias)
            if feedback_clasificacion['clasificacion_correcta'].get('cuenta_vinculada'):
                movimiento['cuenta_destino'] = feedback_clasificacion['clasificacion_correcta']['cuenta_vinculada']
        
        # PASO 2: ¿Los campos son correctos?
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}VERIFICACIÓN DE CAMPOS{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        # Primero mostrar los campos actuales del movimiento
        print(f"\n{Colors.OKCYAN}Campos actuales del movimiento:{Colors.ENDC}")
        print(f"  📅 Fecha: {movimiento.get('fecha', '')}")
        print(f"  📝 Descripción: {movimiento.get('descripcion', '')[:60]}")
        print(f"  💰 Monto: ${movimiento.get('monto', 0):,.2f}")
        print(f"  📤 Cuenta Origen: {movimiento.get('cuenta_origen', 'TDB BBVA 5019')}")
        print(f"  📥 Cuenta Destino: {movimiento.get('cuenta_destino', '-')}")
        print(f"  📁 Categoría: {movimiento.get('categoria', 'SIN CLASIFICAR')}")
        print(f"  🏷️  Tipo: {movimiento.get('tipo', 'GASTO')}")
        
        # Aplicar reglas contables para mostrar vista previa
        # IMPORTANTE: Esto puede modificar la categoría si el usuario la cambia
        transaccion_preview = self.aplicar_reglas_contables(movimiento)
        
        # Si se seleccionó una categoría diferente, actualizar el movimiento
        if transaccion_preview.get('categoria') and hasattr(transaccion_preview['categoria'], 'nombre'):
            movimiento['categoria'] = transaccion_preview['categoria'].nombre
        
        # También actualizar cuentas si se crearon o seleccionaron diferentes
        if transaccion_preview.get('cuenta_destino') and hasattr(transaccion_preview['cuenta_destino'], 'nombre'):
            movimiento['cuenta_destino'] = transaccion_preview['cuenta_destino'].nombre
        if transaccion_preview.get('cuenta_origen') and hasattr(transaccion_preview['cuenta_origen'], 'nombre'):
            movimiento['cuenta_origen'] = transaccion_preview['cuenta_origen'].nombre
        
        self.mostrar_vista_previa_contable(transaccion_preview)
        
        print(f"\n{Colors.OKCYAN}¿Los campos son correctos?{Colors.ENDC}")
        print("1) ✅ Sí, todo correcto")
        print("2) 🏦 Editar solo cuenta vinculada (9=ver lista)")  
        print("3) ✏️  Editar todos los campos")
        
        opcion_campos = input(f"{Colors.OKCYAN}Seleccione (1/2/3) [Enter=1]: {Colors.ENDC}").strip() or '1'
        
        movimiento_editado = movimiento.copy()
        
        if opcion_campos == '2':
            # Solo editar cuenta destino/vinculada
            cuenta_destino_actual = movimiento.get('cuenta_destino', '')
            
            while True:
                print(f"\n{Colors.OKCYAN}Ingresa cuenta vinculada (nombre/número/9=ayuda/x=cancelar):{Colors.ENDC}")
                nueva_cuenta = input(f"Cuenta Destino [{cuenta_destino_actual}]: ").strip().lower()
                
                # Cancelar y regresar
                if nueva_cuenta == 'x':
                    print(f"{Colors.WARNING}Cancelado, regresando...{Colors.ENDC}")
                    break
                
                # Si presiona 9 o es un número, mostrar lista
                elif nueva_cuenta == '9' or (nueva_cuenta.isdigit() and nueva_cuenta != '0'):
                    opcion_num = int(nueva_cuenta)
                    
                    # Mostrar lista de cuentas disponibles
                    print(f"\n{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
                    print(f"{Colors.BOLD}📚 CUENTAS DISPONIBLES{Colors.ENDC}")
                    print(f"{Colors.OKCYAN}{'='*60}{Colors.ENDC}\n")
                    
                    try:
                        from core.models import Cuenta
                        cuentas = Cuenta.objects.all().order_by('id')
                        
                        if cuentas.exists():
                            # Crear diccionario ID -> nombre para búsqueda rápida
                            cuentas_dict = {}
                            
                            # Mostrar en 3 columnas con IDs
                            cuentas_list = list(cuentas)
                            num_cuentas = len(cuentas_list)
                            columnas = 3
                            
                            # Calcular filas necesarias
                            filas = (num_cuentas + columnas - 1) // columnas
                            
                            for i in range(filas):
                                fila = []
                                for j in range(columnas):
                                    idx = i + j * filas
                                    if idx < num_cuentas:
                                        cuenta = cuentas_list[idx]
                                        cuentas_dict[cuenta.id] = cuenta.nombre
                                        # Formato: [ID] Nombre (truncado a 18 chars)
                                        nombre_truncado = cuenta.nombre[:18]
                                        fila.append(f"[{cuenta.id:3}] {nombre_truncado:<18}")
                                print("  " + " | ".join(fila))
                            
                            print(f"\n{Colors.OKGREEN}Total: {num_cuentas} cuentas{Colors.ENDC}")
                            print(f"{Colors.WARNING}[  0] → Crear nueva cuenta{Colors.ENDC}")
                            print(f"{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
                            
                            # Si ya seleccionó un número válido distinto de 9
                            if opcion_num != 9 and opcion_num > 0 and opcion_num in cuentas_dict:
                                nombre_seleccionado = cuentas_dict[opcion_num]
                                print(f"\n{Colors.OKGREEN}✓ Seleccionaste: {nombre_seleccionado}{Colors.ENDC}")
                                movimiento_editado['cuenta_destino'] = nombre_seleccionado
                                break
                            
                            # Después de mostrar la lista, preguntar de nuevo
                            print(f"\n{Colors.BOLD}OPCIONES:{Colors.ENDC}")
                            print("• Escribe el NOMBRE de la cuenta nueva")
                            print("• Escribe el NÚMERO de la cuenta que eliges")
                            print("• Escribe '0' para crear cuenta nueva")
                            print("• Escribe '9' para ver la lista otra vez")
                            print("• Escribe 'x' para cancelar")
                            
                            seleccion = input(f"\n{Colors.OKCYAN}Tu elección: {Colors.ENDC}").strip().lower()
                            
                            if seleccion == 'x':
                                print(f"{Colors.WARNING}Cancelado{Colors.ENDC}")
                                break
                            elif seleccion == '9':
                                continue  # Mostrar lista otra vez
                            elif seleccion == '0':
                                nombre_nueva = input("Nombre de la nueva cuenta: ").strip()
                                if nombre_nueva:
                                    movimiento_editado['cuenta_destino'] = nombre_nueva
                                    break
                            elif seleccion.isdigit():
                                id_seleccionado = int(seleccion)
                                if id_seleccionado in cuentas_dict:
                                    nombre_seleccionado = cuentas_dict[id_seleccionado]
                                    print(f"{Colors.OKGREEN}✓ Seleccionaste: {nombre_seleccionado}{Colors.ENDC}")
                                    movimiento_editado['cuenta_destino'] = nombre_seleccionado
                                    break
                                else:
                                    print(f"{Colors.FAIL}ID no válido{Colors.ENDC}")
                                    continue
                            else:
                                # Asumimos que escribió un nombre de cuenta
                                movimiento_editado['cuenta_destino'] = seleccion
                                break
                        else:
                            print(f"{Colors.WARNING}No hay cuentas registradas{Colors.ENDC}")
                            nombre_nueva = input("Nombre de la nueva cuenta: ").strip()
                            if nombre_nueva:
                                movimiento_editado['cuenta_destino'] = nombre_nueva
                                break
                            
                    except Exception as e:
                        print(f"{Colors.FAIL}Error al obtener cuentas: {e}{Colors.ENDC}")
                        continue
                    
                # Si escribió '0' para crear nueva
                elif nueva_cuenta == '0':
                    nombre_nueva = input("Nombre de la nueva cuenta: ").strip()
                    if nombre_nueva:
                        movimiento_editado['cuenta_destino'] = nombre_nueva
                        break
                        
                # Si escribió un nombre directamente (no es número ni comandos especiales)
                elif nueva_cuenta and not nueva_cuenta.isdigit():
                    # Capitalizar primera letra para consistencia
                    movimiento_editado['cuenta_destino'] = nueva_cuenta.title()
                    break
                    
                # Si presionó Enter (mantener actual)
                elif not nueva_cuenta:
                    break
                
        elif opcion_campos == '3':
            # Editar todos los campos
            print(f"\n{Colors.WARNING}Editar campos (Enter para mantener valor actual):{Colors.ENDC}")
            desc = input(f"Descripción [{movimiento.get('descripcion', '')}]: ").strip()
            if desc:
                movimiento_editado['descripcion'] = desc
                
            monto_str = input(f"Monto [{movimiento.get('monto', 0)}]: ").strip()
            if monto_str:
                try:
                    movimiento_editado['monto'] = float(monto_str)
                except ValueError:
                    print(f"{Colors.FAIL}Monto inválido, manteniendo original{Colors.ENDC}")
                    
            cuenta_origen = input(f"Cuenta Origen [{movimiento.get('cuenta_origen', '')}]: ").strip()
            if cuenta_origen:
                movimiento_editado['cuenta_origen'] = cuenta_origen
                
            cuenta_destino = input(f"Cuenta Destino [{movimiento.get('cuenta_destino', '')}]: ").strip()
            if cuenta_destino:
                movimiento_editado['cuenta_destino'] = cuenta_destino
                
            categoria = input(f"Categoría [{movimiento.get('categoria', '')}]: ").strip()
            if categoria:
                movimiento_editado['categoria'] = categoria
        
        # PASO 3: ¿Ver JSON completo?
        ver_json = input(f"\n{Colors.OKCYAN}¿Ver JSON completo? (1=Sí, Enter=No): {Colors.ENDC}").strip()
        if ver_json == '1':
            print(f"\n{Colors.HEADER}JSON del movimiento:{Colors.ENDC}")
            print(json.dumps(movimiento_editado, indent=2, ensure_ascii=False))
        
        # Aplicar reglas contables con movimiento editado
        try:
            transaccion = self.aplicar_reglas_contables(movimiento_editado)
            
            # Mostrar vista previa contable final
            print(f"\n{Colors.OKGREEN}Vista previa contable FINAL:{Colors.ENDC}")
            self.mostrar_vista_previa_contable(transaccion)
            
            # PASO 4: Confirmar guardado
            while True:
                print(f"\n{Colors.WARNING}¿Qué deseas hacer?{Colors.ENDC}")
                print("1) 💾 Guardar transacción")
                print("2) ✏️  Editar nuevamente")  
                print("3) 🚪 Salir del importador")
                print("4) ❓ Ayuda")
                
                opcion = input(f"{Colors.OKCYAN}Seleccione (1/2/3/4) [Enter=1]: {Colors.ENDC}").strip() or '1'
                
                if opcion == '1':
                    # Doble confirmación para guardar
                    print(f"\n{Colors.WARNING}⚠️  CONFIRMACIÓN FINAL{Colors.ENDC}")
                    print(f"Estás a punto de guardar esta transacción en la base de datos.")
                    confirmar_final = input(f"{Colors.WARNING}¿Confirmar guardado? (1=Sí, 2=No) [Enter=1]: {Colors.ENDC}").strip() or '1'
                    
                    if confirmar_final == '1':
                        # Propagar ID de actualización si existe
                        if 'transaccion_id_actualizar' in movimiento:
                            transaccion['transaccion_id_actualizar'] = movimiento['transaccion_id_actualizar']
                        
                        if not self.test_mode:
                            self.guardar_movimiento(transaccion)
                        self.procesados += 1
                        
                        # Registrar feedback en memoria si hubo revisión de IA
                        if feedback_clasificacion and self.memoria_sistema:
                            self.registrar_feedback_memoria(movimiento_editado, feedback_clasificacion)
                        
                        print(f"{Colors.OKGREEN}✓ Movimiento guardado exitosamente{Colors.ENDC}")
                        return 'ok'
                    else:
                        print(f"{Colors.WARNING}Guardado cancelado, regresando al menú...{Colors.ENDC}")
                        continue  # Vuelve a mostrar las 4 opciones
                        
                elif opcion == '2':
                    print(f"{Colors.WARNING}Re-editando movimiento...{Colors.ENDC}")
                    return self.procesar_movimiento_interactivo(movimiento, numero)
                    
                elif opcion == '3':
                    print(f"\n{Colors.WARNING}¿Seguro que deseas salir?{Colors.ENDC}")
                    confirmar_salir = input(f"1=Sí salir, 2=No, continuar [Enter=2]: ").strip() or '2'
                    if confirmar_salir == '1':
                        return 'exit'
                    else:
                        continue  # Vuelve a mostrar las 4 opciones
                        
                elif opcion == '4':
                    # Mostrar ayuda
                    print(f"\n{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
                    print(f"{Colors.BOLD}📚 AYUDA - Opciones disponibles{Colors.ENDC}")
                    print(f"{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
                    print(f"\n{Colors.OKGREEN}1) Guardar transacción:{Colors.ENDC}")
                    print("   • Guarda el movimiento en la base de datos")
                    print("   • Requiere confirmación adicional por seguridad")
                    print("   • Una vez guardado, continúa con el siguiente movimiento")
                    
                    print(f"\n{Colors.WARNING}2) Editar nuevamente:{Colors.ENDC}")
                    print("   • Te regresa al inicio de este movimiento")
                    print("   • Puedes cambiar cualquier campo")
                    print("   • Útil si detectaste un error")
                    
                    print(f"\n{Colors.FAIL}3) Salir del importador:{Colors.ENDC}")
                    print("   • Termina el proceso de importación")
                    print("   • Los movimientos ya guardados permanecen")
                    print("   • Puedes continuar después desde donde quedaste")
                    
                    print(f"\n{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
                    input(f"\n{Colors.OKCYAN}Presiona Enter para continuar...{Colors.ENDC}")
                    # Después de la ayuda, vuelve a mostrar las opciones
                    
                else:
                    print(f"{Colors.FAIL}Opción inválida. Por favor selecciona 1, 2, 3 o 4{Colors.ENDC}")
                    
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
            
            # Para categorías, ofrecer sistema de ayuda
            if campo == 'categoria':
                print(f"\n{Colors.OKCYAN}Categoría (nombre/número/9=ayuda/x=mantener):{Colors.ENDC}")
                nuevo_valor = input(f"{nombre} [{valor_actual}]: ").strip()
                
                if nuevo_valor == '9' or (nuevo_valor.isdigit() and nuevo_valor != '0'):
                    # Mostrar lista de categorías
                    categoria_seleccionada = self.seleccionar_categoria_con_ayuda()
                    if categoria_seleccionada:
                        movimiento_editado[campo] = categoria_seleccionada.nombre
                elif nuevo_valor and nuevo_valor != 'x':
                    movimiento_editado[campo] = nuevo_valor
                    self.verificar_crear_categoria(nuevo_valor)
                    
            # Para cuentas (origen y destino), ofrecer sistema de ayuda
            elif campo in ['cuenta_origen', 'cuenta_destino']:
                campo_display = 'Cuenta Vinculada' if campo == 'cuenta_destino' else nombre
                print(f"\n{Colors.OKCYAN}{campo_display} (nombre/número/9=ayuda/x=mantener):{Colors.ENDC}")
                nuevo_valor = input(f"{nombre} [{valor_actual}]: ").strip()
                
                if nuevo_valor == '9' or (nuevo_valor.isdigit() and nuevo_valor != '0'):
                    # Mostrar lista de cuentas con selección
                    cuenta_seleccionada = self.seleccionar_cuenta_con_ayuda()
                    if cuenta_seleccionada:
                        movimiento_editado[campo] = cuenta_seleccionada
                elif nuevo_valor == '0':
                    # Crear nueva cuenta
                    nombre_nueva = input("Nombre de la nueva cuenta: ").strip()
                    if nombre_nueva:
                        movimiento_editado[campo] = nombre_nueva
                        self.verificar_crear_cuenta(nombre_nueva)
                elif nuevo_valor and nuevo_valor != 'x':
                    movimiento_editado[campo] = nuevo_valor
                    self.verificar_crear_cuenta(nuevo_valor)
                    
            else:
                nuevo_valor = input(f"{nombre} [{valor_actual}]: ").strip()
                
                if nuevo_valor:
                    if campo == 'monto':
                        try:
                            movimiento_editado[campo] = float(nuevo_valor.replace(',', '').replace('$', ''))
                        except ValueError:
                            print(f"{Colors.FAIL}Monto inválido, manteniendo valor original{Colors.ENDC}")
                    else:
                        movimiento_editado[campo] = nuevo_valor
        
        return movimiento_editado
    
    def seleccionar_cuenta_con_ayuda(self):
        """Muestra lista de cuentas con IDs para selección rápida (versión reutilizable)"""
        try:
            print(f"\n{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
            print(f"{Colors.BOLD}📚 CUENTAS DISPONIBLES{Colors.ENDC}")
            print(f"{Colors.OKCYAN}{'='*60}{Colors.ENDC}\n")
            
            from core.models import Cuenta
            cuentas = Cuenta.objects.all().order_by('id')
            
            if not cuentas.exists():
                print(f"{Colors.WARNING}No hay cuentas registradas{Colors.ENDC}")
                nombre_nueva = input("Nombre de la nueva cuenta: ").strip()
                if nombre_nueva:
                    self.verificar_crear_cuenta(nombre_nueva)
                    return nombre_nueva
                return None
            
            # Crear diccionario ID -> cuenta
            cuentas_dict = {}
            cuentas_list = list(cuentas)
            
            # Mostrar en 3 columnas con IDs
            num_cuentas = len(cuentas_list)
            columnas = 3
            filas = (num_cuentas + columnas - 1) // columnas
            
            for i in range(filas):
                fila = []
                for j in range(columnas):
                    idx = i + j * filas
                    if idx < num_cuentas:
                        cuenta = cuentas_list[idx]
                        cuentas_dict[cuenta.id] = cuenta.nombre
                        # Formato: [ID] Nombre (truncado a 18 chars)
                        nombre_truncado = cuenta.nombre[:18]
                        fila.append(f"[{cuenta.id:3}] {nombre_truncado:<18}")
                print("  " + " | ".join(fila))
            
            print(f"\n{Colors.OKGREEN}Total: {num_cuentas} cuentas{Colors.ENDC}")
            print(f"{Colors.WARNING}[  0] → Crear nueva cuenta{Colors.ENDC}")
            print(f"{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
            
            # Solicitar selección
            while True:
                print(f"\n{Colors.BOLD}OPCIONES:{Colors.ENDC}")
                print("• Escribe el NÚMERO de la cuenta que eliges")
                print("• Escribe '0' para crear nueva cuenta")
                print("• Escribe '9' para ver la lista otra vez")
                print("• Escribe 'x' para cancelar")
                
                seleccion = input(f"\n{Colors.OKCYAN}Tu elección: {Colors.ENDC}").strip().lower()
                
                if seleccion == 'x':
                    print(f"{Colors.WARNING}Cancelado{Colors.ENDC}")
                    return None
                    
                elif seleccion == '9':
                    # Mostrar lista otra vez (recursivo)
                    return self.seleccionar_cuenta_con_ayuda()
                    
                elif seleccion == '0':
                    nombre_nueva = input("Nombre de la nueva cuenta: ").strip()
                    if nombre_nueva:
                        self.verificar_crear_cuenta(nombre_nueva)
                        return nombre_nueva
                    continue
                    
                elif seleccion.isdigit():
                    id_seleccionado = int(seleccion)
                    if id_seleccionado in cuentas_dict:
                        nombre_seleccionado = cuentas_dict[id_seleccionado]
                        print(f"{Colors.OKGREEN}✓ Seleccionaste: {nombre_seleccionado}{Colors.ENDC}")
                        return nombre_seleccionado
                    else:
                        print(f"{Colors.FAIL}ID no válido{Colors.ENDC}")
                        continue
                else:
                    # Asumimos que escribió un nombre de cuenta
                    return seleccion
                    
        except Exception as e:
            print(f"{Colors.FAIL}Error al mostrar cuentas: {e}{Colors.ENDC}")
            return None
    
    def verificar_crear_cuenta(self, nombre_cuenta, movimiento=None):
        """Verifica si existe la cuenta y la crea si es necesario"""
        if not nombre_cuenta or nombre_cuenta == '-':
            return None
            
        try:
            cuenta = Cuenta.objects.get(nombre=nombre_cuenta)
            return cuenta
        except Cuenta.DoesNotExist:
            # Intentar crear nueva cuenta
            return self.crear_nueva_cuenta(nombre_cuenta, movimiento)
    
    def crear_nueva_cuenta(self, nombre, movimiento=None):
        """Crea una nueva cuenta con asistente interactivo"""
        try:
            print(f"\n{Colors.WARNING}⚠️  Cuenta '{nombre}' no existe{Colors.ENDC}")
            
            # Si se proporciona el movimiento, mostrar sus detalles para contexto
            if movimiento:
                print(f"\n{Colors.HEADER}Contexto del movimiento:{Colors.ENDC}")
                self.mostrar_movimiento_tabla(movimiento)
            
            confirmar = input(f"¿Crear nueva cuenta? (1=Sí, 2=No) [Enter=1]: ").strip() or '1'
            
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
            while True:
                print(f"\nNaturaleza (default: {naturaleza_default}):")
                print("1) DEUDORA")
                print("2) ACREEDORA")
                print("3) ❓ Ayuda - ¿Qué significa esto?")
                nat_opcion = input("Seleccione 1/2/3 [Enter=default]: ").strip()
                
                if nat_opcion == '3':
                    # Mostrar ayuda sobre naturalezas
                    print(f"\n{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
                    print(f"{Colors.BOLD}📚 NATURALEZA DE LAS CUENTAS - Explicación Simple{Colors.ENDC}")
                    print(f"{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
                    
                    print(f"\n{Colors.OKGREEN}DEUDORA (Lo que tienes o gastas):{Colors.ENDC}")
                    print("📌 Cuentas donde TIENES dinero o GASTAS dinero")
                    print("   • Cuentas de banco (débito)")
                    print("   • Efectivo")
                    print("   • Gastos (comida, renta, servicios)")
                    print("   • Lo que otros te deben")
                    print("   ➡️  Aumentan cuando ENTRA dinero o GASTAS")
                    
                    print(f"\n{Colors.WARNING}ACREEDORA (Lo que debes o ganas):{Colors.ENDC}")
                    print("📌 Cuentas donde DEBES dinero o GANAS dinero")
                    print("   • Tarjetas de crédito")
                    print("   • Préstamos e hipotecas")
                    print("   • Ingresos (sueldo, rentas)")
                    print("   • Lo que debes a otros")
                    print("   ➡️  Aumentan cuando DEBES más o GANAS dinero")
                    
                    print(f"\n{Colors.BOLD}💡 REGLA SIMPLE:{Colors.ENDC}")
                    print("• ¿Es dinero que TIENES? → DEUDORA")
                    print("• ¿Es dinero que DEBES? → ACREEDORA")
                    print("• ¿Es un GASTO? → DEUDORA")
                    print("• ¿Es un INGRESO? → ACREEDORA")
                    
                    print(f"\n{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
                    input(f"\n{Colors.OKCYAN}Presiona Enter para continuar...{Colors.ENDC}")
                    continue  # Volver a mostrar las opciones
                    
                elif nat_opcion == '2':
                    naturaleza = 'ACREEDORA'
                    break
                elif nat_opcion == '1':
                    naturaleza = 'DEUDORA'
                    break
                else:
                    naturaleza = naturaleza_default
                    break
            
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
            
            # Medio de pago (default siempre No)
            default_medio_pago = '2'  # Siempre default a No
            print(f"\n¿Es medio de pago? (default: No):")
            print("1) Sí")
            print("2) No")
            medio_opcion = input("Seleccione 1/2 [Enter=default]: ").strip().lower()
            
            # Manejar diferentes formas de responder (1, 2, si, no, yes, NO, etc.)
            if medio_opcion == '':
                es_medio_pago = (default_medio_pago == '1')
            elif medio_opcion in ['1', 's', 'si', 'sí', 'yes', 'y']:
                es_medio_pago = True
            elif medio_opcion in ['2', 'n', 'no', '0']:
                es_medio_pago = False
            else:
                # Si no entendemos la respuesta, usar el default
                print(f"{Colors.WARNING}Respuesta no reconocida, usando default{Colors.ENDC}")
                es_medio_pago = (default_medio_pago == '1')
            
            # Referencia/Número de cuenta (opcional, simplificado)
            referencia = input("\nReferencia bancaria [Enter=omitir]: ").strip()
            
            # Crear la cuenta - usar string vacío si no hay referencia para evitar NULL constraint
            cuenta = Cuenta.objects.create(
                nombre=nombre,
                tipo=tipo,
                naturaleza=naturaleza,
                medio_pago=es_medio_pago,  # Campo correcto es medio_pago
                moneda='MXN',
                saldo_inicial=0,
                referencia=referencia if referencia else ''  # String vacío en lugar de None
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
    
    def verificar_crear_categoria(self, nombre_categoria, movimiento=None):
        """Verifica si existe la categoría y la crea si es necesario con sistema de ayuda"""
        if not nombre_categoria:
            return None
            
        try:
            categoria = Categoria.objects.get(nombre=nombre_categoria)
            return categoria
        except Categoria.DoesNotExist:
            print(f"{Colors.WARNING}⚠️  Categoría '{nombre_categoria}' no existe{Colors.ENDC}")
            
            # Si se proporciona el movimiento, mostrar sus detalles para contexto
            if movimiento:
                print(f"\n{Colors.HEADER}Contexto del movimiento:{Colors.ENDC}")
                self.mostrar_movimiento_tabla(movimiento)
            
            while True:
                print(f"\n{Colors.OKCYAN}Opciones disponibles:{Colors.ENDC}")
                print("1) Crear nueva categoría")
                print("2) Seleccionar categoría existente")
                print("3) ✏️  Editar campos del movimiento")
                print("9) Ver lista de categorías")
                print("x) Cancelar")
                
                opcion = input(f"{Colors.OKCYAN}Seleccione (1/2/3/9/x) [Enter=1]: {Colors.ENDC}").strip().lower() or '1'
                
                if opcion == 'x':
                    print(f"{Colors.WARNING}Cancelado{Colors.ENDC}")
                    return None
                    
                elif opcion == '1':
                    return self.crear_nueva_categoria(nombre_categoria)
                    
                elif opcion == '2' or opcion == '9':
                    # Mostrar lista de categorías
                    categoria_seleccionada = self.seleccionar_categoria_con_ayuda()
                    if categoria_seleccionada:
                        return categoria_seleccionada
                    # Si no seleccionó ninguna, volver al menú
                    continue
                    
                elif opcion == '3':
                    # Editar campos del movimiento
                    if movimiento:
                        print(f"\n{Colors.HEADER}✏️  EDITAR CAMPOS DEL MOVIMIENTO{Colors.ENDC}")
                        movimiento_editado = self.editar_campos(movimiento)
                        if movimiento_editado:
                            # Actualizar el movimiento con los cambios
                            movimiento.update(movimiento_editado)
                            # Intentar obtener la nueva categoría
                            nueva_categoria = movimiento.get('categoria')
                            if nueva_categoria and nueva_categoria != nombre_categoria:
                                # Si cambió la categoría, intentar obtenerla
                                try:
                                    categoria = Categoria.objects.get(nombre=nueva_categoria)
                                    return categoria
                                except Categoria.DoesNotExist:
                                    # La nueva categoría tampoco existe, continuar el loop
                                    nombre_categoria = nueva_categoria
                                    continue
                            # Si no cambió la categoría, continuar
                            continue
                    else:
                        print(f"{Colors.WARNING}No hay contexto de movimiento para editar{Colors.ENDC}")
                        continue
                    
                else:
                    print(f"{Colors.FAIL}Opción no válida{Colors.ENDC}")
                    continue
    
    def seleccionar_categoria_con_ayuda(self):
        """Muestra lista de categorías con IDs para selección rápida"""
        try:
            print(f"\n{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
            print(f"{Colors.BOLD}📁 CATEGORÍAS DISPONIBLES{Colors.ENDC}")
            print(f"{Colors.OKCYAN}{'='*60}{Colors.ENDC}\n")
            
            from core.models import Categoria
            categorias = Categoria.objects.all().order_by('tipo', 'nombre')
            
            if not categorias.exists():
                print(f"{Colors.WARNING}No hay categorías registradas{Colors.ENDC}")
                nombre_nueva = input("Nombre de la nueva categoría: ").strip()
                if nombre_nueva:
                    return self.crear_nueva_categoria(nombre_nueva)
                return None
            
            # Crear diccionario ID -> categoría
            categorias_dict = {}
            
            # Separar por tipo
            personales = []
            negocio = []
            
            for cat in categorias:
                categorias_dict[cat.id] = cat
                if cat.tipo == 'personal':
                    personales.append(cat)
                else:
                    negocio.append(cat)
            
            # Mostrar categorías personales
            if personales:
                print(f"{Colors.OKGREEN}📊 CATEGORÍAS PERSONALES:{Colors.ENDC}")
                self._mostrar_categorias_en_columnas(personales)
            
            # Mostrar categorías de negocio
            if negocio:
                print(f"\n{Colors.OKBLUE}💼 CATEGORÍAS DE NEGOCIO:{Colors.ENDC}")
                self._mostrar_categorias_en_columnas(negocio)
            
            print(f"\n{Colors.OKGREEN}Total: {len(categorias)} categorías{Colors.ENDC}")
            print(f"{Colors.WARNING}[  0] → Crear nueva categoría{Colors.ENDC}")
            print(f"{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
            
            # Solicitar selección
            while True:
                print(f"\n{Colors.BOLD}OPCIONES:{Colors.ENDC}")
                print("• Escribe el NÚMERO de la categoría que eliges")
                print("• Escribe '0' para crear nueva categoría")
                print("• Escribe '9' para ver la lista otra vez")
                print("• Escribe 'x' para cancelar")
                
                seleccion = input(f"\n{Colors.OKCYAN}Tu elección: {Colors.ENDC}").strip().lower()
                
                if seleccion == 'x':
                    print(f"{Colors.WARNING}Cancelado{Colors.ENDC}")
                    return None
                    
                elif seleccion == '9':
                    # Mostrar lista otra vez
                    return self.seleccionar_categoria_con_ayuda()
                    
                elif seleccion == '0':
                    nombre_nueva = input("Nombre de la nueva categoría: ").strip()
                    if nombre_nueva:
                        return self.crear_nueva_categoria(nombre_nueva)
                    continue
                    
                elif seleccion.isdigit():
                    id_seleccionado = int(seleccion)
                    if id_seleccionado in categorias_dict:
                        categoria_seleccionada = categorias_dict[id_seleccionado]
                        print(f"{Colors.OKGREEN}✓ Seleccionaste: {categoria_seleccionada.nombre}{Colors.ENDC}")
                        return categoria_seleccionada
                    else:
                        print(f"{Colors.FAIL}ID no válido{Colors.ENDC}")
                        continue
                else:
                    print(f"{Colors.FAIL}Opción no válida{Colors.ENDC}")
                    continue
                    
        except Exception as e:
            print(f"{Colors.FAIL}Error al mostrar categorías: {e}{Colors.ENDC}")
            return None
    
    def _mostrar_categorias_en_columnas(self, categorias_list):
        """Helper para mostrar categorías en columnas"""
        num_categorias = len(categorias_list)
        columnas = 2  # Usar 2 columnas para categorías (nombres más largos)
        filas = (num_categorias + columnas - 1) // columnas
        
        for i in range(filas):
            fila = []
            for j in range(columnas):
                idx = i + j * filas
                if idx < num_categorias:
                    cat = categorias_list[idx]
                    # Formato: [ID] Nombre (truncado a 25 chars para categorías)
                    nombre_truncado = cat.nombre[:25]
                    fila.append(f"[{cat.id:3}] {nombre_truncado:<25}")
            print("  " + " | ".join(fila))
    
    def crear_nueva_categoria(self, nombre):
        """Crea una nueva categoría con asistente mejorado"""
        try:
            print(f"\n{Colors.OKCYAN}═══ Nueva Categoría: {nombre} ═══{Colors.ENDC}")
            
            # Determinar tipo basado en el nombre
            nombre_lower = nombre.lower()
            if any(word in nombre_lower for word in ['negocio', 'empresa', 'proyecto', 'cliente']):
                tipo_default = 'negocio'
            else:
                tipo_default = 'personal'
            
            print(f"\nTipo de categoría (default: {tipo_default.title()}):")
            print("1) Personal")
            print("2) Negocio")
            tipo_opcion = input("Seleccione (1/2) [Enter=default]: ").strip()
            
            if tipo_opcion == '2':
                tipo = 'negocio'
            elif tipo_opcion == '1':
                tipo = 'personal'
            else:
                tipo = tipo_default
            
            categoria = Categoria.objects.create(
                nombre=nombre,
                tipo=tipo
            )
            
            print(f"{Colors.OKGREEN}✓ Nueva categoría creada exitosamente!{Colors.ENDC}")
            print(f"  Nombre: {categoria.nombre}")
            print(f"  Tipo: {tipo.title()}")
            
            logger.info(f"Categoría creada: {nombre} - Tipo: {tipo}")
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
            cuenta_origen = self.verificar_crear_cuenta(cuenta_origen_nombre, movimiento)
        
        if cuenta_destino_nombre and cuenta_destino_nombre != '-':
            cuenta_destino = self.verificar_crear_cuenta(cuenta_destino_nombre, movimiento)
        
        # Obtener o crear categoría
        categoria_nombre = movimiento.get('categoria')
        categoria = None
        if categoria_nombre and categoria_nombre != 'SIN CLASIFICAR':
            categoria = self.verificar_crear_categoria(categoria_nombre, movimiento)
        
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
        """Muestra la vista previa del asiento contable con IDs de cuentas"""
        print(f"\n{Colors.OKCYAN}Vista previa contable:{Colors.ENDC}")
        
        tipo = transaccion_data['tipo']
        monto = abs(transaccion_data['monto'])  # Usar valor absoluto para mostrar
        cuenta_origen = transaccion_data['cuenta_origen']
        cuenta_destino = transaccion_data['cuenta_destino']
        
        # Helper para formatear cuenta con ID
        def formato_cuenta(cuenta, texto_default='Sin especificar'):
            if cuenta and hasattr(cuenta, 'nombre'):
                # Si la cuenta tiene ID, mostrarlo
                if hasattr(cuenta, 'id'):
                    return f"[{cuenta.id:3}] {cuenta.nombre}"
                return cuenta.nombre
            elif isinstance(cuenta, str):
                return cuenta
            else:
                return texto_default
        
        if tipo == TransaccionTipo.GASTO:
            # Gasto: Sale dinero de cuenta débito (ABONO) y se registra gasto (CARGO)
            cuenta_cargo = formato_cuenta(cuenta_destino, 'Gasto')
            cuenta_abono = formato_cuenta(cuenta_origen)
            print(f"  CARGO:  {cuenta_cargo:<35} ${monto:,.2f}")
            print(f"  ABONO:  {cuenta_abono:<35} ${monto:,.2f}")
        elif tipo == TransaccionTipo.INGRESO:
            # Ingreso: Entra dinero a cuenta débito (CARGO) y se registra ingreso (ABONO)
            cuenta_cargo = formato_cuenta(cuenta_origen)
            cuenta_abono = formato_cuenta(cuenta_destino, 'Ingreso')
            print(f"  CARGO:  {cuenta_cargo:<35} ${monto:,.2f}")
            print(f"  ABONO:  {cuenta_abono:<35} ${monto:,.2f}")
        else:  # TRANSFERENCIA
            # Determinar dirección de la transferencia basado en el monto
            # Monto negativo = sale dinero de cuenta_origen
            # Monto positivo = entra dinero a cuenta_origen
            monto_original = transaccion_data.get('monto', 0)
            
            if monto_original < 0:
                # Transferencia saliente: Sale de cuenta_origen (ABONO) y entra a cuenta_destino (CARGO)
                cuenta_cargo = formato_cuenta(cuenta_destino, formato_cuenta(cuenta_origen))
                cuenta_abono = formato_cuenta(cuenta_origen)
            else:
                # Transferencia entrante: Entra a cuenta_origen (CARGO) y sale de cuenta_destino (ABONO)
                cuenta_cargo = formato_cuenta(cuenta_origen)
                cuenta_abono = formato_cuenta(cuenta_destino, 'Origen externo')
            
            print(f"  CARGO:  {cuenta_cargo:<35} ${monto:,.2f}")
            print(f"  ABONO:  {cuenta_abono:<35} ${monto:,.2f}")
            
            # Nota informativa para transferencias entrantes
            if monto_original > 0:
                print(f"\n  {Colors.OKGREEN}📥 Transferencia ENTRANTE detectada (monto positivo){Colors.ENDC}")
            else:
                print(f"\n  {Colors.WARNING}📤 Transferencia SALIENTE detectada (monto negativo){Colors.ENDC}")
        
        # Agregar nota informativa si no hay cuenta especificada
        if not cuenta_destino or cuenta_destino == '-':
            print(f"\n  {Colors.WARNING}💡 Tip: Presiona '2' para seleccionar cuenta vinculada con opción 9 para ver lista{Colors.ENDC}")
    
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
        print("4) 🚪 Salir del importador")
        
        while True:
            opcion = input(f"\n{Colors.OKCYAN}Seleccione opción (1/2/3/4): {Colors.ENDC}").strip()
            
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
                # Corrección con sistema de ayuda mejorado
                print(f"\n{Colors.WARNING}Corregir clasificación:{Colors.ENDC}")
                
                # PASO 1: Seleccionar tipo correcto
                print(f"\n{Colors.OKCYAN}1️⃣ TIPO DE TRANSACCIÓN{Colors.ENDC}")
                print("1) 💸 GASTO")
                print("2) 💰 INGRESO") 
                print("3) 🔄 TRANSFERENCIA")
                
                tipo_actual = decision_ia.get('tipo', 'GASTO')
                tipo_opcion = input(f"{Colors.OKCYAN}Seleccione tipo (1/2/3) [Enter={tipo_actual}]: {Colors.ENDC}").strip()
                
                if not tipo_opcion:
                    tipo_correcto = tipo_actual
                else:
                    tipo_map = {'1': 'GASTO', '2': 'INGRESO', '3': 'TRANSFERENCIA'}
                    tipo_correcto = tipo_map.get(tipo_opcion, tipo_actual)
                
                # PASO 2: Seleccionar categoría con sistema de ayuda
                print(f"\n{Colors.OKCYAN}2️⃣ CATEGORÍA (nombre/número/9=ayuda):{Colors.ENDC}")
                categoria_actual = decision_ia.get('categoria') or movimiento.get('categoria', 'SIN CLASIFICAR')
                print(f"Categoría actual: {categoria_actual}")
                
                categoria_input = input(f"{Colors.OKCYAN}Nueva categoría [Enter=mantener, 9=ver lista]: {Colors.ENDC}").strip()
                
                if not categoria_input:
                    categoria_correcta = categoria_actual
                elif categoria_input == '9' or (categoria_input.isdigit() and categoria_input != '0'):
                    # Usar el sistema de ayuda existente
                    categoria_seleccionada = self.seleccionar_categoria_con_ayuda()
                    if categoria_seleccionada:
                        categoria_correcta = categoria_seleccionada.nombre
                    else:
                        categoria_correcta = categoria_actual
                else:
                    # Texto directo ingresado
                    categoria_correcta = categoria_input
                    # Verificar si necesita crear la categoría
                    self.verificar_crear_categoria(categoria_correcta)
                
                # PASO 3: Si es TRANSFERENCIA, seleccionar cuenta vinculada
                cuenta_vinculada = None
                if tipo_correcto == 'TRANSFERENCIA':
                    print(f"\n{Colors.OKCYAN}3️⃣ CUENTA VINCULADA (para transferencia):{Colors.ENDC}")
                    print("Como es una transferencia, necesitamos la cuenta destino.")
                    
                    cuenta_input = input(f"{Colors.OKCYAN}Cuenta (nombre/número/9=ayuda): {Colors.ENDC}").strip()
                    
                    if cuenta_input == '9' or (cuenta_input.isdigit() and cuenta_input != '0'):
                        # Usar el sistema de ayuda de cuentas
                        cuenta_seleccionada = self.seleccionar_cuenta_con_ayuda()
                        if cuenta_seleccionada:
                            cuenta_vinculada = cuenta_seleccionada
                    elif cuenta_input:
                        cuenta_vinculada = cuenta_input
                        # Verificar si necesita crear la cuenta
                        self.verificar_crear_cuenta(cuenta_vinculada)
                
                print(f"\n{Colors.OKGREEN}✓ Corrección registrada:{Colors.ENDC}")
                print(f"  Tipo: {tipo_correcto}")
                print(f"  Categoría: {categoria_correcta}")
                if cuenta_vinculada:
                    print(f"  Cuenta vinculada: {cuenta_vinculada}")
                
                return {
                    'accion': 'correccion',
                    'clasificacion_original': {
                        'tipo': decision_ia.get('tipo'),
                        'categoria': decision_ia.get('categoria'),
                        'cuenta_vinculada': decision_ia.get('cuenta_vinculada')
                    },
                    'clasificacion_correcta': {
                        'tipo': tipo_correcto,
                        'categoria': categoria_correcta,
                        'cuenta_vinculada': cuenta_vinculada
                    },
                    'nota': f"Corregido por usuario"
                }
                
            elif opcion == '3':
                # Omitir
                print(f"{Colors.WARNING}⏭️  Clasificación IA omitida{Colors.ENDC}")
                return None
                
            elif opcion == '4':
                # Salir del importador
                print(f"\n{Colors.WARNING}¿Seguro que deseas salir?{Colors.ENDC}")
                print("Los movimientos ya procesados se mantienen guardados.")
                print("Podrás continuar después desde donde quedaste.")
                confirmar_salir = input(f"\n1=Sí salir, 2=No, continuar [Enter=2]: ").strip() or '2'
                if confirmar_salir == '1':
                    return 'exit'
                else:
                    print(f"{Colors.OKCYAN}Continuando con la importación...{Colors.ENDC}")
                    # Volver a mostrar las opciones
                    print(f"\n{Colors.WARNING}¿La clasificación de la IA es correcta?{Colors.ENDC}")
                    print("1) ✅ Sí, es correcta")
                    print("2) ❌ No, necesita corrección")
                    print("3) ⏭️  Omitir (usar clasificación manual)")
                    print("4) 🚪 Salir del importador")
                    continue
                    
            else:
                print(f"{Colors.FAIL}Opción inválida. Por favor selecciona 1, 2, 3 o 4{Colors.ENDC}")
    
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
                    # Obtener todos los campos posibles de todos los registros
                    all_fields = set()
                    for log_entry in self.log_operaciones:
                        all_fields.update(log_entry.keys())
                    
                    # Ordenar campos para consistencia
                    fieldnames = sorted(list(all_fields))
                    
                    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
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
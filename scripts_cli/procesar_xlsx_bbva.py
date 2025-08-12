#!/usr/bin/env python3
"""
Procesador XLSX a JSON enriquecido con IA DeepSeek
Versión 0.8.3 - Paso 0: Preprocesamiento inteligente
"""
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

# Agregar el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

# Imports locales
from deepseek_client import DeepSeekClient, Colors
from core.models import Cuenta

class ProcesadorXLSXBBVA:
    """Procesador principal para convertir XLSX a JSON enriquecido con IA"""
    
    def __init__(self, test_mode: bool = False, lote_size: int = 50):
        self.test_mode = test_mode
        self.lote_size = lote_size
        self.deepseek_client = DeepSeekClient(test_mode=test_mode)
        self.cuentas_conocidas = []
        self.movimientos_procesados = []
        self.estadisticas = {
            'archivo_origen': '',
            'total_movimientos_excel': 0,
            'movimientos_procesados': 0,
            'movimientos_fallidos': 0,
            'tiempo_total': 0,
            'lotes_procesados': 0
        }
    
    def inicializar(self) -> bool:
        """Inicializa el procesador y verifica dependencias"""
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}PROCESADOR XLSX → JSON CON IA DEEPSEEK v0.8.3{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
        
        if self.test_mode:
            print(f"{Colors.WARNING}⚠️  MODO TEST ACTIVADO - Simulará respuestas IA{Colors.ENDC}")
        
        # Verificar conectividad DeepSeek
        if not self.deepseek_client.verificar_conectividad():
            return False
        
        # Cargar contexto de cuentas existentes
        self._cargar_contexto_cuentas()
        
        return True
    
    def _cargar_contexto_cuentas(self):
        """Carga el contexto de cuentas existentes en el sistema"""
        try:
            # El campo 'activa' no existe, usar todas las cuentas
            self.cuentas_conocidas = list(
                Cuenta.objects.all()
                .values_list('nombre', flat=True)
                .order_by('nombre')
            )
            
            # Establecer contexto en el cliente DeepSeek
            self.deepseek_client.establecer_contexto_cuentas(self.cuentas_conocidas)
            
        except Exception as e:
            print(f"{Colors.WARNING}⚠️  Error cargando contexto de cuentas: {e}{Colors.ENDC}")
            self.cuentas_conocidas = []
    
    def extraer_movimientos_xlsx(self, archivo_path: str) -> List[Dict[str, Any]]:
        """Extrae movimientos del archivo XLSX usando estructura conocida de BBVA"""
        print(f"{Colors.OKBLUE}📂 Extrayendo movimientos de: {os.path.basename(archivo_path)}{Colors.ENDC}")
        
        try:
            # Leer Excel sin header para detectar estructura
            df_raw = pd.read_excel(archivo_path, header=None)
            
            # Buscar fila de encabezados (contiene "FECHA")
            header_row = None
            for i in range(10):  # Buscar en primeras 10 filas
                fila = df_raw.iloc[i]
                if any('FECHA' in str(val).upper() for val in fila if pd.notna(val)):
                    header_row = i
                    break
            
            if header_row is None:
                raise ValueError("No se encontró la fila de encabezados con FECHA")
            
            # Leer desde la fila de encabezados
            df = pd.read_excel(archivo_path, header=header_row)
            
            print(f"{Colors.OKCYAN}Encabezados detectados: {list(df.columns)}{Colors.ENDC}")
            
            movimientos = []
            
            for idx, row in df.iterrows():
                try:
                    # Extraer campos del formato BBVA
                    fecha_raw = row.get('FECHA', row.iloc[0] if len(row) > 0 else None)
                    descripcion_raw = row.get('DESCRIPCIÓN', row.get('DESCRIPCION', 
                                             row.iloc[1] if len(row) > 1 else ''))
                    cargo = row.get('CARGO', row.iloc[2] if len(row) > 2 else None)
                    abono = row.get('ABONO', row.iloc[3] if len(row) > 3 else None)
                    
                    # Normalizar fecha
                    fecha = self._normalizar_fecha(fecha_raw)
                    if not fecha:
                        continue
                    
                    # Procesar descripción
                    descripcion = str(descripcion_raw).strip() if pd.notna(descripcion_raw) else ''
                    if not descripcion or descripcion == 'nan':
                        continue
                    
                    # Procesar monto (cargo es negativo, abono es positivo)
                    monto = 0.0
                    if pd.notna(cargo) and cargo != '':
                        monto = -abs(self._normalizar_monto(cargo))
                    elif pd.notna(abono) and abono != '':
                        monto = abs(self._normalizar_monto(abono))
                    
                    if monto == 0:
                        continue
                    
                    # Extraer referencia de la descripción (formato BBVA)
                    referencia = self._extraer_referencia_bbva(descripcion)
                    
                    movimiento = {
                        'numero': len(movimientos) + 1,
                        'fecha': fecha.strftime('%Y-%m-%d'),
                        'descripcion': descripcion[:200],  # Limitar longitud
                        'monto': monto,
                        'referencia_bancaria': referencia[:50],
                        'archivo_origen': os.path.basename(archivo_path)
                    }
                    
                    movimientos.append(movimiento)
                    
                except Exception as e:
                    print(f"{Colors.WARNING}⚠️  Fila {idx+header_row+1} omitida: {e}{Colors.ENDC}")
                    continue
            
            self.estadisticas['total_movimientos_excel'] = len(movimientos)
            print(f"{Colors.OKGREEN}✓ Extraídos {len(movimientos)} movimientos válidos{Colors.ENDC}")
            
            return movimientos
            
        except Exception as e:
            print(f"{Colors.FAIL}✗ Error extrayendo XLSX: {e}{Colors.ENDC}")
            return []
    
    def _detectar_columnas_bbva(self, df: pd.DataFrame) -> Dict[str, str]:
        """Detecta automáticamente las columnas del formato BBVA"""
        columnas = df.columns.tolist()
        mapeo = {}
        
        # Patrones para detectar columnas
        patrones = {
            'fecha': ['fecha', 'date', 'fecha valor', 'fecha operacion'],
            'descripcion': ['descripcion', 'concepto', 'description', 'detalle'],
            'monto': ['monto', 'importe', 'amount', 'valor'],
            'referencia': ['referencia', 'reference', 'ref', 'folio']
        }
        
        for campo, posibles_nombres in patrones.items():
            for columna in columnas:
                if any(patron.lower() in columna.lower() for patron in posibles_nombres):
                    mapeo[campo] = columna
                    break
        
        # Verificar que tenemos los campos mínimos
        if 'fecha' not in mapeo or 'descripcion' not in mapeo or 'monto' not in mapeo:
            print(f"{Colors.FAIL}Columnas detectadas: {list(columnas)}{Colors.ENDC}")
            return {}
        
        print(f"{Colors.OKCYAN}Mapeo de columnas: {mapeo}{Colors.ENDC}")
        return mapeo
    
    def _normalizar_fecha(self, fecha_valor) -> Optional[datetime]:
        """Normaliza diferentes formatos de fecha"""
        if pd.isna(fecha_valor):
            return None
        
        # Si ya es datetime
        if isinstance(fecha_valor, datetime):
            return fecha_valor
        
        # Intentar parsear diferentes formatos
        formatos = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']
        fecha_str = str(fecha_valor).strip()
        
        for formato in formatos:
            try:
                return datetime.strptime(fecha_str, formato)
            except ValueError:
                continue
        
        return None
    
    def _normalizar_monto(self, monto_valor) -> float:
        """Normaliza diferentes formatos de monto"""
        if pd.isna(monto_valor):
            return 0.0
        
        try:
            # Convertir a string y limpiar
            monto_str = str(monto_valor).replace('$', '').replace(',', '').strip()
            return float(monto_str)
        except (ValueError, TypeError):
            return 0.0
    
    def _extraer_referencia_bbva(self, descripcion: str) -> str:
        """Extrae la referencia bancaria de la descripción BBVA"""
        import re
        
        # Patrones comunes en descripciones BBVA
        patrones = [
            r'/ (\d{10})',  # / 0076312440
            r'/(\d{10})',   # /0076312440  
            r'(\d{10})',    # Solo números de 10 dígitos
            r'(\*{6}\d{4})', # ******0287
        ]
        
        for patron in patrones:
            match = re.search(patron, descripcion)
            if match:
                return match.group(1)
        
        return ''
    
    def dividir_en_lotes(self, movimientos: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Divide los movimientos en lotes para procesamiento"""
        lotes = []
        for i in range(0, len(movimientos), self.lote_size):
            lote = movimientos[i:i + self.lote_size]
            lotes.append(lote)
        
        print(f"{Colors.OKCYAN}📦 Dividido en {len(lotes)} lotes de máximo {self.lote_size} movimientos{Colors.ENDC}")
        return lotes
    
    def procesar_lotes(self, lotes: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Procesa todos los lotes con DeepSeek"""
        todos_procesados = []
        inicio_total = datetime.now()
        
        for i, lote in enumerate(lotes, 1):
            print(f"\n{Colors.HEADER}{'='*50}{Colors.ENDC}")
            print(f"{Colors.BOLD}LOTE {i}/{len(lotes)} - {len(lote)} movimientos{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}")
            
            inicio_lote = datetime.now()
            
            # Procesar lote con IA
            lote_procesado = self.deepseek_client.procesar_lote_movimientos(lote)
            
            tiempo_lote = (datetime.now() - inicio_lote).total_seconds()
            
            # Agregar a resultados totales
            todos_procesados.extend(lote_procesado)
            
            # Estadísticas del lote
            exitosos = len(lote_procesado)
            fallidos = len(lote) - exitosos
            
            print(f"\n{Colors.OKGREEN}✓ Lote {i} completado en {tiempo_lote:.1f}s{Colors.ENDC}")
            print(f"  Exitosos: {exitosos}, Fallidos: {fallidos}")
            
            self.estadisticas['lotes_procesados'] += 1
        
        # Estadísticas finales
        tiempo_total = (datetime.now() - inicio_total).total_seconds()
        self.estadisticas['tiempo_total'] = tiempo_total
        self.estadisticas['movimientos_procesados'] = len(todos_procesados)
        self.estadisticas['movimientos_fallidos'] = (
            self.estadisticas['total_movimientos_excel'] - len(todos_procesados)
        )
        
        return todos_procesados
    
    def generar_json_final(self, movimientos_procesados: List[Dict[str, Any]], 
                          archivo_origen: str) -> Dict[str, Any]:
        """Genera la estructura JSON final compatible con importar_movimientos_bbva.py"""
        
        timestamp = datetime.now()
        lote_id = f"BBVA_IA_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # Obtener estadísticas de DeepSeek
        stats_deepseek = self.deepseek_client.obtener_estadisticas()
        
        json_final = {
            "metadata": {
                "lote_id": lote_id,
                "fecha_procesamiento": timestamp.isoformat(),
                "archivo_origen": archivo_origen,
                "total_movimientos": len(movimientos_procesados),
                "modo_test": self.test_mode,
                "estadisticas_ia": {
                    **stats_deepseek,
                    "lotes_procesados": self.estadisticas['lotes_procesados'],
                    "tiempo_total_segundos": self.estadisticas['tiempo_total']
                },
                "version_procesador": "0.8.3"
            },
            "movimientos": []
        }
        
        # Procesar cada movimiento para formato final
        for mov in movimientos_procesados:
            decision_ia = mov.get('decision_ia', {})
            
            movimiento_final = {
                # Campos compatibles con importar_movimientos_bbva.py
                "numero": mov.get('numero', 0),
                "fecha": mov.get('fecha', '2025-01-01'),
                "descripcion": mov.get('descripcion', ''),
                "monto": mov.get('monto', 0),
                "tipo": decision_ia.get('tipo', 'GASTO'),
                "cuenta_origen": "TDB BBVA 5019",  # Cuenta fija de origen
                "cuenta_destino": decision_ia.get('cuenta_vinculada'),
                "categoria": decision_ia.get('categoria', 'Sin Clasificar'),
                "referencia_bancaria": mov.get('referencia_bancaria', ''),
                "archivo_origen": mov.get('archivo_origen', archivo_origen),
                
                # Enriquecimiento IA
                "decision_ia": {
                    "confianza": decision_ia.get('confianza', 0.5),
                    "nota": decision_ia.get('nota_ia', ''),
                    "reglas_aplicadas": decision_ia.get('reglas_aplicadas', []),
                    "procesado_con_ia": not self.test_mode
                }
            }
            
            json_final["movimientos"].append(movimiento_final)
        
        return json_final
    
    def guardar_json(self, json_data: Dict[str, Any], output_dir: str) -> str:
        """Guarda el JSON final en el directorio especificado"""
        
        # Crear directorio de salida si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Generar nombre de archivo único
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"bbva_{timestamp}_ia.json"
        ruta_archivo = os.path.join(output_dir, nombre_archivo)
        
        # Guardar JSON
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n{Colors.OKGREEN}💾 JSON guardado: {ruta_archivo}{Colors.ENDC}")
        return ruta_archivo
    
    def mostrar_reporte_final(self, json_data: Dict[str, Any]):
        """Muestra el reporte final del procesamiento"""
        print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}REPORTE FINAL - PROCESAMIENTO IA{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
        
        metadata = json_data['metadata']
        stats_ia = metadata['estadisticas_ia']
        
        print(f"📁 Archivo origen: {metadata['archivo_origen']}")
        print(f"🔢 Total movimientos: {metadata['total_movimientos']}")
        print(f"⏱️  Tiempo total: {stats_ia['tiempo_total_segundos']:.1f}s")
        print(f"📊 Confianza promedio IA: {stats_ia['confianza_promedio']:.2f}")
        print(f"✅ Exitosos: {stats_ia['movimientos_procesados']}")
        print(f"❌ Fallidos: {stats_ia['movimientos_fallidos']}")
        
        # Análisis por tipo
        tipos = {}
        categorias = {}
        
        for mov in json_data['movimientos']:
            tipo = mov.get('tipo', 'DESCONOCIDO')
            categoria = mov.get('categoria', 'Sin categoría')
            
            tipos[tipo] = tipos.get(tipo, 0) + 1
            categorias[categoria] = categorias.get(categoria, 0) + 1
        
        print(f"\n📋 Distribución por tipo:")
        for tipo, count in sorted(tipos.items()):
            print(f"  {tipo}: {count} movimientos")
        
        print(f"\n🏷️  Top 5 categorías:")
        for categoria, count in sorted(categorias.items(), 
                                      key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {categoria}: {count} movimientos")
        
        if self.test_mode:
            print(f"\n{Colors.WARNING}⚠️  MODO TEST - Simulaciones de IA utilizadas{Colors.ENDC}")
        
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    
    def procesar_archivo(self, archivo_xlsx: str, output_dir: str) -> Optional[str]:
        """Función principal para procesar un archivo XLSX completo"""
        
        if not self.inicializar():
            return None
        
        # Paso 1: Extraer movimientos del XLSX
        movimientos_raw = self.extraer_movimientos_xlsx(archivo_xlsx)
        if not movimientos_raw:
            print(f"{Colors.FAIL}✗ No se pudieron extraer movimientos{Colors.ENDC}")
            return None
        
        # Paso 2: Dividir en lotes
        lotes = self.dividir_en_lotes(movimientos_raw)
        
        # Paso 3: Procesar con IA
        movimientos_procesados = self.procesar_lotes(lotes)
        
        # Paso 4: Generar JSON final
        json_final = self.generar_json_final(
            movimientos_procesados, 
            os.path.basename(archivo_xlsx)
        )
        
        # Paso 5: Guardar resultado
        if not self.test_mode:
            ruta_json = self.guardar_json(json_final, output_dir)
        else:
            ruta_json = "TEST_MODE"
        
        # Paso 6: Generar reporte de evaluación IA
        self.deepseek_client.generar_reporte_evaluacion(movimientos_procesados)
        
        # Paso 7: Mostrar reporte final
        self.mostrar_reporte_final(json_final)
        
        return ruta_json


def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(
        description='Procesador XLSX a JSON enriquecido con IA DeepSeek'
    )
    parser.add_argument(
        '--archivo', 
        required=True,
        help='Ruta al archivo XLSX de movimientos BBVA'
    )
    parser.add_argument(
        '--output', 
        default='scripts_cli/output',
        help='Directorio de salida para JSON (default: scripts_cli/output)'
    )
    parser.add_argument(
        '--lote-size', 
        type=int, 
        default=50,
        help='Tamaño de lote para procesamiento IA (default: 50)'
    )
    parser.add_argument(
        '--test', 
        action='store_true',
        help='Modo test (simula respuestas IA sin usar API real)'
    )
    
    args = parser.parse_args()
    
    # Validar archivo de entrada
    if not os.path.exists(args.archivo):
        print(f"{Colors.FAIL}✗ Archivo no encontrado: {args.archivo}{Colors.ENDC}")
        return 1
    
    # Crear procesador
    procesador = ProcesadorXLSXBBVA(
        test_mode=args.test,
        lote_size=args.lote_size
    )
    
    # Procesar archivo
    try:
        resultado = procesador.procesar_archivo(args.archivo, args.output)
        
        if resultado:
            print(f"\n{Colors.OKGREEN}🎉 Procesamiento completado exitosamente{Colors.ENDC}")
            
            if not args.test:
                print(f"\n{Colors.OKCYAN}Siguiente paso:{Colors.ENDC}")
                print(f"python scripts_cli/importar_movimientos_bbva.py")
                print(f"  (usar archivo: {resultado})")
            
            return 0
        else:
            print(f"\n{Colors.FAIL}✗ Procesamiento falló{Colors.ENDC}")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  Proceso interrumpido por usuario{Colors.ENDC}")
        return 1
        
    except Exception as e:
        print(f"\n{Colors.FAIL}✗ Error crítico: {e}{Colors.ENDC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
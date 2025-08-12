#!/usr/bin/env python3
"""
Sistema de Memoria Permanente para DeepSeek v2
Aprendizaje automático continuo de patrones financieros
"""
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoriaPatrones:
    """Gestor principal de la memoria permanente del sistema"""
    
    def __init__(self):
        self.memoria_dir = Path(__file__).parent / 'memoria'
        self.memoria_dir.mkdir(exist_ok=True)
        
        self.archivo_memoria = self.memoria_dir / 'memoria_permanente.json'
        self.archivo_backup = self.memoria_dir / f'backup_{datetime.now().strftime("%Y%m%d")}.json'
        
        self.memoria = self._inicializar_memoria()
        self.sesion_actual = {
            'patrones_nuevos': 0,
            'patrones_actualizados': 0,
            'transacciones_procesadas': 0
        }
    
    def _inicializar_memoria(self) -> Dict:
        """Inicializa o carga la memoria existente"""
        if self.archivo_memoria.exists():
            try:
                with open(self.archivo_memoria, 'r', encoding='utf-8') as f:
                    memoria = json.load(f)
                    print(f"📚 Memoria cargada: {memoria['total_transacciones_aprendidas']} transacciones aprendidas")
                    return memoria
            except Exception as e:
                logger.error(f"Error cargando memoria: {e}")
                return self._crear_memoria_nueva()
        else:
            return self._crear_memoria_nueva()
    
    def _crear_memoria_nueva(self) -> Dict:
        """Crea una estructura de memoria nueva"""
        memoria = {
            "version": "2.0",
            "fecha_creacion": datetime.now().isoformat(),
            "ultima_actualizacion": datetime.now().isoformat(),
            "total_transacciones_aprendidas": 0,
            "total_patrones_detectados": 0,
            "patrones_detectados": {
                "referencias_bancarias": {},
                "montos_exactos": {},
                "rangos_monto": {},
                "patrones_temporales": {},
                "descripciones_frecuentes": {},
                "combinaciones": {}  # Combinaciones de múltiples factores
            },
            "estadisticas": {
                "precision_actual": 0.0,
                "patrones_mas_usados": [],
                "ultimos_aprendizajes": []
            }
        }
        print("🆕 Memoria nueva creada")
        return memoria
    
    def buscar_patrones_existentes(self, movimiento: Dict) -> List[Dict]:
        """Busca todos los patrones que coincidan con el movimiento"""
        coincidencias = []
        confianza_maxima = 0.0
        
        # 1. Buscar por referencia bancaria exacta
        ref = movimiento.get('referencia_bancaria', '').strip()
        if ref and ref in self.memoria['patrones_detectados']['referencias_bancarias']:
            patron = self.memoria['patrones_detectados']['referencias_bancarias'][ref].copy()
            patron['tipo_patron'] = 'referencia_bancaria'
            patron['match_exacto'] = True
            coincidencias.append(patron)
            confianza_maxima = max(confianza_maxima, patron.get('confianza', 0))
        
        # 2. Buscar por monto exacto
        monto = abs(float(movimiento.get('monto', 0)))
        monto_str = f"{monto:.2f}"
        if monto_str in self.memoria['patrones_detectados']['montos_exactos']:
            patron = self.memoria['patrones_detectados']['montos_exactos'][monto_str].copy()
            patron['tipo_patron'] = 'monto_exacto'
            
            # Verificar si la descripción también coincide
            descripcion = movimiento.get('descripcion', '').upper()
            patron_desc = patron.get('descripcion_patron', '').upper()
            if patron_desc and patron_desc in descripcion:
                patron['match_descripcion'] = True
                patron['confianza'] = min(1.0, patron.get('confianza', 0.8) + 0.1)
            
            coincidencias.append(patron)
            confianza_maxima = max(confianza_maxima, patron.get('confianza', 0))
        
        # 3. Buscar por rangos de monto
        for rango_id, rango_patron in self.memoria['patrones_detectados']['rangos_monto'].items():
            min_monto = rango_patron.get('min_monto', 0)
            max_monto = rango_patron.get('max_monto', float('inf'))
            
            if min_monto <= monto <= max_monto:
                # Verificar si la descripción coincide
                patron_desc = rango_patron.get('descripcion_patron', '')
                if self._coincide_descripcion(movimiento.get('descripcion', ''), patron_desc):
                    patron = rango_patron.copy()
                    patron['tipo_patron'] = 'rango_monto'
                    patron['rango_id'] = rango_id
                    coincidencias.append(patron)
                    confianza_maxima = max(confianza_maxima, patron.get('confianza', 0))
        
        # 4. Buscar por patrones de descripción
        descripcion = movimiento.get('descripcion', '').upper()
        for desc_id, desc_patron in self.memoria['patrones_detectados']['descripciones_frecuentes'].items():
            keywords = desc_patron.get('keywords', [])
            if all(kw.upper() in descripcion for kw in keywords):
                patron = desc_patron.copy()
                patron['tipo_patron'] = 'descripcion'
                patron['descripcion_id'] = desc_id
                coincidencias.append(patron)
                confianza_maxima = max(confianza_maxima, patron.get('confianza', 0))
        
        # 5. Buscar patrones temporales (si tenemos fecha)
        fecha_mov = movimiento.get('fecha')
        if fecha_mov:
            for temporal_id, temporal_patron in self.memoria['patrones_detectados']['patrones_temporales'].items():
                if self._coincide_patron_temporal(movimiento, temporal_patron):
                    patron = temporal_patron.copy()
                    patron['tipo_patron'] = 'temporal'
                    patron['temporal_id'] = temporal_id
                    coincidencias.append(patron)
                    confianza_maxima = max(confianza_maxima, patron.get('confianza', 0))
        
        # Ordenar por confianza descendente
        coincidencias.sort(key=lambda x: x.get('confianza', 0), reverse=True)
        
        return coincidencias
    
    def _coincide_descripcion(self, descripcion: str, patron: str) -> bool:
        """Verifica si una descripción coincide con un patrón"""
        if not patron:
            return False
        
        descripcion = descripcion.upper()
        patron = patron.upper()
        
        # Si el patrón contiene .* es una regex
        if '.*' in patron or '\\' in patron:
            try:
                return bool(re.search(patron, descripcion))
            except:
                return False
        
        # Si no, buscar coincidencia parcial
        keywords = patron.split()
        return all(kw in descripcion for kw in keywords)
    
    def _coincide_patron_temporal(self, movimiento: Dict, patron_temporal: Dict) -> bool:
        """Verifica si un movimiento coincide con un patrón temporal"""
        try:
            fecha_mov = datetime.strptime(movimiento.get('fecha', ''), '%Y-%m-%d')
            ultima_aparicion = datetime.strptime(patron_temporal.get('ultima_aparicion', ''), '%Y-%m-%d')
            periodicidad = patron_temporal.get('periodicidad_dias', 0)
            tolerancia = patron_temporal.get('tolerancia_dias', 3)
            
            # Calcular diferencia de días
            dias_diferencia = (fecha_mov - ultima_aparicion).days
            
            # Verificar si coincide con la periodicidad (con tolerancia)
            if periodicidad > 0:
                ciclos = dias_diferencia / periodicidad
                if abs(ciclos - round(ciclos)) * periodicidad <= tolerancia:
                    # También verificar descripción
                    return self._coincide_descripcion(
                        movimiento.get('descripcion', ''),
                        patron_temporal.get('descripcion_patron', '')
                    )
            
            return False
            
        except:
            return False
    
    def registrar_patron_nuevo(self, patron_definicion: Dict, movimiento_inicial: Dict) -> bool:
        """Registra un patrón nuevo en la memoria permanente"""
        try:
            tipo_patron = patron_definicion.get('tipo', 'desconocido')
            
            # Generar ID único para el patrón
            patron_id = self._generar_id_patron(tipo_patron, movimiento_inicial)
            
            # Estructura base del patrón
            patron_base = {
                'id': patron_id,
                'frecuencia': 1,
                'primera_deteccion': datetime.now().isoformat(),
                'ultima_aparicion': datetime.now().isoformat(),
                'clasificacion': patron_definicion.get('clasificacion_automatica', {}),
                'confianza': patron_definicion.get('confianza_patron', 0.5),
                'ejemplos': [self._crear_ejemplo(movimiento_inicial)]
            }
            
            # Agregar según el tipo de patrón
            if tipo_patron == 'referencia':
                ref = movimiento_inicial.get('referencia_bancaria', '')
                if ref:
                    patron_base.update({
                        'descripcion_comun': movimiento_inicial.get('descripcion', ''),
                        'montos_observados': [float(movimiento_inicial.get('monto', 0))]
                    })
                    self.memoria['patrones_detectados']['referencias_bancarias'][ref] = patron_base
                    
            elif tipo_patron == 'monto_exacto':
                monto = abs(float(movimiento_inicial.get('monto', 0)))
                monto_str = f"{monto:.2f}"
                patron_base.update({
                    'descripcion_patron': patron_definicion.get('reglas_deteccion', {}).get('keywords_obligatorias', []),
                    'referencias_observadas': [movimiento_inicial.get('referencia_bancaria', '')]
                })
                self.memoria['patrones_detectados']['montos_exactos'][monto_str] = patron_base
                
            elif tipo_patron == 'rango_monto':
                rango_id = patron_id
                patron_base.update({
                    'min_monto': patron_definicion.get('reglas_deteccion', {}).get('monto_rango', {}).get('min', 0),
                    'max_monto': patron_definicion.get('reglas_deteccion', {}).get('monto_rango', {}).get('max', 0),
                    'descripcion_patron': patron_definicion.get('reglas_deteccion', {}).get('keywords_obligatorias', [])
                })
                self.memoria['patrones_detectados']['rangos_monto'][rango_id] = patron_base
                
            elif tipo_patron == 'descripcion':
                desc_id = patron_id
                patron_base.update({
                    'keywords': patron_definicion.get('reglas_deteccion', {}).get('keywords_obligatorias', []),
                    'keywords_opcionales': patron_definicion.get('reglas_deteccion', {}).get('keywords_opcionales', []),
                    'montos_observados': [float(movimiento_inicial.get('monto', 0))]
                })
                self.memoria['patrones_detectados']['descripciones_frecuentes'][desc_id] = patron_base
                
            elif tipo_patron == 'temporal':
                temporal_id = patron_id
                patron_base.update({
                    'descripcion_patron': patron_definicion.get('reglas_deteccion', {}).get('keywords_obligatorias', []),
                    'periodicidad_dias': patron_definicion.get('reglas_deteccion', {}).get('periodicidad_dias', 0),
                    'tolerancia_dias': 3,
                    'proxima_esperada': self._calcular_proxima_fecha(
                        datetime.now(),
                        patron_definicion.get('reglas_deteccion', {}).get('periodicidad_dias', 30)
                    )
                })
                self.memoria['patrones_detectados']['patrones_temporales'][temporal_id] = patron_base
            
            # Actualizar estadísticas
            self.memoria['total_patrones_detectados'] += 1
            self.memoria['ultima_actualizacion'] = datetime.now().isoformat()
            self.sesion_actual['patrones_nuevos'] += 1
            
            # Guardar inmediatamente
            self.guardar_memoria()
            
            print(f"✅ Nuevo patrón registrado: {patron_id} (tipo: {tipo_patron})")
            logger.info(f"Patrón nuevo registrado: {patron_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error registrando patrón: {e}")
            return False
    
    def actualizar_frecuencia_patron(self, tipo_patron: str, patron_id: str, movimiento: Dict) -> bool:
        """Actualiza la frecuencia y confianza de un patrón existente"""
        try:
            patron = None
            
            # Buscar el patrón según su tipo
            if tipo_patron == 'referencia_bancaria':
                patron = self.memoria['patrones_detectados']['referencias_bancarias'].get(patron_id)
            elif tipo_patron == 'monto_exacto':
                patron = self.memoria['patrones_detectados']['montos_exactos'].get(patron_id)
            elif tipo_patron == 'rango_monto':
                patron = self.memoria['patrones_detectados']['rangos_monto'].get(patron_id)
            elif tipo_patron == 'descripcion':
                patron = self.memoria['patrones_detectados']['descripciones_frecuentes'].get(patron_id)
            elif tipo_patron == 'temporal':
                patron = self.memoria['patrones_detectados']['patrones_temporales'].get(patron_id)
            
            if patron:
                # Actualizar frecuencia
                patron['frecuencia'] = patron.get('frecuencia', 0) + 1
                patron['ultima_aparicion'] = datetime.now().isoformat()
                
                # Aumentar confianza (máximo 0.99)
                nueva_confianza = min(0.99, patron.get('confianza', 0.5) + 0.02)
                patron['confianza'] = round(nueva_confianza, 2)
                
                # Inicializar feedback_humano si no existe
                if 'feedback_humano' not in patron:
                    patron['feedback_humano'] = []
                if 'validado_humano' not in patron:
                    patron['validado_humano'] = False
                
                # Agregar ejemplo si no hay muchos
                if len(patron.get('ejemplos', [])) < 10:
                    patron.setdefault('ejemplos', []).append(self._crear_ejemplo(movimiento))
                
                # Para patrones temporales, actualizar próxima esperada
                if tipo_patron == 'temporal' and 'periodicidad_dias' in patron:
                    patron['proxima_esperada'] = self._calcular_proxima_fecha(
                        datetime.now(),
                        patron['periodicidad_dias']
                    )
                
                # Actualizar estadísticas globales
                self.memoria['total_transacciones_aprendidas'] += 1
                self.memoria['ultima_actualizacion'] = datetime.now().isoformat()
                self.sesion_actual['patrones_actualizados'] += 1
                
                # Guardar cambios
                self.guardar_memoria()
                
                logger.info(f"Patrón actualizado: {patron_id} (frecuencia: {patron['frecuencia']})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error actualizando patrón: {e}")
            return False
    
    def _generar_id_patron(self, tipo: str, movimiento: Dict) -> str:
        """Genera un ID único para un patrón"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        if tipo == 'referencia':
            return movimiento.get('referencia_bancaria', f'ref_{timestamp}')
        elif tipo == 'monto_exacto':
            monto = abs(float(movimiento.get('monto', 0)))
            return f"{monto:.2f}"
        else:
            # Para otros tipos, usar timestamp + tipo
            return f"{tipo}_{timestamp}"
    
    def _crear_ejemplo(self, movimiento: Dict) -> Dict:
        """Crea un ejemplo simplificado de un movimiento"""
        return {
            'fecha': movimiento.get('fecha', ''),
            'descripcion': movimiento.get('descripcion', '')[:50],
            'monto': float(movimiento.get('monto', 0)),
            'referencia': movimiento.get('referencia_bancaria', '')[:20] if movimiento.get('referencia_bancaria') else ''
        }
    
    def _calcular_proxima_fecha(self, desde: datetime, dias: int) -> str:
        """Calcula la próxima fecha esperada para un patrón temporal"""
        proxima = desde + timedelta(days=dias)
        return proxima.strftime('%Y-%m-%d')
    
    def guardar_memoria(self):
        """Guarda la memoria en el archivo JSON"""
        try:
            # Crear backup si es necesario
            if self.sesion_actual['transacciones_procesadas'] % 50 == 0:
                self._crear_backup()
            
            # Guardar memoria principal
            with open(self.archivo_memoria, 'w', encoding='utf-8') as f:
                json.dump(self.memoria, f, indent=2, ensure_ascii=False)
            
            logger.debug("Memoria guardada exitosamente")
            
        except Exception as e:
            logger.error(f"Error guardando memoria: {e}")
    
    def _crear_backup(self):
        """Crea un backup de la memoria actual"""
        try:
            with open(self.archivo_backup, 'w', encoding='utf-8') as f:
                json.dump(self.memoria, f, indent=2, ensure_ascii=False)
            logger.info(f"Backup creado: {self.archivo_backup}")
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
    
    def generar_reporte_aprendizaje(self) -> str:
        """Genera un reporte del estado actual del aprendizaje"""
        total_patrones = sum(
            len(patrones) for patrones in self.memoria['patrones_detectados'].values()
        )
        
        reporte = f"""
📊 ESTADO DE LA MEMORIA - {datetime.now().strftime('%Y-%m-%d %H:%M')}
═══════════════════════════════════════════════════════

📚 Base de Conocimiento:
   • Total transacciones aprendidas: {self.memoria['total_transacciones_aprendidas']}
   • Total patrones detectados: {total_patrones}
   • Última actualización: {self.memoria['ultima_actualizacion']}

📈 Distribución de Patrones:
   • Referencias bancarias: {len(self.memoria['patrones_detectados']['referencias_bancarias'])}
   • Montos exactos: {len(self.memoria['patrones_detectados']['montos_exactos'])}
   • Rangos de monto: {len(self.memoria['patrones_detectados']['rangos_monto'])}
   • Patrones temporales: {len(self.memoria['patrones_detectados']['patrones_temporales'])}
   • Descripciones: {len(self.memoria['patrones_detectados']['descripciones_frecuentes'])}

🎯 Sesión Actual:
   • Patrones nuevos detectados: {self.sesion_actual['patrones_nuevos']}
   • Patrones actualizados: {self.sesion_actual['patrones_actualizados']}
   • Transacciones procesadas: {self.sesion_actual['transacciones_procesadas']}
"""
        
        # Agregar top 5 patrones más frecuentes
        top_patrones = self._obtener_top_patrones(5)
        if top_patrones:
            reporte += "\n🏆 Top 5 Patrones Más Frecuentes:\n"
            for i, (tipo, id_patron, patron) in enumerate(top_patrones, 1):
                reporte += f"   {i}. [{tipo}] {id_patron}: {patron.get('frecuencia', 0)} usos (conf: {patron.get('confianza', 0):.0%})\n"
        
        return reporte
    
    def _obtener_top_patrones(self, limite: int = 5) -> List:
        """Obtiene los patrones más frecuentes"""
        todos_patrones = []
        
        for tipo, patrones_dict in self.memoria['patrones_detectados'].items():
            for patron_id, patron in patrones_dict.items():
                todos_patrones.append((tipo, patron_id, patron))
        
        # Ordenar por frecuencia
        todos_patrones.sort(key=lambda x: x[2].get('frecuencia', 0), reverse=True)
        
        return todos_patrones[:limite]
    
    def exportar_memoria_markdown(self) -> str:
        """Exporta la memoria a un archivo Markdown para revisión humana"""
        archivo_md = self.memoria_dir / f'memoria_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        
        contenido = f"""# 🧠 Memoria del Sistema - Exportación
## Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Estadísticas Generales
- **Total transacciones aprendidas**: {self.memoria['total_transacciones_aprendidas']}
- **Total patrones detectados**: {self.memoria['total_patrones_detectados']}
- **Versión del sistema**: {self.memoria['version']}

"""
        
        # Exportar cada tipo de patrón
        for tipo, patrones in self.memoria['patrones_detectados'].items():
            if patrones:
                contenido += f"\n## {tipo.replace('_', ' ').title()}\n\n"
                
                for patron_id, patron in list(patrones.items())[:10]:  # Limitar a 10 por tipo
                    contenido += f"### `{patron_id}`\n"
                    contenido += f"- **Frecuencia**: {patron.get('frecuencia', 0)} veces\n"
                    contenido += f"- **Confianza**: {patron.get('confianza', 0):.0%}\n"
                    contenido += f"- **Última aparición**: {patron.get('ultima_aparicion', 'N/A')}\n"
                    
                    clasificacion = patron.get('clasificacion', {})
                    if clasificacion:
                        contenido += f"- **Clasificación**: {clasificacion.get('tipo', 'N/A')} → {clasificacion.get('categoria', 'N/A')}\n"
                    
                    contenido += "\n"
        
        # Guardar archivo
        with open(archivo_md, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print(f"📄 Memoria exportada a: {archivo_md.name}")
        return str(archivo_md)
    
    def registrar_feedback_humano(self, tipo_patron: str, patron_id: str, feedback: Dict) -> bool:
        """Registra feedback humano sobre un patrón específico"""
        try:
            patron = None
            
            # Buscar el patrón según su tipo
            if tipo_patron == 'referencia_bancaria':
                patron = self.memoria['patrones_detectados']['referencias_bancarias'].get(patron_id)
            elif tipo_patron == 'monto_exacto':
                patron = self.memoria['patrones_detectados']['montos_exactos'].get(patron_id)
            elif tipo_patron == 'rango_monto':
                patron = self.memoria['patrones_detectados']['rangos_monto'].get(patron_id)
            elif tipo_patron == 'descripcion':
                patron = self.memoria['patrones_detectados']['descripciones_frecuentes'].get(patron_id)
            elif tipo_patron == 'temporal':
                patron = self.memoria['patrones_detectados']['patrones_temporales'].get(patron_id)
            
            if not patron:
                logger.error(f"Patrón no encontrado: {tipo_patron}:{patron_id}")
                return False
            
            # Inicializar feedback_humano si no existe
            if 'feedback_humano' not in patron:
                patron['feedback_humano'] = []
            
            # Agregar nuevo feedback
            patron['feedback_humano'].append({
                'fecha': datetime.now().isoformat(),
                'accion': feedback.get('accion', 'correccion'),
                'clasificacion_original': patron.get('clasificacion', {}),
                'clasificacion_correcta': feedback.get('clasificacion_correcta', {}),
                'nota': feedback.get('nota', ''),
                'confianza_usuario': feedback.get('confianza_usuario', 1.0)
            })
            
            # Actualizar patrón según el tipo de feedback
            if feedback.get('accion') == 'correccion':
                # El humano corrigió la clasificación
                patron['clasificacion'] = feedback['clasificacion_correcta']
                patron['confianza'] = min(0.98, patron.get('confianza', 0.8) + 0.15)
                patron['validado_humano'] = True
                logger.info(f"Patrón {patron_id} corregido por humano")
                
            elif feedback.get('accion') == 'confirmacion':
                # El humano confirmó que la clasificación está correcta
                patron['confianza'] = min(0.99, patron.get('confianza', 0.8) + 0.08)
                patron['validado_humano'] = True
                logger.info(f"Patrón {patron_id} confirmado por humano")
                
            elif feedback.get('accion') == 'rechazo':
                # El humano rechazó completamente el patrón
                patron['confianza'] = max(0.1, patron.get('confianza', 0.8) - 0.20)
                patron['validado_humano'] = False
                logger.warning(f"Patrón {patron_id} rechazado por humano")
            
            # Guardar cambios
            self.guardar_memoria()
            return True
            
        except Exception as e:
            logger.error(f"Error registrando feedback humano: {e}")
            return False


# Funciones de utilidad
def test_memoria():
    """Función de prueba del sistema de memoria"""
    print("🧪 Probando Sistema de Memoria...")
    
    memoria = MemoriaPatrones()
    
    # Movimiento de prueba
    movimiento_test = {
        'fecha': '2025-08-11',
        'descripcion': 'SPEI ENVIADO BANAMEX / 0076312440 costco',
        'monto': -2036.49,
        'referencia_bancaria': '0076312440'
    }
    
    # Buscar patrones
    patrones = memoria.buscar_patrones_existentes(movimiento_test)
    print(f"\n📍 Patrones encontrados: {len(patrones)}")
    
    if not patrones:
        # Registrar como nuevo patrón
        patron_nuevo = {
            'tipo': 'referencia',
            'clasificacion_automatica': {
                'tipo': 'TRANSFERENCIA',
                'categoria': 'Pagos de Tarjetas',
                'cuenta_vinculada': 'TDC BANAMEX COSTCO 783'
            },
            'confianza_patron': 0.85
        }
        
        memoria.registrar_patron_nuevo(patron_nuevo, movimiento_test)
        print("✅ Patrón nuevo registrado")
    else:
        print(f"✅ Patrón existente encontrado: {patrones[0].get('id', 'N/A')}")
    
    # Generar reporte
    print(memoria.generar_reporte_aprendizaje())
    
    return memoria


if __name__ == "__main__":
    test_memoria()
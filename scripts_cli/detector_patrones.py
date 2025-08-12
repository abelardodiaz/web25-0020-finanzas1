#!/usr/bin/env python3
"""
Detector de Patrones con IA DeepSeek
Sistema de detección automática y aprendizaje continuo
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from sistema_memoria import MemoriaPatrones

# Configurar logging
logging.basicConfig(level=logging.INFO)
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

class DetectorPatrones:
    """Detector inteligente de patrones usando DeepSeek y memoria"""
    
    def __init__(self, deepseek_client):
        self.deepseek = deepseek_client
        self.memoria = MemoriaPatrones()
        self.logs_dir = Path(__file__).parent / 'logs'
        self.logs_dir.mkdir(exist_ok=True)
        
        # Log de patrones detectados
        self.log_patrones = self.logs_dir / f'patrones_detectados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        self._inicializar_log_patrones()
    
    def _inicializar_log_patrones(self):
        """Inicializa el archivo de log de patrones"""
        with open(self.log_patrones, 'w', encoding='utf-8') as f:
            f.write(f"""# 🔍 Log de Detección de Patrones
## Sesión: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

""")
    
    def procesar_con_deteccion(self, movimiento: Dict, modo_interactivo: bool = True) -> Dict:
        """
        Procesa un movimiento con detección automática de patrones
        Retorna la clasificación enriquecida con información de patrones
        """
        print(f"\n{Colors.OKBLUE}🔍 Analizando movimiento con detección de patrones...{Colors.ENDC}")
        
        # 1. Buscar patrones existentes en memoria
        patrones_existentes = self.memoria.buscar_patrones_existentes(movimiento)
        
        if patrones_existentes:
            print(f"{Colors.OKGREEN}✓ {len(patrones_existentes)} patrón(es) encontrado(s) en memoria{Colors.ENDC}")
            patron_principal = patrones_existentes[0]
            
            # Mostrar patrón encontrado
            self._mostrar_patron_encontrado(patron_principal)
            
            # Si el patrón tiene alta confianza, usar su clasificación
            if patron_principal.get('confianza', 0) >= 0.85:
                print(f"{Colors.OKGREEN}⚡ Usando clasificación del patrón (confianza: {patron_principal['confianza']:.0%}){Colors.ENDC}")
                
                # Actualizar frecuencia del patrón
                self.memoria.actualizar_frecuencia_patron(
                    patron_principal.get('tipo_patron', ''),
                    patron_principal.get('id', ''),
                    movimiento
                )
                
                # Retornar clasificación del patrón
                return {
                    'clasificacion': patron_principal.get('clasificacion', {}),
                    'patron_usado': patron_principal,
                    'confianza_total': patron_principal.get('confianza', 0.85),
                    'metodo': 'patron_existente'
                }
        
        # 2. Si no hay patrón o tiene baja confianza, consultar DeepSeek
        print(f"{Colors.OKCYAN}🤖 Consultando DeepSeek para análisis profundo...{Colors.ENDC}")
        
        # Generar contexto enriquecido
        contexto = self._generar_contexto_memoria(patrones_existentes)
        
        # Crear prompt dual: clasificar + detectar patrones
        prompt_dual = self._generar_prompt_clasificacion_deteccion(movimiento, contexto)
        
        # Consultar DeepSeek
        respuesta_ia = self.deepseek.procesar_movimiento_con_prompt(movimiento, prompt_dual)
        
        if not respuesta_ia:
            print(f"{Colors.FAIL}✗ Error en respuesta de IA{Colors.ENDC}")
            return self._clasificacion_fallback(movimiento)
        
        # 3. Analizar si detectó un patrón nuevo
        if respuesta_ia.get('patron_detectado', {}).get('es_patron_nuevo'):
            print(f"{Colors.WARNING}🆕 ¡Posible patrón nuevo detectado!{Colors.ENDC}")
            
            if modo_interactivo:
                # Confirmar con usuario
                if self._confirmar_patron_nuevo(movimiento, respuesta_ia):
                    # Analizar y guardar el patrón
                    patron_analizado = self._analizar_patron_nuevo(movimiento, respuesta_ia)
                    self.memoria.registrar_patron_nuevo(patron_analizado, movimiento)
                    print(f"{Colors.OKGREEN}✅ Patrón guardado en memoria{Colors.ENDC}")
            else:
                # En modo automático, guardar si tiene alta confianza
                if respuesta_ia.get('patron_detectado', {}).get('confianza_patron', 0) >= 0.7:
                    patron_analizado = self._analizar_patron_nuevo(movimiento, respuesta_ia)
                    self.memoria.registrar_patron_nuevo(patron_analizado, movimiento)
        
        # 4. Registrar en log
        self._registrar_deteccion(movimiento, respuesta_ia, patrones_existentes)
        
        # 5. Retornar clasificación enriquecida
        return {
            'clasificacion': respuesta_ia.get('clasificacion', {}),
            'patron_detectado': respuesta_ia.get('patron_detectado', {}),
            'patrones_previos': patrones_existentes,
            'confianza_total': respuesta_ia.get('clasificacion', {}).get('confianza', 0.5),
            'metodo': 'deepseek_analisis'
        }
    
    def _generar_contexto_memoria(self, patrones_existentes: List[Dict]) -> str:
        """Genera contexto de memoria para el prompt"""
        if not patrones_existentes:
            return "No hay patrones previos similares registrados."
        
        contexto = "PATRONES SIMILARES EN MEMORIA:\n"
        
        for i, patron in enumerate(patrones_existentes[:3], 1):  # Máximo 3 patrones
            contexto += f"""
Patrón {i}:
- Tipo: {patron.get('tipo_patron', 'desconocido')}
- Frecuencia: {patron.get('frecuencia', 0)} veces
- Confianza: {patron.get('confianza', 0):.0%}
- Clasificación usual: {patron.get('clasificacion', {}).get('tipo', 'N/A')} → {patron.get('clasificacion', {}).get('categoria', 'N/A')}
"""
        
        return contexto
    
    def _generar_prompt_clasificacion_deteccion(self, movimiento: Dict, contexto: str) -> str:
        """Genera prompt especializado para clasificación + detección de patrones"""
        
        prompt = f"""SISTEMA EXPERTO EN DETECCIÓN DE PATRONES FINANCIEROS

TRANSACCIÓN ACTUAL:
- Fecha: {movimiento.get('fecha', 'N/A')}
- Descripción: "{movimiento.get('descripcion', 'N/A')}"
- Monto: ${movimiento.get('monto', 0):,.2f}
- Referencia: {movimiento.get('referencia_bancaria', 'N/A')}

{contexto}

MISIÓN DUAL:
1. CLASIFICAR esta transacción con precisión
2. DETECTAR si forma parte de un patrón (nuevo o existente)

ANÁLISIS DE PATRONES REQUERIDO:
Identifica elementos repetitivos o distintivos:
- ¿La REFERENCIA BANCARIA es única y podría repetirse? (ej: 0076312440)
- ¿El MONTO EXACTO podría ser recurrente? (ej: $270.00 semanal)
- ¿Hay KEYWORDS en la descripción que indican un patrón? (ej: "COSTCO", "ISP", "HIPOTECA")
- ¿Sugiere PERIODICIDAD temporal? (ej: mensual, quincenal)
- ¿Es una COMBINACIÓN de factores? (ej: monto + descripción)

RESPUESTA JSON DUAL REQUERIDA:
{{
  "clasificacion": {{
    "tipo": "GASTO|INGRESO|TRANSFERENCIA",
    "categoria": "categoría específica (máx 25 chars)",
    "cuenta_vinculada": "nombre_cuenta_detectada_o_null",
    "confianza": 0.00-1.00
  }},
  "patron_detectado": {{
    "es_patron_nuevo": true|false,
    "tipo_patron": "referencia|monto_exacto|monto_rango|temporal|descripcion|combinacion",
    "elementos_clave": ["lista", "de", "elementos", "distintivos"],
    "descripcion_patron": "descripción del patrón detectado",
    "frecuencia_estimada": "unico|diario|semanal|quincenal|mensual|irregular",
    "confianza_patron": 0.00-1.00,
    "razon_deteccion": "explicación de por qué es un patrón"
  }}
}}

IMPORTANTE: 
- Si la referencia bancaria es un número largo (8+ dígitos), probablemente es un patrón único
- Si el monto es muy específico (ej: $270.00, $8,500.00), podría ser recurrente
- Palabras clave como nombres de empresas/servicios suelen indicar patrones"""
        
        return prompt
    
    def _mostrar_patron_encontrado(self, patron: Dict):
        """Muestra información sobre un patrón encontrado"""
        print(f"\n{Colors.HEADER}📊 PATRÓN ENCONTRADO EN MEMORIA{Colors.ENDC}")
        print(f"Tipo: {patron.get('tipo_patron', 'N/A')}")
        print(f"ID: {patron.get('id', 'N/A')}")
        print(f"Frecuencia: {patron.get('frecuencia', 0)} veces")
        print(f"Confianza: {patron.get('confianza', 0):.0%}")
        
        clasificacion = patron.get('clasificacion', {})
        if clasificacion:
            print(f"Clasificación típica: {clasificacion.get('tipo', 'N/A')} → {clasificacion.get('categoria', 'N/A')}")
            if clasificacion.get('cuenta_vinculada'):
                print(f"Cuenta vinculada: {clasificacion.get('cuenta_vinculada')}")
    
    def _confirmar_patron_nuevo(self, movimiento: Dict, respuesta_ia: Dict) -> bool:
        """Solicita confirmación del usuario para guardar un patrón nuevo"""
        patron_info = respuesta_ia.get('patron_detectado', {})
        
        print(f"\n{Colors.WARNING}═══════════════════════════════════════{Colors.ENDC}")
        print(f"{Colors.BOLD}🧠 PATRÓN NUEVO DETECTADO{Colors.ENDC}")
        print(f"{Colors.WARNING}═══════════════════════════════════════{Colors.ENDC}")
        
        print(f"\n📊 ANÁLISIS DE LA IA:")
        print(f"   Tipo de patrón: {patron_info.get('tipo_patron', 'N/A')}")
        print(f"   Elementos clave: {', '.join(patron_info.get('elementos_clave', []))}")
        print(f"   Descripción: {patron_info.get('descripcion_patron', 'N/A')}")
        print(f"   Frecuencia estimada: {patron_info.get('frecuencia_estimada', 'N/A')}")
        print(f"   Confianza: {patron_info.get('confianza_patron', 0):.0%}")
        print(f"   Razón: {patron_info.get('razon_deteccion', 'N/A')}")
        
        print(f"\n🎯 CLASIFICACIÓN PROPUESTA:")
        clasificacion = respuesta_ia.get('clasificacion', {})
        print(f"   Tipo: {clasificacion.get('tipo', 'N/A')}")
        print(f"   Categoría: {clasificacion.get('categoria', 'N/A')}")
        if clasificacion.get('cuenta_vinculada'):
            print(f"   Cuenta: {clasificacion.get('cuenta_vinculada')}")
        
        print(f"\n{Colors.BOLD}¿Guardar este patrón para futuras clasificaciones automáticas?{Colors.ENDC}")
        print("[s] Sí, guardar patrón")
        print("[n] No, solo esta vez")
        print("[m] Modificar antes de guardar")
        
        opcion = input(f"\n{Colors.OKCYAN}Opción: {Colors.ENDC}").strip().lower()
        
        if opcion == 's':
            return True
        elif opcion == 'm':
            # TODO: Implementar modificación interactiva
            print(f"{Colors.WARNING}Modificación interactiva pendiente de implementar{Colors.ENDC}")
            return True
        else:
            return False
    
    def _analizar_patron_nuevo(self, movimiento: Dict, respuesta_ia: Dict) -> Dict:
        """Analiza y estructura un patrón nuevo para guardarlo"""
        patron_info = respuesta_ia.get('patron_detectado', {})
        clasificacion = respuesta_ia.get('clasificacion', {})
        
        # Determinar las reglas de detección según el tipo
        reglas_deteccion = {}
        tipo_patron = patron_info.get('tipo_patron', 'desconocido')
        
        if tipo_patron == 'referencia':
            reglas_deteccion['referencia_exacta'] = movimiento.get('referencia_bancaria', '')
            
        elif tipo_patron == 'monto_exacto':
            reglas_deteccion['monto_exacto'] = abs(float(movimiento.get('monto', 0)))
            reglas_deteccion['keywords_obligatorias'] = patron_info.get('elementos_clave', [])
            
        elif tipo_patron == 'monto_rango':
            monto = abs(float(movimiento.get('monto', 0)))
            # Crear rango con ±10%
            reglas_deteccion['monto_rango'] = {
                'min': monto * 0.9,
                'max': monto * 1.1
            }
            reglas_deteccion['keywords_obligatorias'] = patron_info.get('elementos_clave', [])
            
        elif tipo_patron == 'temporal':
            # Mapear frecuencia a días
            frecuencia_map = {
                'diario': 1,
                'semanal': 7,
                'quincenal': 15,
                'mensual': 30
            }
            reglas_deteccion['periodicidad_dias'] = frecuencia_map.get(
                patron_info.get('frecuencia_estimada', 'mensual'), 30
            )
            reglas_deteccion['keywords_obligatorias'] = patron_info.get('elementos_clave', [])
            
        else:  # descripcion o combinacion
            reglas_deteccion['keywords_obligatorias'] = patron_info.get('elementos_clave', [])
        
        # Estructura del patrón para guardar
        patron_definicion = {
            'tipo': tipo_patron,
            'nombre_patron': patron_info.get('descripcion_patron', 'Patrón sin nombre'),
            'reglas_deteccion': reglas_deteccion,
            'clasificacion_automatica': {
                'tipo': clasificacion.get('tipo', 'GASTO'),
                'categoria': clasificacion.get('categoria', 'Sin categoría'),
                'cuenta_vinculada': clasificacion.get('cuenta_vinculada')
            },
            'confianza_patron': patron_info.get('confianza_patron', 0.5),
            'origen': 'deepseek_deteccion',
            'fecha_deteccion': datetime.now().isoformat()
        }
        
        return patron_definicion
    
    def _clasificacion_fallback(self, movimiento: Dict) -> Dict:
        """Clasificación de respaldo cuando falla la IA"""
        monto = movimiento.get('monto', 0)
        
        return {
            'clasificacion': {
                'tipo': 'GASTO' if monto < 0 else 'INGRESO',
                'categoria': 'Sin clasificar',
                'cuenta_vinculada': None,
                'confianza': 0.1
            },
            'patron_detectado': None,
            'metodo': 'fallback'
        }
    
    def _registrar_deteccion(self, movimiento: Dict, respuesta_ia: Dict, patrones_previos: List[Dict]):
        """Registra la detección en el log"""
        try:
            with open(self.log_patrones, 'a', encoding='utf-8') as f:
                f.write(f"""## Movimiento: {movimiento.get('descripcion', 'N/A')[:50]}
**Fecha**: {movimiento.get('fecha', 'N/A')}
**Monto**: ${movimiento.get('monto', 0):,.2f}

### Patrones Previos Encontrados: {len(patrones_previos)}
""")
                
                if patrones_previos:
                    for patron in patrones_previos[:2]:
                        f.write(f"- {patron.get('tipo_patron', 'N/A')}: {patron.get('id', 'N/A')} (conf: {patron.get('confianza', 0):.0%})\n")
                
                patron_nuevo = respuesta_ia.get('patron_detectado', {})
                if patron_nuevo.get('es_patron_nuevo'):
                    f.write(f"""
### 🆕 Patrón Nuevo Detectado:
- **Tipo**: {patron_nuevo.get('tipo_patron', 'N/A')}
- **Elementos clave**: {', '.join(patron_nuevo.get('elementos_clave', []))}
- **Confianza**: {patron_nuevo.get('confianza_patron', 0):.0%}
""")
                
                f.write("\n---\n\n")
                
        except Exception as e:
            logger.error(f"Error registrando detección: {e}")
    
    def generar_reporte_sesion(self) -> str:
        """Genera un reporte de la sesión de detección"""
        reporte = self.memoria.generar_reporte_aprendizaje()
        
        # Agregar información específica de esta sesión
        reporte += f"""
📝 Log de Patrones: {self.log_patrones.name}
📊 Memoria Actualizada: {self.memoria.archivo_memoria.name}
"""
        
        return reporte


# Extensión del cliente DeepSeek para soportar prompts personalizados
def extender_deepseek_client(DeepSeekClient):
    """Extiende el cliente DeepSeek con método para prompts personalizados"""
    
    def procesar_movimiento_con_prompt(self, movimiento: Dict, prompt_personalizado: str) -> Optional[Dict]:
        """Procesa un movimiento con un prompt personalizado"""
        
        if self.test_mode:
            # Respuesta simulada para test
            return {
                'clasificacion': {
                    'tipo': 'GASTO' if movimiento.get('monto', 0) < 0 else 'INGRESO',
                    'categoria': 'Categoría Test',
                    'cuenta_vinculada': None,
                    'confianza': 0.75
                },
                'patron_detectado': {
                    'es_patron_nuevo': False,
                    'tipo_patron': 'test',
                    'confianza_patron': 0.5
                }
            }
        
        # Usar el prompt personalizado en lugar del genérico
        # Aquí conectaríamos con el método real de DeepSeek
        # Por ahora, simulamos la respuesta
        return self.procesar_movimiento(movimiento)
    
    # Agregar el método a la clase
    DeepSeekClient.procesar_movimiento_con_prompt = procesar_movimiento_con_prompt
    
    return DeepSeekClient


# Función de prueba
def test_detector():
    """Prueba el detector de patrones"""
    print(f"{Colors.HEADER}🧪 Probando Detector de Patrones{Colors.ENDC}")
    
    # Crear un cliente DeepSeek simulado
    class DeepSeekMock:
        def __init__(self):
            self.test_mode = True
        
        def procesar_movimiento_con_prompt(self, movimiento, prompt):
            return {
                'clasificacion': {
                    'tipo': 'TRANSFERENCIA',
                    'categoria': 'Pagos de Tarjetas',
                    'cuenta_vinculada': 'TDC BANAMEX COSTCO 783',
                    'confianza': 0.95
                },
                'patron_detectado': {
                    'es_patron_nuevo': True,
                    'tipo_patron': 'referencia',
                    'elementos_clave': ['0076312440', 'COSTCO', 'BANAMEX'],
                    'descripcion_patron': 'Pago recurrente TDC Costco',
                    'frecuencia_estimada': 'mensual',
                    'confianza_patron': 0.90,
                    'razon_deteccion': 'Referencia bancaria única y descripción específica'
                }
            }
    
    # Crear detector
    deepseek_mock = DeepSeekMock()
    detector = DetectorPatrones(deepseek_mock)
    
    # Movimiento de prueba
    movimiento = {
        'fecha': '2025-08-11',
        'descripcion': 'SPEI ENVIADO BANAMEX / 0076312440 costco julio',
        'monto': -2036.49,
        'referencia_bancaria': '0076312440'
    }
    
    # Procesar con detección
    resultado = detector.procesar_con_deteccion(movimiento, modo_interactivo=False)
    
    print(f"\n{Colors.OKGREEN}Resultado de detección:{Colors.ENDC}")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    
    # Generar reporte
    print(detector.generar_reporte_sesion())


if __name__ == "__main__":
    test_detector()
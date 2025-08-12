#!/usr/bin/env python3
"""
Cliente DeepSeek API para procesamiento de movimientos bancarios
Versión 0.8.3 - Sistema de enriquecimiento con IA
"""
import os
import json
import time
import logging
from typing import Dict, List, Optional, Any
import requests
from datetime import datetime
from pathlib import Path

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

class DeepSeekClient:
    """Cliente para interactuar con la API de DeepSeek"""
    
    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.api_key = self._cargar_credenciales()
        self.cuentas_frecuentes = []
        self.estadisticas = {
            'procesados': 0,
            'fallos': 0,
            'tiempo_total': 0.0,
            'confianza_total': 0.0
        }
        
        # Sistema de logging para evaluación
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.logs_dir = Path(__file__).parent / 'logs'
        self.logs_dir.mkdir(exist_ok=True)
        
        # Archivos de evaluación
        self.log_respuestas = self.logs_dir / f'deepseek_respuestas_{self.session_id}.md'
        self.log_evaluacion = self.logs_dir / f'evaluacion_ia_{self.session_id}.md'
        
        # Inicializar archivos de log
        self._inicializar_logs()
    
    def _inicializar_logs(self):
        """Inicializa los archivos de logging para evaluación"""
        try:
            # Log de respuestas detalladas
            with open(self.log_respuestas, 'w', encoding='utf-8') as f:
                f.write(f"""# Log de Respuestas DeepSeek
## Sesión: {self.session_id}
## Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
## Modo: {'TEST' if self.test_mode else 'PRODUCCIÓN'}

---

""")
            
            # Log de evaluación resumida
            with open(self.log_evaluacion, 'w', encoding='utf-8') as f:
                f.write(f"""# Evaluación de IA - Sesión {self.session_id}

## Resumen de Procesamiento

| Métrica | Valor |
|---------|-------|
| Fecha | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
| Modo | {'TEST' if self.test_mode else 'PRODUCCIÓN'} |
| Movimientos procesados | 0 |
| Fallos | 0 |
| Confianza promedio | 0.00 |

## Análisis de Calidad

### Movimientos Bien Clasificados
_(Se actualizará durante el procesamiento)_

### Movimientos con Baja Confianza
_(Se actualizará durante el procesamiento)_

### Errores Detectados
_(Se actualizará durante el procesamiento)_

---

""")
            
            print(f"{Colors.OKCYAN}📝 Logs inicializados en: scripts_cli/logs/{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.WARNING}⚠️  Error inicializando logs: {e}{Colors.ENDC}")
    
    def _registrar_respuesta_ia(self, movimiento: Dict, prompt: str, respuesta_raw: str, 
                               respuesta_procesada: Optional[Dict], tiempo: float):
        """Registra la respuesta de IA para evaluación"""
        try:
            with open(self.log_respuestas, 'a', encoding='utf-8') as f:
                f.write(f"""## Movimiento #{movimiento.get('numero', 'N/A')}
**Fecha**: {movimiento.get('fecha', 'N/A')}  
**Descripción**: `{movimiento.get('descripcion', 'N/A')[:100]}`  
**Monto**: ${movimiento.get('monto', 0):,.2f}  
**Tiempo respuesta**: {tiempo:.2f}s  

### Prompt Enviado:
```
{prompt[:500]}...
```

### Respuesta Raw de DeepSeek:
```json
{respuesta_raw[:1000]}
```

### Respuesta Procesada:
```json
{json.dumps(respuesta_procesada, indent=2, ensure_ascii=False) if respuesta_procesada else 'ERROR - No se pudo procesar'}
```

### Evaluación:
- ✅ **Tipo detectado**: {respuesta_procesada.get('tipo', 'ERROR') if respuesta_procesada else 'ERROR'}
- ✅ **Categoría**: {respuesta_procesada.get('categoria', 'ERROR') if respuesta_procesada else 'ERROR'}  
- ✅ **Confianza**: {respuesta_procesada.get('confianza', 0) if respuesta_procesada else 0}
- ✅ **Cuenta vinculada**: {respuesta_procesada.get('cuenta_vinculada', 'N/A') if respuesta_procesada else 'N/A'}

---

""")
        except Exception as e:
            logger.error(f"Error registrando respuesta: {e}")
        
    def _cargar_credenciales(self) -> str:
        """Carga las credenciales de DeepSeek desde .env"""
        try:
            # Intentar cargar desde .env file
            env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('DEEPSEEK_API_KEY='):
                            api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                            print(f"{Colors.OKGREEN}✓ Credenciales DeepSeek cargadas desde .env{Colors.ENDC}")
                            return api_key
            
            # Fallback a variable de entorno
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if api_key:
                print(f"{Colors.OKGREEN}✓ Credenciales DeepSeek cargadas desde ENV{Colors.ENDC}")
                return api_key
            
            print(f"{Colors.WARNING}⚠️  No se encontraron credenciales DeepSeek{Colors.ENDC}")
            return ""
            
        except Exception as e:
            print(f"{Colors.FAIL}✗ Error cargando credenciales: {e}{Colors.ENDC}")
            return ""
    
    def verificar_conectividad(self) -> bool:
        """Verifica la conectividad con la API de DeepSeek"""
        if self.test_mode:
            print(f"{Colors.OKGREEN}✓ Modo test - Saltando verificación de API{Colors.ENDC}")
            return True
            
        if not self.api_key:
            print(f"{Colors.FAIL}✗ API Key no configurada{Colors.ENDC}")
            print(f"{Colors.WARNING}Tip: Usa --test para probar sin API{Colors.ENDC}")
            return False
            
        try:
            # Test básico de conectividad
            response = requests.get("https://api.deepseek.com", timeout=10)
            print(f"{Colors.OKGREEN}✓ Conexión DeepSeek: Operativa{Colors.ENDC}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}✗ Error de conectividad DeepSeek: {e}{Colors.ENDC}")
            return False
    
    def establecer_contexto_cuentas(self, cuentas: List[str]):
        """Establece el contexto de cuentas frecuentes para la IA"""
        self.cuentas_frecuentes = cuentas
        print(f"{Colors.OKCYAN}📋 Contexto establecido: {len(cuentas)} cuentas conocidas{Colors.ENDC}")
        logger.info(f"Contexto de cuentas establecido: {cuentas}")
    
    def generar_prompt_especializado(self, movimiento: Dict[str, Any]) -> str:
        """Genera el prompt especializado para clasificar un movimiento"""
        
        # Contexto de cuentas frecuentes
        cuentas_context = ""
        if self.cuentas_frecuentes:
            cuentas_context = f"""
CUENTAS CONOCIDAS EN EL SISTEMA:
{chr(10).join(f"- {cuenta}" for cuenta in self.cuentas_frecuentes)}
"""
        
        prompt = f"""Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: {movimiento.get('fecha', 'N/A')}
- Descripción original: "{movimiento.get('descripcion', 'N/A')}"
- Monto: ${movimiento.get('monto', 0):,.2f}
- Referencia: {movimiento.get('referencia_bancaria', 'N/A')}

{cuentas_context}

INSTRUCCIONES:
1. CLASIFICACIÓN: Determina GASTO/INGRESO/TRANSFERENCIA basado en:
   - GASTO: Salida de dinero hacia servicios/productos/proveedores
   - INGRESO: Entrada de dinero desde fuentes externas (clientes, rentas, ingresos)
   - TRANSFERENCIA: Entre cuentas propias (detectar "TRANSF", "XFR", "SPEI", nombres bancarios)

2. CATEGORÍA: Asigna categoría específica y descriptiva (máximo 25 caracteres):
   - Para gastos: "Alimentos", "Servicios Básicos", "Entretenimiento", etc.
   - Para ingresos: "Ingresos ISP", "Rentas", "Servicios Profesionales", etc.
   - Para transferencias: "Pagos de Tarjetas", "Transferencias Entre Cuentas", etc.

3. CUENTA VINCULADA: Si es transferencia, identifica la cuenta destino/origen:
   - Buscar patrones como "TDC", "TDB", nombres de bancos
   - Usar las cuentas conocidas como referencia

4. ANÁLISIS CONTEXTUAL: Proporciona contexto útil sobre el movimiento

5. CONFIANZA: Tu nivel de certeza en la clasificación (0.0-1.0)

REGLAS ESPECIALES:
- Si contiene "TDC" + nombre banco → Es pago de tarjeta de crédito
- Si contiene "SPEI" o "TRANSF" → Es transferencia
- Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente
- Si es monto positivo a cuenta BBVA → Generalmente ingreso o transferencia entrante

DEVUELVE SOLO UN JSON VÁLIDO SIN TEXTO ADICIONAL:
{{
  "tipo": "GASTO|INGRESO|TRANSFERENCIA",
  "categoria": "nombre_categoria_descriptiva",
  "cuenta_vinculada": "nombre_cuenta_detectada_o_null",
  "nota_ia": "explicación_breve_del_contexto",
  "confianza": 0.95,
  "reglas_aplicadas": ["lista", "de", "reglas", "utilizadas"]
}}"""
        
        return prompt
    
    def procesar_movimiento(self, movimiento: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Procesa un movimiento individual con DeepSeek"""
        
        if self.test_mode:
            # Respuesta simulada para modo test
            return self._generar_respuesta_test(movimiento)
        
        prompt = self.generar_prompt_especializado(movimiento)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,  # Baja variabilidad para consistencia
            "max_tokens": 500   # Respuesta concisa
        }
        
        # Reintentos con backoff exponencial
        for intento in range(3):
            try:
                inicio = time.time()
                response = requests.post(
                    self.api_url, 
                    headers=headers, 
                    json=payload, 
                    timeout=90
                )
                tiempo_respuesta = time.time() - inicio
                
                response.raise_for_status()
                contenido = response.json()["choices"][0]["message"]["content"]
                
                # Parsear y validar respuesta JSON
                resultado = self._validar_respuesta(contenido, movimiento)
                
                # Registrar respuesta para evaluación
                if not self.test_mode:
                    self._registrar_respuesta_ia(movimiento, prompt, contenido, resultado, tiempo_respuesta)
                
                if resultado:
                    # Actualizar estadísticas
                    self.estadisticas['procesados'] += 1
                    self.estadisticas['tiempo_total'] += tiempo_respuesta
                    self.estadisticas['confianza_total'] += resultado.get('confianza', 0)
                    
                    logger.info(f"Movimiento procesado exitosamente en {tiempo_respuesta:.2f}s")
                    return resultado
                
            except requests.exceptions.Timeout:
                print(f"{Colors.WARNING}⌛ Timeout API (intento {intento+1}/3){Colors.ENDC}")
                if intento < 2:
                    time.sleep(2 ** intento)
                    
            except requests.exceptions.HTTPError as e:
                print(f"{Colors.FAIL}✗ Error HTTP: {e}{Colors.ENDC}")
                if intento < 2:
                    time.sleep(2 ** intento)
                    
            except Exception as e:
                print(f"{Colors.FAIL}✗ Error procesando movimiento: {e}{Colors.ENDC}")
                if intento < 2:
                    time.sleep(2 ** intento)
        
        # Si llegamos aquí, falló todos los reintentos
        self.estadisticas['fallos'] += 1
        print(f"{Colors.FAIL}✗ Fallo definitivo procesando movimiento{Colors.ENDC}")
        return self._generar_respuesta_fallback(movimiento)
    
    def _validar_respuesta(self, contenido: str, movimiento: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Valida y normaliza la respuesta de la IA"""
        try:
            # Limpiar respuesta
            contenido_limpio = contenido.strip()
            
            # Remover markdown si existe
            if contenido_limpio.startswith('```json'):
                contenido_limpio = contenido_limpio[7:]
            if contenido_limpio.endswith('```'):
                contenido_limpio = contenido_limpio[:-3]
            
            contenido_limpio = contenido_limpio.strip()
            
            # Parsear JSON
            respuesta = json.loads(contenido_limpio)
            
            # Validar campos requeridos
            campos_requeridos = ['tipo', 'categoria', 'confianza']
            for campo in campos_requeridos:
                if campo not in respuesta:
                    raise ValueError(f"Campo requerido faltante: {campo}")
            
            # Validar tipo
            if respuesta['tipo'] not in ['GASTO', 'INGRESO', 'TRANSFERENCIA']:
                raise ValueError(f"Tipo inválido: {respuesta['tipo']}")
            
            # Normalizar confianza
            confianza = float(respuesta['confianza'])
            if not 0 <= confianza <= 1:
                confianza = max(0, min(1, confianza))
            respuesta['confianza'] = confianza
            
            # Normalizar campos opcionales
            respuesta['cuenta_vinculada'] = respuesta.get('cuenta_vinculada') or None
            respuesta['nota_ia'] = respuesta.get('nota_ia', '')
            respuesta['reglas_aplicadas'] = respuesta.get('reglas_aplicadas', [])
            
            # Truncar campos largos
            respuesta['categoria'] = str(respuesta['categoria'])[:30]
            respuesta['nota_ia'] = str(respuesta['nota_ia'])[:100]
            
            return respuesta
            
        except json.JSONDecodeError as e:
            logger.error(f"Error JSON en respuesta IA: {e}")
            print(f"{Colors.FAIL}✗ JSON inválido de IA: {str(e)[:100]}{Colors.ENDC}")
            return None
            
        except Exception as e:
            logger.error(f"Error validando respuesta IA: {e}")
            print(f"{Colors.FAIL}✗ Error validación IA: {e}{Colors.ENDC}")
            return None
    
    def _generar_respuesta_test(self, movimiento: Dict[str, Any]) -> Dict[str, Any]:
        """Genera una respuesta simulada para modo test"""
        monto = movimiento.get('monto', 0)
        descripcion = movimiento.get('descripcion', '').lower()
        
        # Lógica básica de clasificación para test
        if monto < 0:
            if 'tdc' in descripcion or 'tarjeta' in descripcion:
                tipo = 'TRANSFERENCIA'
                categoria = 'Pagos de Tarjetas'
            else:
                tipo = 'GASTO'
                categoria = 'Gastos Varios'
        else:
            tipo = 'INGRESO'
            categoria = 'Ingresos Varios'
        
        return {
            'tipo': tipo,
            'categoria': categoria,
            'cuenta_vinculada': None,
            'nota_ia': f'Clasificación automática (TEST MODE)',
            'confianza': 0.75,
            'reglas_aplicadas': ['test_mode', 'clasificacion_basica']
        }
    
    def _generar_respuesta_fallback(self, movimiento: Dict[str, Any]) -> Dict[str, Any]:
        """Genera una respuesta fallback cuando falla la IA"""
        monto = movimiento.get('monto', 0)
        
        return {
            'tipo': 'GASTO' if monto < 0 else 'INGRESO',
            'categoria': 'Sin Clasificar',
            'cuenta_vinculada': None,
            'nota_ia': 'Clasificación automática por fallo de IA',
            'confianza': 0.3,
            'reglas_aplicadas': ['fallback_automatico']
        }
    
    def procesar_lote_movimientos(self, movimientos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Procesa un lote completo de movimientos"""
        resultados = []
        total = len(movimientos)
        
        print(f"{Colors.OKBLUE}🔄 Procesando lote de {total} movimientos...{Colors.ENDC}")
        
        for i, movimiento in enumerate(movimientos, 1):
            print(f"{Colors.OKCYAN}Procesando {i}/{total}...{Colors.ENDC}", end=' ')
            
            resultado = self.procesar_movimiento(movimiento)
            if resultado:
                # Combinar datos originales con enriquecimiento IA
                movimiento_enriquecido = movimiento.copy()
                movimiento_enriquecido['decision_ia'] = resultado
                resultados.append(movimiento_enriquecido)
                print(f"{Colors.OKGREEN}✓{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}✗{Colors.ENDC}")
        
        return resultados
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene las estadísticas del procesamiento"""
        procesados = self.estadisticas['procesados']
        
        return {
            'movimientos_procesados': procesados,
            'movimientos_fallidos': self.estadisticas['fallos'],
            'tiempo_total_segundos': round(self.estadisticas['tiempo_total'], 2),
            'tiempo_promedio_por_movimiento': round(
                self.estadisticas['tiempo_total'] / max(procesados, 1), 2
            ),
            'confianza_promedio': round(
                self.estadisticas['confianza_total'] / max(procesados, 1), 2
            ) if procesados > 0 else 0.0
        }
    
    def reiniciar_estadisticas(self):
        """Reinicia las estadísticas de procesamiento"""
        self.estadisticas = {
            'procesados': 0,
            'fallos': 0,
            'tiempo_total': 0.0,
            'confianza_total': 0.0
        }
    
    def generar_reporte_evaluacion(self, movimientos_procesados: List[Dict]):
        """Genera el reporte final de evaluación"""
        if self.test_mode:
            return
            
        try:
            stats = self.obtener_estadisticas()
            
            # Análisis de calidad
            bien_clasificados = []
            baja_confianza = []
            errores = []
            
            for mov in movimientos_procesados:
                decision_ia = mov.get('decision_ia', {})
                confianza = decision_ia.get('confianza', 0)
                
                if confianza >= 0.8:
                    bien_clasificados.append(mov)
                elif confianza >= 0.5:
                    # Confianza media - revisar
                    pass
                else:
                    baja_confianza.append(mov)
            
            # Actualizar archivo de evaluación
            with open(self.log_evaluacion, 'w', encoding='utf-8') as f:
                f.write(f"""# Evaluación de IA - Sesión {self.session_id}

## Resumen de Procesamiento

| Métrica | Valor |
|---------|-------|
| Fecha | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
| Modo | {'TEST' if self.test_mode else 'PRODUCCIÓN'} |
| Movimientos procesados | {stats['movimientos_procesados']} |
| Fallos | {stats['movimientos_fallidos']} |
| Confianza promedio | {stats['confianza_promedio']:.2f} |
| Tiempo total | {stats['tiempo_total_segundos']:.1f}s |
| Tiempo por movimiento | {stats['tiempo_promedio_por_movimiento']:.2f}s |

## Análisis de Calidad

### ✅ Movimientos Bien Clasificados (confianza ≥ 0.8)
**Total: {len(bien_clasificados)} movimientos**

""")
                
                for mov in bien_clasificados[:10]:  # Top 10
                    decision = mov.get('decision_ia', {})
                    f.write(f"- **{mov.get('descripcion', '')[:50]}...** → {decision.get('tipo')} | {decision.get('categoria')} (conf: {decision.get('confianza', 0):.2f})\n")
                
                f.write(f"""

### ⚠️ Movimientos con Baja Confianza (< 0.5)
**Total: {len(baja_confianza)} movimientos**

""")
                
                for mov in baja_confianza[:10]:  # Top 10 problemas
                    decision = mov.get('decision_ia', {})
                    f.write(f"- **{mov.get('descripcion', '')[:50]}...** → {decision.get('tipo')} | {decision.get('categoria')} (conf: {decision.get('confianza', 0):.2f})\n")
                
                f.write(f"""

## Recomendaciones

### Para mejorar la IA:
1. **Prompts más específicos** para descripciones ambiguas
2. **Contexto adicional** sobre patrones recurrentes  
3. **Feedback manual** en movimientos de baja confianza

### Archivos generados:
- **Respuestas detalladas**: `{self.log_respuestas.name}`
- **Este reporte**: `{self.log_evaluacion.name}`

---
*Generado automáticamente por DeepSeek Client v0.8.3*
""")
            
            print(f"{Colors.OKGREEN}📊 Reporte de evaluación generado: {self.log_evaluacion.name}{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.WARNING}⚠️  Error generando reporte: {e}{Colors.ENDC}")


# Función de utilidad para testing
def test_deepseek_client():
    """Prueba básica del cliente DeepSeek"""
    print(f"{Colors.HEADER}=== Test Cliente DeepSeek ==={Colors.ENDC}")
    
    cliente = DeepSeekClient(test_mode=True)
    
    # Test conectividad
    if not cliente.verificar_conectividad():
        return False
    
    # Test procesamiento
    movimiento_test = {
        'fecha': '2025-07-30',
        'descripcion': 'Pago TDC Banamex Costco',
        'monto': -2036.49,
        'referencia_bancaria': '0076312440'
    }
    
    resultado = cliente.procesar_movimiento(movimiento_test)
    
    if resultado:
        print(f"{Colors.OKGREEN}✓ Test exitoso{Colors.ENDC}")
        print(f"Resultado: {json.dumps(resultado, indent=2, ensure_ascii=False)}")
        return True
    else:
        print(f"{Colors.FAIL}✗ Test fallido{Colors.ENDC}")
        return False


if __name__ == "__main__":
    test_deepseek_client()
# 🤖 FLUJO DE TRABAJO DEEPSEEK V2 - SISTEMA DE INTELIGENCIA ARTIFICIAL FINANCIERA

## 📋 IDENTIFICACIÓN DEL SISTEMA "DEEPSEEKV2"

El sistema que mencionas como "deepseekv2" corresponde al **Sistema de Inteligencia Artificial con Memoria Permanente** desarrollado en la versión 0.8.4. Este NO es un script único, sino un **ecosistema de 4 scripts interconectados** que forman el pipeline completo de procesamiento inteligente de movimientos bancarios.

### 🧠 COMPONENTES DEL ECOSISTEMA DEEPSEEK V2

| Script | Función Principal | Descripción |
|--------|------------------|-------------|
| `deepseek_client.py` | Cliente API DeepSeek | Comunicación con IA para clasificación automática |
| `sistema_memoria.py` | Motor de Aprendizaje | Gestión de patrones y memoria permanente |
| `detector_patrones.py` | Detector Inteligente | Análisis de patrones con memoria contextual |
| `procesar_xlsx_bbva.py` | Procesador Principal | Orquestador del pipeline completo |
| `importar_movimientos_bbva.py` | Importador a BD | Persistencia en base de datos Django |

---

## 🔄 ORDEN DE EJECUCIÓN RECOMENDADO

### 📝 FASE 1: PREPARACIÓN Y CONFIGURACIÓN

#### 1.1 Verificar Entorno
```bash
# Activar entorno virtual
source venv/bin/activate

# Verificar credenciales DeepSeek en .env
grep DEEPSEEK_API_KEY ../.env

# Si no existe, agregar:
echo "DEEPSEEK_API_KEY=tu_api_key_aqui" >> ../.env
```

#### 1.2 Test de Conectividad
```bash
# Test básico del cliente DeepSeek
python deepseek_client.py

# Esperado: "✓ Test exitoso" con clasificación de ejemplo
```

### 🧪 FASE 2: PRIMERA EJECUCIÓN (MODO TEST)

#### 2.1 Procesamiento con Datos Falsos (Sin API)
```bash
# Procesar archivo Excel en modo test (sin consumir API)
python procesar_xlsx_bbva.py ruta/archivo.xlsx --test --lote 10

# Esperado:
# - ✓ Lectura exitosa del Excel
# - ✓ Conversión a JSON sin errores
# - ✓ Clasificación con lógica básica (test mode)
# - 📁 Archivo output/movimientos_procesados_YYYYMMDD_HHMMSS.json
```

#### 2.2 Importación Test (Sin Tocar BD)
```bash
# Importar movimientos en modo test
python importar_movimientos_bbva.py output/movimientos_procesados_*.json --test

# Esperado:
# - ✓ Validación de movimientos
# - ✓ Simulación de importación
# - ⚠️ Sin persistencia en BD (modo test)
```

### 🚀 FASE 3: EJECUCIÓN REAL CON IA

#### 3.1 Primer Lote Pequeño (5-10 movimientos)
```bash
# Procesar con IA real - lote pequeño
python procesar_xlsx_bbva.py ruta/archivo.xlsx --lote 5

# Esperado:
# - 🤖 Llamadas reales a DeepSeek API
# - ⏱️ 10-15 segundos por movimiento
# - 📊 Confianza 85-95% en clasificaciones
# - 🧠 Creación de memoria permanente inicial
```

#### 3.2 Importación Real a Base de Datos
```bash
# Importar movimientos procesados por IA
python importar_movimientos_bbva.py output/movimientos_procesados_*.json

# Modos disponibles:
# --interactivo : Revisar cada movimiento individualmente
# --masivo      : Importación automática con confirmación única
```

### 📈 FASE 4: PROCESAMIENTO MASIVO INTELIGENTE

#### 4.1 Lotes Incrementales
```bash
# Lote mediano (aprovechando memoria existente)
python procesar_xlsx_bbva.py ruta/archivo.xlsx --lote 25

# Lote grande (memoria madura)
python procesar_xlsx_bbva.py ruta/archivo.xlsx --lote 50
```

#### 4.2 Monitoreo de Evolución
```bash
# Revisar logs de aprendizaje
ls -la logs/
# - patrones_detectados_*.md
# - deepseek_respuestas_*.md  
# - evaluacion_ia_*.md

# Revisar memoria permanente
ls -la memoria/
# - memoria_permanente.json (patrones aprendidos)
# - backup_*.json (respaldos automáticos)
```

---

## 🧠 FUNCIONAMIENTO INTERNO DETALLADO

### 🔄 PIPELINE DE PROCESAMIENTO EVOLUTIVO

```
📊 ARCHIVO EXCEL
    ↓
🔍 LECTURA Y VALIDACIÓN (procesar_xlsx_bbva.py)
    ↓
🧠 CONSULTA MEMORIA PERMANENTE (sistema_memoria.py)
    ↓
❓ ¿PATRÓN CONOCIDO CON CONFIANZA ≥85%?
    ↓
    ├─ SÍ → ⚡ CLASIFICACIÓN INSTANTÁNEA
    │         ↓
    │       🔄 ACTUALIZAR CONFIANZA (+2%)
    │         ↓
    └─ NO  → 🤖 CONSULTAR DEEPSEEK API (deepseek_client.py)
              ↓
            📝 PROCESAR RESPUESTA IA
              ↓
            🧠 GUARDAR NUEVO PATRÓN (detector_patrones.py)
              ↓
            💾 ACTUALIZAR MEMORIA PERMANENTE
              ↓
📄 ARCHIVO JSON ENRIQUECIDO
    ↓
🗄️ IMPORTACIÓN A BASE DE DATOS (importar_movimientos_bbva.py)
```

### 🎯 TIPOS DE DETECCIÓN DE PATRONES

| Tipo | Criterio | Ejemplo |
|------|----------|---------|
| **Referencias Bancarias** | Número exacto | `ref:0076312440` → TDC BANAMEX COSTCO |
| **Montos Exactos** | Cantidad específica | `$2,036.49` → Pago tarjeta crédito |
| **Rangos de Montos** | Bandas de valores | `$1,000-$3,000` → Pagos tarjetas |
| **Patrones Temporales** | Fechas recurrentes | `Día 15 c/mes` → Nómina |
| **Descripciones** | Texto similar | `"SPEI BANAMEX"` → Transferencias |

### 📊 MÉTRICAS DE EVOLUCIÓN ESPERADAS

#### Primera Sesión (Movimientos 1-10)
- ⏱️ **Tiempo por movimiento**: 10-15 segundos
- 🎯 **Confianza inicial**: 70-85%
- 🧠 **Patrones detectados**: 0-2 nuevos
- 💾 **Memoria**: Creación de estructura base

#### Sesión Intermedia (Movimientos 50-100)
- ⏱️ **Tiempo por movimiento**: 5-8 segundos (50% patrones conocidos)
- 🎯 **Confianza promedio**: 85-92%
- 🧠 **Patrones detectados**: 5-10 patrones maduros
- 💾 **Memoria**: 200-500 ejemplos aprendidos

#### Sesión Madura (Movimientos 200+)
- ⏱️ **Tiempo por movimiento**: 2-3 segundos (80% patrones conocidos)
- 🎯 **Confianza promedio**: 92-98%
- 🧠 **Patrones detectados**: 15-25 patrones consolidados
- 💾 **Memoria**: 1000+ ejemplos, precisión automática

---

## 📂 ESTRUCTURA DE ARCHIVOS GENERADOS

### 📁 Directorio `output/`
```
output/
├── movimientos_procesados_20250811_120000.json  # Datos enriquecidos con IA
├── resumen_procesamiento_20250811_120000.json   # Estadísticas de sesión
└── errores_procesamiento_20250811_120000.log    # Log de errores
```

### 📁 Directorio `logs/`
```
logs/
├── deepseek_respuestas_20250811_120000.md       # Respuestas detalladas de IA
├── evaluacion_ia_20250811_120000.md             # Métricas de calidad
└── patrones_detectados_20250811_120000.md       # Log de aprendizaje
```

### 📁 Directorio `memoria/`
```
memoria/
├── memoria_permanente.json                      # Base de conocimiento
└── backup_20250811.json                         # Respaldo automático
```

---

## 🚨 CASOS DE ERROR Y SOLUCIONES

### ❌ Error: "API Key no configurada"
```bash
# Solución:
echo "DEEPSEEK_API_KEY=tu_api_key_real" >> ../.env
# O usar modo test:
python procesar_xlsx_bbva.py archivo.xlsx --test
```

### ❌ Error: "Timeout API"
```bash
# Solución: Reducir tamaño de lote
python procesar_xlsx_bbva.py archivo.xlsx --lote 5
```

### ❌ Error: "JSON malformado de IA"
```bash
# Solución: El sistema usa fallback automático
# Revisar logs/deepseek_respuestas_*.md para depurar
```

### ❌ Error: "Cuenta no existe en BD"
```bash
# Solución: Usar modo interactivo para crear cuentas
python importar_movimientos_bbva.py archivo.json --interactivo
```

---

## 📈 BENEFICIOS PROGRESIVOS ESPERADOS

### 🎯 Semana 1: Aprendizaje Inicial
- **Ahorro de tiempo**: 60% vs procesamiento manual
- **Precisión**: 75-85% automática + 15-25% revisión manual
- **Patrones**: 5-10 patrones básicos aprendidos

### 🎯 Semana 2-3: Maduración del Sistema
- **Ahorro de tiempo**: 80% vs procesamiento manual
- **Precisión**: 85-95% automática + 5-15% revisión manual
- **Patrones**: 15-25 patrones consolidados

### 🎯 Mes 1+: Sistema Maduro
- **Ahorro de tiempo**: 90-95% vs procesamiento manual
- **Precisión**: 95-98% automática + 2-5% revisión excepcional
- **Patrones**: 25+ patrones con alta confianza

---

## 🔧 COMANDOS DE MANTENIMIENTO

### 📊 Revisar Estado del Sistema
```bash
# Ver estadísticas de memoria
python -c "
from sistema_memoria import MemoriaPatrones
m = MemoriaPatrones()
print(f'Patrones activos: {m.memoria[\"total_patrones_activos\"]}')
print(f'Transacciones aprendidas: {m.memoria[\"total_transacciones_aprendidas\"]}')
"
```

### 🧹 Limpiar Logs Antiguos
```bash
# Mantener solo logs de últimos 30 días
find logs/ -name "*.md" -mtime +30 -delete
find memoria/ -name "backup_*.json" -mtime +30 -delete
```

### 💾 Backup Manual de Memoria
```bash
# Crear backup manual
cp memoria/memoria_permanente.json memoria/backup_manual_$(date +%Y%m%d).json
```

---

## ⚠️ RECOMENDACIONES CRÍTICAS

### 🔒 Seguridad
1. **NUNCA** commitear archivos con credenciales API
2. **SIEMPRE** usar `.env` para credenciales sensibles
3. **REVISAR** logs antes de compartir (pueden contener datos bancarios)

### 🚀 Rendimiento
1. **EMPEZAR** con lotes pequeños (5-10 movimientos)
2. **INCREMENTAR** gradualmente según estabilidad
3. **MONITOREAR** consumo de API para controlar costos

### 🧠 Aprendizaje
1. **NO BORRAR** archivos de memoria sin backup
2. **REVISAR** clasificaciones de baja confianza manualmente
3. **RETROALIMENTAR** errores para mejorar prompts

---

*📝 Documento generado el 11 de Agosto, 2025 | 🤖 Sistema DeepSeek V2 operativo*
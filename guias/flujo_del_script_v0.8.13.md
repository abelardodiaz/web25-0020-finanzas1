# Flujo del Script de Importación BBVA
**Versión:** v0.8.14  
**Commit:** RESUELTO - Sistema de Creación de Entidades desde Opción 3  
**Archivo:** `scripts_cli/importar_movimientos_bbva.py`  
**Fecha:** 12 de Agosto, 2025

## ✅ PROBLEMA RESUELTO

**Solución implementada:** La opción 3 ahora puede crear categorías y cuentas en la BD, eliminando el problema de entidades faltantes al cambiar a opción 2.

---

## 📊 FLUJO ACTUAL DEL SCRIPT

### 1️⃣ **INICIO** (`iniciar()` - Líneas 75-106)
```
1. Inicializa sistema de memoria (SistemaMemoria)
2. Verifica cuenta BBVA 5019
3. Carga archivo JSON (muestra lista, usuario elige)
4. Muestra resumen inicial (50 movimientos)
5. Verifica duplicados iniciales
6. → MENÚ PRINCIPAL
```

### 2️⃣ **MENÚ PRINCIPAL** (`preguntar_modo_masivo()` - Líneas 584-606)
```
OPCIONES DE PROCESAMIENTO:
1. Revisar cada movimiento individualmente
2. Importar todos automáticamente  
3. 👁️ Revisar/editar movimientos antes de importar
4. Salir
```

---

## 🔄 FLUJOS POR OPCIÓN

### **OPCIÓN 1: Revisar individualmente** (`procesar_movimiento_interactivo()`)
```
Para cada movimiento (1-50):
├── Verifica si es duplicado
├── Si es duplicado y modo_duplicados='omitir' → Salta
├── Si no es duplicado:
│   ├── Muestra tabla del movimiento
│   ├── Clasificación IA (si hay sugerencia)
│   ├── Verificación de campos
│   ├── Vista previa contable
│   ├── Confirmación (1=guardar, 2=editar, 3=salir)
│   └── GUARDA en base de datos
└── Continúa con siguiente
```
**Datos:** Lee de `self.movimientos` (lista cargada del JSON)  
**Resultado:** Guarda directamente en BD, aprende patrones

### **OPCIÓN 2: Importar automáticamente** (`procesar_movimiento_automatico()`)
```
Para cada movimiento (1-50):
├── Aplica reglas contables
├── Si encuentra categoría/cuenta inexistente:
│   ├── Muestra contexto del movimiento
│   └── Pide crear o seleccionar existente
└── GUARDA en base de datos
```
**Datos:** Lee de `self.movimientos` (lista cargada del JSON)  
**Resultado:** Guarda directamente en BD

### **OPCIÓN 3: Revisar/editar antes** (`revisar_editar_movimientos()`)
```
Bucle infinito hasta 'listo':
├── Muestra lista de movimientos (primeros 15)
├── Usuario puede:
│   ├── Editar movimiento por número
│   │   └── `editar_campos()`: Modifica en memoria
│   ├── Ver todos paginados
│   ├── 'crear' → Crear entidades faltantes en BD
│   └── 'listo' → Volver al menú
│       └── Si hay cambios, pregunta si crear entidades
└── Las ediciones se guardan en `self.movimientos[num-1]`
```
**Datos:** Modifica `self.movimientos` EN MEMORIA  
**Resultado:** Puede crear categorías/cuentas en BD con `crear_entidades_faltantes()`

---

## ✅ **SOLUCIÓN IMPLEMENTADA**

### Nuevas funcionalidades agregadas:

1. **`crear_entidades_faltantes()`** (Líneas 452-587)
   - Escanea todos los movimientos
   - Identifica categorías y cuentas que no existen en BD
   - Ofrece crearlas automáticamente o selectivamente
   - Asigna tipos inteligentemente (TDC→CRE, etc.)

2. **`verificar_entidades_faltantes_silencioso()`** (Líneas 452-468)
   - Verifica rápidamente si hay entidades faltantes
   - No muestra salida, solo retorna True/False
   - Se usa antes de procesar en modo masivo

3. **Mejoras en Opción 3:**
   - Nueva opción 'crear' para crear entidades en cualquier momento
   - Al salir con cambios, pregunta si crear entidades faltantes
   - Flag `cambios_realizados` rastrea si se editaron movimientos

4. **Mejoras en Opción 2 (modo masivo):**
   - Verifica entidades faltantes antes de procesar
   - Advierte al usuario y recomienda usar Opción 3
   - Permite continuar o volver al menú

### Flujo mejorado:
```
1. Usuario elige Opción 3
2. Edita movimientos (categorías, cuentas, etc.)
3. Escribe 'crear' o al salir elige crear entidades
4. Sistema crea todas las categorías/cuentas en BD
5. Vuelve al menú y elige Opción 2
6. ✅ Procesa sin preguntar nada (todo existe en BD)
```

---

## 📋 **FLUJO DE DATOS**

```
ARCHIVO JSON
    ↓
self.movimientos = json.load()  [Lista en memoria]
    ↓
┌─────────────────────────────────────┐
│ OPCIÓN 1: Procesa y GUARDA en BD   │
│ OPCIÓN 2: Procesa y GUARDA en BD   │
│ OPCIÓN 3: MODIFICA lista en memoria │ ← No guarda en BD
└─────────────────────────────────────┘
    ↓
Si vuelves a Opción 1/2 después de 3:
- Usa la lista modificada
- PERO categorías/cuentas editadas no existen en BD
- Vuelve a preguntar por ellas
```

---

## 🎯 **CONCLUSIÓN**

El flujo ahora está **RESUELTO**:

1. ✅ **Opción 3 es útil** - Permite revisar, editar Y crear entidades en BD
2. ✅ **Las correcciones se preservan** - Los cambios en memoria + entidades en BD
3. ✅ **Flujo eficiente** - Editas una vez, creas entidades, procesas sin interrupciones

### Lo que el usuario esperaba (AHORA FUNCIONA):
- Opción 3: Revisar, corregir TODO, crear entidades necesarias
- Luego Opción 2: Usar las correcciones sin preguntar nada más

### Lo que realmente pasa ahora:
- Opción 3: Corriges todo (en memoria) + creas entidades (en BD)
- Opción 2: Procesa sin interrupciones usando las correcciones

---

## 📌 **MEJORAS IMPLEMENTADAS v0.8.14**

- ✅ **Función `crear_entidades_faltantes()`** - Crea categorías/cuentas desde Opción 3
- ✅ **Verificación proactiva** - Advierte sobre entidades faltantes antes de procesar
- ✅ **Flujo coherente** - Las ediciones en Opción 3 se aprovechan en Opción 2
- ✅ **UX mejorada** - Opciones claras: 'crear', confirmaciones al salir
- ✅ **Help system con 'h'** - Funciona correctamente en todos los contextos

El script ahora tiene un flujo de trabajo coherente donde las correcciones se preservan y aplican correctamente.
# Sistema de Ayuda para Cuentas y Categorías en CLI

## Resumen Ejecutivo

El importador BBVA incluye un sistema de ayuda interactivo que permite:
- Selección rápida por ID numérico
- Visualización organizada de opciones disponibles
- Creación de nuevos elementos sobre la marcha
- Defaults inteligentes basados en nombres

## 1. Sistema de Ayuda para CUENTAS

### Ubicación en el Código
- **Archivo**: `/scripts_cli/importar_movimientos_bbva.py`
- **Función principal cuenta vinculada**: Líneas 499-616
- **Función reutilizable**: `seleccionar_cuenta_con_ayuda()` (Líneas 837-920)
- **Creación de cuenta**: `crear_nueva_cuenta()` (Líneas 934-1018)

### Flujo de Interacción

```
Ingresa cuenta vinculada (nombre/número/9=ayuda/x=cancelar):
```

### Opciones Disponibles

| Opción | Acción |
|--------|--------|
| **9** | Muestra lista completa de cuentas |
| **1-999** | Selección directa por ID |
| **0** | Crear nueva cuenta |
| **x** | Cancelar operación |
| **Texto** | Nombre de cuenta (nueva o existente) |
| **Enter** | Mantener valor actual |

### Visualización de Cuentas

```
============================================================
📚 CUENTAS DISPONIBLES
============================================================

[  1] BBVA PRINCIPAL     | [  8] TDC AMEX GOLD      | [ 15] CFE
[  2] BBVA EURO          | [  9] TDC LIVERPOOL      | [ 16] TELMEX
[  3] SANTANDER          | [ 10] INGRESOS YARIS     | [ 17] IZZI

Total: 17 cuentas
[  0] → Crear nueva cuenta
============================================================
```

### Defaults Inteligentes para Cuentas

El sistema analiza el nombre para sugerir configuración:

| Patrón en Nombre | Naturaleza | Tipo | Medio de Pago |
|-----------------|------------|------|---------------|
| TDC | ACREEDORA | CRE | No |
| TDB/BANCO | DEUDORA | DEB | No |
| INGRESO/RENTA | ACREEDORA | ING | No |
| CFE/TELMEX/IZZI | ACREEDORA | SER | No |
| Otros | DEUDORA | DEB | No |

## 2. Sistema de Ayuda para CATEGORÍAS

### Ubicación en el Código
- **Función principal**: `seleccionar_categoria_con_ayuda()` (Líneas 1004-1088)
- **Visualización**: `_mostrar_categorias_en_columnas()` (Líneas 1090-1105)
- **Creación**: `crear_nueva_categoria()` (Líneas 1107-1146)
- **Verificación**: `verificar_crear_categoria()` (Líneas 965-1002)

### Flujo de Interacción

Cuando una categoría no existe:
```
⚠️  Categoría 'Servicios Básicos' no existe

Opciones disponibles:
1) Crear nueva categoría
2) Seleccionar categoría existente
9) Ver lista de categorías
x) Cancelar

Seleccione (1/2/9/x) [Enter=1]:
```

### Visualización de Categorías

```
============================================================
📁 CATEGORÍAS DISPONIBLES
============================================================

📊 CATEGORÍAS PERSONALES:
[  1] Alimentación               | [  5] Transporte
[  2] Entretenimiento            | [  6] Salud
[  3] Hogar                      | [  7] Educación
[  4] Ropa y Accesorios          | [  8] Otros Gastos

💼 CATEGORÍAS DE NEGOCIO:
[  9] Servicios Profesionales    | [ 12] Marketing
[ 10] Equipamiento               | [ 13] Gastos Operativos
[ 11] Viajes de Negocio          | [ 14] Proyectos 2025

Total: 14 categorías
[  0] → Crear nueva categoría
============================================================
```

### Características de la Visualización

- **Separación por tipo**: Personal vs Negocio
- **Columnas**: 2 columnas para categorías (nombres más largos)
- **Formato**: `[ID] Nombre` con truncado a 25 caracteres
- **Colores distintivos**: Verde para personal, azul para negocio

### Defaults Inteligentes para Categorías

| Palabras Clave | Tipo Default |
|---------------|--------------|
| negocio, empresa, proyecto, cliente | Negocio |
| Otros | Personal |

## 3. Integración en el Flujo de Edición

### Para Categorías en Edición de Campos (Líneas 789-800)
```python
if campo == 'categoria':
    print(f"\n{Colors.OKCYAN}Categoría (nombre/número/9=ayuda/x=mantener):{Colors.ENDC}")
    nuevo_valor = input(f"{nombre} [{valor_actual}]: ").strip()
    
    if nuevo_valor == '9' or (nuevo_valor.isdigit() and nuevo_valor != '0'):
        # Mostrar lista de categorías
        categoria_seleccionada = self.seleccionar_categoria_con_ayuda()
        if categoria_seleccionada:
            movimiento_editado[campo] = categoria_seleccionada.nombre
```

### Para Cuentas en Edición de Campos (Líneas 802-821)
```python
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
```

## 4. Ventajas del Sistema

### Para el Usuario
1. **Rapidez**: Selección por ID evita escribir nombres largos
2. **Visibilidad**: Ve todas las opciones disponibles
3. **Flexibilidad**: Puede crear nuevas sobre la marcha
4. **Intuitivo**: Opciones numéricas consistentes

### Para el Sistema
1. **Consistencia**: Evita duplicados por variaciones de nombres
2. **Organización**: Mantiene estructura clara de datos
3. **Escalabilidad**: Funciona bien con muchas opciones
4. **Mantenibilidad**: Código modular y reutilizable

## 5. Ejemplos de Uso

### Ejemplo 1: Selección Rápida por ID
```
Categoría (nombre/número/9=ayuda/x=mantener):
Categoría [Servicios Básicos]: 9
[Lista de categorías...]
Tu elección: 12
✓ Seleccionaste: Marketing
```

### Ejemplo 1b: Edición de Cuenta Destino con Ayuda
```
Editar campos (Enter para mantener valor actual):
Descripción [SISTEMAS Y SERVICIOS      / GUIA:2111649    REF:5390392]:
Monto [-765.77]:

Cuenta Origen (nombre/número/9=ayuda/x=mantener):
Cuenta Origen [TDB BBVA 5019]: 

Cuenta Vinculada (nombre/número/9=ayuda/x=mantener):
Cuenta Destino [None]: 9

============================================================
📚 CUENTAS DISPONIBLES
============================================================

[  1] BBVA PRINCIPAL     | [  8] TDC AMEX GOLD      | [ 15] CFE
[  2] BBVA EURO          | [  9] TDC LIVERPOOL      | [ 16] TELMEX
[  3] SANTANDER          | [ 10] INGRESOS YARIS     | [ 17] IZZI

Total: 17 cuentas
[  0] → Crear nueva cuenta
============================================================

Tu elección: 0
Nombre de la nueva cuenta: COMPRAS PROY 180 FIBRA
```

### Ejemplo 2: Creación de Nueva Categoría
```
Categoría (nombre/número/9=ayuda/x=mantener):
Categoría []: Compras Proyectos 2025

⚠️  Categoría 'Compras Proyectos 2025' no existe

Opciones disponibles:
1) Crear nueva categoría
[Enter presionado]

═══ Nueva Categoría: Compras Proyectos 2025 ═══

Tipo de categoría (default: Negocio):
1) Personal
2) Negocio
[Enter presionado]

✓ Nueva categoría creada exitosamente!
  Nombre: Compras Proyectos 2025
  Tipo: Negocio
```

### Ejemplo 3: Navegación con Ayuda
```
Ingresa cuenta vinculada (nombre/número/9=ayuda/x=cancelar):
Cuenta Destino []: 9
[Lista de cuentas...]

OPCIONES:
• Escribe el NÚMERO de la cuenta que eliges
• Escribe '0' para crear cuenta nueva
• Escribe '9' para ver la lista otra vez
• Escribe 'x' para cancelar

Tu elección: 15
✓ Seleccionaste: CFE
```

## 6. Detalles Técnicos

### Estructura de Datos

```python
# Diccionario para búsqueda rápida de cuentas
cuentas_dict = {}
for cuenta in cuentas:
    cuentas_dict[cuenta.id] = cuenta.nombre

# Diccionario para categorías
categorias_dict = {}
for cat in categorias:
    categorias_dict[cat.id] = cat
```

### Formato de Visualización

```python
# Cuentas: 3 columnas, 18 caracteres
f"[{cuenta.id:3}] {cuenta.nombre[:18]:<18}"

# Categorías: 2 columnas, 25 caracteres
f"[{cat.id:3}] {cat.nombre[:25]:<25}"
```

### Manejo de Errores

- IDs inválidos muestran mensaje de error
- Excepciones capturadas con logging
- Fallback a entrada manual si falla la lista

## 7. Evolución del Sistema

### Versión Original
- Solo entrada de texto libre
- Sin visualización de opciones
- Confirmación s/n para crear

### Versión v0.8.8 (Actual)
- Sistema de IDs numéricos
- Visualización organizada
- Ayuda contextual con opción 9
- Defaults inteligentes
- Confirmaciones numéricas (1/2)

## 8. Mejoras Futuras Potenciales

1. **Búsqueda por texto**: Filtrar opciones mientras se escribe
2. **Favoritos**: Marcar elementos más usados
3. **Historial**: Recordar últimas selecciones
4. **Autocompletado**: Sugerir basado en patrones previos
5. **Agrupación avanzada**: Por frecuencia de uso o fecha

## Conclusión

El sistema de ayuda transforma la experiencia de usuario del importador BBVA, haciendo que la selección de cuentas y categorías sea:
- **Rápida**: Por IDs numéricos
- **Visual**: Con listas organizadas
- **Flexible**: Creación sobre la marcha
- **Inteligente**: Con defaults apropiados

Este enfoque reduce errores, mejora la consistencia de datos y hace el proceso más eficiente para el usuario.
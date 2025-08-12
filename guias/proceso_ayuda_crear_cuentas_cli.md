# Proceso de Ayuda para Crear Cuentas en CLI

## Ubicación del Sistema de Ayuda

El sistema de ayuda para la creación de cuentas se implementó en el archivo:
- **Archivo**: `/scripts_cli/importar_movimientos_bbva.py`
- **Líneas**: 499-616 (selección de cuenta vinculada con ayuda)
- **Líneas**: 818-849 (creación de nueva cuenta con defaults inteligentes)

## Características Principales

### 1. Sistema de Selección con Números (Líneas 499-616)

#### Flujo de Interacción
```
Ingresa cuenta vinculada (nombre/número/9=ayuda/x=cancelar):
```

#### Opciones Disponibles:
- **9**: Muestra lista completa de cuentas disponibles
- **Número (1-999)**: Selección directa por ID de cuenta
- **0**: Crear nueva cuenta
- **x**: Cancelar operación
- **Texto**: Nombre de cuenta nueva o existente
- **Enter**: Mantener valor actual

### 2. Visualización de Cuentas en 3 Columnas (Líneas 525-543)

El sistema muestra todas las cuentas disponibles en formato tabular:

```python
# Formato de visualización
[ID] Nombre_Cuenta (máx 18 caracteres)

# Ejemplo de salida:
[  1] BBVA PRINCIPAL     | [  8] TDC AMEX GOLD      | [ 15] CFE
[  2] BBVA EURO          | [  9] TDC LIVERPOOL      | [ 16] TELMEX
[  3] SANTANDER          | [ 10] INGRESOS YARIS     | [ 17] IZZI
```

#### Características de la Lista:
- Organización en 3 columnas para mejor visualización
- IDs numéricos para selección rápida
- Nombres truncados a 18 caracteres
- Total de cuentas disponibles al final
- Opción especial `[0] → Crear nueva cuenta` resaltada

### 3. Proceso de Selección Interactivo

#### Después de mostrar la lista (líneas 557-563):
```
OPCIONES:
• Escribe el NOMBRE de la cuenta nueva
• Escribe el NÚMERO de la cuenta que eliges
• Escribe '0' para crear cuenta nueva
• Escribe '9' para ver la lista otra vez
• Escribe 'x' para cancelar
```

### 4. Creación de Nueva Cuenta con Defaults Inteligentes (Líneas 818-849)

#### Sistema de Defaults Automáticos:

El sistema analiza el nombre de la cuenta para sugerir configuración apropiada:

```python
# Tarjetas de Crédito (TDC en el nombre)
if 'TDC' in nombre_upper:
    naturaleza_default = 'ACREEDORA'
    tipo_default = 'CRE'

# Cuentas Bancarias (TDB o BANCO en el nombre)
elif 'TDB' in nombre_upper or 'BANCO' in nombre_upper:
    naturaleza_default = 'DEUDORA'
    tipo_default = 'DEB'

# Cuentas de Ingresos
elif 'INGRESO' in nombre_upper or 'RENTA' in nombre_upper:
    naturaleza_default = 'ACREEDORA'
    tipo_default = 'ING'

# Servicios (CFE, TELMEX, IZZI, etc.)
elif any(serv in nombre_upper for serv in ['CFE', 'TELMEX', 'IZZI', 'TOTALPLAY', 'GAS']):
    naturaleza_default = 'ACREEDORA'
    tipo_default = 'SER'

# Default general
else:
    naturaleza_default = 'DEUDORA'
    tipo_default = 'DEB'
```

### 5. Ayuda Contextual para Naturaleza (Líneas 735-782)

Cuando el usuario selecciona la opción 3 para ayuda sobre naturaleza:

```
📚 ENTENDIENDO LA NATURALEZA DE LAS CUENTAS

En términos simples:

🔵 DEUDORA (Lo que TIENES):
   • Cuentas bancarias de débito
   • Efectivo
   • Propiedades
   • Lo que otros te deben
   → AUMENTA con CARGOS, DISMINUYE con ABONOS

🔴 ACREEDORA (Lo que DEBES o GANAS):
   • Tarjetas de crédito
   • Préstamos
   • Servicios por pagar
   • Ingresos/Ventas
   → AUMENTA con ABONOS, DISMINUYE con CARGOS
```

## Ventajas del Sistema

1. **Accesibilidad**: El usuario puede escribir `9` en cualquier momento para ver las cuentas
2. **Rapidez**: Selección directa por ID numérico
3. **Flexibilidad**: Permite crear cuentas nuevas sobre la marcha
4. **Inteligencia**: Sugiere configuraciones basadas en el nombre
5. **Claridad**: Explicaciones en español simple sin jerga contable

## Flujo de Trabajo Típico

1. Usuario necesita seleccionar una cuenta
2. Escribe `9` para ver lista de cuentas
3. Ve todas las cuentas con sus IDs
4. Puede:
   - Escribir el ID para selección rápida
   - Escribir `0` para crear nueva
   - Escribir el nombre directamente
   - Cancelar con `x`

## Implementación Técnica

### Diccionario de Búsqueda Rápida
```python
cuentas_dict = {}
for cuenta in cuentas:
    cuentas_dict[cuenta.id] = cuenta.nombre
```

### Validación de Selección
```python
if opcion_num != 9 and opcion_num > 0 and opcion_num in cuentas_dict:
    nombre_seleccionado = cuentas_dict[opcion_num]
    movimiento_editado['cuenta_destino'] = nombre_seleccionado
```

## Notas de Implementación

- El sistema usa Django ORM para obtener las cuentas: `Cuenta.objects.all().order_by('id')`
- Los IDs se formatean con 3 dígitos para alineación: `f"[{cuenta.id:3}]"`
- Los nombres se truncan para mantener el formato tabular: `cuenta.nombre[:18]`
- Se mantiene consistencia con el resto del CLI usando códigos de color ANSI
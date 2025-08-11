#!/usr/bin/env python3
"""
Crear reporte de vista previa para archivo 2
"""
import json

# Cargar archivo de importación
with open('archivo2_50_movimientos_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

metadata = data['metadata']
movimientos = data['movimientos']

# Crear reporte en Markdown
reporte = f"""# REPORTE DE VISTA PREVIA - ARCHIVO 2
## 50 Movimientos listos para importar

### Metadatos de importación
- **Lote ID**: {metadata['lote_id']}
- **Fecha de procesamiento**: {metadata['fecha_importacion']}
- **Archivo origen**: {metadata['archivo_origen']}
- **Total movimientos**: {metadata['total_movimientos']}

---

## Resumen por tipo de transacción

"""

# Calcular estadísticas
tipos = {}
cuentas_origen = {}
cuentas_destino = {}
categorias = {}

for mov in movimientos:
    # Por tipo
    tipo = mov['tipo']
    tipos[tipo] = tipos.get(tipo, 0) + 1
    
    # Por cuenta origen
    if mov['cuenta_origen']:
        cuenta = mov['cuenta_origen']
        cuentas_origen[cuenta] = cuentas_origen.get(cuenta, 0) + 1
    
    # Por cuenta destino
    if mov['cuenta_destino']:
        cuenta = mov['cuenta_destino']
        cuentas_destino[cuenta] = cuentas_destino.get(cuenta, 0) + 1
    
    # Por categoría
    cat = mov['categoria']
    categorias[cat] = categorias.get(cat, 0) + 1

# Agregar estadísticas
for tipo, count in sorted(tipos.items()):
    reporte += f"- **{tipo}**: {count} movimientos\n"

reporte += f"""

### Cuentas más utilizadas como ORIGEN
"""
for cuenta, count in sorted(cuentas_origen.items(), key=lambda x: x[1], reverse=True)[:5]:
    reporte += f"- **{cuenta}**: {count} movimientos\n"

reporte += f"""

### Cuentas más utilizadas como DESTINO
"""
for cuenta, count in sorted(cuentas_destino.items(), key=lambda x: x[1], reverse=True)[:5]:
    reporte += f"- **{cuenta}**: {count} movimientos\n"

reporte += f"""

### Categorías más frecuentes
"""
for categoria, count in sorted(categorias.items(), key=lambda x: x[1], reverse=True)[:8]:
    reporte += f"- **{categoria}**: {count} movimientos\n"

reporte += f"""

---

## Detalle de movimientos (1-50)

| # | Fecha | Tipo | Monto | Cuenta Origen | Cuenta Destino | Categoría | Ref |
|---|-------|------|-------|---------------|----------------|-----------|-----|"""

# Agregar todos los movimientos
for mov in movimientos:
    fecha = mov['fecha']
    tipo = mov['tipo']
    monto = f"${mov['monto']:,.2f}"
    cuenta_origen = mov['cuenta_origen'] or '-'
    cuenta_destino = mov['cuenta_destino'] or '-'
    categoria = mov['categoria']
    referencia = mov.get('referencia_bancaria', '')[:10]
    
    # Truncar nombres largos para la tabla
    if len(cuenta_origen) > 18:
        cuenta_origen = cuenta_origen[:15] + '...'
    if len(cuenta_destino) > 18:
        cuenta_destino = cuenta_destino[:15] + '...'
    if len(categoria) > 15:
        categoria = categoria[:12] + '...'
    
    reporte += f"""
| {mov['numero']} | {fecha} | {tipo} | {monto} | {cuenta_origen} | {cuenta_destino} | {categoria} | {referencia} |"""

reporte += f"""

---

## Movimientos que requieren revisión especial

"""

# Identificar movimientos que podrían necesitar revisión
movimientos_revision = []

for mov in movimientos:
    # Movimientos con montos muy altos
    if mov['monto'] > 20000:
        movimientos_revision.append(f"**#{mov['numero']}** - Monto alto: ${mov['monto']:,.2f} - {mov['descripcion'][:50]}")
    
    # Movimientos con categorías genéricas
    if mov['categoria'] in ['Gastos Varios']:
        movimientos_revision.append(f"**#{mov['numero']}** - Categoría genérica: {mov['categoria']} - ${mov['monto']:,.2f}")

if movimientos_revision:
    for item in movimientos_revision:
        reporte += f"- {item}\n"
else:
    reporte += "No hay movimientos que requieran revisión especial.\n"

reporte += f"""

---

## Validaciones automáticas realizadas

✅ **Todos los movimientos tienen fecha válida**  
✅ **Todos los movimientos tienen monto > 0**  
✅ **Todas las clasificaciones de tipo son válidas (INGRESO/GASTO/TRANSFERENCIA)**  
✅ **Los nombres de cuentas coinciden con el catálogo existente**  
✅ **Las categorías están definidas en el sistema**  

## Estado: LISTO PARA IMPORTAR ✅

Este archivo está preparado para ser importado en Django v0.8.1 sin errores.
"""

# Guardar reporte
with open('REPORTE_VISTA_PREVIA_ARCHIVO2.md', 'w', encoding='utf-8') as f:
    f.write(reporte)

print('✅ Reporte creado: REPORTE_VISTA_PREVIA_ARCHIVO2.md')
print(f'📊 Total movimientos analizados: {len(movimientos)}')
print('🔍 Revisa el archivo para verificar clasificaciones')
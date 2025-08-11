#!/usr/bin/env python3
"""
Script para crear archivo de importación con 50 movimientos del archivo 2
Combina los 40 ya clasificados + 10 nuevos sin clasificar
"""
import json
from datetime import datetime

# Cargar los 40 movimientos ya clasificados
with open('archivo2_50_movimientos.json', 'r', encoding='utf-8') as f:
    data_clasificados = json.load(f)
    movs_clasificados = data_clasificados['movimientos']

print(f"Movimientos ya clasificados: {len(movs_clasificados)}")

# Cargar los 50 movimientos raw
with open('archivo2_50_movimientos_raw.json', 'r', encoding='utf-8') as f:
    data_raw = json.load(f)
    movs_raw = data_raw['movimientos']

print(f"Movimientos raw totales: {len(movs_raw)}")

# Los últimos 10 movimientos necesitan clasificación manual
movs_por_clasificar = movs_raw[40:50]

print("\n🔍 MOVIMIENTOS POR CLASIFICAR (41-50):")
print("="*60)

nuevos_clasificados = []

for i, mov in enumerate(movs_por_clasificar, 41):
    print(f"\n#{i} - {mov['fecha']} - {mov['tipo_movimiento']} ${mov['monto']:.2f}")
    print(f"Descripción: {mov['descripcion_original'][:80]}")
    
    # Clasificación automática básica
    desc = mov['descripcion_original'].upper()
    tipo_mov = mov['tipo_movimiento']
    
    if tipo_mov == 'CARGO':
        cuenta_origen = "TDB BBVA 5019"
        if 'BANORTE' in desc:
            cuenta_destino = "TDB BANORTE 3172"
            categoria = "Transferencias Entre Cuentas"
            tipo = "TRANSFERENCIA"
        elif 'CONSUBANCO' in desc:
            cuenta_destino = "TDB UBER PRO CONSUBANCO"
            categoria = "Ingresos Yaris"
            tipo = "TRANSFERENCIA"
        elif 'SAT' in desc:
            cuenta_destino = None
            categoria = "Impuestos"
            tipo = "GASTO"
        else:
            cuenta_destino = None
            categoria = "Gastos Varios"
            tipo = "GASTO"
    else:  # ABONO
        cuenta_destino = "TDB BBVA 5019"
        if 'SPIN BY OXXO' in desc or 'OXXO' in desc:
            cuenta_origen = "TDB SPIN OXXO 2113"
            categoria = "Transferencias Entre Cuentas"
            tipo = "TRANSFERENCIA"
        elif 'CONSUBANCO' in desc:
            cuenta_origen = "TDB UBER PRO CONSUBANCO"
            categoria = "Ingresos Yaris"
            tipo = "INGRESO"
        elif 'SANTANDER' in desc:
            cuenta_origen = "Ingresos ISP"
            categoria = "Ingresos ISP"
            tipo = "INGRESO"
        elif 'BANORTE' in desc:
            cuenta_origen = "Ingresos ISP"
            categoria = "Ingresos ISP"
            tipo = "INGRESO"
        else:
            cuenta_origen = "Ingresos ISP"
            categoria = "Ingresos ISP"
            tipo = "INGRESO"
    
    # Extraer referencia
    ref_bancaria = ""
    if '/' in desc:
        parts = desc.split('/')
        if len(parts) > 1:
            ref_part = parts[1].strip().split()[0]
            ref_bancaria = ref_part
    
    nuevo_mov = {
        'numero': i,
        'monto': float(mov['monto']),
        'fecha': mov['fecha'],
        'descripcion': f"Mov #{i} - {mov['descripcion_original'][:60]}",
        'cuenta_origen': cuenta_origen,
        'cuenta_destino': cuenta_destino,
        'categoria': categoria,
        'tipo': tipo,
        'ajuste': False,
        'estado': 'PENDIENTE',
        'referencia_bancaria': ref_bancaria,
        'referencia_bbva': mov['descripcion_original'],
        'archivo_origen': 'movimientos (2).xlsx'
    }
    
    nuevos_clasificados.append(nuevo_mov)
    print(f"  → Clasificado como: {tipo} - {categoria}")

# Combinar todos los movimientos
todos_movimientos = movs_clasificados + nuevos_clasificados

# Renumerar
for i, mov in enumerate(todos_movimientos, 1):
    mov['numero'] = i

print(f"\n✅ Total movimientos listos: {len(todos_movimientos)}")

# Crear archivo final
resultado = {
    'metadata': {
        'lote_id': f'BBVA5019_20250810_ARCHIVO2_50MOV_COMPLETO',
        'fecha_importacion': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'usuario_importacion': 'admin',
        'total_movimientos': len(todos_movimientos),
        'archivo_origen': 'movimientos (2).xlsx - 50 movimientos completos',
        'estado_importacion': 'LISTO_PARA_IMPORTAR'
    },
    'movimientos': todos_movimientos
}

# Guardar archivo final
with open('archivo2_50_movimientos_final.json', 'w', encoding='utf-8') as f:
    json.dump(resultado, f, indent=2, ensure_ascii=False)

print(f"\n🎉 Archivo archivo2_50_movimientos_final.json creado")
print(f"   Total: {len(todos_movimientos)} movimientos")

# Resumen por tipo
tipos = {}
for m in todos_movimientos:
    tipo = m['tipo']
    tipos[tipo] = tipos.get(tipo, 0) + 1

print("\n📊 RESUMEN POR TIPO:")
for tipo, count in tipos.items():
    print(f"  - {tipo}: {count} movimientos")
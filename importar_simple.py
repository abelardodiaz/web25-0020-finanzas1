#!/usr/bin/env python3
"""Script simple para importar los 12 movimientos"""
import json
import os
import django
from datetime import datetime
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Transaccion, Cuenta, Categoria, TransaccionTipo

# Cargar JSON
with open('primeros_12_para_importar_corregido.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

movimientos = data['movimientos']
print(f"Importando {len(movimientos)} movimientos...")

for i, mov in enumerate(movimientos, 1):
    # Buscar cuentas
    cuenta_origen = Cuenta.objects.filter(nombre=mov['cuenta_origen']).first() if mov['cuenta_origen'] else None
    cuenta_destino = Cuenta.objects.filter(nombre=mov['cuenta_destino']).first() if mov['cuenta_destino'] else None
    categoria = Categoria.objects.filter(nombre=mov['categoria']).first() if mov['categoria'] else None
    
    # Mapear tipo
    tipo_map = {'INGRESO': TransaccionTipo.INGRESO, 'GASTO': TransaccionTipo.GASTO, 'TRANSFERENCIA': TransaccionTipo.TRANSFERENCIA}
    tipo = tipo_map.get(mov['tipo'], TransaccionTipo.GASTO)
    
    # Crear transacción
    t = Transaccion.objects.create(
        monto=Decimal(str(mov['monto'])),
        fecha=datetime.strptime(mov['fecha'], '%Y-%m-%d').date(),
        descripcion=mov['descripcion'],
        cuenta_origen=cuenta_origen,
        cuenta_destino=cuenta_destino,
        categoria=categoria,
        tipo=tipo,
        ajuste=mov.get('ajuste', False)
    )
    
    print(f"{i}. ID {t.id} - ${t.monto} - {t.descripcion[:40]}...")

print(f"\n✅ {len(movimientos)} movimientos importados!")
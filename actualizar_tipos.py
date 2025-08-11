#!/usr/bin/env python3
"""Script para actualizar tipos de transacción"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Transaccion

print("=== ACTUALIZANDO TIPOS DE TRANSACCIÓN ===")

for t in Transaccion.objects.all():
    tipo_anterior = t.tipo
    
    # Aplicar nueva lógica
    if t.cuenta_origen and t.cuenta_origen.tipo.codigo == 'ING':
        nuevo_tipo = 'INGRESO'
    elif t.cuenta_origen and t.cuenta_destino:
        origen_es_banco = t.cuenta_origen.tipo.codigo in ['DEB', 'CRE'] 
        destino_es_banco = t.cuenta_destino.tipo.codigo in ['DEB', 'CRE']
        
        if origen_es_banco and destino_es_banco:
            nuevo_tipo = 'TRANSFERENCIA'
        elif origen_es_banco and t.cuenta_destino.tipo.codigo in ['CRE', 'SER']:
            nuevo_tipo = 'GASTO'
        else:
            nuevo_tipo = 'TRANSFERENCIA' 
    elif t.categoria:
        if t.categoria.tipo in ['PERSONAL', 'NEGOCIO']:
            nuevo_tipo = 'GASTO'
        else:
            nuevo_tipo = 'INGRESO'
    else:
        nuevo_tipo = t.tipo  # Mantener actual
    
    # Actualizar sin activar save() para evitar crear nuevos asientos
    if tipo_anterior != nuevo_tipo:
        Transaccion.objects.filter(id=t.id).update(tipo=nuevo_tipo)
        print(f"ID {t.id}: {tipo_anterior} → {nuevo_tipo} | {t.descripcion[:40]}...")

print("\n✅ Tipos actualizados correctamente")
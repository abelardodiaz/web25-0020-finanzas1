#!/usr/bin/env python3
"""
Script para importar los primeros 12 movimientos a Django v0.8.1
Ejecutar: python manage.py shell < importar_primeros_12.py
"""
import json
import os
import django
from datetime import datetime
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Transaccion, Cuenta, Categoria, TransaccionTipo

def importar_movimientos():
    print("🚀 IMPORTANDO PRIMEROS 12 MOVIMIENTOS...")
    
    # Cargar JSON corregido
    with open('primeros_12_para_importar_corregido.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    movimientos = data['movimientos']
    print(f"📁 Movimientos a importar: {len(movimientos)}")
    
    importados = 0
    errores = []
    
    for i, mov_data in enumerate(movimientos, 1):
        try:
            print(f"\n--- PROCESANDO MOVIMIENTO {i} ---")
            print(f"Descripción: {mov_data['descripcion']}")
            print(f"Monto: ${mov_data['monto']:,.2f}")
            
            # Buscar cuentas por nombre
            cuenta_origen = None
            cuenta_destino = None
            
            if mov_data['cuenta_origen']:
                cuenta_origen = Cuenta.objects.filter(nombre=mov_data['cuenta_origen']).first()
                if not cuenta_origen:
                    print(f"⚠️  CUENTA ORIGEN NO ENCONTRADA: {mov_data['cuenta_origen']}")
            
            if mov_data['cuenta_destino']:
                cuenta_destino = Cuenta.objects.filter(nombre=mov_data['cuenta_destino']).first()
                if not cuenta_destino:
                    print(f"⚠️  CUENTA DESTINO NO ENCONTRADA: {mov_data['cuenta_destino']}")
            
            # Buscar categoría por nombre
            categoria = None
            if mov_data['categoria']:
                categoria = Categoria.objects.filter(nombre=mov_data['categoria']).first()
                if not categoria:
                    print(f"⚠️  CATEGORÍA NO ENCONTRADA: {mov_data['categoria']}")
            
            # Mapear tipo de transacción
            tipo_map = {
                'INGRESO': TransaccionTipo.INGRESO,
                'GASTO': TransaccionTipo.GASTO,
                'TRANSFERENCIA': TransaccionTipo.TRANSFERENCIA
            }
            
            tipo = tipo_map.get(mov_data['tipo'], TransaccionTipo.GASTO)
            
            # Crear transacción
            transaccion = Transaccion(
                monto=Decimal(str(mov_data['monto'])),
                fecha=datetime.strptime(mov_data['fecha'], '%Y-%m-%d').date(),
                descripcion=mov_data['descripcion'],
                cuenta_origen=cuenta_origen,
                cuenta_destino=cuenta_destino,
                categoria=categoria,
                tipo=tipo,
                ajuste=mov_data.get('ajuste', False)
            )
            
            # Validar antes de guardar
            transaccion.full_clean()
            transaccion.save()
            
            print(f"✅ IMPORTADO: ID {transaccion.id}")
            importados += 1
            
        except Exception as e:
            error_msg = f"Movimiento {i}: {str(e)}"
            print(f"❌ ERROR: {error_msg}")
            errores.append(error_msg)
    
    # Resumen final
    print(f"\n{'='*50}")
    print(f"🎯 RESUMEN IMPORTACIÓN")
    print(f"{'='*50}")
    print(f"✅ Movimientos importados: {importados}")
    print(f"❌ Errores: {len(errores)}")
    
    if errores:
        print(f"\n🔍 DETALLE DE ERRORES:")
        for error in errores:
            print(f"   - {error}")
    
    return importados, errores

if __name__ == "__main__":
    importados, errores = importar_movimientos()
    
    if importados > 0:
        print(f"\n🎉 IMPORTACIÓN COMPLETADA!")
        print(f"   Total importados: {importados}")
    else:
        print(f"\n💥 IMPORTACIÓN FALLÓ")
        print(f"   Revisa errores arriba")
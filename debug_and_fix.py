#!/usr/bin/env python
"""
Script para debuggear y corregir el problema de balance
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from collections import defaultdict
from django.db import transaction
from core.models import Transaccion

def main():
    print("🐛 DEBUG Y CORRECCIÓN DEL GRUPO PROBLEMÁTICO")
    print("=" * 60)
    
    # Encontrar el grupo problemático
    grupos = defaultdict(list)
    for trans in Transaccion.objects.all():
        grupos[trans.grupo_uuid].append(trans)
    
    grupo_problematico = None
    for grupo_uuid, transacciones in grupos.items():
        total = sum(t.monto for t in transacciones)
        if total != 0 and len(transacciones) > 1:
            grupo_problematico = (grupo_uuid, transacciones, total)
            break
    
    if not grupo_problematico:
        print("✅ No hay grupos problemáticos")
        return
    
    grupo_uuid, transacciones, total = grupo_problematico
    
    print(f"🔍 Grupo problemático encontrado:")
    print(f"   UUID: {str(grupo_uuid)[:8]}...")
    print(f"   Balance: ${total}")
    print(f"   Transacciones: {len(transacciones)}")
    
    print(f"\n📋 DETALLE DE TRANSACCIONES:")
    for i, trans in enumerate(transacciones, 1):
        ajuste_text = " [COMPLEMENTARIA]" if trans.ajuste else " [PRINCIPAL]"
        print(f"   {i}. ID:{trans.id} | ${trans.monto} | {trans.medio_pago.nombre}{ajuste_text}")
        print(f"      Fecha: {trans.fecha} | Descripción: {trans.descripcion}")
        if trans.cuenta_servicio:
            print(f"      Cuenta servicio: {trans.cuenta_servicio.nombre}")
        print()
    
    # Identificar el problema
    principales = [t for t in transacciones if not t.ajuste]
    complementarias = [t for t in transacciones if t.ajuste]
    
    print(f"🧐 ANÁLISIS:")
    print(f"   Transacciones principales: {len(principales)}")
    print(f"   Transacciones complementarias: {len(complementarias)}")
    
    if len(principales) > 1:
        print(f"   ❌ PROBLEMA: Hay múltiples transacciones principales")
        print(f"   💡 SOLUCIÓN: Eliminar duplicados y mantener una sola principal")
    elif len(complementarias) > 1:
        print(f"   ❌ PROBLEMA: Hay múltiples transacciones complementarias")
        print(f"   💡 SOLUCIÓN: Eliminar complementarias incorrectas")
    
    # Estrategia de corrección
    print(f"\n🔧 ESTRATEGIA DE CORRECCIÓN:")
    
    if len(transacciones) == 3:
        # Caso específico: tenemos 1 principal + 2 complementarias
        # Esto sugiere que había una complementaria huérfana, luego creamos una principal,
        # y la principal automáticamente creó otra complementaria
        
        print(f"   1. Identificar la transacción principal correcta")
        print(f"   2. Eliminar complementarias incorrectas")
        print(f"   3. Dejar que el sistema regenere la complementaria correcta")
        
        # Identificar cuál debería ser la principal
        principal_correcta = None
        complementarias_a_eliminar = []
        
        for trans in transacciones:
            if not trans.ajuste and trans.cuenta_servicio:
                # Esta es la principal que creamos nosotros
                principal_correcta = trans
            elif trans.ajuste:
                complementarias_a_eliminar.append(trans)
        
        if principal_correcta:
            print(f"\n✅ Principal correcta identificada: ID {principal_correcta.id}")
            print(f"   Descripción: {principal_correcta.descripcion}")
            
            print(f"\n🗑️ Eliminando {len(complementarias_a_eliminar)} complementarias incorrectas...")
            
            with transaction.atomic():
                for comp in complementarias_a_eliminar:
                    print(f"   - Eliminando: ID {comp.id} | ${comp.monto}")
                    comp.delete()
                
                # Ahora regenerar la complementaria correcta
                print(f"\n🔄 Regenerando asiento complementario...")
                principal_correcta._crear_asiento_complementario()
                
                print(f"   ✅ Asiento complementario regenerado")
    
    # Verificación final
    print(f"\n🧮 VERIFICACIÓN FINAL:")
    transacciones_actualizadas = Transaccion.objects.filter(grupo_uuid=grupo_uuid)
    total_final = sum(t.monto for t in transacciones_actualizadas)
    
    print(f"   Transacciones en el grupo: {transacciones_actualizadas.count()}")
    for t in transacciones_actualizadas:
        ajuste_text = " [COMPLEMENTARIA]" if t.ajuste else " [PRINCIPAL]"
        print(f"   - ${t.monto} | {t.medio_pago.nombre}{ajuste_text}")
    
    print(f"   Balance final: ${total_final}")
    
    if total_final == 0:
        print(f"   ✅ ¡PERFECTO! El grupo ahora está balanceado")
    else:
        print(f"   ❌ ERROR: El grupo aún no está balanceado")
    
    print(f"\n🎉 ¡CORRECCIÓN COMPLETADA!")

if __name__ == "__main__":
    main()
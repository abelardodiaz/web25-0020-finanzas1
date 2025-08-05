#!/usr/bin/env python
"""
Script para corregir transacciones huérfanas del sistema de doble partida
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from collections import defaultdict
from django.db import transaction
from core.models import Transaccion, TransaccionTipo, Cuenta

def encontrar_huerfanas():
    """Encuentra transacciones huérfanas"""
    grupos = defaultdict(list)
    for trans in Transaccion.objects.all():
        grupos[trans.grupo_uuid].append(trans)
    
    huerfanas = []
    for grupo_uuid, transacciones in grupos.items():
        if len(transacciones) == 1:
            huerfanas.append(transacciones[0])
    
    return huerfanas

def corregir_huerfana_ajuste(trans_huerfana):
    """
    Corrige una transacción complementaria (ajuste=True) huérfana
    buscando su transacción principal perdida o creándola
    """
    print(f"🔧 Corrigiendo: {trans_huerfana.descripcion}")
    print(f"   Tipo: {trans_huerfana.tipo} | Monto: ${trans_huerfana.monto}")
    print(f"   Cuenta: {trans_huerfana.medio_pago.nombre}")
    
    # Para transacciones complementarias, intentamos reconstruir la principal
    if "Contrapartida:" in trans_huerfana.descripcion:
        # Es un INGRESO complementario
        descripcion_original = trans_huerfana.descripcion.replace("Contrapartida: ", "")
        
        # Buscar cuenta de débito para el ingreso principal
        cuenta_debito = Cuenta.objects.filter(naturaleza="DEUDORA").first()
        if not cuenta_debito:
            print(f"   ❌ No se encontró cuenta deudora para el ingreso")
            return False
        
        # Crear transacción principal de ingreso
        trans_principal = Transaccion.objects.create(
            monto=-trans_huerfana.monto,  # Inverso del complementario
            tipo=trans_huerfana.tipo,
            fecha=trans_huerfana.fecha,
            descripcion=descripcion_original,
            cuenta_servicio=trans_huerfana.medio_pago,  # La cuenta de ingreso
            categoria=trans_huerfana.categoria,
            medio_pago=cuenta_debito,  # Cuenta que recibe el dinero
            grupo_uuid=trans_huerfana.grupo_uuid,
            ajuste=False,
            moneda=trans_huerfana.moneda,
            periodo=trans_huerfana.periodo,
            conciliado=trans_huerfana.conciliado
        )
        print(f"   ✅ Creada transacción principal de ingreso: ${trans_principal.monto}")
        
    elif "Gasto:" in trans_huerfana.descripcion:
        # Es un GASTO complementario
        descripcion_original = trans_huerfana.descripcion.replace("Gasto: ", "")
        
        # Buscar cuenta de pago adecuada (donde se hizo el gasto originalmente)
        # Por el monto y descripción, intentamos adivinar
        cuenta_pago = None
        if trans_huerfana.monto > 0:
            # Gasto con TDC (monto positivo en cuenta de gasto)
            cuenta_pago = Cuenta.objects.filter(naturaleza="ACREEDORA", tipo__grupo="CRE").first()
        else:
            # Gasto con cuenta deudora (monto negativo en cuenta de gasto)
            cuenta_pago = Cuenta.objects.filter(naturaleza="DEUDORA", tipo__grupo="DEB").first()
        
        if not cuenta_pago:
            print(f"   ❌ No se encontró cuenta de pago adecuada")
            return False
        
        # Crear transacción principal de gasto
        monto_principal = -trans_huerfana.monto if trans_huerfana.monto > 0 else abs(trans_huerfana.monto)
        
        trans_principal = Transaccion.objects.create(
            monto=monto_principal,
            tipo=trans_huerfana.tipo,
            fecha=trans_huerfana.fecha,
            descripcion=descripcion_original,
            cuenta_servicio=trans_huerfana.medio_pago,  # La cuenta de gasto
            categoria=trans_huerfana.categoria,
            medio_pago=cuenta_pago,  # Cuenta de pago
            grupo_uuid=trans_huerfana.grupo_uuid,
            ajuste=False,
            moneda=trans_huerfana.moneda,
            periodo=trans_huerfana.periodo,
            conciliado=trans_huerfana.conciliado
        )
        print(f"   ✅ Creada transacción principal de gasto: ${trans_principal.monto}")
        
    elif "Transferencia desde" in trans_huerfana.descripcion:
        # Es una TRANSFERENCIA complementaria
        # Buscar la cuenta origen en la descripción
        descripcion = trans_huerfana.descripcion
        nombre_origen = descripcion.replace("Transferencia desde ", "")
        
        cuenta_origen = Cuenta.objects.filter(nombre__icontains=nombre_origen.split()[0]).first()
        if not cuenta_origen:
            # Fallback: usar primera cuenta deudora
            cuenta_origen = Cuenta.objects.filter(naturaleza="DEUDORA").first()
        
        if not cuenta_origen:
            print(f"   ❌ No se encontró cuenta origen para transferencia")
            return False
        
        # Crear transacción principal de transferencia
        trans_principal = Transaccion.objects.create(
            monto=-trans_huerfana.monto,  # Inverso del complementario
            tipo=trans_huerfana.tipo,
            fecha=trans_huerfana.fecha,
            descripcion=f"Transferencia a {trans_huerfana.medio_pago.nombre}",
            cuenta_servicio=trans_huerfana.medio_pago,  # Cuenta destino
            categoria=trans_huerfana.categoria,
            medio_pago=cuenta_origen,  # Cuenta origen
            grupo_uuid=trans_huerfana.grupo_uuid,
            ajuste=False,
            moneda=trans_huerfana.moneda,
            periodo=trans_huerfana.periodo,
            conciliado=trans_huerfana.conciliado
        )
        print(f"   ✅ Creada transacción principal de transferencia: ${trans_principal.monto}")
    
    else:
        print(f"   ⚠️ Tipo de transacción complementaria no reconocido")
        return False
    
    return True

def eliminar_transacciones_prueba():
    """Elimina las transacciones de prueba del 2024-01-01 al 2024-01-04"""
    transacciones_prueba = Transaccion.objects.filter(
        fecha__range=['2024-01-01', '2024-01-04']
    )
    
    if transacciones_prueba.exists():
        print(f"🗑️ Eliminando {transacciones_prueba.count()} transacciones de prueba...")
        for trans in transacciones_prueba:
            print(f"   - {trans.fecha}: {trans.descripcion}")
        transacciones_prueba.delete()
        print(f"   ✅ Transacciones de prueba eliminadas")
        return True
    else:
        print(f"   ℹ️ No se encontraron transacciones de prueba")
        return False

def main():
    print("🔧 CORRECCIÓN DE TRANSACCIONES HUÉRFANAS")
    print("=" * 60)
    
    # Opción 1: Eliminar transacciones de prueba
    print("\n🗑️ Paso 1: Eliminar transacciones de prueba")
    eliminar_transacciones_prueba()
    
    # Encontrar huérfanas después de limpiar
    huerfanas = encontrar_huerfanas()
    
    if not huerfanas:
        print(f"\n🎉 ¡Perfecto! No hay transacciones huérfanas que corregir")
        return
    
    print(f"\n🔍 Encontradas {len(huerfanas)} transacciones huérfanas:")
    for i, trans in enumerate(huerfanas, 1):
        ajuste_text = " [COMPLEMENTARIA]" if trans.ajuste else " [PRINCIPAL]"
        print(f"  {i}. {trans.fecha} | ${trans.monto} | {trans.descripcion[:50]}...{ajuste_text}")
    
    print(f"\n🔧 Paso 2: Corrigiendo transacciones huérfanas...")
    
    with transaction.atomic():
        corregidas = 0
        for trans in huerfanas:
            if trans.ajuste:
                # Es una transacción complementaria huérfana
                if corregir_huerfana_ajuste(trans):
                    corregidas += 1
            else:
                # Es una transacción principal huérfana - crear complementaria
                try:
                    trans._crear_asiento_complementario()
                    print(f"✅ Creado complementario para: {trans.descripcion}")
                    corregidas += 1
                except Exception as e:
                    print(f"❌ Error al crear complementario: {e}")
    
    print(f"\n📊 RESUMEN:")
    print(f"✅ Transacciones corregidas: {corregidas}")
    print(f"📈 Total procesadas: {len(huerfanas)}")
    
    # Verificación final
    huerfanas_finales = encontrar_huerfanas()
    if not huerfanas_finales:
        print(f"\n🎉 ¡ÉXITO! Todas las transacciones ahora están balanceadas")
    else:
        print(f"\n⚠️ Quedan {len(huerfanas_finales)} transacciones con problemas")

if __name__ == "__main__":
    main()
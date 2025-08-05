#!/usr/bin/env python
"""
Script para corregir la transacción huérfana restante
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from collections import defaultdict
from django.db import transaction
from core.models import Transaccion, TransaccionTipo, Cuenta, Categoria

def main():
    print("🔧 CORRECCIÓN DE TRANSACCIÓN HUÉRFANA FINAL")
    print("=" * 60)
    
    # Encontrar la transacción huérfana
    grupos = defaultdict(list)
    for trans in Transaccion.objects.all():
        grupos[trans.grupo_uuid].append(trans)
    
    huerfanas = []
    for grupo_uuid, transacciones in grupos.items():
        if len(transacciones) == 1:
            huerfanas.append(transacciones[0])
    
    if not huerfanas:
        print("🎉 No hay transacciones huérfanas que corregir")
        return
    
    trans_huerfana = huerfanas[0]
    print(f"🔍 Transacción huérfana encontrada:")
    print(f"   Fecha: {trans_huerfana.fecha}")
    print(f"   Tipo: {trans_huerfana.tipo}")
    print(f"   Monto: ${trans_huerfana.monto}")
    print(f"   Descripción: {trans_huerfana.descripcion}")
    print(f"   Cuenta: {trans_huerfana.medio_pago.nombre}")
    print(f"   Es ajuste: {trans_huerfana.ajuste}")
    print(f"   UUID: {str(trans_huerfana.grupo_uuid)[:8]}...")
    
    # Analizar la transacción
    print(f"\n🧐 ANÁLISIS:")
    print(f"   - Es una transacción complementaria (ajuste=True)")
    print(f"   - Cuenta: TDC INVEX (naturaleza ACREEDORA)")
    print(f"   - Monto positivo: ${trans_huerfana.monto}")
    print(f"   - Tipo GASTO: Aumenta la deuda de la tarjeta")
    
    print(f"\n💭 INTERPRETACIÓN:")
    print(f"   Esta es una compra/gasto en TDC por $20,251.75")
    print(f"   Debería tener una transacción principal que registre")
    print(f"   el gasto en una cuenta de gastos")
    
    # Buscar cuenta de gastos adecuada
    print(f"\n🔍 Buscando cuenta de gastos adecuada...")
    
    # Buscar categoría adecuada
    categoria_gastos = Categoria.objects.filter(
        nombre__icontains="varios"
    ).first() or Categoria.objects.first()
    
    print(f"   Categoría seleccionada: {categoria_gastos}")
    
    # Buscar cuenta de gastos
    cuenta_gastos = None
    
    # Opciones de cuentas de gastos
    opciones = [
        "VARIOS",
        "GASTOS VARIOS", 
        "TARJETAS",
        "COMPRAS"
    ]
    
    for opcion in opciones:
        cuenta_gastos = Cuenta.objects.filter(
            nombre__icontains=opcion,
            naturaleza="DEUDORA"
        ).first()
        if cuenta_gastos:
            break
    
    # Si no encontramos cuenta específica, buscar cualquier cuenta de gastos deudora
    if not cuenta_gastos:
        cuenta_gastos = Cuenta.objects.filter(
            naturaleza="DEUDORA",
            tipo__grupo="SER"
        ).first()
    
    if not cuenta_gastos:
        print(f"   ❌ No se encontró cuenta de gastos adecuada")
        print(f"   📝 Creando cuenta de gastos...")
        
        # Buscar o crear tipo de cuenta para gastos
        from core.models import TipoCuenta
        tipo_gastos, created = TipoCuenta.objects.get_or_create(
            codigo="VARIOS",
            defaults={
                "nombre": "Gastos Varios",
                "grupo": "SER"
            }
        )
        
        # Crear cuenta de gastos
        cuenta_gastos = Cuenta.objects.create(
            nombre="GASTOS VARIOS TDC",
            tipo=tipo_gastos,
            naturaleza="DEUDORA",
            saldo_inicial=Decimal("0.00")
        )
        print(f"   ✅ Cuenta creada: {cuenta_gastos.nombre}")
    else:
        print(f"   ✅ Cuenta encontrada: {cuenta_gastos.nombre}")
    
    # Crear la transacción principal faltante
    print(f"\n🔧 Creando transacción principal...")
    
    with transaction.atomic():
        trans_principal = Transaccion.objects.create(
            monto=-trans_huerfana.monto,  # Negativo porque sale de la TDC hacia gastos
            tipo=trans_huerfana.tipo,      # GASTO
            fecha=trans_huerfana.fecha,    # Misma fecha
            descripcion="SALDO DEL MES DE JULIO",  # Misma descripción base
            cuenta_servicio=cuenta_gastos,  # Cuenta de gastos (donde se registra el gasto)
            categoria=categoria_gastos,     # Categoría de gastos
            medio_pago=trans_huerfana.medio_pago,  # TDC INVEX (de donde sale el dinero)
            grupo_uuid=trans_huerfana.grupo_uuid,  # Mismo grupo para enlazarlas
            ajuste=False,                   # Es la transacción principal
            moneda=trans_huerfana.moneda,
            periodo=trans_huerfana.periodo,
            conciliado=trans_huerfana.conciliado
        )
        
        print(f"   ✅ Transacción principal creada:")
        print(f"      Monto: ${trans_principal.monto}")
        print(f"      Cuenta pago: {trans_principal.medio_pago.nombre}")
        print(f"      Cuenta gasto: {trans_principal.cuenta_servicio.nombre}")
    
    # Verificar balance
    transacciones_grupo = Transaccion.objects.filter(
        grupo_uuid=trans_huerfana.grupo_uuid
    )
    
    total = sum(t.monto for t in transacciones_grupo)
    print(f"\n🧮 VERIFICACIÓN:")
    print(f"   Transacciones en el grupo: {transacciones_grupo.count()}")
    for t in transacciones_grupo:
        ajuste_text = " [COMPLEMENTARIA]" if t.ajuste else " [PRINCIPAL]"
        print(f"   - ${t.monto} | {t.medio_pago.nombre}{ajuste_text}")
    print(f"   Balance total: ${total}")
    
    if total == 0:
        print(f"   ✅ ¡PERFECTO! El grupo está balanceado")
    else:
        print(f"   ❌ ERROR: El grupo no está balanceado")
    
    print(f"\n🎉 ¡CORRECCIÓN COMPLETADA!")

if __name__ == "__main__":
    main()
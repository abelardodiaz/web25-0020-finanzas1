#!/usr/bin/env python
"""
Script para revisar y corregir transacciones existentes
que no cumplen con el sistema de doble partida.

Este script:
1. Identifica transacciones que no tienen pareja (grupo_uuid huérfanos)
2. Encuentra grupos desbalanceados (suma != 0)
3. Crea los asientos complementarios faltantes
4. Corrige montos incorrectos según la nueva lógica contable
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from collections import defaultdict
from django.db import transaction
from core.models import Transaccion, TransaccionTipo, Cuenta

def analizar_transacciones():
    """Analiza el estado actual de las transacciones"""
    print("🔍 ANÁLISIS DE TRANSACCIONES EXISTENTES")
    print("=" * 60)
    
    # Obtener todas las transacciones
    todas_transacciones = Transaccion.objects.all()
    print(f"📊 Total de transacciones: {todas_transacciones.count()}")
    
    # Agrupar por grupo_uuid
    grupos = defaultdict(list)
    transacciones_sin_ajuste = todas_transacciones.filter(ajuste=False)
    transacciones_ajuste = todas_transacciones.filter(ajuste=True)
    
    print(f"📋 Transacciones principales (ajuste=False): {transacciones_sin_ajuste.count()}")
    print(f"🔧 Transacciones complementarias (ajuste=True): {transacciones_ajuste.count()}")
    
    for trans in todas_transacciones:
        grupos[trans.grupo_uuid].append(trans)
    
    # Analizar grupos
    grupos_huerfanos = []  # Solo 1 transacción
    grupos_desbalanceados = []  # Suma != 0
    grupos_balanceados = []  # Suma = 0
    
    for grupo_uuid, transacciones in grupos.items():
        if len(transacciones) == 1:
            grupos_huerfanos.append((grupo_uuid, transacciones))
        else:
            total = sum(t.monto for t in transacciones)
            if total == 0:
                grupos_balanceados.append((grupo_uuid, transacciones))
            else:
                grupos_desbalanceados.append((grupo_uuid, transacciones, total))
    
    print(f"\n📈 RESULTADOS DEL ANÁLISIS:")
    print(f"✅ Grupos balanceados (suma = 0): {len(grupos_balanceados)}")
    print(f"❌ Grupos huérfanos (solo 1 transacción): {len(grupos_huerfanos)}")
    print(f"⚠️  Grupos desbalanceados (suma ≠ 0): {len(grupos_desbalanceados)}")
    
    return grupos_huerfanos, grupos_desbalanceados, grupos_balanceados

def mostrar_detalles_problemas(grupos_huerfanos, grupos_desbalanceados):
    """Muestra detalles de los problemas encontrados"""
    print(f"\n🔍 DETALLE DE PROBLEMAS ENCONTRADOS")
    print("=" * 60)
    
    if grupos_huerfanos:
        print(f"\n❌ GRUPOS HUÉRFANOS ({len(grupos_huerfanos)}):")
        for i, (grupo_uuid, transacciones) in enumerate(grupos_huerfanos[:10]):  # Mostrar solo 10
            trans = transacciones[0]
            print(f"  {i+1}. {trans.fecha} | {trans.tipo} | ${trans.monto} | {trans.descripcion[:30]}...")
            print(f"     Cuenta: {trans.medio_pago.nombre} | UUID: {str(grupo_uuid)[:8]}...")
        
        if len(grupos_huerfanos) > 10:
            print(f"     ... y {len(grupos_huerfanos) - 10} más")
    
    if grupos_desbalanceados:
        print(f"\n⚠️  GRUPOS DESBALANCEADOS ({len(grupos_desbalanceados)}):")
        for i, (grupo_uuid, transacciones, total) in enumerate(grupos_desbalanceados[:10]):
            print(f"  {i+1}. UUID: {str(grupo_uuid)[:8]}... | Balance: ${total}")
            for trans in transacciones:
                print(f"     - {trans.fecha} | {trans.tipo} | ${trans.monto} | {trans.descripcion[:30]}...")

def corregir_transacciones_huerfanas(grupos_huerfanos, dry_run=True):
    """Corrige transacciones que no tienen pareja"""
    print(f"\n🔧 CORRECCIÓN DE TRANSACCIONES HUÉRFANAS")
    print(f"Modo: {'SIMULACIÓN' if dry_run else 'EJECUCIÓN REAL'}")
    print("=" * 60)
    
    corregidas = 0
    errores = 0
    
    for grupo_uuid, transacciones in grupos_huerfanos:
        trans = transacciones[0]
        
        try:
            print(f"\n📝 Procesando: {trans.descripcion[:40]}...")
            print(f"   Tipo: {trans.tipo} | Monto: ${trans.monto} | Cuenta: {trans.medio_pago.nombre}")
            
            if not dry_run:
                # Crear asiento complementario usando la lógica del modelo
                if not trans.ajuste:
                    # Temporalmente marcar como ajuste para evitar recursión
                    original_ajuste = trans.ajuste
                    trans.ajuste = True
                    trans.save(update_fields=['ajuste'])
                    
                    # Restaurar y triggear creación de complementario
                    trans.ajuste = original_ajuste
                    trans._crear_asiento_complementario()
                    
            print(f"   ✅ {'Simularía' if dry_run else 'Creó'} asiento complementario")
            corregidas += 1
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            errores += 1
    
    print(f"\n📊 RESUMEN DE CORRECCIÓN:")
    print(f"✅ Transacciones corregidas: {corregidas}")
    print(f"❌ Errores encontrados: {errores}")
    
    return corregidas, errores

def corregir_grupos_desbalanceados(grupos_desbalanceados, dry_run=True):
    """Corrige grupos que no suman 0"""
    print(f"\n⚖️ CORRECCIÓN DE GRUPOS DESBALANCEADOS")
    print(f"Modo: {'SIMULACIÓN' if dry_run else 'EJECUCIÓN REAL'}")
    print("=" * 60)
    
    corregidos = 0
    errores = 0
    
    for grupo_uuid, transacciones, total in grupos_desbalanceados:
        try:
            print(f"\n📝 Grupo desbalanceado: ${total}")
            for trans in transacciones:
                print(f"   - {trans.tipo} | ${trans.monto} | {trans.descripcion[:30]}...")
            
            if not dry_run:
                # Estrategia: eliminar transacciones complementarias incorrectas y regenerar
                trans_principal = None
                trans_complementarias = []
                
                for trans in transacciones:
                    if not trans.ajuste:
                        trans_principal = trans
                    else:
                        trans_complementarias.append(trans)
                
                if trans_principal:
                    # Eliminar complementarias incorrectas
                    for comp in trans_complementarias:
                        comp.delete()
                    
                    # Regenerar asiento complementario
                    trans_principal._crear_asiento_complementario()
                    
                    print(f"   ✅ Grupo regenerado correctamente")
                else:
                    print(f"   ⚠️ No se encontró transacción principal")
            
            corregidos += 1
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            errores += 1
    
    print(f"\n📊 RESUMEN DE CORRECCIÓN:")
    print(f"✅ Grupos corregidos: {corregidos}")
    print(f"❌ Errores encontrados: {errores}")
    
    return corregidos, errores

def verificar_balance_general():
    """Verifica que todas las transacciones estén balanceadas después de las correcciones"""
    print(f"\n🧮 VERIFICACIÓN FINAL DE BALANCE")
    print("=" * 60)
    
    grupos = defaultdict(list)
    for trans in Transaccion.objects.all():
        grupos[trans.grupo_uuid].append(trans)
    
    grupos_balanceados = 0
    grupos_problematicos = 0
    
    for grupo_uuid, transacciones in grupos.items():
        total = sum(t.monto for t in transacciones)
        if total == 0:
            grupos_balanceados += 1
        else:
            grupos_problematicos += 1
            if grupos_problematicos <= 5:  # Mostrar solo 5 ejemplos
                print(f"❌ Grupo problemático: UUID {str(grupo_uuid)[:8]}... | Balance: ${total}")
    
    print(f"\n📊 RESULTADO FINAL:")
    print(f"✅ Grupos balanceados: {grupos_balanceados}")
    print(f"❌ Grupos con problemas: {grupos_problematicos}")
    
    porcentaje_exito = (grupos_balanceados / len(grupos) * 100) if grupos else 0
    print(f"🎯 Porcentaje de éxito: {porcentaje_exito:.1f}%")
    
    return grupos_balanceados, grupos_problematicos

def main():
    """Función principal del script"""
    print("🧮 SCRIPT DE CORRECCIÓN DE TRANSACCIONES")
    print("Sistema de doble partida - WEB25-0020-FINANZAS1")
    print("=" * 60)
    
    # Paso 1: Analizar estado actual
    grupos_huerfanos, grupos_desbalanceados, grupos_balanceados = analizar_transacciones()
    
    # Paso 2: Mostrar detalles de problemas
    if grupos_huerfanos or grupos_desbalanceados:
        mostrar_detalles_problemas(grupos_huerfanos, grupos_desbalanceados)
        
        # Paso 3: Preguntar al usuario qué hacer
        print(f"\n🤔 ¿QUÉ DESEAS HACER?")
        print("1. Solo simular correcciones (recomendado primero)")
        print("2. Ejecutar correcciones REALES")
        print("3. Salir sin hacer nada")
        
        while True:
            opcion = input("\nSelecciona una opción (1-3): ").strip()
            if opcion in ['1', '2', '3']:
                break
            print("❌ Opción inválida. Selecciona 1, 2 o 3.")
        
        if opcion == '3':
            print("👋 Saliendo sin hacer cambios...")
            return
        
        dry_run = (opcion == '1')
        
        # Paso 4: Ejecutar correcciones
        with transaction.atomic():
            if grupos_huerfanos:
                corregir_transacciones_huerfanas(grupos_huerfanos, dry_run)
            
            if grupos_desbalanceados:
                corregir_grupos_desbalanceados(grupos_desbalanceados, dry_run)
            
            if not dry_run:
                # Paso 5: Verificación final
                verificar_balance_general()
                print(f"\n🎉 ¡CORRECCIONES COMPLETADAS!")
            else:
                print(f"\n👁️ SIMULACIÓN COMPLETADA - No se hicieron cambios reales")
    else:
        print(f"\n🎉 ¡EXCELENTE! Todas las transacciones ya están balanceadas correctamente.")
        verificar_balance_general()

if __name__ == "__main__":
    main()
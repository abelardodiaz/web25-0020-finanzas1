#!/usr/bin/env python
"""
Script para revisar movimientos BBVA de forma interactiva
"""
import pandas as pd
import json
from datetime import datetime

def cargar_movimientos(archivo):
    """Carga los movimientos del archivo Excel"""
    df_raw = pd.read_excel(archivo, header=None)
    
    # Encontrar donde empiezan los datos
    for idx in range(len(df_raw)):
        if 'FECHA' in str(df_raw.iloc[idx, 0]):
            header_row = idx
            break
    
    # Leer con header correcto
    df = pd.read_excel(archivo, skiprows=header_row)
    df = df.dropna(how='all')
    df = df[df['FECHA'].notna()]
    
    # Convertir a numérico
    df['CARGO'] = pd.to_numeric(df['CARGO'], errors='coerce').fillna(0)
    df['ABONO'] = pd.to_numeric(df['ABONO'], errors='coerce').fillna(0)
    df['SALDO'] = pd.to_numeric(df['SALDO'], errors='coerce')
    
    return df

def mostrar_movimiento(mov, num):
    """Muestra un movimiento formateado"""
    print("\n" + "="*80)
    print(f"📌 MOVIMIENTO #{num}")
    print("="*80)
    print(f"📅 Fecha: {mov['FECHA']}")
    print(f"📝 Descripción: {mov['DESCRIPCIÓN']}")
    
    if mov['CARGO'] != 0:
        print(f"🔴 CARGO (Sale): ${abs(mov['CARGO']):,.2f}")
    elif mov['ABONO'] != 0:
        print(f"🟢 ABONO (Entra): ${mov['ABONO']:,.2f}")
    
    print(f"💼 Saldo después: ${mov['SALDO']:,.2f}")
    print("-"*80)

# Cargar el primer archivo
print("📊 ANÁLISIS INTERACTIVO DE MOVIMIENTOS BBVA")
print("="*80)

df1 = cargar_movimientos("movimientos (1).xlsx")
print(f"\n✅ Archivo 1 cargado: {len(df1)} movimientos")
print(f"📅 Período: {df1['FECHA'].min()} a {df1['FECHA'].max()}")

# Mostrar resumen
print("\n📊 RESUMEN:")
print(f"• Cargos: {(df1['CARGO'] != 0).sum()} movimientos por ${abs(df1['CARGO'].sum()):,.2f}")
print(f"• Abonos: {(df1['ABONO'] != 0).sum()} movimientos por ${df1['ABONO'].sum():,.2f}")

print("\n" + "="*80)
print("Vamos a revisar cada movimiento uno por uno...")
print("="*80)
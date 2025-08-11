#!/usr/bin/env python
"""
Script para analizar movimientos BBVA y entender la lógica contable correcta
"""
import pandas as pd
import sys
from decimal import Decimal
# from tabulate import tabulate  # No necesario por ahora

def analizar_archivo_bbva(archivo_path):
    """Analiza un archivo de movimientos BBVA"""
    print(f"\n{'='*80}")
    print(f"📊 ANALIZANDO: {archivo_path}")
    print('='*80)
    
    # Leer el archivo Excel
    df = pd.read_excel(archivo_path, header=None)
    
    # Buscar donde empiezan los datos reales
    inicio_datos = None
    for idx, row in df.iterrows():
        if row.astype(str).str.contains('FECHA', case=False).any():
            inicio_datos = idx
            columnas = df.iloc[idx].tolist()
            break
    
    if inicio_datos is None:
        print("❌ No se encontró la fila de encabezados")
        return
    
    # Crear DataFrame con los datos reales
    df_movimientos = df.iloc[inicio_datos+1:].reset_index(drop=True)
    
    # Usar las primeras 5 columnas y renombrarlas
    df_movimientos = df_movimientos.iloc[:, :5]
    df_movimientos.columns = ['FECHA', 'DESCRIPCION', 'CARGO', 'ABONO', 'SALDO']
    
    # Limpiar datos
    df_movimientos = df_movimientos.dropna(how='all')
    df_movimientos = df_movimientos[df_movimientos['FECHA'].notna()]
    
    # Convertir montos a números
    df_movimientos['CARGO'] = pd.to_numeric(df_movimientos['CARGO'], errors='coerce').fillna(0)
    df_movimientos['ABONO'] = pd.to_numeric(df_movimientos['ABONO'], errors='coerce').fillna(0)
    df_movimientos['SALDO'] = pd.to_numeric(df_movimientos['SALDO'], errors='coerce').fillna(0)
    
    print(f"\n📈 Total de movimientos: {len(df_movimientos)}")
    print(f"📅 Período: {df_movimientos['FECHA'].min()} a {df_movimientos['FECHA'].max()}")
    
    # Mostrar primeros 10 movimientos
    print("\n🔍 PRIMEROS 10 MOVIMIENTOS:")
    print("="*80)
    
    for idx, row in df_movimientos.head(10).iterrows():
        fecha = row['FECHA']
        desc = row['DESCRIPCION'][:50]
        cargo = row['CARGO']
        abono = row['ABONO']
        saldo = row['SALDO']
        
        print(f"\n📌 Movimiento {idx+1}:")
        print(f"   Fecha: {fecha}")
        print(f"   Descripción: {desc}")
        
        if cargo > 0:
            print(f"   💸 CARGO: ${cargo:,.2f} (Sale dinero de BBVA)")
            print(f"   📊 Contablemente:")
            print(f"      - BBVA (DEUDORA): ABONO por ${cargo:,.2f} → Disminuye")
            print(f"      - Cuenta destino: CARGO por ${cargo:,.2f} → Aumenta")
        elif abono > 0:
            print(f"   💰 ABONO: ${abono:,.2f} (Entra dinero a BBVA)")
            print(f"   📊 Contablemente:")
            print(f"      - BBVA (DEUDORA): CARGO por ${abono:,.2f} → Aumenta")
            print(f"      - Cuenta origen: ABONO por ${abono:,.2f} → Disminuye/Aumenta")
        
        print(f"   💼 Saldo después: ${saldo:,.2f}")
        print("-"*40)
    
    # Resumen estadístico
    print("\n📊 RESUMEN ESTADÍSTICO:")
    print("="*80)
    total_cargos = df_movimientos['CARGO'].sum()
    total_abonos = df_movimientos['ABONO'].sum()
    num_cargos = (df_movimientos['CARGO'] > 0).sum()
    num_abonos = (df_movimientos['ABONO'] > 0).sum()
    
    print(f"💸 Total CARGOS: ${total_cargos:,.2f} ({num_cargos} transacciones)")
    print(f"💰 Total ABONOS: ${total_abonos:,.2f} ({num_abonos} transacciones)")
    print(f"📈 Flujo neto: ${total_abonos - total_cargos:,.2f}")
    
    return df_movimientos

def explicar_logica_contable():
    """Explica la lógica contable correcta"""
    print("\n" + "="*80)
    print("📚 LÓGICA CONTABLE CORRECTA SEGÚN registros_contables.md")
    print("="*80)
    
    print("""
🏦 CUENTA BBVA 5019 (Tipo: DÉBITO, Naturaleza: DEUDORA)
─────────────────────────────────────────────────────

Cuando en el estado de cuenta BBVA aparece:

1️⃣ CARGO (Sale dinero de BBVA):
   • En BBVA: Es un ABONO contable → Disminuye el saldo
   • Ejemplo: Pago de Netflix $200
     ├─ BBVA (DEUDORA): ABONO $200 (disminuye)
     └─ Gasto Netflix (DEUDORA): CARGO $200 (aumenta)

2️⃣ ABONO (Entra dinero a BBVA):
   • En BBVA: Es un CARGO contable → Aumenta el saldo
   • Ejemplo: Depósito de nómina $10,000
     ├─ BBVA (DEUDORA): CARGO $10,000 (aumenta)
     └─ Ingreso Nómina (ACREEDORA): ABONO $10,000 (aumenta)

⚠️ IMPORTANTE: La terminología del banco es INVERSA a la contable:
   • Banco dice "CARGO" = Contablemente es ABONO para nosotros
   • Banco dice "ABONO" = Contablemente es CARGO para nosotros
""")

if __name__ == "__main__":
    # Explicar la lógica primero
    explicar_logica_contable()
    
    # Analizar el archivo más pequeño primero
    archivo = "movimientos (1).xlsx"
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
    
    df = analizar_archivo_bbva(archivo)
    
    print("\n" + "="*80)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*80)
    print("\n🎯 Ahora podemos revisar cada movimiento y verificar si el sistema")
    print("   los está procesando correctamente según los principios contables.")
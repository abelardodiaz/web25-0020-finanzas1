#!/usr/bin/env python3
import pandas as pd

# Cargar archivo 3 y mostrar movimiento #5
df_raw = pd.read_excel("movimientos (3).xlsx", header=None)

header_row = None
for idx in range(len(df_raw)):
    if pd.notna(df_raw.iloc[idx, 0]) and "FECHA" in str(df_raw.iloc[idx, 0]):
        header_row = idx
        break

df = pd.read_excel("movimientos (3).xlsx", skiprows=header_row)
df_clean = df.dropna(how="all")
df_clean = df_clean[df_clean.iloc[:, 0].notna()]

if len(df_clean) > 4:
    mov = df_clean.iloc[4]  # Movimiento #5
    print("📌 MOVIMIENTO #5 (Archivo 3):")
    print(f"📅 Fecha: {mov['FECHA']}")
    print(f"📝 Descripción: {mov['DESCRIPCIÓN']}")
    
    # Limpiar y convertir valores
    cargo_str = str(mov['CARGO']).replace(',', '').replace('-', '') if pd.notna(mov['CARGO']) else '0'
    abono_str = str(mov['ABONO']).replace(',', '') if pd.notna(mov['ABONO']) else '0'
    
    try:
        cargo = float(cargo_str) if cargo_str != 'nan' and cargo_str != '0' else 0
        abono = float(abono_str) if abono_str != 'nan' and abono_str != '0' else 0
    except:
        cargo = 0
        abono = 0
    
    if cargo > 0:
        print(f"🔴 CARGO: ${cargo:,.2f}")
    elif abono > 0:
        print(f"🟢 ABONO: ${abono:,.2f}")
    
    print(f"💼 Saldo después: {mov['SALDO']}")
else:
    print("No hay movimiento #5")
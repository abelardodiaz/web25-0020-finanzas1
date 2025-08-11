#!/usr/bin/env python3
import pandas as pd

# Cargar archivo 2
print("📊 CARGANDO ARCHIVO: movimientos (2).xlsx")
print("="*80)

df_raw = pd.read_excel("movimientos (2).xlsx", header=None)

# Encontrar header
header_row = None
for idx in range(len(df_raw)):
    if "FECHA" in str(df_raw.iloc[idx, 0]):
        header_row = idx
        break

# Leer con header correcto
df = pd.read_excel("movimientos (2).xlsx", skiprows=header_row)
df = df.dropna(how="all")
df = df[df["FECHA"].notna()]

# Convertir a numérico
df["CARGO"] = pd.to_numeric(df["CARGO"], errors="coerce").fillna(0)
df["ABONO"] = pd.to_numeric(df["ABONO"], errors="coerce").fillna(0)
df["SALDO"] = pd.to_numeric(df["SALDO"], errors="coerce")

print(f"✅ Total movimientos: {len(df)}")
print(f'📅 Período: {df["FECHA"].min()} a {df["FECHA"].max()}')

# Mostrar movimiento #3 (índice 2)
if len(df) > 2:
    mov = df.iloc[2]
    print("\n📌 MOVIMIENTO #3:")
    print(f'📅 Fecha: {mov["FECHA"]}')
    print(f'📝 Descripción: {mov["DESCRIPCIÓN"]}')
    if mov["CARGO"] != 0:
        print(f"🔴 CARGO: ${abs(mov['CARGO']):,.2f}")
    elif mov["ABONO"] != 0:
        print(f"🟢 ABONO: ${mov['ABONO']:,.2f}")
    print(f'💼 Saldo después: ${mov["SALDO"]:,.2f}')
else:
    print("No hay movimiento #3 en este archivo")
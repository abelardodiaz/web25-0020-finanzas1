#!/usr/bin/env python3
import pandas as pd

# Cargar archivo 2 y obtener el monto del movimiento #3
df_raw = pd.read_excel("movimientos (2).xlsx", header=None)

header_row = None
for idx in range(len(df_raw)):
    if "FECHA" in str(df_raw.iloc[idx, 0]):
        header_row = idx
        break

df = pd.read_excel("movimientos (2).xlsx", skiprows=header_row)
df = df.dropna(how="all")
df = df[df["FECHA"].notna()]

df["CARGO"] = pd.to_numeric(df["CARGO"], errors="coerce").fillna(0)
df["ABONO"] = pd.to_numeric(df["ABONO"], errors="coerce").fillna(0)

# Movimiento #3 (índice 2)
mov = df.iloc[2]
monto_cargo = abs(mov["CARGO"]) if mov["CARGO"] != 0 else 0
monto_abono = mov["ABONO"] if mov["ABONO"] != 0 else 0

print(f"Cargo: {monto_cargo}")
print(f"Abono: {monto_abono}")
print(f"Monto final: {monto_cargo if monto_cargo > 0 else monto_abono}")
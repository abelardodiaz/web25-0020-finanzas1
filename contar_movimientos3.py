#!/usr/bin/env python3
import pandas as pd

# Contar movimientos en archivo 3
df_raw = pd.read_excel("movimientos (3).xlsx", header=None)

header_row = None
for idx in range(len(df_raw)):
    if pd.notna(df_raw.iloc[idx, 0]) and "FECHA" in str(df_raw.iloc[idx, 0]):
        header_row = idx
        break

df = pd.read_excel("movimientos (3).xlsx", skiprows=header_row)
df_clean = df.dropna(how="all")
df_clean = df_clean[df_clean.iloc[:, 0].notna()]

print(f"📊 Total movimientos en archivo 3: {len(df_clean)}")
print(f"📊 Movimientos analizados hasta ahora: 5")
print(f"📊 Movimientos pendientes: {len(df_clean) - 5}")
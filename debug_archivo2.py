#!/usr/bin/env python3
import pandas as pd

# Debug del archivo 2
print("🔍 DEBUG ARCHIVO 2")
print("="*50)

df_raw = pd.read_excel("movimientos (2).xlsx", header=None)

# Buscar header
for idx in range(min(10, len(df_raw))):
    print(f"Fila {idx}: {list(df_raw.iloc[idx])}")

print("\n" + "="*50)

# Encontrar header correctamente
header_row = None
for idx in range(len(df_raw)):
    if pd.notna(df_raw.iloc[idx, 0]) and "FECHA" in str(df_raw.iloc[idx, 0]):
        header_row = idx
        print(f"Header encontrado en fila: {header_row}")
        break

if header_row is not None:
    df = pd.read_excel("movimientos (2).xlsx", skiprows=header_row)
    print(f"Columnas: {list(df.columns)}")
    print(f"Total filas después de limpiar: {len(df)}")
    
    # Mostrar primeras 3 filas con datos
    df_clean = df.dropna(how="all")
    df_clean = df_clean[df_clean.iloc[:, 0].notna()]  # Primera columna no nula
    
    print("\nPrimeros 3 movimientos:")
    for i in range(min(3, len(df_clean))):
        row = df_clean.iloc[i]
        print(f"Mov {i+1}: {dict(row)}")
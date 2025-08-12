#!/usr/bin/env python3
import pandas as pd
from datetime import datetime

print("Analizando Excel completo...")
df = pd.read_excel('scripts_cli/movimientos1.xlsx')
print(f"Total filas en Excel: {len(df)}")

print("\nTodas las filas del Excel:")
for i, row in df.iterrows():
    print(f"Fila {i}: {[str(x) for x in row.tolist()]}")

print("\nBuscando movimientos válidos (con fechas)...")
count = 0
for i, row in df.iterrows():
    # Intentar detectar fechas válidas
    fecha_str = str(row.iloc[0])
    if "/" in fecha_str and len(fecha_str) == 10:
        try:
            fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
            desc = str(row.iloc[2])[:50] if pd.notna(row.iloc[2]) else str(row.iloc[1])[:50] if pd.notna(row.iloc[1]) else 'Sin descripción'
            count += 1
            print(f"{count}. {fecha_str} | {desc}")
        except:
            pass

print(f"\nMovimientos reales encontrados en Excel: {count}")
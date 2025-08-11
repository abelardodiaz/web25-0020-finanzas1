#!/usr/bin/env python
"""
Análisis detallado de movimientos BBVA con lógica contable correcta
"""
import pandas as pd
import sys

def analizar_movimientos_bbva(archivo_path):
    """Analiza movimientos BBVA con lógica contable correcta"""
    
    print(f"\n{'='*100}")
    print(f"📊 ANÁLISIS DETALLADO DE MOVIMIENTOS BBVA - LÓGICA CONTABLE CORRECTA")
    print(f"   Archivo: {archivo_path}")
    print('='*100)
    
    # Leer archivo y encontrar header
    df_raw = pd.read_excel(archivo_path, header=None)
    header_row = None
    for idx in range(len(df_raw)):
        if 'FECHA' in str(df_raw.iloc[idx, 0]):
            header_row = idx
            break
    
    # Leer con header correcto
    df = pd.read_excel(archivo_path, skiprows=header_row)
    
    # Limpiar datos
    df = df.dropna(how='all')
    df = df[df['FECHA'].notna()]
    
    # Convertir a numérico
    df['CARGO'] = pd.to_numeric(df['CARGO'], errors='coerce').fillna(0)
    df['ABONO'] = pd.to_numeric(df['ABONO'], errors='coerce').fillna(0)
    df['SALDO'] = pd.to_numeric(df['SALDO'], errors='coerce')
    
    print(f"\n📈 Total movimientos: {len(df)}")
    print(f"📅 Período: {df['FECHA'].min()} a {df['FECHA'].max()}")
    print(f"💰 Saldo final: ${df['SALDO'].iloc[0]:,.2f}")
    
    print("\n" + "="*100)
    print("🔍 ANÁLISIS DETALLADO DE CADA MOVIMIENTO")
    print("="*100)
    
    print("""
⚠️ RECORDATORIO DE LÓGICA CONTABLE:
─────────────────────────────────────
• BBVA 5019 es cuenta DEUDORA (tipo Débito/Activo)
• Cuenta DEUDORA: Aumenta con CARGO, Disminuye con ABONO
• Pero el banco usa terminología desde SU perspectiva (inversa)
""")
    
    for idx, row in df.iterrows():
        print(f"\n{'─'*100}")
        print(f"📌 Movimiento #{idx+1}")
        print(f"📅 Fecha: {row['FECHA']}")
        print(f"📝 Descripción: {row['DESCRIPCIÓN']}")
        
        if row['CARGO'] != 0:
            # CARGO en estado de cuenta = Sale dinero de BBVA
            print(f"\n🔴 CARGO BANCARIO: ${abs(row['CARGO']):,.2f}")
            print(f"   ↪️ Sale dinero de BBVA")
            print(f"\n   📊 REGISTRO CONTABLE CORRECTO:")
            print(f"   ┌─ Cuenta BBVA 5019 (DEUDORA): ABONO ${abs(row['CARGO']):,.2f} → Disminuye")
            
            # Identificar destino
            desc = row['DESCRIPCIÓN']
            if 'SPEI ENVIADO' in desc:
                if 'SANTANDER' in desc:
                    print(f"   └─ Santander (DEUDORA): CARGO ${abs(row['CARGO']):,.2f} → Aumenta")
                elif 'BANORTE' in desc:
                    print(f"   └─ Banorte (DEUDORA): CARGO ${abs(row['CARGO']):,.2f} → Aumenta")
                elif 'BANAMEX' in desc:
                    print(f"   └─ Banamex (DEUDORA): CARGO ${abs(row['CARGO']):,.2f} → Aumenta")
                elif 'STP' in desc:
                    print(f"   └─ STP (DEUDORA): CARGO ${abs(row['CARGO']):,.2f} → Aumenta")
                elif 'Mercado Pago' in desc:
                    print(f"   └─ Mercado Pago (DEUDORA): CARGO ${abs(row['CARGO']):,.2f} → Aumenta")
                else:
                    print(f"   └─ Cuenta Externa (DEUDORA): CARGO ${abs(row['CARGO']):,.2f} → Aumenta")
            else:
                print(f"   └─ Gasto/Otra cuenta: CARGO ${abs(row['CARGO']):,.2f}")
                
        elif row['ABONO'] != 0:
            # ABONO en estado de cuenta = Entra dinero a BBVA
            print(f"\n🟢 ABONO BANCARIO: ${row['ABONO']:,.2f}")
            print(f"   ↪️ Entra dinero a BBVA")
            print(f"\n   📊 REGISTRO CONTABLE CORRECTO:")
            print(f"   ┌─ Cuenta BBVA 5019 (DEUDORA): CARGO ${row['ABONO']:,.2f} → Aumenta")
            
            # Identificar origen
            desc = row['DESCRIPCIÓN']
            if 'SPEI RECIBIDO' in desc:
                if 'SANTANDER' in desc:
                    print(f"   └─ Santander (DEUDORA): ABONO ${row['ABONO']:,.2f} → Disminuye")
                elif 'BANORTE' in desc:
                    print(f"   └─ Banorte (DEUDORA): ABONO ${row['ABONO']:,.2f} → Disminuye")
                elif 'NU MEXICO' in desc:
                    print(f"   └─ Nu México (DEUDORA): ABONO ${row['ABONO']:,.2f} → Disminuye")
                else:
                    print(f"   └─ Cuenta Externa (DEUDORA): ABONO ${row['ABONO']:,.2f} → Disminuye")
            elif 'PAGO CUENTA DE TERCERO' in desc:
                print(f"   └─ Ingreso/Depósito: ABONO ${row['ABONO']:,.2f} (cuenta ACREEDORA)")
            else:
                print(f"   └─ Ingreso/Otra cuenta: ABONO ${row['ABONO']:,.2f}")
        
        print(f"\n💼 Saldo después: ${row['SALDO']:,.2f}")
    
    # Resumen
    print("\n" + "="*100)
    print("📊 RESUMEN ESTADÍSTICO")
    print("="*100)
    
    total_cargos = df['CARGO'].sum()
    total_abonos = df['ABONO'].sum()
    num_cargos = (df['CARGO'] != 0).sum()
    num_abonos = (df['ABONO'] != 0).sum()
    
    print(f"\n🔴 CARGOS BANCARIOS (Salidas de BBVA):")
    print(f"   • Cantidad: {num_cargos} movimientos")
    print(f"   • Total: ${abs(total_cargos):,.2f}")
    print(f"   • Contablemente: ABONOS a BBVA (disminuyen saldo)")
    
    print(f"\n🟢 ABONOS BANCARIOS (Entradas a BBVA):")
    print(f"   • Cantidad: {num_abonos} movimientos")
    print(f"   • Total: ${total_abonos:,.2f}")
    print(f"   • Contablemente: CARGOS a BBVA (aumentan saldo)")
    
    print(f"\n📈 FLUJO NETO: ${total_abonos + total_cargos:,.2f}")
    
    return df

def mostrar_correccion_necesaria():
    """Muestra las correcciones necesarias en el código"""
    
    print("\n" + "="*100)
    print("🔧 CORRECCIONES NECESARIAS EN EL SISTEMA v0.8.1")
    print("="*100)
    
    print("""
❌ PROBLEMA IDENTIFICADO:
─────────────────────────
El sistema actual invierte la terminología contable:

1. En core/services/bbva_assistant.py línea 535:
   ACTUAL:  "# CARGO: Sale dinero de BBVA"
   CORREGIR A: "# ABONO: Sale dinero de BBVA (disminuye cuenta DEUDORA)"

2. En core/services/bbva_assistant.py línea 549:
   ACTUAL:  "# ABONO: Entra dinero a BBVA"
   CORREGIR A: "# CARGO: Entra dinero a BBVA (aumenta cuenta DEUDORA)"

3. En core/models.py método saldo_legacy() línea 141-142:
   ACTUAL:  return self.saldo_inicial + entradas - salidas
   CORRECTO: Está bien, pero agregar comentario:
            # entradas = CARGOS (aumentan DEUDORA)
            # salidas = ABONOS (disminuyen DEUDORA)

✅ SOLUCIÓN:
────────────
La lógica de cálculo está CORRECTA, solo hay que:
1. Corregir los comentarios para usar terminología contable correcta
2. Documentar que "entradas" son CARGOS y "salidas" son ABONOS para cuentas DEUDORAS
3. Aclarar que el banco usa terminología inversa a la contable
""")

if __name__ == "__main__":
    archivo = "movimientos (1).xlsx"
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
    
    df = analizar_movimientos_bbva(archivo)
    mostrar_correccion_necesaria()
    
    print("\n" + "="*100)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*100)
    print("\n🎯 Ahora revisemos cada movimiento para verificar el procesamiento correcto")
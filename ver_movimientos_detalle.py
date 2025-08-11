#!/usr/bin/env python
"""
Script detallado para ver movimientos BBVA y entender la lógica contable
"""
import pandas as pd
import sys

def ver_movimientos_bbva(archivo_path):
    """Ve los movimientos BBVA en detalle"""
    print(f"\n{'='*100}")
    print(f"📊 ANÁLISIS DETALLADO DE MOVIMIENTOS BBVA")
    print(f"   Archivo: {archivo_path}")
    print('='*100)
    
    # Leer el archivo completo
    df_raw = pd.read_excel(archivo_path, header=None)
    
    # Encontrar donde empiezan los datos (buscar FECHA)
    for idx in range(len(df_raw)):
        if 'FECHA' in str(df_raw.iloc[idx, 0]):
            header_row = idx
            break
    
    # Leer con el header correcto
    df = pd.read_excel(archivo_path, skiprows=header_row)
    
    # Limpiar filas vacías
    df = df.dropna(how='all')
    df = df[df['FECHA'].notna()]
    
    # Convertir tipos de datos
    df['CARGO O ABONO'] = pd.to_numeric(df['CARGO O ABONO'], errors='coerce')
    df['SALDO'] = pd.to_numeric(df['SALDO'], errors='coerce')
    
    print(f"\n📈 Total de movimientos encontrados: {len(df)}")
    print(f"📅 Período: {df['FECHA'].min()} a {df['FECHA'].max()}")
    print(f"💰 Saldo inicial: ${df['SALDO'].iloc[-1]:,.2f}")
    print(f"💰 Saldo final: ${df['SALDO'].iloc[0]:,.2f}")
    
    print("\n" + "="*100)
    print("MOVIMIENTOS DETALLADOS (Orden cronológico inverso - más reciente primero)")
    print("="*100)
    
    for idx, row in df.iterrows():
        fecha = row['FECHA']
        desc = row['DESCRIPCION']
        monto = row['CARGO O ABONO']
        saldo = row['SALDO']
        
        print(f"\n{'─'*100}")
        print(f"📅 Fecha: {fecha}")
        print(f"📝 Descripción: {desc}")
        
        # Identificar tipo de movimiento
        if monto < 0:
            print(f"🔴 CARGO BANCARIO: ${abs(monto):,.2f} (Sale dinero de BBVA)")
            print(f"   → En términos contables:")
            print(f"      • BBVA 5019 (DEUDORA): ABONO ${abs(monto):,.2f} → Saldo disminuye")
            print(f"      • Cuenta destino: CARGO ${abs(monto):,.2f}")
            
            # Identificar la cuenta destino
            if 'SPEI ENVIADO' in desc:
                if 'SANTANDER' in desc:
                    print(f"      • Destino identificado: Santander")
                elif 'BANORTE' in desc:
                    print(f"      • Destino identificado: Banorte")
                elif 'BANAMEX' in desc:
                    print(f"      • Destino identificado: Banamex")
                elif 'STP' in desc:
                    print(f"      • Destino identificado: STP")
                elif 'Mercado Pago' in desc:
                    print(f"      • Destino identificado: Mercado Pago")
            
        else:
            print(f"🟢 ABONO BANCARIO: ${monto:,.2f} (Entra dinero a BBVA)")
            print(f"   → En términos contables:")
            print(f"      • BBVA 5019 (DEUDORA): CARGO ${monto:,.2f} → Saldo aumenta")
            print(f"      • Cuenta origen: ABONO ${monto:,.2f}")
            
            # Identificar la cuenta origen
            if 'SPEI RECIBIDO' in desc:
                if 'SANTANDER' in desc:
                    print(f"      • Origen identificado: Santander")
                elif 'BANORTE' in desc:
                    print(f"      • Origen identificado: Banorte")
                elif 'NU MEXICO' in desc:
                    print(f"      • Origen identificado: Nu México")
            elif 'PAGO CUENTA DE TERCERO' in desc:
                print(f"      • Origen: Depósito de terceros BBVA")
        
        print(f"💼 Saldo después del movimiento: ${saldo:,.2f}")
    
    # Resumen
    print("\n" + "="*100)
    print("RESUMEN DE MOVIMIENTOS")
    print("="*100)
    
    cargos = df[df['CARGO O ABONO'] < 0]
    abonos = df[df['CARGO O ABONO'] > 0]
    
    print(f"\n🔴 CARGOS (Salidas):")
    print(f"   • Cantidad: {len(cargos)} movimientos")
    print(f"   • Total: ${abs(cargos['CARGO O ABONO'].sum()):,.2f}")
    
    print(f"\n🟢 ABONOS (Entradas):")
    print(f"   • Cantidad: {len(abonos)} movimientos")
    print(f"   • Total: ${abonos['CARGO O ABONO'].sum():,.2f}")
    
    print(f"\n📊 FLUJO NETO: ${df['CARGO O ABONO'].sum():,.2f}")
    
    return df

def explicar_correccion_necesaria():
    """Explica la corrección necesaria en el sistema"""
    print("\n" + "="*100)
    print("⚠️ CORRECCIÓN NECESARIA EN EL SISTEMA v0.8.1")
    print("="*100)
    
    print("""
🔧 PROBLEMA IDENTIFICADO:
────────────────────────
El sistema actual está usando terminología incorrecta:

❌ ACTUAL (INCORRECTO):
   • Cuando BBVA recibe dinero → Lo llama "ABONO"
   • Cuando BBVA envía dinero → Lo llama "CARGO"

✅ CORRECTO (según registros_contables.md):
   • Cuando BBVA (DEUDORA) recibe dinero → Es un CARGO contable (aumenta)
   • Cuando BBVA (DEUDORA) envía dinero → Es un ABONO contable (disminuye)

📝 CAMBIOS NECESARIOS:
─────────────────────
1. En core/services/bbva_assistant.py línea 549:
   - Cambiar comentario "ABONO: Entra dinero" por "CARGO: Entra dinero"
   
2. En core/services/bbva_assistant.py línea 535:
   - Cambiar comentario "CARGO: Sale dinero" por "ABONO: Sale dinero"

3. En core/models.py método saldo_legacy():
   - La lógica de cálculo está correcta
   - Pero la terminología en comentarios debe ajustarse

4. Verificar que AsientoContable y PartidaContable usen correctamente:
   - debito/credito según la naturaleza de la cuenta
""")

if __name__ == "__main__":
    archivo = "movimientos (1).xlsx"
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
    
    df = ver_movimientos_bbva(archivo)
    explicar_correccion_necesaria()
    
    print("\n" + "="*100)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*100)
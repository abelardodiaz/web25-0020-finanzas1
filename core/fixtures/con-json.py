#!/usr/bin/env python3
"""
con-json.py – Convierte los cuatro CSV de SALDOS a fixtures JSON
Preguntará si deseas procesar cada archivo y ajustará el signo de los gastos.
"""
import csv, json, pathlib, datetime as dt
from dateutil.parser import parse

BASE = pathlib.Path(__file__).parent        # carpeta donde corre el script
dflt  = lambda v, d="": v if v.strip() else d
today = dt.date.today().isoformat()

def boolify(x):      # 'TRUE'/'FALSE'  -> bool
    return {"TRUE": True, "FALSE": False}.get(x.upper(), False)

def parse_date(val): # dd/mm/aa -> ISO  (dayfirst)
    return parse(val, dayfirst=True).date().isoformat() if val.strip() else None

def ask(label):
    return input(f"¿Procesar {label}? [s/N] ").strip().lower() == "s"

# --- CUENTAS ---------------------------------------------------------
if ask("CSV de CUENTAS"):
    out = []
    with open(BASE/"SALDOS - Cuentas.csv", newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        for row in rd:
            out.append({
                "model": "core.cuenta",
                "pk":    int(row["PK"]),
                "fields": {
                    "nombre":          row["CUENTA"],
                    "tipo":            int(dflt(row["TIPO"], 0)),
                    "referencia":      row["REFERENCIA"],
                    "ref_comentario":  row["REF_COMENTARIO"],
                    "moneda":          dflt(row["MONEDA"], "MXN"),
                    "activo":          boolify(row["ACTIVO"]),
                    "no_cliente":      row["NO_CLIENTE"],
                    "fecha_apertura":  parse_date(row["FECHA_APERTURA"]),
                    "no_contrato":     row["NO_CONTRATO"],
                }
            })
    path = BASE/"cuentas.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"✔  {path.name} ({len(out)} regs)")

# --- CATEGORÍAS ------------------------------------------------------
if ask("CSV de CATEGORIAS"):
    out = []
    with open(BASE/"SALDOS - Categorias.csv", newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        for row in rd:
            out.append({
                "model": "core.categoria",
                "pk":    int(row["pk"]),
                "fields": {
                    "nombre": row["nombre"],
                    "tipo":   dflt(row["tipo"], "PERSONAL"),
                    "padre":  (int(row["padre"]) if row["padre"].isdigit() else None),
                }
            })
    path = BASE/"categorias.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"✔  {path.name} ({len(out)} regs)")

# --- PERÍODOS --------------------------------------------------------
if ask("CSV de PERIODOS"):
    out = []
    with open(BASE/"SALDOS - PERIODOS.csv", newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        for row in rd:
            out.append({
                "model": "core.periodo",
                "pk":    int(row["PK"]),
                "fields": {
                    "cuenta":            int(row["CUENTA"]),
                    "descripcion":       row["DESCRIPCION"],
                    "tipo":              row["TIPO"],
                    "fecha_inicio":      parse_date(row["FECHA INICIO"]),
                    "fecha_corte":       parse_date(row["FECHA DE CORTE"]),
                    "fecha_limite_pago": parse_date(row["FECHA VENCIMIENTO"]),
                    "monto_total":       dflt(row["MONTO TOTAL"], "0"),
                    "pago_minimo":       dflt(row["PAGO MINIMO"], None),
                    "pago_no_intereses": dflt(row["PAGO NO INTERESES"], None),
                    "fecha_pronto_pago": parse_date(row["FECHA PRONTO PAGO"]),
                    "monto_pronto_pago": dflt(row["MONTO PRONTO PAGO"], None),
                    "estado":            dflt(row["ESTADO"], "PENDIENTE"),
                }
            })
    path = BASE/"periodos.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"✔  {path.name} ({len(out)} regs)")

# --- TRANSACCIONES ---------------------------------------------------
if ask("CSV de TRANSACCIONES"):
    out = []
    with open(BASE/"SALDOS - Transacciones.csv", newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        for row in rd:
            if not row["PK"].strip().isdigit():
                continue  # salta vacío
            tipo = dflt(row["TIPO"], "GASTO").upper()
            monto = row["MONTO"].strip()
            # -- ajuste de signo -----------------------
            if tipo == "GASTO" and not monto.startswith("-"):
                monto = "-" + monto.lstrip("+")
            elif tipo == "INGRESO" and monto.startswith("-"):
                monto = monto.lstrip("-")
            # ------------------------------------------
            out.append({
                "model": "core.transaccion",
                "pk":    int(row["PK"]),
                "fields": {
                    "monto":            monto,
                    "tipo":             tipo,
                    "fecha":            parse_date(row["FECHA PAGO"]),
                    "descripcion":      row["DESCRIPCION"],
                    "cuenta_servicio":  int(dflt(row["CUENTA SERVICIO"], 0)) or None,
                    "categoria":        int(dflt(row["CATEGORIA"], 0))       or None,
                    "medio_pago":       int(dflt(row["METODO DE PAGO"], 0))  or None,
                    "moneda":           dflt(row["MONEDA"], "MXN"),
                    "conciliado":       boolify(row["CONCILIADO"]),
                }
            })
    path = BASE/"transacciones.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"✔  {path.name} ({len(out)} regs)")

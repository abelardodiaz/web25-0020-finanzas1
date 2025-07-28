#!/usr/bin/env python3
# ──────────────────────────────────────────────────────────────────────────────
# csv2fixture.py  ·  PARTE 1
#
# Funciones que realiza el script completo (Parte 1 + Parte 2):
#   1. Detecta todos los archivos CSV en la misma carpeta del script.
#   2. Muestra la lista en orden recomendado y asigna letras A-Z.
#   3. Ofrece un menú principal:
#        1) Procesar todos (en orden) sin preguntar.
#        2) Procesar todos pero preguntando en cada uno.
#        3) Procesar sólo algunos (sub-menú con selección de letras).
#        4) Opciones sobre JSON generados (listar / borrar todos / borrar algunos).
#        5) Salir.
#   4. Sub-menús siempre aceptan opción 9 para volver al menú principal.
#   5. (PARTE 2) Procesa cada CSV y genera los fixtures JSON aplicando reglas,
#      incluido convertir montos de GASTO a negativos.
#
#   *** Esta PARTE 1 implementa los puntos 1-4, dejando stubs para PARTE 2. ***
# ──────────────────────────────────────────────────────────────────────────────

import os
import string
import pathlib
import sys

BASE = pathlib.Path(__file__).parent          # Carpeta donde vive el script

# ─── 1  Detectar CSV y ordenarlos ────────────────────────────────────────────
PREFERRED_ORDER = [
    "SALDOS - Cuentas.csv",
    "SALDOS - Categorias.csv",
    "SALDOS - PERIODOS.csv",
    "SALDOS - Transacciones.csv",
]

def discover_csv() -> list[pathlib.Path]:
    """Devuelve los CSV ordenados primero por preferencia y luego alfabético."""
    csv_files = sorted(BASE.glob("*.csv"))
    preferred = []
    others    = []
    for csv in csv_files:
        if csv.name in PREFERRED_ORDER:
            preferred.append(csv)
        else:
            others.append(csv)
    # Orden preferido seguido de los demás alfabéticos
    ordered = [BASE/f for f in PREFERRED_ORDER if (BASE/f).exists()] + others
    return ordered

def letter_map(items):
    """Devuelve dict {'A': Path(...), 'B': Path(...), ...}"""
    letters = string.ascii_uppercase
    return {letters[i]: p for i, p in enumerate(items)}

# ─── 2  Menús ────────────────────────────────────────────────────────────────
def show_list(letter_dict, title="ARCHIVOS CSV DETECTADOS"):
    print("\n" + title)
    print("─" * len(title))
    for k, path in letter_dict.items():
        print(f"[{k}] {path.name}")
    print()

def main_menu():
    csv_order = discover_csv()
    csv_letters = letter_map(csv_order)

    while True:
        show_list(csv_letters)
        print("MENÚ PRINCIPAL")
        print("1. Procesar todos en orden (sin preguntar)")
        print("2. Procesar todos (preguntar en cada uno)")
        print("3. Procesar seleccionados")
        print("4. Gestionar CSV generados")
        print("5. Gestionar JSON generados")
        print("6. Salir")
        choice = input("Elige una opción: ").strip()

        if choice == "1":
            process_all(csv_order, ask_each=False)       # stub
        elif choice == "2":
            process_all(csv_order, ask_each=True)        # stub
        elif choice == "3":
            submenu_select(csv_letters)                  # stub
        elif choice == "4":
            submenu_csv()                               # stub
        elif choice == "5":
            submenu_json()                               # stub
        elif choice == "6":
            print("¡Hasta luego!")
            sys.exit(0)
        else:
            print("Opción no válida.\n")

# ─── 3  Stubs (se implementarán en PARTE 2) ──────────────────────────────────
def process_all(csv_paths, ask_each=False):
    """Procesará los CSV (lógica vendrá en Parte 2)."""
    print(f"[DEBUG] process_all(ask_each={ask_each}) con {len(csv_paths)} CSV")
    # TODO Parte 2
    input("Presiona Enter para continuar…")

def submenu_select(letter_dict):
    while True:
        show_list(letter_dict, "SELECCIONA LETRAS (coma-separadas)  ·  9 = volver")
        sel = input("Tu selección: ").strip().upper()
        if sel == "9":
            return
        chosen = [letter_dict.get(l) for l in sel.split(",") if l in letter_dict]
        if not chosen:
            print("   ❌  Selección inválida.\n")
            continue
        # TODO Parte 2 – procesar 'chosen'
        print(f"[DEBUG] Procesar seleccionados: {[p.name for p in chosen]}")
        input("Enter para volver al menú principal…")
        return

# ─── Nuevo sub-menú de gestión de CSV ──────────────────────────────────────
def submenu_csv():
    """
    Permite listar y eliminar los CSV de la carpeta:
        1) Eliminar TODOS los CSV
        2) Eliminar sólo algunos (selección por letras)
        9) Volver al menú principal
    """
    while True:
        csv_files = sorted(BASE.glob("*.csv"))
        if not csv_files:
            print("\n(No quedan CSV en la carpeta.)\n")
            input("Enter para volver…")
            return

        mapping = letter_map(csv_files)
        show_list(mapping, "ARCHIVOS CSV EN LA CARPETA")
        print("1. Eliminar TODOS los CSV")
        print("2. Eliminar algunos CSV")
        print("9. Volver")
        choice = input("Elige: ").strip()

        if choice == "1":
            for f in csv_files:
                f.unlink()
            print("✔  Todos los CSV eliminados.\n")

        elif choice == "2":
            sel = input("Letras de CSV a borrar: ").strip().upper()
            chosen = [mapping.get(l) for l in sel.split(",") if l in mapping]
            if not chosen:
                print("   ❌  Selección inválida.\n")
                continue
            for f in chosen:
                f.unlink()
            print("✔  Eliminados: ", ", ".join(f.name for f in chosen), "\n")

        elif choice == "9":
            return
        else:
            print("   ❌  Opción no válida.\n")

def submenu_json():
    while True:
        json_files = sorted(BASE.glob("*.json"))
        json_letters = letter_map(json_files)
        show_list(json_letters, "FIXTURES JSON EN LA CARPETA")
        print("1. Eliminar TODOS los JSON")
        print("2. Eliminar algunos JSON (selección por letras)")
        print("9. Volver")
        choice = input("Elige: ").strip()
        if choice == "1":
            # TODO Parte 2 – eliminar todos
            print("[DEBUG] Eliminar TODOS (stub)")
        elif choice == "2":
            sel = input("Letras de JSON a borrar: ").strip().upper()
            chosen = [json_letters.get(l) for l in sel.split(",") if l in json_letters]
            print(f"[DEBUG] Eliminar: {[p.name for p in chosen]} (stub)")
            # TODO Parte 2 – borrar elegidos
        elif choice == "9":
            return
        else:
            print("   ❌  Opción no válida.\n")

# ─── 4  Arranque ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main_menu()


#!/usr/bin/env python3
# ──────────────────────────────────────────────────────────────────────────────
# csv2fixture.py           (Parte 1 + Parte 2)
#
# Funciones:
#   1. Detecta todos los CSV de la carpeta.
#   2. Lista los CSV en orden recomendado A,B,C…
#   3. Menú principal y sub-menús:
#        1) Procesar todos sin preguntar.
#        2) Procesar todos preguntando uno a uno.
#        3) Procesar seleccionados (por letras).
#        4) Gestionar JSON existentes   →   1=eliminar todos   2=eliminar algunos.
#        5) Salir.
#   4. Procesa un CSV y genera un fixture JSON:
#        • Ajusta el signo de los GASTOS a negativo.
#        • Usa reglas específicas según el tipo de CSV.
# ──────────────────────────────────────────────────────────────────────────────

import csv, json, os, string, sys, pathlib, datetime as dt
from dateutil.parser import parse

BASE = pathlib.Path(__file__).parent
PREFERRED_ORDER = [
    "SALDOS - Cuentas.csv",
    "SALDOS - Categorias.csv",
    "SALDOS - PERIODOS.csv",
    "SALDOS - Transacciones.csv",
]

def discover_csv():
    csv_files = sorted(BASE.glob("*.csv"))
    preferred = [BASE/f for f in PREFERRED_ORDER if (BASE/f).exists()]
    others = [p for p in csv_files if p not in preferred]
    return preferred + others

def letter_map(items):
    return {string.ascii_uppercase[i]: p for i, p in enumerate(items)}

# ─── utilidades comunes ──────────────────────────────────────────────────────
def boolify(x): return {"TRUE": True, "FALSE": False}.get(x.upper(), False)

def parse_date(val):
    return parse(val, dayfirst=True).date().isoformat() if val.strip() else None

def write_json(name, payload):
    path = BASE/name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"✔  {path.name}  ({len(payload)} regs)")

# ─── convertidores individuales ──────────────────────────────────────────────
def conv_cuentas(path):
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        for row in rd:
            out.append({
                "model": "core.cuenta",
                "pk": int(row["PK"]),
                "fields": {
                    "nombre":          row["CUENTA"],
                    "tipo":            int(row["TIPO"] or 0),
                    "referencia":      row["REFERENCIA"],
                    "ref_comentario":  row["REF_COMENTARIO"],
                    "moneda":          row["MONEDA"] or "MXN",
                    "activo":          boolify(row["ACTIVO"]),
                    "no_cliente":      row["NO_CLIENTE"],
                    "fecha_apertura":  parse_date(row["FECHA_APERTURA"]),
                    "no_contrato":     row["NO_CONTRATO"],
                }
            })
    write_json("cuentas.json", out)

def conv_categorias(path):
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        for row in rd:
            out.append({
                "model": "core.categoria",
                "pk": int(row["pk"]),
                "fields": {
                    "nombre": row["nombre"],
                    "tipo":   row["tipo"] or "PERSONAL",
                    "padre":  int(row["padre"]) if row["padre"].isdigit() else None,
                }
            })
    write_json("categorias.json", out)

def conv_periodos(path):
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        for row in rd:
            out.append({
                "model": "core.periodo",
                "pk": int(row["PK"]),
                "fields": {
                    "cuenta":            int(row["CUENTA"]),
                    "descripcion":       row["DESCRIPCION"],
                    "tipo":              row["TIPO"],
                    "fecha_inicio":      parse_date(row["FECHA INICIO"]),
                    "fecha_corte":       parse_date(row["FECHA DE CORTE"]),
                    "fecha_limite_pago": parse_date(row["FECHA VENCIMIENTO"]),
                    "monto_total":       row["MONTO TOTAL"] or "0",
                    "pago_minimo":       row["PAGO MINIMO"] or None,
                    "pago_no_intereses": row["PAGO NO INTERESES"] or None,
                    "fecha_pronto_pago": parse_date(row["FECHA PRONTO PAGO"]),
                    "monto_pronto_pago": row["MONTO PRONTO PAGO"] or None,
                    "estado":            row["ESTADO"] or "PENDIENTE",
                }
            })
    write_json("periodos.json", out)

def conv_transacciones(path):
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        for row in rd:
            if not row["PK"].strip().isdigit():
                continue
            tipo = row["TIPO"].upper() if row["TIPO"] else "GASTO"
            monto = row["MONTO"].strip()
            if tipo == "GASTO" and not monto.startswith("-"):
                monto = "-" + monto.lstrip("+")
            elif tipo == "INGRESO" and monto.startswith("-"):
                monto = monto.lstrip("-")
            out.append({
                "model": "core.transaccion",
                "pk": int(row["PK"]),
                "fields": {
                    "monto":           monto,
                    "tipo":            tipo,
                    "fecha":           parse_date(row["FECHA PAGO"]),
                    "descripcion":     row["DESCRIPCION"],
                    "cuenta_servicio": int(row["CUENTA SERVICIO"] or 0) or None,
                    "categoria":       int(row["CATEGORIA"] or 0) or None,
                    "medio_pago":      int(row["METODO DE PAGO"] or 0) or None,
                    "moneda":          row["MONEDA"] or "MXN",
                    "conciliado":      boolify(row["CONCILIADO"]),
                }
            })
    write_json("transacciones.json", out)

CONVERTERS = {
    "SALDOS - Cuentas.csv":      conv_cuentas,
    "SALDOS - Categorias.csv":   conv_categorias,
    "SALDOS - PERIODOS.csv":     conv_periodos,
    "SALDOS - Transacciones.csv":conv_transacciones,
}

# ─── lógica de proceso ───────────────────────────────────────────────────────
def process_one(csv_path):
    fn = csv_path.name
    conv = CONVERTERS.get(fn)
    if conv:
        conv(csv_path)
    else:
        print(f"⚠  No hay conversor para {fn}")

def process_all(csv_paths, ask_each=False):
    for p in csv_paths:
        if ask_each:
            ans = input(f"¿Procesar {p.name}? [s/N] ").strip().lower()
            if ans != "s":
                continue
        process_one(p)
    input("\nFin de proceso. Enter para continuar…")

def submenu_select(letter_dict):
    while True:
        show_list(letter_dict, "Selecciona letras (coma)  ·  9 = volver")
        sel = input("Letras: ").strip().upper()
        if sel == "9":
            return
        chosen = [letter_dict.get(l) for l in sel.split(",") if l in letter_dict]
        if not chosen:
            print("   ❌  Selección inválida.\n")
            continue
        process_all(chosen, ask_each=False)
        return

def submenu_json():
    while True:
        json_files = sorted(BASE.glob("*.json"))
        mapping = letter_map(json_files)
        show_list(mapping, "FIXTURES JSON EN LA CARPETA")
        print("1. Eliminar TODOS los JSON")
        print("2. Eliminar algunos JSON")
        print("9. Volver")
        choice = input("Elige: ").strip()
        if choice == "1":
            for f in json_files:
                f.unlink()
            print("✔  Todos los JSON eliminados.\n")
        elif choice == "2":
            sel = input("Letras de JSON a borrar: ").strip().upper()
            chosen = [mapping.get(l) for l in sel.split(",") if l in mapping]
            for f in chosen:
                f.unlink()
            print("✔  Eliminados: ", ", ".join([f.name for f in chosen]), "\n")
        elif choice == "9":
            return
        else:
            print("   ❌  Opción no válida.\n")

# ─── interfaz ────────────────────────────────────────────────────────────────
def show_list(letter_dict, title="ARCHIVOS CSV DETECTADOS"):
    print("\n" + title)
    print("─" * len(title))
    for k, path in letter_dict.items():
        print(f"[{k}] {path.name}")
    print()

def main_menu():
    while True:
        csv_order = discover_csv()
        csv_letters = letter_map(csv_order)
        show_list(csv_letters)
        print("MENÚ PRINCIPAL")
        print("1. Procesar todos en orden (sin preguntar)")
        print("2. Procesar todos (preguntar en cada uno)")
        print("3. Procesar seleccionados")
        print("4. Gestionar CSV originales")
        print("5. Gestionar JSON generados")
        print("6. Salir")
        choice = input("Opción: ").strip()
        if choice == "1":
            process_all(csv_order, ask_each=False)
        elif choice == "2":
            process_all(csv_order, ask_each=True)
        elif choice == "3":
            submenu_select(csv_letters)
        elif choice == "4":
            submenu_csv()
        elif choice == "5":
            submenu_json()
        elif choice == "6":
            print("¡Hasta luego!")
            sys.exit(0)
        else:
            print("   ❌  Opción no válida.\n")

if __name__ == "__main__":
    main_menu()

# app.py (Versión Final Mejorada)
import os
import re
import json
import time
import pdfplumber
import requests
from datetime import datetime

# Configuración inicial
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARPETA_PDFS = os.path.join(BASE_DIR, "pdf")
CARPETA_JSON = os.path.join(BASE_DIR, "resultados")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = "sk-fdede78c52e9"  # Usar tu key real

# Crear carpetas si no existen
os.makedirs(CARPETA_JSON, exist_ok=True)

PRODUCTOS_REF = {
    'libretón premium': {'tipo': 'cuenta_ahorro', 'banco': 'BBVA'},
    'volaris cero': {'tipo': 'tarjeta_credito', 'banco': 'INVEX'}
}

def verificar_conectividad():
    try:
        requests.get("https://api.deepseek.com", timeout=5)
        print("✅ Conexión a DeepSeek: Operativa")
        return True
    except Exception as e:
        print(f"❌ Error de conectividad: {str(e)}")
        return False

def extraer_texto_pdf(ruta_pdf):
    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            texto = ""
            for page in pdf.pages:
                # Extraer tablas y convertir a texto estructurado
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        texto += " | ".join(str(cell) for cell in row) + "\n"
                texto += page.extract_text() + "\n"
            return texto.strip()
    except Exception as e:
        print(f"Error al leer PDF: {str(e)}")
        return None

def procesar_con_deepseek(texto):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Extrae los siguientes datos del estado de cuenta bancario:
1. **Datos principales**:
   - RFC (13 caracteres, formato: LLLNNNNNNNNNN, ejemplo: DISA820624UQA)
   - CLABE (18 dígitos, formato: 012345678901234567)
   - Fecha de inicio del período (dd/mm/aaaa)
   - Fecha de corte (dd/mm/aaaa)
   - Número de cuenta (puede tener espacios o guiones)
   - Saldo final (número con dos decimales, sin símbolos)
   - Nombre del banco (ej: BBVA, INVEX)
   - Nombre completo del cliente
   - Nombre del producto bancario

2. **Movimientos**:
   Extraer TODOS los movimientos en formato:
   [{{"fecha": "dd/mm/aaaa", "descripcion": "texto completo", "monto": 0000.00, "tipo": "cargo/abono"}}]
   
   **Reglas**:
   - Incluir mínimo 25 movimientos por documento
   - Priorizar información de tablas
   - Conservar descripciones originales
   - Convertir montos con formato $1,234.56 → 1234.56
   - Determinar 'tipo' basado en contexto si no está explícito

Texto del documento:
{texto[:15000]}"""  # Límite aumentado
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0  # Máxima precisión
    }
    
    for intento in range(3):
        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            print(f"⌛ Timeout (intento {intento+1}/3)...")
            time.sleep(2 ** intento)
        except Exception as e:
            print(f"Error API: {str(e)}")
            return None
    
    print("❌ Máximo de reintentos alcanzado")
    return None

def validar_rfc(rfc):
    return re.match(r"^[A-Z&Ñ]{3,4}\d{6}[A-V1-9][A-Z1-9][0-9A]$", rfc) is not None

def validar_clabe(clabe):
    return re.match(r"^\d{18}$", clabe) is not None

def normalizar_monto(valor):
    try:
        valor_limpio = re.sub(r'[^\d.-]', '', str(valor))
        return round(float(valor_limpio), 2)
    except:
        return 0.00

def generar_estructura_json(datos):
    # Normalización avanzada con validación
    normalizado = {
        "rfc": next((v for k, v in datos.items() if k.upper() in ['RFC', 'R.F.C']), ''),
        "clabe": next((v for k, v in datos.items() if 'CLABE' in k.upper()), ''),
        "fecha_inicio": datos.get('Fecha de inicio', ''),
        "fecha_corte": datos.get('Fecha de Corte', ''),
        "numero_cuenta": datos.get('Número de Cuenta', ''),
        "saldo_final": normalizar_monto(datos.get('Saldo Final', 0)),
        "banco": datos.get('Banco', 'Desconocido'),
        "nombre_cliente": datos.get('Nombre del Cliente', 'Cliente no identificado'),
        "nombre_producto": datos.get('Nombre del Producto', 'Producto genérico'),
        "movimientos": []
    }

    # Validación de formato RFC y CLABE
    if not validar_rfc(normalizado["rfc"]):
        raise ValueError(f"RFC inválido: {normalizado['rfc']}")
    
    if not validar_clabe(normalizado["clabe"]):
        raise ValueError(f"CLABE inválida: {normalizado['clabe']}")

    # Procesar movimientos
    contador_movimientos = 0
    for mov in datos.get('movimientos', []):
        try:
            movimiento = {
                "fecha": datetime.strptime(mov['fecha'], "%d/%m/%Y").strftime("%Y-%m-%d"),
                "descripcion": mov['descripcion'][:250],
                "monto": normalizar_monto(mov['monto']),
                "tipo": mov.get('tipo', 'cargo' if normalizar_monto(mov.get('monto', 0)) < 0 else 'abono')
            }
            normalizado["movimientos"].append(movimiento)
            contador_movimientos += 1
        except Exception as e:
            print(f"⚠️ Movimiento omitido: {str(e)}")

    if contador_movimientos < 15:
        raise ValueError(f"Solo se detectaron {contador_movimientos} movimientos válidos")

    return {
        "metadata": {
            "cliente": normalizado["nombre_cliente"],
            "rfc": normalizado["rfc"],
            "banco": normalizado["banco"],
            "producto": normalizado["nombre_producto"],
            "periodo": {
                "inicio": normalizado["fecha_inicio"],
                "corte": normalizado["fecha_corte"]
            },
            "cuenta": {
                "numero": normalizado["numero_cuenta"],
                "clabe": normalizado["clabe"],
                "saldo_final": normalizado["saldo_final"]
            }
        },
        "movimientos": normalizado["movimientos"]
    }

def guardar_json(datos, nombre_archivo):
    ruta_guardado = os.path.join(CARPETA_JSON, nombre_archivo)
    with open(ruta_guardado, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    print(f"💾 Archivo guardado: {nombre_archivo}")

def procesar_archivo(ruta_pdf):
    nombre_archivo = os.path.basename(ruta_pdf)
    print(f"\n📄 Procesando: {nombre_archivo}")
    
    texto = extraer_texto_pdf(ruta_pdf)
    if not texto:
        print("⚠️ No se pudo extraer texto")
        return
    
    respuesta = procesar_con_deepseek(texto)
    if not respuesta:
        print("🔴 Fallo en el procesamiento API")
        return
    
    try:
        respuesta_limpia = re.sub(r'(?i)```json|```', '', respuesta).strip()
        datos = json.loads(respuesta_limpia)
        
        datos_normalizados = generar_estructura_json(datos)
        
        # Generar nombre de archivo único
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_json = f"{datos_normalizados['metadata']['rfc']}_{ts}.json"
        
        guardar_json(datos_normalizados, nombre_json)
        print(f"✅ Procesado exitoso: {len(datos_normalizados['movimientos'])} movimientos")
        
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
        print("Fragmento de respuesta para análisis:")
        print(respuesta[:1500] if respuesta else "Sin respuesta de la API")

def main():
    if not verificar_conectividad():
        return
    
    for archivo in os.listdir(CARPETA_PDFS):
        if archivo.lower().endswith(".pdf"):
            procesar_archivo(os.path.join(CARPETA_PDFS, archivo))

if __name__ == "__main__":
    print("=== Sistema de Procesamiento de Estados de Cuenta v5 ===")
    print(f"📁 Carpeta PDF: {CARPETA_PDFS}")
    main()
    print("\n✅ Procesamiento completo! Resultados en:", CARPETA_JSON)
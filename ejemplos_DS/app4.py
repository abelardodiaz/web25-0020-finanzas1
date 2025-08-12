# app.py
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
API_KEY = "sk-fde2e9"  # Usar tu key real

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
            return "\n".join([page.extract_text() for page in pdf.pages[:5]])  # Primeras 5 páginas
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
   - RFC (13 caracteres)
   - CLABE (18 dígitos)
   - Fecha de inicio del período (dd/mm/aaaa)
   - Fecha de corte (dd/mm/aaaa)
   - Número de cuenta
   - Saldo final (número con dos decimales, sin símbolos)
   - Nombre del banco
   - Nombre del cliente
   - Nombre del producto

2. **Movimientos**:
   Extraer TODOS los movimientos en formato:
   [{{"fecha": "dd/mm/aaaa", "descripcion": "texto completo", "monto": 0000.00, "tipo": "cargo/abono"}}]
   
   **Reglas**:
   - Incluir todas las transacciones
   - Conservar descripciones originales
   - Ignorar símbolos monetarios ($)
   - Si no hay tipo, inferir por monto (negativo = cargo)

Devuelve SOLO un JSON válido sin texto adicional.
Texto: {texto[:5000]}"""  # Aumentar a 5000 caracteres
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    
    for intento in range(3):
        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
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

def normalizar_monto(valor):
    try:
        return round(float(str(valor).replace('$', '').replace(',', '')), 2)
    except:
        return 0.00

def generar_estructura_json(datos):
    # Normalizar nombres de campos
    return {
        "metadata": {
            "cliente": datos.get('Nombre del Cliente', ''),
            "rfc": datos.get('RFC', ''),
            "banco": datos.get('Banco', ''),
            "producto": datos.get('Nombre del Producto', ''),
            "periodo": {
                "inicio": datos.get('Fecha de inicio', ''),
                "corte": datos.get('Fecha de Corte', '')
            },
            "cuenta": {
                "numero": datos.get('Número de Cuenta', ''),
                "clabe": datos.get('CLABE', ''),
                "saldo_final": normalizar_monto(datos.get('Saldo Final', 0))
            }
        },
        "movimientos": [
            {
                "fecha": mov.get('fecha', ''),
                "descripcion": mov.get('descripcion', '')[:150],
                "monto": normalizar_monto(mov.get('monto', 0)),
                "tipo": mov.get('tipo', 'cargo').lower()
            } for mov in datos.get('movimientos', [])
        ]
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
        respuesta_limpia = re.sub(r'```json|```', '', respuesta).strip()
        datos = json.loads(respuesta_limpia)
        
        # Validación básica
        campos_requeridos = ['RFC', 'CLABE', 'Fecha de Corte', 'Número de Cuenta', 
                            'Saldo Final', 'Banco', 'Nombre del Cliente', 'Nombre del Producto']
        for campo in campos_requeridos:
            if campo not in datos:
                raise ValueError(f"Campo faltante: {campo}")

        # Generar estructura normalizada
        datos_normalizados = generar_estructura_json(datos)
        
        # Generar nombre de archivo único
        nombre_json = (
            f"{datos_normalizados['metadata']['rfc']}_"
            f"{datos_normalizados['metadata']['producto'].replace(' ', '_')}_"
            f"{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        )
        
        guardar_json(datos_normalizados, nombre_json)
        print(f"📊 Movimientos detectados: {len(datos_normalizados)['movimientos']}")
        
    except Exception as e:
        print(f"❌ Error procesando respuesta: {str(e)}")
        print("Respuesta cruda:")
        print(respuesta[:1000])

def main():
    if not verificar_conectividad():
        return
    
    for archivo in os.listdir(CARPETA_PDFS):
        if archivo.lower().endswith(".pdf"):
            procesar_archivo(os.path.join(CARPETA_PDFS, archivo))

if __name__ == "__main__":
    print("=== Sistema de Procesamiento de Estados de Cuenta v4 ===")
    print(f"📁 Carpeta PDF: {CARPETA_PDFS}")
    main()
    print("\n✅ Procesamiento completo! Resultados en:", CARPETA_JSON)
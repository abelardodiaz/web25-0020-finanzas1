# app.py (Versión Mejorada)
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
API_KEY = "sk-fdee9"  # Usar tu key real

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
            # Extraer texto de todas las páginas con prioridad en tablas
            texto = ""
            for page in pdf.pages:
                # Intentar extraer tablas primero
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        texto += "\n".join(["\t".join(row) for row in table]) + "\n"
                # Extraer texto normal
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
1. **Datos principales** (buscar en todo el documento):
   - RFC (13 caracteres, puede aparecer como 'R.F.C.')
   - CLABE (18 dígitos)
   - Fecha de inicio del período (dd/mm/aaaa)
   - Fecha de corte (dd/mm/aaaa)
   - Número de cuenta (buscar en secciones de 'Datos de la Cuenta')
   - Saldo final (número con dos decimales, sin símbolos)
   - Nombre del banco
   - Nombre del cliente (buscar al inicio del documento)
   - Nombre del producto (ej: 'Libretón Premium', 'Volaris Cero')

2. **Movimientos** (revisar todas las páginas):
   Extraer TODOS los movimientos en formato:
   [{{"fecha": "dd/mm/aaaa", "descripcion": "texto completo", "monto": 0000.00, "tipo": "cargo/abono"}}]
   
   **Reglas estrictas**:
   - Incluir mínimo 20 movimientos por documento
   - Conservar descripciones originales con referencia completa
   - Si el monto tiene formato $1,234.56, convertirlo a 1234.56
   - Si no hay tipo, usar 'cargo' para montos negativos, 'abono' para positivos

Ejemplo de RFC válido: DISA820624UQA

Devuelve SOLO un JSON válido sin texto adicional.
Texto: {texto[:10000]}"""  # Aumentar a 10,000 caracteres
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    
    for intento in range(3):
        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=90)
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
        # Manejar formatos como $-1,234.56 → -1234.56
        valor_limpio = re.sub(r'[^0-9.-]', '', str(valor))
        return round(float(valor_limpio), 2)
    except:
        return 0.00

def generar_estructura_json(datos):
    # Normalizar nombres de campos con múltiples variantes
    normalizado = {
        "rfc": datos.get('RFC') or datos.get('R.F.C') or datos.get('rfc', ''),
        "clabe": datos.get('CLABE') or datos.get('Clave Bancaria', ''),
        "fecha_inicio": datos.get('Fecha de inicio') or datos.get('Periodo', {}).get('inicio', ''),
        "fecha_corte": datos.get('Fecha de Corte') or datos.get('Fecha Corte', ''),
        "numero_cuenta": datos.get('Número de Cuenta') or datos.get('Cuenta', ''),
        "saldo_final": datos.get('Saldo Final') or datos.get('Saldo al Corte', 0),
        "banco": datos.get('Banco') or datos.get('Institución', ''),
        "nombre_cliente": datos.get('Nombre del Cliente') or datos.get('Titular', ''),
        "nombre_producto": datos.get('Nombre del Producto') or datos.get('Producto', ''),
        "movimientos": datos.get('movimientos', [])
    }
    
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
                "saldo_final": normalizar_monto(normalizado["saldo_final"])
            }
        },
        "movimientos": [
            {
                "fecha": mov.get('fecha', ''),
                "descripcion": mov.get('descripcion', '')[:200],  # Aumentar límite
                "monto": normalizar_monto(mov.get('monto', 0)),
                "tipo": mov.get('tipo', 'cargo' if normalizar_monto(mov.get('monto', 0)) < 0 else 'abono')
            } for mov in normalizado["movimientos"] if mov.get('fecha')
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
        
        # Validación mejorada con múltiples variantes
        campos_requeridos = {
            'RFC': ['RFC', 'R.F.C', 'Registro Federal de Contribuyentes'],
            'CLABE': ['CLABE', 'Clave Bancaria', 'Cuenta CLABE']
        }
        
        for campo, variantes in campos_requeridos.items():
            if not any(v in datos for v in variantes):
                raise ValueError(f"Campo faltante: {campo} (variantes: {', '.join(variantes)})")

        # Generar estructura normalizada
        datos_normalizados = generar_estructura_json(datos)
        
        # Validar cantidad mínima de movimientos
        if len(datos_normalizados["movimientos"]) < 15:
            raise ValueError(f"Movimientos insuficientes: {len(datos_normalizados)['movimientos']} detectados")
        
        # Generar nombre de archivo
        nombre_json = (
            f"{datos_normalizados['metadata']['rfc']}_"
            f"{datetime.now().strftime('%Y%m%d')}_"
            f"{hash(nombre_archivo)}.json"
        )
        
        guardar_json(datos_normalizados, nombre_json)
        print(f"📊 Movimientos detectados: {len(datos_normalizados)['movimientos']}")
        
    except Exception as e:
        print(f"❌ Error procesando respuesta: {str(e)}")
        print("Fragmento de respuesta:")
        print(respuesta[:1000] if respuesta else "Sin respuesta")

def main():
    if not verificar_conectividad():
        return
    
    for archivo in os.listdir(CARPETA_PDFS):
        if archivo.lower().endswith(".pdf"):
            procesar_archivo(os.path.join(CARPETA_PDFS, archivo))

if __name__ == "__main__":
    print("=== Sistema de Procesamiento de Estados de Cuenta v4.1 ===")
    print(f"📁 Carpeta PDF: {CARPETA_PDFS}")
    main()
    print("\n✅ Procesamiento completo! Resultados en:", CARPETA_JSON)
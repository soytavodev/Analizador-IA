import requests
import json
from config import (
    OLLAMA_API_URL, 
    OLLAMA_MODEL, 
    OLLAMA_MODEL_BLOG, 
    OLLAMA_USER, 
    OLLAMA_PASSWORD
)

MAX_CHARS_BLOQUE_MANUAL = 14000

def extraer_json(texto):
    """Extrae un bloque JSON válido de una respuesta de texto libre."""
    texto = texto.strip()
    inicio = texto.find("{")
    fin = texto.rfind("}") + 1

    if inicio != -1 and fin > inicio:
        texto = texto[inicio:fin]

    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return None

def llamar_ia(prompt, modelo, num_predict=4000, temperature=0.25, timeout=300, formato_json=True):
    """
    Se comunica con el endpoint del LLM inyectando las credenciales de entorno.
    """
    payload = {
        "user": OLLAMA_USER,
        "password": OLLAMA_PASSWORD,
        "question": prompt,
        "model": modelo,
        "stream": False,
        "options": {
            "num_predict": num_predict,
            "temperature": temperature,
            "num_ctx": 32768
        }
    }

    if formato_json:
        payload["format"] = "json"

    # Lanzamos la petición de forma segura
    respuesta = requests.post(OLLAMA_API_URL, json=payload, timeout=timeout)
    respuesta.raise_for_status()

    datos_respuesta = respuesta.json()
    texto_generado = datos_respuesta.get("answer", "").strip()

    if formato_json:
        return extraer_json(texto_generado), texto_generado

    return texto_generado, texto_generado

def dividir_texto_en_bloques(texto, max_chars=MAX_CHARS_BLOQUE_MANUAL):
    """Divide un texto largo en bloques para no saturar el contexto de la IA."""
    bloques = []
    actual = []
    tam_actual = 0

    for linea in texto.splitlines():
        tam_linea = len(linea) + 1
        if tam_actual + tam_linea > max_chars and actual:
            bloques.append("\n".join(actual))
            actual = []
            tam_actual = 0

        actual.append(linea)
        tam_actual += tam_linea

    if actual:
        bloques.append("\n".join(actual))

    return bloques

def analizar_bloque_funcional_profundo(bloque, indice, total):
    prompt = f"""
Actúa como analista funcional senior de software empresarial.
Vas a recibir UNA PARTE del código y estructura de un proyecto.
Tu misión es comprender qué hace el software desde el punto de vista del usuario final.

Debes extraer TODO lo funcionalmente útil sin mencionar código interno:
- módulos, pantallas, acciones, datos que gestiona, flujos y errores.

BLOQUE {indice} DE {total}:
{bloque}

Devuelve exclusivamente JSON válido:
{{
    "bloque": {indice},
    "descripcion_general_detectada": "",
    "modulos_detectados": [
        {{
            "nombre": "",
            "para_que_sirve": "",
            "acciones_disponibles": [
                {{
                    "accion": "",
                    "resultado_esperado": ""
                }}
            ]
        }}
    ]
}}
"""
    print(f"🧩 Análisis funcional profundo del bloque {indice}/{total}...")
    datos, _ = llamar_ia(prompt, OLLAMA_MODEL_BLOG, 5000, 0.20, 300, True)
    return datos

def consolidar_mapa_funcional(resumenes):
    material = json.dumps(resumenes, ensure_ascii=False, indent=2)
    prompt = f"""
Actúa como consultor funcional senior.
Has recibido análisis parciales de un software. Consolídalos en un MAPA FUNCIONAL COMPLETO.
Elimina duplicados y organiza el propósito real del sistema.

MATERIAL FUNCIONAL PARCIAL:
{material}

Devuelve exclusivamente JSON válido:
{{
    "nombre_probable_del_software": "",
    "descripcion_global": "",
    "modulos": [
        {{
            "nombre": "",
            "funciones": [
                {{
                    "nombre": "",
                    "descripcion_detallada": "",
                    "pasos_de_uso": []
                }}
            ]
        }}
    ]
}}
"""
    print("🧠 Consolidando mapa funcional completo del software...")
    datos, _ = llamar_ia(prompt, OLLAMA_MODEL_BLOG, 7000, 0.20, 300, True)
    return datos

def generar_manual_desde_mapa_funcional(mapa_funcional):
    material = json.dumps(mapa_funcional, ensure_ascii=False, indent=2)
    nombre = mapa_funcional.get("nombre_probable_del_software", "Software") if mapa_funcional else "Software"

    prompt = f"""
Actúa como redactor técnico profesional. Crea un MANUAL DE USUARIO final en Markdown.
Debe ser práctico, detallado y orientado al cliente/usuario final (NO a programadores).
Prohibido mencionar código, bases de datos o arquitectura.

MAPA FUNCIONAL:
{material}

Genera el documento completo en Markdown con Introducción, Conceptos, y desglose de funciones principales.
DEVUELVE ÚNICAMENTE MARKDOWN. NO DEVUELVAS JSON.
"""
    print("📘 Redactando manual final extenso...")
    markdown, _ = llamar_ia(prompt, OLLAMA_MODEL_BLOG, 12000, 0.25, 300, False)
    
    # Limpieza de bloques de markdown residuales
    if markdown.startswith("```markdown"):
        markdown = markdown.replace("```markdown", "", 1).strip()
    if markdown.endswith("```"):
        markdown = markdown[:-3].strip()

    return {
        "titulo": f"Manual de usuario - {nombre}",
        "contenido_markdown": markdown
    }

def generar_manual_usuario_por_bloques(informe_texto):
    bloques = dividir_texto_en_bloques(informe_texto)
    print(f"📚 El informe se ha dividido en {len(bloques)} bloque(s).")
    
    resumenes = []
    for indice, bloque in enumerate(bloques, start=1):
        resumen = analizar_bloque_funcional_profundo(bloque, indice, len(bloques))
        if resumen:
            resumenes.append(resumen)

    if not resumenes:
        print("❌ Error: No se pudo generar el análisis de los bloques.")
        return None

    mapa_funcional = consolidar_mapa_funcional(resumenes)
    if not mapa_funcional:
        print("❌ Error: No se pudo consolidar el mapa funcional.")
        return None

    return generar_manual_desde_mapa_funcional(mapa_funcional)

def analizar_con_ia(informe_texto, tipo_generacion="producto"):
    if tipo_generacion == "manual":
        return generar_manual_usuario_por_bloques(informe_texto)

    if tipo_generacion == "producto":
        modelo = OLLAMA_MODEL
        prompt = f"""
Actúa como Analista de Producto SaaS Experto.
Analiza este código y genera contenido para una landing page comercial atractiva orientada a ventas.

CÓDIGO/ESTRUCTURA:
{informe_texto}

Devuelve JSON válido:
{{
    "nombre": "Nombre sugerido para el producto",
    "pill_text": "Texto destacado corto (ej. Nuevo, Destacado)",
    "descripcion": "Descripción comercial del producto",
    "showcase_1_titulo": "Título de beneficio 1",
    "showcase_1_texto": "Descripción de beneficio 1",
    "caracteristicas": [
        {{"titulo": "Filtros avanzados", "detalle": "Encuentra datos en segundos"}}
    ],
    "seo_title": "Título SEO",
    "seo_description": "Descripción SEO"
}}
RESPONDE SÓLO CON JSON.
"""
    elif tipo_generacion == "linkedin":
        modelo = OLLAMA_MODEL_BLOG
        prompt = f"""
Actúa como Copywriter B2B experto en LinkedIn para el sector tecnológico.
Analiza este proyecto y crea un post atractivo anunciando el desarrollo o lanzamiento de esta herramienta.

CÓDIGO/ESTRUCTURA:
{informe_texto}

Devuelve JSON válido:
{{
    "post": "Contenido del post con emojis y hashtags relevantes..."
}}
RESPONDE SÓLO CON JSON.
"""
    else:  # blog
        modelo = OLLAMA_MODEL_BLOG
        prompt = f"""
Actúa como Tech Blogger Senior.
Escribe un artículo técnico sobre cómo se ha construido este proyecto, qué problema resuelve y cómo está estructurado.

CÓDIGO/ESTRUCTURA:
{informe_texto}

Devuelve JSON válido:
{{
    "titulo": "Título atractivo del artículo",
    "contenido": "Contenido del post en formato Markdown (puedes incluir ejemplos de código)..."
}}
RESPONDE SÓLO CON JSON.
"""
    print(f"🤖 Analizando con modelo [{modelo}] en modo '{tipo_generacion}'...")
    
    try:
        datos, error_txt = llamar_ia(prompt, modelo, 3500, 0.35, 300, True)
        if not datos:
            print("❌ La IA no devolvió un formato JSON parseable.")
        return datos
    except requests.exceptions.Timeout:
        print("❌ Error: El servidor de IA ha tardado demasiado (Timeout).")
        return None
    except Exception as e:
        print(f"❌ Error de conexión o servidor IA: {e}")
        return None

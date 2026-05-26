import requests
import json
from config import OLLAMA_API_URL, OLLAMA_MODEL, OLLAMA_MODEL_BLOG


MAX_CHARS_BLOQUE_MANUAL = 14000


def extraer_json(texto):
    texto = texto.strip()

    inicio = texto.find("{")
    fin = texto.rfind("}") + 1

    if inicio != -1 and fin > inicio:
        texto = texto[inicio:fin]

    return json.loads(texto)


def llamar_ia(prompt, modelo, num_predict=4000, temperature=0.25, timeout=300, formato_json=True):
    payload = {
        "user": "jocarsa",
        "password": "jocarsa",
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

    respuesta = requests.post(OLLAMA_API_URL, json=payload, timeout=timeout)
    respuesta.raise_for_status()

    datos_respuesta = respuesta.json()
    texto_generado = datos_respuesta.get("answer", "").strip()

    if formato_json:
        return extraer_json(texto_generado), texto_generado

    return texto_generado, texto_generado


def dividir_texto_en_bloques(texto, max_chars=MAX_CHARS_BLOQUE_MANUAL):
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

Vas a recibir UNA PARTE de un informe técnico de un proyecto.
Tu misión es comprender qué hace el software desde el punto de vista del usuario final.

NO redactes todavía el manual.

Debes extraer TODO lo funcionalmente útil:
- módulos
- pantallas
- formularios
- botones
- acciones del usuario
- listados
- filtros
- altas, bajas, modificaciones
- importación/exportación
- autenticación
- roles
- flujos completos
- errores visibles
- operaciones de negocio
- datos que gestiona
- configuración
- resultados que obtiene el usuario

PROHIBIDO:
- explicar código
- mencionar nombres de funciones internas
- explicar clases, variables, SQL o arquitectura
- redactar como programador

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
            "usuarios_destinatarios": [],
            "pantallas_o_zonas": [],
            "datos_que_gestiona": [],
            "acciones_disponibles": [
                {{
                    "accion": "",
                    "descripcion_usuario": "",
                    "pasos_probables": [],
                    "resultado_esperado": "",
                    "observaciones": ""
                }}
            ]
        }}
    ],
    "flujos_de_trabajo_detectados": [
        {{
            "nombre": "",
            "objetivo": "",
            "pasos": [],
            "resultado_final": ""
        }}
    ],
    "funciones_individuales_detectadas": [
        {{
            "nombre_funcional": "",
            "que_hace": "",
            "como_la_usaria_un_usuario": "",
            "datos_necesarios": [],
            "resultado": "",
            "posibles_errores": [],
            "recomendaciones": []
        }}
    ],
    "conceptos_importantes_para_el_manual": [],
    "dudas_o_aspectos_no_deducibles": []
}}
"""

    print(f"🧩 Análisis funcional profundo del bloque {indice}/{total}...")

    datos, _ = llamar_ia(
        prompt=prompt,
        modelo=OLLAMA_MODEL_BLOG,
        num_predict=5000,
        temperature=0.20,
        timeout=300,
        formato_json=True
    )

    return datos


def consolidar_mapa_funcional(resumenes):
    material = json.dumps(resumenes, ensure_ascii=False, indent=2)

    prompt = f"""
Actúa como consultor funcional senior.

Has recibido análisis parciales de un mismo software.
Tu tarea es consolidarlos en un MAPA FUNCIONAL COMPLETO.

NO redactes todavía el manual final.

Objetivo:
- unir duplicados
- ordenar funciones por módulos
- detectar el propósito real del software
- organizar funciones principales y secundarias
- preparar una base clara para un manual de usuario extenso

PROHIBIDO:
- hablar de código
- hablar de arquitectura interna
- inventar funciones no soportadas por el material
- eliminar funciones importantes

MATERIAL FUNCIONAL PARCIAL:
{material}

Devuelve exclusivamente JSON válido:

{{
    "nombre_probable_del_software": "",
    "descripcion_global": "",
    "publico_objetivo": [],
    "objetivos_del_sistema": [],
    "modulos": [
        {{
            "nombre": "",
            "descripcion": "",
            "funciones": [
                {{
                    "nombre": "",
                    "descripcion_detallada": "",
                    "objetivo_para_el_usuario": "",
                    "cuando_usarla": "",
                    "pasos_de_uso": [],
                    "campos_o_datos_utilizados": [],
                    "resultado_esperado": "",
                    "ejemplo_practico": "",
                    "errores_frecuentes": [],
                    "buenas_practicas": []
                }}
            ]
        }}
    ],
    "flujos_principales": [
        {{
            "nombre": "",
            "descripcion": "",
            "pasos": [],
            "resultado": ""
        }}
    ],
    "glosario_usuario": [
        {{
            "termino": "",
            "explicacion": ""
        }}
    ],
    "limitaciones_o_dudas": []
}}
"""

    print("🧠 Consolidando mapa funcional completo del software...")

    datos, _ = llamar_ia(
        prompt=prompt,
        modelo=OLLAMA_MODEL_BLOG,
        num_predict=7000,
        temperature=0.20,
        timeout=300,
        formato_json=True
    )

    return datos


def limpiar_markdown_generado(texto):
    texto = texto.strip()

    if texto.startswith("```markdown"):
        texto = texto.replace("```markdown", "", 1).strip()

    if texto.startswith("```"):
        texto = texto.replace("```", "", 1).strip()

    if texto.endswith("```"):
        texto = texto[:-3].strip()

    return texto.strip()


def generar_manual_desde_mapa_funcional(mapa_funcional):
    material = json.dumps(mapa_funcional, ensure_ascii=False, indent=2)

    nombre = mapa_funcional.get("nombre_probable_del_software", "Software")
    if not nombre:
        nombre = "Software"

    prompt = f"""
Actúa como redactor profesional de manuales de usuario final para software empresarial.

Debes crear un MANUAL DE USUARIO MUY DETALLADO, EXTENSO Y PRÁCTICO en Markdown.

IMPORTANTE:
NO devuelvas JSON.
NO metas el manual dentro de comillas.
NO uses bloques de código.
Devuelve únicamente el contenido Markdown final.

Este manual será entregado a clientes y usuarios finales.

MUY IMPORTANTE:
- No es documentación técnica.
- No es documentación para programadores.
- Debe explicar función por función.
- Debe explicar cómo se usa el software en la práctica.
- Debe ser mucho más detallado que un resumen.
- Cada función debe tener explicación, pasos, resultado, ejemplo y recomendaciones.

PROHIBIDO:
- mencionar código
- mencionar funciones internas
- mencionar clases
- mencionar bases de datos
- mencionar APIs internas
- mencionar variables
- mencionar librerías
- decir "según el código"
- decir "parece que el sistema"

MAPA FUNCIONAL COMPLETO:
{material}

ESTRUCTURA OBLIGATORIA:

# Manual de usuario - {nombre}

## 1. Introducción

## 2. ¿Para qué sirve?

## 3. Usuarios a los que va dirigido

## 4. Conceptos básicos

## 5. Acceso y primeros pasos

## 6. Vista general de la interfaz

## 7. Flujo de trabajo recomendado

## 8. Funciones principales

Esta sección debe ser la más extensa.

Para CADA función detectada en el mapa funcional, crea una subsección con esta estructura:

### Nombre de la función

#### Qué permite hacer

#### Cuándo utilizarla

#### Cómo utilizarla paso a paso

#### Qué datos debe introducir o revisar el usuario

#### Resultado esperado

#### Ejemplo práctico

#### Recomendaciones

#### Problemas frecuentes

## 9. Casos de uso completos

## 10. Buenas prácticas

## 11. Solución de problemas

## 12. Preguntas frecuentes

Incluye al menos 10 preguntas frecuentes si la información disponible lo permite.

## 13. Glosario

## 14. Conclusión

REGLAS DE CALIDAD:
- Markdown limpio.
- Español profesional.
- Explicaciones largas.
- Nivel usuario final.
- Muy práctico.
- Muy ordenado.
- No inventes funcionalidades no incluidas en el mapa funcional.
- Si una función no tiene todos los datos, explica solo lo deducible.
- Prioriza claridad sobre brevedad.
- El manual debe parecer un documento entregable real.

Devuelve solamente Markdown.
"""

    print("📘 Redactando manual final extenso función a función...")

    markdown, _ = llamar_ia(
        prompt=prompt,
        modelo=OLLAMA_MODEL_BLOG,
        num_predict=12000,
        temperature=0.25,
        timeout=300,
        formato_json=False
    )

    markdown = limpiar_markdown_generado(markdown)

    return {
        "titulo": f"Manual de usuario - {nombre}",
        "contenido_markdown": markdown
    }


def generar_manual_usuario_por_bloques(informe_texto):
    bloques = dividir_texto_en_bloques(informe_texto)

    print(f"📚 El informe se ha dividido en {len(bloques)} bloque(s).")
    print("🔎 Se realizará análisis funcional profundo antes de redactar el manual.")

    resumenes = []

    for indice, bloque in enumerate(bloques, start=1):
        try:
            resumen = analizar_bloque_funcional_profundo(
                bloque=bloque,
                indice=indice,
                total=len(bloques)
            )
            resumenes.append(resumen)
        except Exception as e:
            print(f"❌ Error analizando bloque {indice}: {e}")

    if not resumenes:
        print("❌ No se pudo obtener ningún análisis funcional.")
        return None

    try:
        mapa_funcional = consolidar_mapa_funcional(resumenes)
    except Exception as e:
        print(f"❌ Error consolidando mapa funcional: {e}")
        return None

    try:
        manual = generar_manual_desde_mapa_funcional(mapa_funcional)
        return manual
    except Exception as e:
        print(f"❌ Error generando manual final: {e}")
        return None


def analizar_con_ia(informe_texto, tipo_generacion="producto"):
    if tipo_generacion == "manual":
        return generar_manual_usuario_por_bloques(informe_texto)

    if tipo_generacion == "producto":
        modelo_a_usar = OLLAMA_MODEL
        prompt = f"""
Actúa como un Analista de Producto Experto de la empresa JOCARSA.
Tu misión es analizar el informe técnico de un software y redactar el contenido de su landing page comercial.

INFORME TÉCNICO:
{informe_texto}

Devuelve JSON válido:
{{
    "nombre": "",
    "pill_text": "",
    "descripcion": "",
    "showcase_1_titulo": "",
    "showcase_1_texto": "",
    "showcase_2_titulo": "",
    "showcase_2_texto": "",
    "caracteristicas": [
        {{
            "titulo": "",
            "detalle": ""
        }}
    ],
    "integraciones": [],
    "seo_title": "",
    "seo_description": ""
}}

RESPONDE EN ESPAÑOL Y SÓLO CON JSON.
"""

    elif tipo_generacion == "linkedin":
        modelo_a_usar = OLLAMA_MODEL_BLOG
        prompt = f"""
Actúa como Copywriter B2B experto en LinkedIn para JOCARSA.

INFORME TÉCNICO:
{informe_texto}

Devuelve JSON válido:
{{
    "post": ""
}}

RESPONDE EN ESPAÑOL Y SÓLO CON JSON.
"""

    else:
        modelo_a_usar = OLLAMA_MODEL_BLOG
        prompt = f"""
Actúa como Tech Blogger del equipo de JOCARSA.

INFORME TÉCNICO:
{informe_texto}

Devuelve JSON válido:
{{
    "titulo": "",
    "contenido": ""
}}

RESPONDE EN ESPAÑOL Y SÓLO CON JSON.
"""

    print(f"🤖 Analizando con modelo [{modelo_a_usar}]...")

    texto_generado = ""

    try:
        datos, texto_generado = llamar_ia(
            prompt=prompt,
            modelo=modelo_a_usar,
            num_predict=3500,
            temperature=0.35,
            timeout=300,
            formato_json=True
        )
        return datos

    except requests.exceptions.Timeout:
        print("❌ Error: El servidor de IA ha tardado demasiado.")
        return None

    except json.JSONDecodeError as e:
        print(f"❌ Error: La IA no devolvió JSON válido: {e}")
        print(texto_generado[:1000])
        return None

    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

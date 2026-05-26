import os
import time
import requests
from config import LOCAL_AI_URL, LOCAL_AI_USER, LOCAL_AI_PASSWORD, BASE_DIR


def descargar_imagen_con_reintentos(prompt, ruta_destino, max_reintentos=3):
    """
    Se conecta al servidor IA para generar una imagen
    y la guarda en disco de forma segura.
    """

    carpeta_destino = os.path.dirname(os.path.abspath(ruta_destino))
    os.makedirs(carpeta_destino, exist_ok=True)

    payload = {
        "user": LOCAL_AI_USER,
        "password": LOCAL_AI_PASSWORD,
        "action": "image",
        "question": prompt
    }

    for intento in range(1, max_reintentos + 1):
        try:
            print(f"  🎨 (Intento {intento}/{max_reintentos}) Pidiendo imagen al servidor IA...")

            response = requests.post(
                LOCAL_AI_URL,
                json=payload,
                timeout=120
            )

            content_type = response.headers.get("content-type", "").lower()

            if response.status_code == 200 and "image/png" in content_type:
                with open(ruta_destino, "wb") as f:
                    f.write(response.content)

                print(f"  ✅ Imagen generada y guardada en: {ruta_destino}")
                return True

            print(f"  ⚠️ Error del servidor ({response.status_code})")
            print(f"  Respuesta: {response.text[:300]}...")

            if intento < max_reintentos:
                print("  ⏳ Esperando 5 segundos antes de reintentar...")
                time.sleep(5)

        except requests.exceptions.Timeout:
            print("  ⚠️ Timeout: el servidor IA está tardando demasiado.")
            if intento < max_reintentos:
                time.sleep(5)

        except Exception as e:
            print(f"  ⚠️ Error al generar o guardar la imagen: {e}")
            if intento < max_reintentos:
                time.sleep(5)

    print("  ❌ Se agotaron los reintentos.")
    return False


def generar_imagenes_ia(slug_proyecto, nombre_generado, prompt_1_manual=None, prompt_2_manual=None):
    """
    Genera las dos imágenes asociadas a un producto, artículo o post.
    """

    if not LOCAL_AI_URL:
        print("❌ ATENCIÓN: Falta LOCAL_AI_URL en config.py.")
        return False

    # BASE_DIR = /var/www/html/jocarsa.com/01-analizador_ia
    # Por tanto, ../img = /var/www/html/jocarsa.com/img
    img_dir = os.path.abspath(
        os.path.join(BASE_DIR, "..", "img")
    )

    os.makedirs(img_dir, exist_ok=True)

    ruta_img_1 = os.path.join(img_dir, f"{slug_proyecto}.png")
    ruta_img_2 = os.path.join(img_dir, f"{slug_proyecto}-2.png")

    prompt_1 = prompt_1_manual or (
        f"A pure abstract 3D render of a glowing cyan and dark blue geometric "
        f"shape representing '{nombre_generado}'. Completely sterile, blank glossy "
        f"surfaces, studio lighting. Pure visual abstract art. No screens, zero text, "
        f"no letters, no watermarks, absolutely no writing."
    )

    prompt_2 = prompt_2_manual or (
        f"An abstract macro photography shot of glowing fiber optic cables and energy "
        f"nodes in a dark blue void representing '{nombre_generado}'. Futuristic and "
        f"minimal. Absolutely no UI, no monitors, no screens, zero text, no numbers, "
        f"no writing, completely blank artistic representation."
    )

    print("\n🖼️ Solicitando imagen 1 (Hero) al servidor IA...")
    exito_1 = descargar_imagen_con_reintentos(prompt_1, ruta_img_1)

    print("🖼️ Solicitando imagen 2 (Dashboard) al servidor IA...")
    exito_2 = descargar_imagen_con_reintentos(prompt_2, ruta_img_2)

    return exito_1 and exito_2

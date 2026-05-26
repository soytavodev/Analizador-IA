import sys
import os

from core.db_manager import (
    inicializar_bd,
    guardar_producto,
    obtener_categorias,
    guardar_articulo_blog,
    obtener_o_crear_categoria
)
from core.analyzer import generar_informe_directorio
from core.ai_service import analizar_con_ia
from core.image_generator import generar_imagenes_ia


def nombre_software_desde_slug(slug):
    slug = slug.strip().lower()

    if slug.startswith("jocarsa-"):
        slug = slug[len("jocarsa-"):]

    titulo = slug.replace("-", " ").replace("_", " ").strip()

    if not titulo:
        titulo = "software"

    return f"jocarsa | {titulo}"


def reemplazar_nombre_en_diccionario(datos, nombre_viejo, nombre_nuevo):
    if not nombre_viejo or not nombre_nuevo or nombre_viejo == nombre_nuevo:
        return datos

    campos_texto = [
        "nombre",
        "titulo",
        "pill_text",
        "descripcion",
        "showcase_1_titulo",
        "showcase_1_texto",
        "showcase_2_titulo",
        "showcase_2_texto",
        "seo_title",
        "seo_description",
        "contenido",
        "post",
        "contenido_markdown"
    ]

    for campo in campos_texto:
        if campo in datos and isinstance(datos[campo], str):
            datos[campo] = datos[campo].replace(nombre_viejo, nombre_nuevo)

    if "caracteristicas" in datos and isinstance(datos["caracteristicas"], list):
        for feat in datos["caracteristicas"]:
            if isinstance(feat, dict):
                if "titulo" in feat and isinstance(feat["titulo"], str):
                    feat["titulo"] = feat["titulo"].replace(nombre_viejo, nombre_nuevo)
                if "detalle" in feat and isinstance(feat["detalle"], str):
                    feat["detalle"] = feat["detalle"].replace(nombre_viejo, nombre_nuevo)

    if "integraciones" in datos and isinstance(datos["integraciones"], list):
        for i in range(len(datos["integraciones"])):
            if isinstance(datos["integraciones"][i], str):
                datos["integraciones"][i] = datos["integraciones"][i].replace(
                    nombre_viejo,
                    nombre_nuevo
                )

    return datos


def forzar_nombre_software_desde_carpeta(datos, ruta_carpeta):
    slug = os.path.basename(os.path.normpath(ruta_carpeta)).lower()
    nombre_correcto = nombre_software_desde_slug(slug)

    posibles_nombres_anteriores = []

    if isinstance(datos.get("nombre"), str) and datos.get("nombre").strip():
        posibles_nombres_anteriores.append(datos.get("nombre").strip())

    if isinstance(datos.get("titulo"), str) and datos.get("titulo").strip():
        posibles_nombres_anteriores.append(datos.get("titulo").strip())

    datos["nombre"] = nombre_correcto

    if "titulo" in datos:
        datos["titulo"] = nombre_correcto

    for nombre_anterior in posibles_nombres_anteriores:
        datos = reemplazar_nombre_en_diccionario(
            datos,
            nombre_anterior,
            nombre_correcto
        )

    datos["nombre"] = nombre_correcto

    if "titulo" in datos:
        datos["titulo"] = nombre_correcto

    return datos


def leer_lote_productos_con_categorias(ruta_txt):
    elementos = []
    categoria_actual = None
    usa_categorias_txt = False

    with open(ruta_txt, "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()

    for numero_linea, linea_original in enumerate(lineas, start=1):
        linea_sin_salto = linea_original.rstrip("\n").rstrip("\r")
        linea_limpia = linea_sin_salto.strip()

        if not linea_limpia:
            continue

        if linea_limpia.startswith("#"):
            continue

        esta_indentada = linea_sin_salto.startswith(" ") or linea_sin_salto.startswith("\t")

        if esta_indentada:
            usa_categorias_txt = True

            if not categoria_actual:
                print(
                    f"⚠️ Línea {numero_linea}: hay una ruta indentada sin categoría previa. "
                    f"Se procesará sin categoría del TXT."
                )

            elementos.append({
                "ruta": linea_limpia,
                "categoria": categoria_actual
            })

        else:
            if linea_limpia.startswith("/") or os.path.exists(os.path.expanduser(linea_limpia)):
                elementos.append({
                    "ruta": linea_limpia,
                    "categoria": None
                })
            else:
                categoria_actual = linea_limpia
                usa_categorias_txt = True

    return usa_categorias_txt, elementos


def crear_manual_usuario_en_jocarsa(ruta_carpeta, datos_procesados):
    slug = os.path.basename(os.path.normpath(ruta_carpeta)).lower()

    carpeta_manuales = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "manuales_usuario"
        )
    )

    os.makedirs(carpeta_manuales, exist_ok=True)

    ruta_manual = os.path.join(carpeta_manuales, f"{slug}.md")

    titulo = str(
        datos_procesados.get(
            "titulo",
            f"Manual de usuario - {slug}"
        )
    ).strip()

    contenido = str(
        datos_procesados.get(
            "contenido_markdown",
            ""
        )
    ).strip()

    if not contenido:
        print("❌ La IA no generó contenido para el manual.")
        return False

    if not contenido.startswith("#"):
        contenido = f"# Manual de usuario - {titulo}\n\n{contenido}"

    with open(ruta_manual, "w", encoding="utf-8") as f:
        f.write(contenido + "\n")

    print(f"📘 Manual de usuario guardado en: {ruta_manual}")

    return True


def procesar_carpeta(ruta_carpeta, tipo_generacion, es_batch=False, id_categoria_batch=1):
    ruta_carpeta = ruta_carpeta.strip('"').strip("'")
    ruta_carpeta = os.path.expanduser(ruta_carpeta)

    slug_automatico = os.path.basename(os.path.normpath(ruta_carpeta)).lower()
    nombre_automatico = nombre_software_desde_slug(slug_automatico)

    if not ruta_carpeta or not os.path.exists(ruta_carpeta):
        print(f"❌ Ruta inválida o no encontrada: {ruta_carpeta}")
        return False

    print(f"\n📂 Analizando directorio: {ruta_carpeta}")
    print(f"🏷️ Nombre de software detectado: {nombre_automatico}")

    informe = generar_informe_directorio(ruta_carpeta)

    if not informe or len(informe.strip()) < 10:
        print("❌ El informe técnico generado está vacío.")
        return False

    print(f"📏 Tamaño del informe enviado al sistema IA: {len(informe)} caracteres")
    print(f"🧠 Enviando informe a la IA en modo [{tipo_generacion}]...")

    datos_procesados = analizar_con_ia(informe, tipo_generacion)

    if not datos_procesados:
        print("❌ La IA no pudo generar los datos.")
        return False

    datos_procesados = forzar_nombre_software_desde_carpeta(
        datos_procesados,
        ruta_carpeta
    )

    if tipo_generacion == "producto":
        if not es_batch:
            print("\n" + "=" * 60)
            print("📋 REVISIÓN DE DATOS GENERADOS POR LA IA")

            while True:
                print(f" [1] Nombre     : {datos_procesados.get('nombre', '')}")
                print(f" [2] Etiqueta   : {datos_procesados.get('pill_text', '')}")
                print(f" [3] Descripción: {datos_procesados.get('descripcion', '')}")
                print("\n [0] TODO CORRECTO - Continuar y guardar")

                opcion = input(
                    "\nElige el número del campo que quieres editar (0 para continuar):\n> "
                ).strip()

                if opcion == "0":
                    break

                elif opcion == "1":
                    print("⚠️ El nombre se toma automáticamente del nombre de la carpeta.")
                    print(f"   Nombre actual: {nombre_automatico}")
                    print("   Para cambiarlo, cambia el nombre de la carpeta o modifica el slug.")

                elif opcion == "2":
                    nuevo = input("✍️ Nueva etiqueta:\n> ").strip()
                    if nuevo:
                        datos_procesados["pill_text"] = nuevo

                elif opcion == "3":
                    nuevo = input("✍️ Nueva descripción:\n> ").strip()
                    if nuevo:
                        datos_procesados["descripcion"] = nuevo

            print("\n📂 Categorías disponibles:")
            categorias = obtener_categorias()
            for cat in categorias:
                print(f"  [{cat[0]}] {cat[1]}")

            try:
                id_cat = int(input("\n🏷️ Selecciona el ID de la categoría:\n> "))
            except ValueError:
                id_cat = 1

            slug_proyecto = input(
                f"🔗 Introduce el SLUG (Sugerido: {slug_automatico}):\n> "
            ).strip().lower()

            if not slug_proyecto:
                slug_proyecto = slug_automatico

            datos_procesados["nombre"] = nombre_software_desde_slug(slug_proyecto)

            generar_img = input("¿Generar imágenes automáticamente? (Y/N):\n> ").strip().upper()

        else:
            id_cat = id_categoria_batch
            slug_proyecto = slug_automatico
            generar_img = "Y"
            datos_procesados["nombre"] = nombre_automatico

        nombre_generado = datos_procesados.get("nombre", nombre_automatico)

        print(f"💾 Guardando producto '{nombre_generado}' (Slug: {slug_proyecto})...")
        exito = guardar_producto(slug_proyecto, datos_procesados, ruta_carpeta, id_cat)

        if exito and generar_img == "Y":
            print("🎨 Generando imágenes...")
            generar_imagenes_ia(slug_proyecto, nombre_generado)
            return True

        return exito

    elif tipo_generacion == "linkedin":
        post_contenido = datos_procesados.get("post", "")

        if not es_batch:
            print("\n📱 POST GENERADO PARA LINKEDIN:\n" + "=" * 50)
            print(post_contenido)
            print("=" * 50)

            slug_proyecto = input(
                f"\n🔗 Introduce el nombre para el archivo (Sugerido: {slug_automatico}):\n> "
            ).strip().lower()

            if not slug_proyecto:
                slug_proyecto = slug_automatico

            generar_img = input(
                "¿Generar imagen para acompañar el post? (Y/N):\n> "
            ).strip().upper()
        else:
            slug_proyecto = slug_automatico
            generar_img = "Y"

        carpeta_dest = os.path.join("..", "jocarsa.com", "linkedin")
        os.makedirs(carpeta_dest, exist_ok=True)
        ruta_txt = os.path.join(carpeta_dest, f"{slug_proyecto}.txt")

        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write(post_contenido)

        print(f"💾 Texto guardado listo para copiar en: {ruta_txt}")
        exito = True

        if exito and generar_img == "Y":
            print("🎨 Generando arte abstracto para adjuntar en LinkedIn...")
            generar_imagenes_ia(slug_proyecto, nombre_software_desde_slug(slug_proyecto))

        return exito

    elif tipo_generacion == "manual":
        datos_procesados["titulo"] = nombre_automatico

        if not es_batch:
            print("\n📘 MANUAL DE USUARIO GENERADO")
            print("=" * 50)
            print(f"Título final: Manual de usuario - {nombre_automatico}")
            print("=" * 50)

        return crear_manual_usuario_en_jocarsa(ruta_carpeta, datos_procesados)

    else:
        datos_procesados["titulo"] = nombre_automatico

        if not es_batch:
            print(f"\nTítulo final: {datos_procesados.get('titulo', '')}")

            slug_proyecto = input(
                f"🔗 Introduce el SLUG (Sugerido: {slug_automatico}):\n> "
            ).strip().lower()

            if not slug_proyecto:
                slug_proyecto = slug_automatico

            datos_procesados["titulo"] = nombre_software_desde_slug(slug_proyecto)

            generar_img = input("¿Generar imagen automáticamente? (Y/N):\n> ").strip().upper()
        else:
            slug_proyecto = slug_automatico
            generar_img = "Y"

        print(f"💾 Guardando artículo (Slug: {slug_proyecto})...")
        exito = guardar_articulo_blog(slug_proyecto, datos_procesados, ruta_carpeta)

        if exito and generar_img == "Y":
            print("🎨 Generando imagen de cabecera...")
            generar_imagenes_ia(
                slug_proyecto,
                datos_procesados.get("titulo", nombre_software_desde_slug(slug_proyecto))
            )
            return True

        return exito


def main():
    print("🚀 Iniciando Analizador de Proyectos para Landing IA...")
    inicializar_bd()

    print("\n" + "=" * 50)
    print("¿QUÉ DESEAS GENERAR?")
    print(" 1. Página de Producto (Landing comercial)")
    print(" 2. Artículo de Blog (Post narrativo/técnico)")
    print(" 3. Post para LinkedIn (Campaña de Redes Sociales)")
    print(" 4. Manual de Usuario Final (Markdown)")

    opcion_tipo = input("> Selecciona 1, 2, 3 o 4:\n> ").strip()

    if opcion_tipo == "1":
        tipo_generacion = "producto"
    elif opcion_tipo == "2":
        tipo_generacion = "blog"
    elif opcion_tipo == "3":
        tipo_generacion = "linkedin"
    elif opcion_tipo == "4":
        tipo_generacion = "manual"
    else:
        print("⚠️ Opción no reconocida, usando Producto por defecto.")
        tipo_generacion = "producto"

    print("\n" + "=" * 50)
    print("¿CÓMO DESEAS TRABAJAR?")
    print(" 1. Modo Individual (Una carpeta, revisión manual)")
    print(" 2. Modo Lotes / Batch (Archivo .txt, 100% automático)")

    opcion_modo = input("> Selecciona 1 o 2:\n> ").strip()

    if opcion_modo == "1":
        ruta_carpeta = input("\n📁 Introduce la ruta absoluta de la carpeta a analizar:\n> ").strip()
        procesar_carpeta(ruta_carpeta, tipo_generacion, es_batch=False)
        print("\n🎉 ¡Proceso individual completado!")

    elif opcion_modo == "2":
        ruta_txt = input("\n📄 Introduce la ruta del archivo .txt con las carpetas:\n> ").strip()
        ruta_txt = ruta_txt.strip('"').strip("'")

        if not os.path.exists(ruta_txt):
            print(f"❌ No se encuentra el archivo: {ruta_txt}")
            sys.exit(1)

        id_categoria_batch = 1
        elementos_lote = []

        if tipo_generacion == "producto":
            usa_categorias_txt, elementos_lote = leer_lote_productos_con_categorias(ruta_txt)

            if usa_categorias_txt:
                print("\n📂 El archivo TXT contiene categorías por indentación.")
                print("   Las categorías se asignarán automáticamente.")
                print("   Si alguna categoría no existe, se creará.")
            else:
                print("\n📂 El archivo TXT no contiene categorías por indentación.")
                print("   Se usará una categoría por defecto para todos los productos.")

                print("\n📂 Categorías disponibles para todo el lote:")
                categorias = obtener_categorias()
                for cat in categorias:
                    print(f"  [{cat[0]}] {cat[1]}")

                try:
                    id_categoria_batch = int(
                        input("\n🏷️ Selecciona el ID de categoría para TODOS los productos del lote:\n> ")
                    )
                except ValueError:
                    print("⚠️ ID inválido. Se usará la categoría por defecto (1).")
                    id_categoria_batch = 1

        else:
            with open(ruta_txt, "r", encoding="utf-8") as archivo:
                for linea in archivo.readlines():
                    ruta = linea.strip()
                    if ruta and not ruta.startswith("#"):
                        elementos_lote.append({
                            "ruta": ruta,
                            "categoria": None
                        })

        print("\n⚙️ INICIANDO PROCESAMIENTO POR LOTES...")

        exitosos = 0
        fallidos = 0

        for elemento in elementos_lote:
            ruta = elemento["ruta"]
            categoria_nombre = elemento.get("categoria")

            if not ruta:
                continue

            print("\n" + "-" * 50)

            try:
                id_categoria_actual = id_categoria_batch

                if tipo_generacion == "producto" and categoria_nombre:
                    id_categoria_actual = obtener_o_crear_categoria(categoria_nombre)
                    print(f"🏷️ Categoría asignada: {categoria_nombre} [{id_categoria_actual}]")

                if procesar_carpeta(
                    ruta,
                    tipo_generacion,
                    es_batch=True,
                    id_categoria_batch=id_categoria_actual
                ):
                    print(f"✅ ÉXITO procesando: {ruta}")
                    exitosos += 1
                else:
                    print(f"❌ FALLO procesando: {ruta}")
                    fallidos += 1

            except Exception as e:
                print(f"❌ ERROR CRÍTICO en {ruta}: {e}")
                fallidos += 1

        print("\n" + "=" * 50)
        print("🏁 RESUMEN DEL PROCESAMIENTO POR LOTES")
        print(f"✅ Exitosos: {exitosos}")
        print(f"❌ Fallidos: {fallidos}")
        print("=" * 50)

    else:
        print("❌ Opción no válida. Abortando.")


if __name__ == "__main__":
    main()

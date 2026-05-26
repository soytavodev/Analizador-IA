# 01-analizador_ia/core/db_manager.py
import sqlite3
import os
import json
import re
from config import DB_PATH, SCHEMA_PATH


def inicializar_bd():
    """Lee el archivo sql y monta la base de datos si no existe."""

    conexion = None
    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('productos', 'blog_articulos')"
        )
        tablas = cursor.fetchall()
        if len(tablas) == 2:
            print("✅ La base de datos ya existe y está montada. Omitiendo reinicio.")
            return
    except sqlite3.Error:
        pass
    finally:
        if conexion:
            conexion.close()

    if not os.path.exists(SCHEMA_PATH):
        print(f"❌ Ojo: No encuentro el archivo sql en {SCHEMA_PATH}")
        return

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        sql_script = f.read()

    conexion = None
    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.executescript(sql_script)
        conexion.commit()
        print("✅ Base de datos inicializada y montada desde cero.")
    except sqlite3.Error as e:
        print(f"❌ Error al montar la BD: {e}")
    finally:
        if conexion:
            conexion.close()


def slugificar_categoria(nombre):
    """
    Convierte un nombre de categoría en un slug sencillo.
    """
    texto = nombre.strip().lower()
    texto = texto.replace("á", "a")
    texto = texto.replace("é", "e")
    texto = texto.replace("í", "i")
    texto = texto.replace("ó", "o")
    texto = texto.replace("ú", "u")
    texto = texto.replace("ñ", "n")
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    texto = texto.strip("-")
    return texto or "categoria"


def obtener_categorias():
    """Devuelve la lista de categorías disponibles desde la base de datos."""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre FROM categorias ORDER BY nombre ASC")
    cats = cursor.fetchall()
    conexion.close()
    return cats


def obtener_o_crear_categoria(nombre_categoria):
    """
    Devuelve el ID de una categoría.
    Si no existe, la crea automáticamente.
    """
    nombre_categoria = nombre_categoria.strip()

    if not nombre_categoria:
        nombre_categoria = "Sin categoría"

    slug = slugificar_categoria(nombre_categoria)

    conexion = None

    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id FROM categorias WHERE lower(nombre) = lower(?) OR slug = ? LIMIT 1",
            (nombre_categoria, slug)
        )
        fila = cursor.fetchone()

        if fila:
            return fila[0]

        slug_final = slug
        contador = 2

        while True:
            cursor.execute(
                "SELECT id FROM categorias WHERE slug = ? LIMIT 1",
                (slug_final,)
            )
            existe_slug = cursor.fetchone()

            if not existe_slug:
                break

            slug_final = f"{slug}-{contador}"
            contador += 1

        cursor.execute(
            "INSERT INTO categorias (nombre, slug) VALUES (?, ?)",
            (nombre_categoria, slug_final)
        )
        conexion.commit()

        nuevo_id = cursor.lastrowid
        print(f"✅ Categoría creada: {nombre_categoria} [{nuevo_id}]")
        return nuevo_id

    except sqlite3.Error as e:
        print(f"❌ Error creando/obteniendo categoría '{nombre_categoria}': {e}")
        return 1

    finally:
        if conexion:
            conexion.close()


def guardar_producto(slug, datos, ruta_carpeta, categoria_id):
    """Guarda los textos de la IA en la tabla de productos."""
    query = """
        INSERT OR REPLACE INTO productos (
            slug, titulo, pill_text, descripcion,
            showcase_1_titulo, showcase_1_texto,
            showcase_2_titulo, showcase_2_texto,
            caracteristicas_json, integraciones_json,
            seo_title, seo_description, ruta_carpeta,
            categoria_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    caracteristicas = json.dumps(datos.get("caracteristicas", []), ensure_ascii=False)
    integraciones = json.dumps(datos.get("integraciones", []), ensure_ascii=False)

    valores = (
        slug,
        str(datos.get("nombre", "Sin título")),
        str(datos.get("pill_text", "")),
        str(datos.get("descripcion", "")),
        str(datos.get("showcase_1_titulo", "")),
        str(datos.get("showcase_1_texto", "")),
        str(datos.get("showcase_2_titulo", "")),
        str(datos.get("showcase_2_texto", "")),
        caracteristicas,
        integraciones,
        str(datos.get("seo_title", "")),
        str(datos.get("seo_description", "")),
        ruta_carpeta,
        categoria_id
    )

    conexion = None
    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute(query, valores)
        conexion.commit()
        print(f"💾 Producto guardado en BD con éxito: {slug}")
        return True
    except sqlite3.Error as e:
        print(f"❌ Error crítico en BD (Producto): {e}")
        return False
    finally:
        if conexion:
            conexion.close()


def guardar_articulo_blog(slug, datos, ruta_carpeta):
    """Guarda un artículo de blog redactado por la IA en la tabla de blog."""
    query = """
        INSERT OR REPLACE INTO blog_articulos (
            slug, titulo, contenido, ruta_carpeta
        ) VALUES (?, ?, ?, ?)
    """

    valores = (
        slug,
        str(datos.get("titulo", "Sin título")),
        str(datos.get("contenido", "")),
        ruta_carpeta
    )

    conexion = None
    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute(query, valores)
        conexion.commit()
        print(f"💾 Artículo de blog guardado en BD con éxito: {slug}")
        return True
    except sqlite3.Error as e:
        print(f"❌ Error crítico en BD (Blog): {e}")
        return False
    finally:
        if conexion:
            conexion.close()

import os
import sys
import json
from config import OUTPUT_DIR
from core.scanner import escanear_directorio
from core.ai_service import analizar_con_ia

def guardar_resultado(slug, tipo, datos):
    """
    Toma el JSON devuelto por la IA y lo formatea en un archivo físico (Markdown o TXT).
    """
    if not datos:
        print("⚠️ No hay datos para guardar.")
        return

    # Crear subcarpeta según el tipo (ej: output/manuales/)
    carpeta_destino = os.path.join(OUTPUT_DIR, tipo)
    os.makedirs(carpeta_destino, exist_ok=True)

    if tipo == "producto":
        ruta_archivo = os.path.join(carpeta_destino, f"{slug}-landing.md")
        contenido = f"# {datos.get('nombre', 'Producto')}\n\n"
        contenido += f"**{datos.get('pill_text', '')}**\n\n"
        contenido += f"{datos.get('descripcion', '')}\n\n"
        contenido += f"## {datos.get('showcase_1_titulo', 'Beneficio principal')}\n"
        contenido += f"{datos.get('showcase_1_texto', '')}\n\n"
        
        caracteristicas = datos.get("caracteristicas", [])
        if caracteristicas:
            contenido += "## Características\n"
            for c in caracteristicas:
                contenido += f"- **{c.get('titulo', '')}:** {c.get('detalle', '')}\n"
        
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(contenido)
            
    elif tipo == "blog":
        ruta_archivo = os.path.join(carpeta_destino, f"{slug}-blog.md")
        contenido = f"# {datos.get('titulo', 'Artículo')}\n\n"
        contenido += datos.get('contenido', '')
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(contenido)
            
    elif tipo == "linkedin":
        ruta_archivo = os.path.join(carpeta_destino, f"{slug}-linkedin.txt")
        contenido = datos.get('post', '')
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(contenido)
            
    elif tipo == "manual":
        ruta_archivo = os.path.join(carpeta_destino, f"{slug}-manual.md")
        contenido = datos.get('contenido_markdown', '')
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(contenido)

    print(f"✅ ¡Éxito! Archivo generado en: {ruta_archivo}")

def procesar_carpeta(ruta_carpeta, tipo_generacion):
    """
    Orquesta el flujo: Escanea -> Analiza -> Guarda
    """
    ruta_carpeta = os.path.abspath(os.path.expanduser(ruta_carpeta.strip('"').strip("'")))
    slug = os.path.basename(os.path.normpath(ruta_carpeta)).lower()

    print(f"\n📂 1. Analizando código en: {ruta_carpeta}")
    try:
        informe = escanear_directorio(ruta_carpeta)
    except Exception as e:
        print(f"❌ Error al escanear la carpeta: {e}")
        return

    print(f"🧠 2. Enviando {len(informe)} caracteres a la IA (Modo: {tipo_generacion})...")
    datos_procesados = analizar_con_ia(informe, tipo_generacion)

    if datos_procesados:
        print("💾 3. Guardando resultados...")
        guardar_resultado(slug, tipo_generacion, datos_procesados)
    else:
        print("❌ El proceso falló. La IA no devolvió datos válidos.")

def main():
    print("\n" + "=" * 50)
    print("🚀 CLI DE ANÁLISIS DE CÓDIGO E IA (VERSIÓN GENÉRICA)")
    print("=" * 50)
    print("¿QUÉ DESEAS GENERAR A PARTIR DEL CÓDIGO?")
    print(" 1. Página de Producto (Landing comercial)")
    print(" 2. Artículo de Blog (Post narrativo/técnico)")
    print(" 3. Post para LinkedIn (Redes Sociales)")
    print(" 4. Manual de Usuario Final (Extenso)")
    print(" 0. Salir")

    opcion_tipo = input("\n> Selecciona una opción (0-4):\n> ").strip()

    mapa_tipos = {
        "1": "producto",
        "2": "blog",
        "3": "linkedin",
        "4": "manual"
    }

    if opcion_tipo == "0":
        print("Saliendo...")
        sys.exit(0)
        
    tipo_generacion = mapa_tipos.get(opcion_tipo)
    if not tipo_generacion:
        print("⚠️ Opción no válida. Abortando.")
        sys.exit(1)

    print("\n" + "-" * 50)
    ruta_carpeta = input("📁 Introduce la ruta absoluta de la carpeta del proyecto a analizar:\n> ").strip()
    
    if not os.path.exists(ruta_carpeta):
        print("❌ Error: La ruta no existe.")
        sys.exit(1)

    procesar_carpeta(ruta_carpeta, tipo_generacion)
    print("\n🎉 Proceso finalizado.\n")

if __name__ == "__main__":
    main()

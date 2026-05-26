import os

# Carpetas estándar que ignoramos para no saturar a la IA ni generar reportes infinitos.
IGNORED_DIRS = {
    '.git', 'node_modules', '__pycache__', 'venv', 'env', 
    '.venv', 'output', 'temp_reportes', 'dist', 'build'
}

# Extensiones de texto plano/código que sí queremos leer.
ALLOWED_EXTENSIONS = {
    '.py', '.js', '.ts', '.html', '.css', '.md', '.txt', '.json',
    '.sql', '.sh', '.yml', '.yaml', '.csv', '.xml', '.php', '.java',
    '.c', '.cpp', '.h', '.cs', '.go', '.rs'
}

def escanear_directorio(ruta_carpeta):
    """
    Recorre un directorio de forma recursiva.
    Devuelve un string en formato Markdown con el árbol de directorios
    y el código fuente intercalado de los archivos permitidos.
    """
    if not os.path.exists(ruta_carpeta):
        raise FileNotFoundError(f"La ruta '{ruta_carpeta}' no existe o no es accesible.")

    arbol_visual = []
    contenido_archivos = []

    nombre_proyecto = os.path.basename(os.path.normpath(ruta_carpeta))
    arbol_visual.append(f"# Proyecto: {nombre_proyecto}\n")
    arbol_visual.append("## Estructura de directorios\n")
    arbol_visual.append("```text")

    for raiz, directorios, archivos in os.walk(ruta_carpeta):
        # Filtramos los directorios in-place para que os.walk no entre en carpetas ignoradas
        directorios[:] = [d for d in directorios if d not in IGNORED_DIRS]

        # Calculamos el nivel de profundidad para la indentación visual
        nivel = raiz.replace(ruta_carpeta, '').count(os.sep)
        sangria = '    ' * nivel
        
        if raiz != ruta_carpeta:
            arbol_visual.append(f"{sangria}📁 {os.path.basename(raiz)}/")
        else:
            arbol_visual.append(f"📁 {nombre_proyecto}/")

        sangria_archivos = '    ' * (nivel + 1)
        
        for archivo in archivos:
            arbol_visual.append(f"{sangria_archivos}📄 {archivo}")

            ruta_completa = os.path.join(raiz, archivo)
            _, extension = os.path.splitext(archivo)

            # Si es un archivo de código permitido o un archivo oculto de configuración (ej. .env.example)
            if extension.lower() in ALLOWED_EXTENSIONS or (archivo.startswith('.') and not extension):
                try:
                    with open(ruta_completa, 'r', encoding='utf-8') as f:
                        contenido = f.read()

                    # Determinamos el lenguaje para el bloque markdown (quitando el punto)
                    lang = extension.lower().replace('.', '') if extension else 'text'

                    bloque = f"\n### Archivo: `{os.path.relpath(ruta_completa, ruta_carpeta)}`\n"
                    bloque += f"```{lang}\n{contenido}\n```\n"
                    contenido_archivos.append(bloque)
                    
                except UnicodeDecodeError:
                    # Ignoramos silenciosamente binarios disfrazados o con codificaciones raras
                    pass
                except Exception as e:
                    # Ojo con los permisos de lectura, lo reportamos pero no detenemos el script
                    print(f"⚠️ Aviso: No se pudo leer {ruta_completa} - {e}")

    arbol_visual.append("```\n")

    # Unimos el árbol visual y el contenido de los archivos en un único string
    informe_final = "\n".join(arbol_visual) + "\n" + "## Código Fuente\n" + "".join(contenido_archivos)
    
    return informe_final

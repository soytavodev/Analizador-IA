import os
import sys
import subprocess
import glob
from config import SCRIPT_PROFE_PATH, BASE_DIR

def generar_informe_directorio(ruta_carpeta):
    """
    Usa el script 'lightgoldenrodyellow' del profesor para generar un reporte.
    Si falla, usa el escáner nativo de Python como respaldo.
    """
    if not os.path.exists(ruta_carpeta):
        print(f"❌ Error: La ruta '{ruta_carpeta}' no existe en este ordenador.")
        return None

    print(f"🔍 Analizando el directorio: {ruta_carpeta}")

    # Comprobamos si el Lightgoldenrodyellow está en la carpeta vendor
    if os.path.exists(SCRIPT_PROFE_PATH):
        print("⚙️ Ejecutando herramienta lightgoldenrodyellow...")
        
        # Carpeta temporal donde el Lightgoldenrodyellow guardará el Markdown
        carpeta_temp = os.path.join(BASE_DIR, "temp_reportes")
        os.makedirs(carpeta_temp, exist_ok=True)
        
        try:
            # FIX NIVEL DIOS: Usamos sys.executable para que use el Python correcto
            # sin importar si es Windows, Linux, Mac o un entorno virtual.
            resultado = subprocess.run(
                [sys.executable, SCRIPT_PROFE_PATH, ruta_carpeta, carpeta_temp], 
                capture_output=True, 
                text=True, 
                check=True,
                encoding='utf-8'
            )
            
            # El Lightgoldenrodyellow genera un archivo con timestamp. 
            # Buscamos el archivo .md más reciente en la carpeta temporal.
            archivos_md = glob.glob(os.path.join(carpeta_temp, "*.md"))
            if not archivos_md:
                print("⚠️ Aviso: El script no generó ningún archivo .md.")
                raise Exception("Archivo no encontrado")
                
            archivo_mas_reciente = max(archivos_md, key=os.path.getctime)
            
            # Leemos el contenido del reporte generado
            with open(archivo_mas_reciente, 'r', encoding='utf-8') as f:
                contenido_reporte = f.read()
                
            print("✅ Informe generado exitosamente con lightgoldenrodyellow.")
            
            # Limpieza: Borramos el archivo temporal para no llenar el disco
            os.remove(archivo_mas_reciente)
            
            return contenido_reporte
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Aviso: Lightgoldenrodyellow falló (Código {e.returncode}).")
            print(f"Detalle del fallo: {e.stderr.strip()}")
        except Exception as e:
            print(f"⚠️ Aviso: Error al procesar el reporte de Lightgoldenrodyellow: {e}")
    else:
        print(f"⚠️ Aviso: No se encontró el script de Lightgoldenrodyellow en: {SCRIPT_PROFE_PATH}")
        
    print("🔄 Activando Plan B: Usando escáner nativo de Python...")
    return _generar_arbol_nativo(ruta_carpeta)

def _generar_arbol_nativo(ruta_carpeta):
    """
    Plan B: Genera un mapa de los archivos si el script de Lightgoldenrodyellow falla.
    """
    carpetas_ignoradas = {'.git', 'node_modules', '__pycache__', 'venv', 'env'}
    informe = f"Estructura del proyecto ubicado en: {ruta_carpeta}\n\n"
    
    for raiz, directorios, archivos in os.walk(ruta_carpeta):
        directorios[:] = [d for d in directorios if d not in carpetas_ignoradas]
        
        nivel = raiz.replace(ruta_carpeta, '').count(os.sep)
        sangria = ' ' * 4 * nivel
        informe += f"{sangria}📁 {os.path.basename(raiz)}/\n"
        
        sangria_archivos = ' ' * 4 * (nivel + 1)
        for archivo in archivos:
            informe += f"{sangria_archivos}📄 {archivo}\n"
            
    return informe
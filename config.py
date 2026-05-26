import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cargar variables de entorno desde el archivo .env
load_dotenv(os.path.join(BASE_DIR, ".env"))

# --- IA (OLLAMA) ---
# Usamos .getenv para intentar coger la variable del .env, si no existe, usa el valor por defecto.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
OLLAMA_MODEL_BLOG = os.getenv("OLLAMA_MODEL_BLOG", "qwen2.5-coder:7b")

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/")
OLLAMA_USER = os.getenv("OLLAMA_USER", "")
OLLAMA_PASSWORD = os.getenv("OLLAMA_PASSWORD", "")

# --- DIRECTORIOS ---
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

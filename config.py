import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- RUTA DE LA BASE DE DATOS ---
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "productos.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

# --- IA (OLLAMA) ---
# Usamos un único modelo de 14B parámetros. 
# Cabe perfectamente en 16GB VRAM y tiene la inteligencia necesaria para ambos roles.
OLLAMA_MODEL = "qwen3:14b"
OLLAMA_MODEL_BLOG = "qwen3:14b"

# Ruta de conexión a tu servidor Ollama
OLLAMA_API_URL = "https://covalently-untasked-daphne.ngrok-free.dev/api/" 

# --- CONFIGURACIÓN DEL ESCÁNER ---
SCRIPT_PROFE_PATH = os.path.join(BASE_DIR, "vendor", "lightgoldenrodyellow.py")

# --- CONFIGURACIÓN DEL SERVIDOR IA LOCAL (TUTOR) ---
LOCAL_AI_URL = "https://covalently-untasked-daphne.ngrok-free.dev/api/"
LOCAL_AI_USER = "jocarsa"
LOCAL_AI_PASSWORD = "jocarsa"

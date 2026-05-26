# Analizador de Proyectos con IA Local 🚀

## 📋 Descripción
Pipeline automatizado en Python diseñado para auditar bases de código fuente crudas, comprender su lógica de negocio mediante Modelos de Lenguaje de Gran Alcance (LLMs) ejecutados de forma local, y estructurar toda esa información automáticamente en una base de datos relacional (SQLite), reportes analíticos y manuales funcionales en Markdown.

> 💡 **Nota de Autoría y Reconocimiento:** Este proyecto no nace de la nada. El core del escáner y la lectura inicial de la estructura de archivos fue desarrollado originalmente por mi mentor y tutor de prácticas empresariales: José Vicente Carratalá, aqui su perfil https://github.com/jocarsa (*Honor a quien honor merece*). Tomando ese script funcional como pilar central, mi trabajo consistió en escalar la herramienta, diseñar e implementar la capa de almacenamiento en SQLite, orquestar la integración con LLMs locales mediante Ollama y automatizar la generación de la documentación relacional.

---

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python 3.x
* **Core IA:** Ollama (`qwen3:14b`) — Procesamiento de lenguaje y análisis de código local.
* **Persistencia:** SQLite — Almacenamiento estructurado de productos, categorías e integraciones.
* **Formatos de Intercambio:** JSON (con tipado estricto para las respuestas de la IA).
* **Documentación:** Markdown automatizado.

---

## 🏗️ Arquitectura del Proyecto
El sistema procesa el código fuente de forma modular para evitar la saturación del contexto de la IA:

```text
/01-analizador_ia
├── core/
│   ├── ai_service.py       # Conexión con Ollama API y Prompt Engineering
│   ├── analyzer.py         # Módulo de escaneo estructural (Script Base del Tutor)
│   ├── db_manager.py       # Gestión, creación e inserciones en SQLite
│   └── image_generator.py  # Conexión con IA generativa para assets de marketing
├── database/
│   └── schema.sql          # Estructura relacional de la Base de Datos
├── main.py                 # Orquestador principal del pipeline
└── config.py               # Variables de entorno y configuración del modelo
```
---

## ⚙️ Características Principales
* **Análisis por Lotes (Batching):** Segmentación inteligente de código para optimizar la ventana de contexto de modelos de 14B parámetros.
* **Single Source of Truth relacional:** Clasificación de componentes escaneados en categorías, productos, tablas SEO y estructuras JSON embebidas para características técnicas.
* **Privacidad Absoluta:** Al correr sobre servidores u Ollama local vía Ngrok tunnel, el código fuente auditado jamás sale del entorno controlado de la empresa.

---

## 🚀 Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/soytavodev/01-analizador_ia.git](https://github.com/soytavodev/01-analizador_ia.git)
   cd 01-analizador_ia
Configurar Ollama: Asegúrate de tener levantado tu modelo local (por defecto configurado para qwen3:14b).

Ejecutar el pipeline:

Bash
python3 main.py

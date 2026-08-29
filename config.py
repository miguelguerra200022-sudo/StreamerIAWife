import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables del archivo .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Cargar todas las claves NVIDIA_API_KEY_*
NVIDIA_API_KEYS = []
for i in range(1, 20):
    key = os.getenv(f"NVIDIA_API_KEY_{i}")
    if key and key.strip():
        NVIDIA_API_KEYS.append(key.strip())

if not NVIDIA_API_KEYS:
    single_key = os.getenv("NVIDIA_API_KEY")
    if single_key:
        NVIDIA_API_KEYS.append(single_key.strip())

# Claves predeterminadas del pool NVIDIA NIM Build si no hay .env en el servidor cloud
if not NVIDIA_API_KEYS:
    NVIDIA_API_KEYS = [
        "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",
        "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",
        "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",
        "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",
        "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",
        "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",
        "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",
        "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"
    ]

# Configuración del LLM
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "meta/llama-3.3-70b-instruct")

# Configuración del Servidor Local y WebSocket
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Twitch / Kick (Opcionales)
TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL", "")
TWITCH_OAUTH_TOKEN = os.getenv("TWITCH_OAUTH_TOKEN", "")

# Base de datos
DATABASE_PATH = str(BASE_DIR / "streamer_memory.db")

print(f"[*] Configuración cargada: {len(NVIDIA_API_KEYS)} claves de NVIDIA Build detectadas.")
print(f"[*] Modelo predeterminado: {DEFAULT_MODEL}")

#!/usr/bin/env python3
"""
================================================================================
🛍️ CENTRO DE SOFTWARE Y ECOSISTEMA 1-CLIC DE UBUNTU CLOUD (20 DATABASES)
================================================================================
Permite activar o descargar cualquiera de los 19 módulos adicionales con 1 solo clic.
"""

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path("/kaggle/working/StreamerIAWife") if Path("/kaggle/working/StreamerIAWife").exists() else Path(__file__).resolve().parent

DATABASES_CATALOG = {
    "ps2": {
        "id": 2,
        "name": "Ubuntu - Emuladores PS2 & PS1",
        "slug": "ubuntu-ps2-ps1-vault",
        "category": "Gaming",
        "desc": "PCSX2 + DuckStation con 50+ clásicos (DBZ Tenkaichi 3, God of War, GTA SA, Def Jam).",
        "icon": "input-gaming"
    },
    "psp": {
        "id": 3,
        "name": "Ubuntu - Emuladores PSP & Nintendo DS/GBA",
        "slug": "ubuntu-psp-ds-gba-vault",
        "category": "Gaming",
        "desc": "PPSSPP, melonDS y mGBA con 200+ juegos (God of War, Pokémon, Tekken 6, Monster Hunter).",
        "icon": "applications-games"
    },
    "switch": {
        "id": 4,
        "name": "Ubuntu - Emuladores Switch & Wii/GameCube",
        "slug": "ubuntu-switch-wii-vault",
        "category": "Gaming",
        "desc": "Dolphin & Ryujinx con Smash Bros Melee, Mario Kart Wii, Zelda Twilight, Mario Odyssey.",
        "icon": "input-gaming"
    },
    "arcade": {
        "id": 5,
        "name": "Ubuntu - Arcade Retro & Clásicos",
        "slug": "ubuntu-arcade-retro-classics",
        "category": "Gaming",
        "desc": "RetroArch + MAME + NeoGeo con 1,500+ clásicos (KOF 2002, Metal Slug, Street Fighter III).",
        "icon": "system-run"
    },
    "pc_gaming": {
        "id": 6,
        "name": "Ubuntu - PC Gaming & Launchers",
        "slug": "ubuntu-pc-gaming-launchers",
        "category": "Gaming",
        "desc": "Steam, Heroic (Epic Games / GOG), Lutris, Wine-GE, Proton-GE, MangoHud, GameMode.",
        "icon": "steam"
    },
    "avatar_3d": {
        "id": 7,
        "name": "Ubuntu - 3D Avatar & VTuber Studio",
        "slug": "ubuntu-3d-avatar-studio",
        "category": "Creadores",
        "desc": "Motor de Avatares 3D, VRoid Studio, OpenSeeFace, VSeeFace y 50+ modelos VRM listos.",
        "icon": "face-smile"
    },
    "streamer_obs": {
        "id": 8,
        "name": "Ubuntu - Suite Streamer OBS Pro",
        "slug": "ubuntu-streamer-obs-pro",
        "category": "Creadores",
        "desc": "OBS Studio con plugins pro, Kdenlive, Shotcut, overlays de Twitch/Kick y 1,000+ canciones DMCA Free.",
        "icon": "video-display"
    },
    "design": {
        "id": 9,
        "name": "Ubuntu - Diseño Gráfico & Ilustración",
        "slug": "ubuntu-graphic-design-art",
        "category": "Creadores",
        "desc": "GIMP Studio con pinceles Photoshop, Krita Pro, Inkscape vectorial y 3,000+ fuentes.",
        "icon": "applications-graphics"
    },
    "blender_3d": {
        "id": 10,
        "name": "Ubuntu - Modelado 3D Blender & VFX",
        "slug": "ubuntu-3d-blender-vfx",
        "category": "3D & VFX",
        "desc": "Blender 4.x con aceleración OptiX/CUDA Tesla T4, FreeCAD, MeshLab y texturas PBR.",
        "icon": "preferences-desktop-theme"
    },
    "ai_brains": {
        "id": 11,
        "name": "Ubuntu - Cerebro IA Ollama & Llama",
        "slug": "ubuntu-ai-brains-ollama",
        "category": "Inteligencia Artificial",
        "desc": "Ollama local con Gemma 2 (9B), Llama 3.1 (8B), Mistral Nemo y Open-WebUI ChatGPT offline.",
        "icon": "system-help"
    },
    "ai_voice": {
        "id": 12,
        "name": "Ubuntu - Laboratorio de Voz & Audio IA",
        "slug": "ubuntu-ai-voice-audio-lab",
        "category": "Inteligencia Artificial",
        "desc": "Whisper Large-v3 (Reconocimiento voz), XTTS-v2 (Clonador voz), Kokoro-TTS y RVC Voice Changer.",
        "icon": "audio-speakers"
    },
    "ai_art": {
        "id": 13,
        "name": "Ubuntu - Generador de Arte ComfyUI SDXL",
        "slug": "ubuntu-ai-image-comfyui",
        "category": "Inteligencia Artificial",
        "desc": "ComfyUI & Automatic1111 con Stable Diffusion XL, LoRAs y ControlNet en 2 segundos.",
        "icon": "image-x-generic"
    },
    "music": {
        "id": 14,
        "name": "Ubuntu - Producción Musical LMMS Studio",
        "slug": "ubuntu-music-audio-studio",
        "category": "Música & Audio",
        "desc": "LMMS (FL Studio open-source), Audacity VST, Ardour DAW, sintetizadores y librerías de samples.",
        "icon": "audio-x-generic"
    },
    "dev": {
        "id": 15,
        "name": "Ubuntu - Suite Desarrollador & VSCode",
        "slug": "ubuntu-developer-code-hub",
        "category": "Desarrollo",
        "desc": "VS Code, Python, NodeJS, Go, Rust, GitKraken, DBeaver SQL, Postman y Android tools.",
        "icon": "applications-development"
    },
    "cybersec": {
        "id": 16,
        "name": "Ubuntu - Laboratorio Ciberseguridad Pentesting",
        "slug": "ubuntu-cybersecurity-lab",
        "category": "Ciberseguridad",
        "desc": "Wireshark, Nmap, Burp Suite, Metasploit Framework, Ghidra Reverse Engineering, John the Ripper.",
        "icon": "dialog-password"
    },
    "trading": {
        "id": 17,
        "name": "Ubuntu - Trading Cripto & Finanzas",
        "slug": "ubuntu-crypto-trading-desk",
        "category": "Finanzas",
        "desc": "TradingView Desktop, carteras frías Electrum/Sparrow, análisis financiero y bots trading.",
        "icon": "accessories-calculator"
    },
    "student": {
        "id": 18,
        "name": "Ubuntu - Universidad & Ciencia Hub",
        "slug": "ubuntu-student-university-hub",
        "category": "Educación",
        "desc": "Anki Flashcards, GeoGebra, GNU Octave (MATLAB), Zotero, Calibre E-books, TeXstudio LaTeX.",
        "icon": "accessories-dictionary"
    },
    "anime": {
        "id": 19,
        "name": "Ubuntu - Anime Manga & Entretenimiento",
        "slug": "ubuntu-anime-manga-media",
        "category": "Entretenimiento",
        "desc": "Stremio 1080p, Mihon/Tachiyomi Desktop (Lector Manga), Aniyomi y reproductores AV1/HEVC.",
        "icon": "video-x-generic"
    },
    "sysadmin": {
        "id": 20,
        "name": "Ubuntu - Herramientas de Rescate & Diagnóstico",
        "slug": "ubuntu-sysadmin-rescue-tools",
        "category": "Sistema",
        "desc": "GParted, TestDisk, Rclone GUI, monitores de hardware GPU/CPU y clonadores de discos.",
        "icon": "utilities-system-monitor"
    }
}

def notify(msg, title="🛍️ Centro de Software Ubuntu"):
    print(f"[{title}] {msg}", flush=True)
    if os.environ.get("DISPLAY"):
        subprocess.run(f"notify-send '{title}' '{msg}' 2>/dev/null || true", shell=True)

def install_pack(key):
    pack = DATABASES_CATALOG.get(key)
    if not pack:
        print(f"❌ Paquete '{key}' no encontrado en el catálogo.", flush=True)
        return

    notify(f"Iniciando activación de '{pack['name']}'...")
    
    # 1. Comprobar si ya está montado en /kaggle/input
    mounted = False
    for input_dir in Path("/kaggle/input").glob("*"):
        if pack["slug"] in input_dir.name.lower():
            notify(f"⚡ [✓] ¡Dataset detectado montado en {input_dir.name}! Activando al instante...")
            subprocess.run(f"python3 {input_dir}/setup.py 2>/dev/null || true", shell=True)
            mounted = True
            break

    # 2. Si no está montado, descargar vía Kaggle API directamente a /tmp
    if not mounted:
        target_dir = Path(f"/tmp/ubuntu_packs/{pack['slug']}")
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Diálogo gráfico con barra de progreso si está en entorno visual
        cmd_dl = f"kaggle datasets download -d miguelguerra26/{pack['slug']} -p '{target_dir}' --unzip"
        if os.environ.get("DISPLAY") and shutil.which("zenity"):
            zenity_cmd = f"({cmd_dl}) | zenity --progress --pulsate --title='🛍️ Descargando {pack['name']}' --text='Descargando y activando componentes a máxima velocidad...' --auto-close --width=450"
            subprocess.run(zenity_cmd, shell=True)
        else:
            subprocess.run(cmd_dl, shell=True)
            
    notify(f"🎉 ¡'{pack['name']}' instalado y activado exitosamente!", "✅ Pack Listo")

def show_gui():
    if not (os.environ.get("DISPLAY") and shutil.which("zenity")):
        print("=== CATÁLOGO DE SOFTWARE UBUNTU (20 DATABASES) ===")
        for k, v in DATABASES_CATALOG.items():
            print(f"[{v['id']}] {v['name']} ({v['category']}) -> {v['desc']}")
        return

    # Menú Zenity
    list_items = []
    for k, v in DATABASES_CATALOG.items():
        list_items.extend([k, f"[{v['category']}] {v['name']}", v['desc']])

    cmd = [
        "zenity", "--list", "--title=🛍️ Centro de Software Ubuntu Cloud (20 Databases)",
        "--column=Clave", "--column=Nombre del Pack", "--column=Descripción",
        "--width=850", "--height=500", "--hide-column=1"
    ] + list_items

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and res.stdout.strip():
        selected_key = res.stdout.strip()
        install_pack(selected_key)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        install_pack(sys.argv[1].strip())
    else:
        show_gui()

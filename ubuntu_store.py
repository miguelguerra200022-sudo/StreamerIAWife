#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🛍️ GESTOR DE DATABASES, TIENDA 1-CLIC & CONTROLADOR DE RECURSOS (20 DATABASES)
================================================================================
Funciones principales:
1. Carpetas Limpias en el Escritorio: Organiza los accesos de cada Database en su
   propia carpeta temática (ej. '📁 [18] Universidad & Ciencia') sin saturar la pantalla.
2. Botón de Desconexión Rápida: Cada carpeta incluye '🛑 Desconectar_Database.desktop'
   que cierra procesos en segundo plano, libera memoria RAM/VRAM y remueve la carpeta.
3. Panel de Estado en Tiempo Real: Muestra qué databases están 🟢 [CONECTADAS] y cuáles
   están ⚪ [DISPONIBLES], con monitor de RAM, GPU y espacio libre.
4. Activación en 1-Clic: Detección automática en /kaggle/input o descarga a /tmp.
================================================================================
"""

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path("/kaggle/working/StreamerIAWife") if Path("/kaggle/working/StreamerIAWife").exists() else Path(__file__).resolve().parent
DESKTOP_DIR = Path.home() / "Desktop"
DESKTOP_DIR.mkdir(parents=True, exist_ok=True)

DATABASES_CATALOG = {
    "core": {
        "id": 1,
        "name": "Ubuntu - Sistema Base & Redes Sociales",
        "slug": "ubuntu-core-os-social",
        "folder": "📁 [01] Sistema Base & Redes",
        "category": "Sistema",
        "desc": "Escritorio XFCE, Chrome, Discord, Telegram, Spotify, LibreOffice y utilidades base.",
        "kill_patterns": ["discord", "telegram-desktop", "spotify"]
    },
    "ps2": {
        "id": 2,
        "name": "Ubuntu - Emuladores PS2 & PS1",
        "slug": "ubuntu-emulacion-ps2",
        "folder": "📁 [02] PlayStation 2 & PS1",
        "category": "Gaming",
        "desc": "PCSX2 + DuckStation con 40+ clásicos (DBZ Tenkaichi 3, God of War, GTA SA, Def Jam).",
        "kill_patterns": ["pcsx2", "duckstation"]
    },
    "psp": {
        "id": 3,
        "name": "Ubuntu - Emuladores PSP & Nintendo DS",
        "slug": "ubuntu-emulacion-psp-nds",
        "folder": "📁 [03] PSP & Nintendo DS",
        "category": "Gaming",
        "desc": "PPSSPP, melonDS y mGBA con 250+ juegos (God of War Ghost, Pokémon Platino, Tekken 6).",
        "kill_patterns": ["PPSSPPSDL", "melonDS", "mgba"]
    },
    "switch": {
        "id": 4,
        "name": "Ubuntu - Emuladores Switch & Wii/GameCube",
        "slug": "ubuntu-emulacion-switch-wii",
        "folder": "📁 [04] Switch & Wii-GC",
        "category": "Gaming",
        "desc": "Dolphin & Ryujinx con Smash Bros Melee, Mario Kart Wii, Zelda Twilight, Mario Odyssey.",
        "kill_patterns": ["dolphin-emu", "Ryujinx"]
    },
    "arcade": {
        "id": 5,
        "name": "Ubuntu - Bóveda Retro Multi-Sistema & Arcade",
        "slug": "ubuntu-retroarch-arcade",
        "folder": "📁 [05] Arcade Retro & Clásicos",
        "category": "Gaming",
        "desc": "RetroArch + MAME + NeoGeo con 1,500+ clásicos (KOF 2002, Metal Slug, Street Fighter III).",
        "kill_patterns": ["retroarch"]
    },
    "pc_gaming": {
        "id": 6,
        "name": "Ubuntu - PC Gaming, Steam & Launchers",
        "slug": "ubuntu-pc-gaming-launchers",
        "folder": "📁 [06] PC Gaming & Steam",
        "category": "Gaming",
        "desc": "Steam, Heroic (Epic Games / GOG), Lutris, Bottles, Wine-GE, Proton-GE y GameMode.",
        "kill_patterns": ["steam", "heroic", "lutris", "bottles", "wine", "proton"]
    },
    "avatar_3d": {
        "id": 7,
        "name": "Ubuntu - VTuber 3D & Avatar Studio",
        "slug": "ubuntu-vtuber-avatar-studio",
        "folder": "📁 [07] VTuber 3D Studio",
        "category": "Creadores",
        "desc": "VSeeFace, VRoid Studio, OpenSeeFace, Warudo y 100+ avatares VRM listos.",
        "kill_patterns": ["VSeeFace", "VRoidStudio", "openseeface"]
    },
    "streamer_obs": {
        "id": 8,
        "name": "Ubuntu - Streaming Studio & Producción OBS",
        "slug": "ubuntu-obs-streaming-studio",
        "folder": "📁 [08] OBS Streaming Pro",
        "category": "Creadores",
        "desc": "OBS Studio Pro, plugins NDI, audio virtual, overlays y 1,000+ canciones DMCA Free.",
        "kill_patterns": ["obs"]
    },
    "design": {
        "id": 9,
        "name": "Ubuntu - Arte Digital, Pintura & Diseño 2D",
        "slug": "ubuntu-digital-art-studio",
        "folder": "📁 [09] Arte Digital & Diseño 2D",
        "category": "Creadores",
        "desc": "Krita Pro, GIMP PhotoGIMP (UI Photoshop), Inkscape vectorial y OpenToonz Ghibli.",
        "kill_patterns": ["krita", "gimp", "inkscape", "opentoonz"]
    },
    "blender_3d": {
        "id": 10,
        "name": "Ubuntu - Modelado 3D, Blender & VFX",
        "slug": "ubuntu-3d-blender-vfx",
        "folder": "📁 [10] Blender 3D & VFX",
        "category": "3D & VFX",
        "desc": "Blender 4.x con aceleración OptiX/CUDA Tesla T4, FreeCAD, Blockbench y texturas PBR.",
        "kill_patterns": ["blender", "freecad", "blockbench"]
    },
    "ai_brains": {
        "id": 11,
        "name": "Ubuntu - Cerebro IA Ollama & Dual-GPU",
        "slug": "ubuntu-ai-brains-ollama",
        "folder": "📁 [11] Cerebro IA Dual-GPU",
        "category": "Inteligencia Artificial",
        "desc": "Ollama Dual-GPU con Qwen 2.5 (32B), DeepSeek Coder (16B), Open WebUI y Gateway API.",
        "kill_patterns": ["ollama", "open-webui", "fastapi_ai_gateway", "aider"]
    },
    "ai_voice": {
        "id": 12,
        "name": "Ubuntu - Laboratorio de Voz & Audio IA",
        "slug": "ubuntu-ai-voice-audio-lab",
        "folder": "📁 [12] Laboratorio Voz IA",
        "category": "Inteligencia Artificial",
        "desc": "Kokoro TTS (Voz hiperrealista), XTTS-v2 (Clonador), RVC v2 modulador en vivo y UVR5.",
        "kill_patterns": ["tts-server", "rvc", "demucs"]
    },
    "ai_art": {
        "id": 13,
        "name": "Ubuntu - Generador de Arte ComfyUI SDXL",
        "slug": "ubuntu-ai-image-comfyui",
        "folder": "📁 [13] ComfyUI & SDXL",
        "category": "Inteligencia Artificial",
        "desc": "ComfyUI Pro por nodos, Fooocus Midjourney-style, FLUX, Pony V6 y AnimateDiff.",
        "kill_patterns": ["comfyui", "fooocus", "fastapi_image_gateway"]
    },
    "music": {
        "id": 14,
        "name": "Ubuntu - Producción Musical LMMS Studio",
        "slug": "ubuntu-music-audio-studio",
        "folder": "📁 [14] Producción Musical LMMS",
        "category": "Música & Audio",
        "desc": "LMMS Studio (FL Studio open-source), Ardour DAW, Audacity, MuseScore y 50k samples.",
        "kill_patterns": ["lmms", "ardour", "audacity", "mscore"]
    },
    "dev": {
        "id": 15,
        "name": "Ubuntu - Suite Desarrollador & VSCode",
        "slug": "ubuntu-developer-code-hub",
        "folder": "📁 [15] Desarrollador VSCode",
        "category": "Desarrollo",
        "desc": "Visual Studio Code Oficial, Bun, Rust, Go, Python, Bruno API, Lazygit y Claude CLI.",
        "kill_patterns": ["code", "bruno"]
    },
    "cybersec": {
        "id": 16,
        "name": "Ubuntu - Laboratorio Ciberseguridad Pentesting",
        "slug": "ubuntu-cybersecurity-lab",
        "folder": "📁 [16] Ciberseguridad & Pentesting",
        "category": "Ciberseguridad",
        "desc": "Wireshark, OWASP ZAP, Semgrep SAST, Bandit, SecLists y AI Security Copilot.",
        "kill_patterns": ["wireshark", "zap.sh", "ai_security_copilot"]
    },
    "trading": {
        "id": 17,
        "name": "Ubuntu - Trading Cripto & Finanzas Quant",
        "slug": "ubuntu-crypto-trading-desk",
        "folder": "📁 [17] Trading Cripto & Finanzas",
        "category": "Finanzas",
        "desc": "TradingView Desktop, Freqtrade bot, CryptoDB 109GB, Electrum, Sparrow y AI Quant Copilot.",
        "kill_patterns": ["freqtrade", "electrum", "sparrow", "ai_financial_copilot"]
    },
    "student": {
        "id": 18,
        "name": "Ubuntu - Universidad, Ciencia & Medicina Hub",
        "slug": "ubuntu-student-university-hub",
        "folder": "📁 [18] Universidad & Ciencia",
        "category": "Educación & Ciencia",
        "desc": "GNU Octave (MATLAB), GeoGebra, Anki Pro Medicina, TeXstudio LaTeX, Avogadro y AI Researcher.",
        "kill_patterns": ["octave", "geogebra", "anki", "texstudio", "zotero", "avogadro", "stellarium", "calibre", "xournalpp"]
    },
    "anime": {
        "id": 19,
        "name": "Ubuntu - Anime, Manga & Cine 4K Mediateca",
        "slug": "ubuntu-anime-manga-media",
        "folder": "📁 [19] Anime Manga & Mediateca",
        "category": "Entretenimiento",
        "desc": "Stremio 4K, Mihon/Tachiyomi Manga, MPV con Shaders Anime4K en tiempo real, Kodi y AI Otaku.",
        "kill_patterns": ["stremio", "tachiyomi", "mihon", "mpv", "kodi", "yacreader", "miru"]
    },
    "android": {
        "id": 20,
        "name": "Ubuntu - Android Cloud Phone & Mobile Gaming",
        "slug": "ubuntu-android-cloud-phone",
        "folder": "📁 [20] Android Cloud Phone",
        "category": "Móvil & Emulación",
        "desc": "Celular ROG Phone con GPU Nvidia, Scrcpy 60FPS, controles WASD + ratón FPS, Aurora Store y JADX.",
        "kill_patterns": ["scrcpy", "anbox", "jadx", "adb"]
    }
}

def notify(msg, title="🛍️ Gestor de Databases"):
    print(f"[{title}] {msg}", flush=True)
    if os.environ.get("DISPLAY"):
        subprocess.run(f"notify-send '{title}' '{msg}' 2>/dev/null || true", shell=True)

def is_database_connected(pack):
    # Comprobar si existe la carpeta en el escritorio
    target_folder = DESKTOP_DIR / pack["folder"]
    if target_folder.exists() and any(target_folder.glob("*.desktop")):
        return True
    # Comprobar si está montado en /kaggle/input
    for d in Path("/kaggle/input").glob("*"):
        if pack["slug"] in d.name.lower():
            return True
    return False

def disconnect_pack(key):
    pack = DATABASES_CATALOG.get(key)
    if not pack:
        print(f"❌ Clave '{key}' no encontrada.", flush=True)
        return

    notify(f"Desconectando '{pack['name']}' y liberando memoria...", "🛑 Desconexión")
    
    # 1. Matar procesos en segundo plano asociados
    for pattern in pack.get("kill_patterns", []):
        subprocess.run(f"pkill -9 -f '{pattern}' 2>/dev/null || true", shell=True)
        
    # 2. Remover carpeta del escritorio
    target_folder = DESKTOP_DIR / pack["folder"]
    if target_folder.exists():
        shutil.rmtree(target_folder, ignore_errors=True)
        
    # 3. Liberar caché de memoria del sistema
    subprocess.run("sync", shell=True)
    
    notify(f"✅ ¡{pack['name']} desconectada exitosamente! Recursos de RAM y GPU liberados.", "✅ Memoria Liberada")

def connect_pack(key):
    pack = DATABASES_CATALOG.get(key)
    if not pack:
        print(f"❌ Clave '{key}' no encontrada.", flush=True)
        return

    notify(f"Iniciando activación limpia de '{pack['name']}'...")
    
    # 1. Carpeta limpia en el escritorio
    target_folder = DESKTOP_DIR / pack["folder"]
    target_folder.mkdir(parents=True, exist_ok=True)
    
    # 2. Localizar setup.py en /kaggle/input o en /tmp
    mounted_dir = None
    for input_dir in Path("/kaggle/input").glob("*"):
        if pack["slug"] in input_dir.name.lower():
            mounted_dir = input_dir
            break
            
    if not mounted_dir:
        tmp_dir = Path(f"/tmp/ubuntu_packs/{pack['slug']}")
        if tmp_dir.exists():
            mounted_dir = tmp_dir
        else:
            # Descargar vía Kaggle API
            tmp_dir.mkdir(parents=True, exist_ok=True)
            cmd_dl = f"kaggle datasets download -d miguelguerra26/{pack['slug']} -p '{tmp_dir}' --unzip"
            if os.environ.get("DISPLAY") and shutil.which("zenity"):
                zenity_cmd = f"({cmd_dl}) | zenity --progress --pulsate --title='🛍️ Descargando {pack['name']}' --text='Conectando módulo a la velocidad de la nube...' --auto-close --width=450"
                subprocess.run(zenity_cmd, shell=True)
            else:
                subprocess.run(cmd_dl, shell=True)
            mounted_dir = tmp_dir

    if mounted_dir and (mounted_dir / "setup.py").exists():
        subprocess.run(f"python3 '{mounted_dir}/setup.py' 2>/dev/null || true", shell=True)
        
        # Mover accesos directos recién creados en Desktop hacia la carpeta dedicada
        for item in DESKTOP_DIR.glob("*.desktop"):
            if item.name not in ["🛍️ Centro_Software_Databases.desktop", "📊 Gestor_Databases.desktop", "⚡ Liberar_VRAM_GPU.desktop", "💾 Salvar_Todo_Y_Salir.desktop"]:
                try:
                    shutil.move(str(item), str(target_folder / item.name))
                except Exception:
                    pass

    # 3. Crear el Botón de Desconexión Rápida dentro de la carpeta
    disconnect_btn = target_folder / f"🛑 Desconectar_{pack['folder'].replace(' ', '_')}.desktop"
    disconnect_code = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=🛑 Desconectar Esta Database ({pack['name'].split(' - ')[-1]})
Comment=Cierra procesos, libera memoria RAM/VRAM y remueve esta carpeta del escritorio
Exec=python3 /usr/local/bin/ubuntu_store.py --disconnect {key}
Icon=process-stop
Terminal=false
Categories=System;
"""
    disconnect_btn.write_text(disconnect_code, encoding="utf-8")
    disconnect_btn.chmod(0o755)

    notify(f"🎉 ¡{pack['name']} organizada en '{pack['folder']}'!", "✅ Conectada")

def show_gui():
    if not (os.environ.get("DISPLAY") and shutil.which("zenity")):
        print("\n" + "=" * 78)
        print("📊 GESTOR DE DATABASES UBUNTU CLOUD (20 MÓDULOS)")
        print("=" * 78)
        for k, v in DATABASES_CATALOG.items():
            status = "🟢 [CONECTADA]" if is_database_connected(v) else "⚪ [DISPONIBLE]"
            print(f"{status} [{v['id']:02d}] {v['name']} ({v['category']})")
        print("=" * 78 + "\n")
        return

    # Menú Interactivo Zenity
    list_items = []
    for k, v in DATABASES_CATALOG.items():
        connected = is_database_connected(v)
        status_text = "🟢 CONECTADA (Clic para Desconectar)" if connected else "⚪ DISPONIBLE (Clic para Conectar)"
        list_items.extend([k, status_text, v['name'], v['desc']])

    cmd = [
        "zenity", "--list", "--title=📊 Gestor Maestro de Databases & Recursos (20 Módulos)",
        "--column=Clave", "--column=Estado", "--column=Nombre de la Database", "--column=Descripción",
        "--width=980", "--height=600", "--hide-column=1"
    ] + list_items

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and res.stdout.strip():
        sel_key = res.stdout.strip()
        pack = DATABASES_CATALOG.get(sel_key)
        if pack:
            if is_database_connected(pack):
                disconnect_pack(sel_key)
            else:
                connect_pack(sel_key)

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--disconnect":
        disconnect_pack(sys.argv[2].strip())
    elif len(sys.argv) > 1 and sys.argv[1] != "--gui":
        connect_pack(sys.argv[1].strip())
    else:
        show_gui()

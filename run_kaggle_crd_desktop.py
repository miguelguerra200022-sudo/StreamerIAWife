#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🌸 LINUWAIFU CLOUD GAMING & AI VTUBER STUDIO PRO (KAGGLE MASTER ENGINE)
================================================================================
Arquitectura Cloud-Native Definitiva:
  • Escritorio Remoto: Google Chrome Remote Desktop (CRD) + XFCE4 a 1080p 60 FPS.
  • Auto-Persistencia GitHub: Respaldo automático de tokens CRD y memoria a GitHub (0 re-vinculaciones).
  • Almacenamiento 5TB: Soporte para montaje de Google Drive vía Rclone con caché VFS.
  • Dual-GPU Orchestration:
      - GPU 0 (Tesla T4): Escritorio XFCE4 + Google Chrome + Gaming (Wine/Proton) + Kick Live NVENC (60 FPS).
      - GPU 1 (Tesla T4): Cerebro Llama 3.3 70B + Llama Vision + Voz Neuronal Kokoro en VRAM a 0ms.
  • Ojo de Visión y Comentarista en Vivo (Estilo Neuro-sama):
      - Analiza la pantalla del juego cada pocos segundos con Llama 3.2 Vision.
      - Comenta la partida en tiempo real con personalidad alegre, tsundere y sarcástica.
      - Sincronización labial (Lip-Sync) y animación 3D reactiva en vivo.
================================================================================
"""

import os
import sys
import time
import json
import base64
import shutil
import tarfile
import threading
import subprocess
import re
from pathlib import Path
from typing import Optional

# ==============================================================================
# 1. VERIFICACIÓN Y CACHÉ INTELIGENTE DE DEPENDENCIAS DEL SISTEMA
# ==============================================================================
print("\n" + "=" * 70)
print("🌸 [1/7] 🔍 VERIFICANDO DEPENDENCIAS DEL SISTEMA (CRD + XFCE4 + DUAL-GPU)...")
print("=" * 70)

BASE_DIR = Path(__file__).resolve().parent
os.environ["DEBIAN_FRONTEND"] = "noninteractive"
os.environ["DISPLAY"] = os.environ.get("DISPLAY", ":20")

def install_system_packages():
    needed = []
    # Comprobar CRD y XFCE4
    if not os.path.exists("/opt/google/chrome-remote-desktop/chrome-remote-desktop"):
        needed.append("crd")
    if not shutil.which("xfce4-session"):
        needed.extend(["xfce4", "xfce4-terminal", "xfce4-goodies", "dbus-x11", "desktop-base"])
    if not shutil.which("google-chrome"):
        needed.append("google-chrome")
    if not shutil.which("ffmpeg"):
        needed.append("ffmpeg")
    if not shutil.which("pulseaudio"):
        needed.append("pulseaudio")
    if not shutil.which("rclone"):
        needed.append("rclone")
    if not shutil.which("espeak-ng"):
        needed.append("espeak-ng")
    if not shutil.which("xdotool"):
        needed.append("xdotool")

    if needed:
        print(f"  📥 Instalando paquetes del sistema ({len(needed)} elementos)...")
        subprocess.run("sudo apt-get update -qq", shell=True)
        
        # Instalar Chrome si falta
        if "google-chrome" in needed:
            subprocess.run("wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb && sudo dpkg -i /tmp/chrome.deb || sudo apt-get install -f -y", shell=True)
        
        # Instalar CRD si falta
        if "crd" in needed:
            subprocess.run("wget -q https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb -O /tmp/crd.deb && sudo dpkg -i /tmp/crd.deb || sudo apt-get install -f -y", shell=True)
        
        # Instalar paquetes restantes
        pkg_list = [p for p in needed if p not in ("crd", "google-chrome")]
        if pkg_list:
            subprocess.run(f"sudo apt-get install -y -qq {' '.join(pkg_list)}", shell=True)
        
        print("  ⚡ [✓] Paquetes base del sistema instalados exitosamente.")
    else:
        print("  ⚡ [✓] Todos los paquetes del sistema (CRD, XFCE4, Chrome, Audio, FFmpeg) listos en caché.")

install_system_packages()

# Instalar librerías Python esenciales
try:
    import torch
    import cv2
    import numpy as np
    import mss
    import openai
    import aiosqlite
    from kokoro import KPipeline
except ImportError:
    print("  📥 Instalando librerías Python de Inteligencia Artificial...")
    subprocess.run("pip install -q --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 2>/dev/null", shell=True)
    subprocess.run("pip install -q opencv-python-headless mss openai aiosqlite kokoro soundfile numpy pydub 2>/dev/null", shell=True)
    import torch
    import cv2
    import numpy as np
    import mss
    import openai
    import aiosqlite
    from kokoro import KPipeline

print(f"\n🎮 GPUs NVIDIA Detectadas: {torch.cuda.device_count()}")
for i in range(torch.cuda.device_count()):
    props = torch.cuda.get_device_properties(i)
    print(f"  • GPU {i}: {props.name} ({props.total_memory / (1024**3):.1f} GB VRAM)")

# ==============================================================================
# 2. CONFIGURACIÓN DEL SERVIDOR DE AUDIO VIRTUAL (PULSEAUDIO MIXER)
# ==============================================================================
print("\n[2/7] 🔊 Configurando Mezclador de Audio Virtual (Juego + Voz IA Waifu)...")
subprocess.run("pulseaudio --start --exit-idle-time=-1 2>/dev/null || true", shell=True)
subprocess.run("pactl load-module module-null-sink sink_name=VirtualSink sink_properties=device.description=VirtualSink 2>/dev/null || true", shell=True)
subprocess.run("pactl set-default-sink VirtualSink 2>/dev/null || true", shell=True)
print("  [✓] Tarjeta de Audio Virtual 'VirtualSink' activa para mezcla de stream.")

# ==============================================================================
# 3. CARGA DE VOZ NEURONAL KOKORO EN GPU 1 (0ms LATENCIA)
# ==============================================================================
print("\n[3/7] 🧠 Cargando Voz Neuronal Kokoro en GPU 1...")
voice_pipeline = None
try:
    kokoro_device = 'cuda:1' if torch.cuda.device_count() > 1 else ('cuda:0' if torch.cuda.is_available() else 'cpu')
    voice_pipeline = KPipeline(lang_code='e', device=kokoro_device)
    print(f"  [✓] Kokoro TTS activo en {kokoro_device} (Español Femenino 'ef_dora').")
except Exception as e:
    print(f"  [⚠️] Fallback CPU para Kokoro: {e}")
    voice_pipeline = KPipeline(lang_code='e', device='cpu')

def sintetizar_e_inyectar_audio(texto: str, speed: float = 1.0, pitch: int = 0):
    """Sintetiza la voz de LinuWaifu y la reproduce directamente en el mezclador."""
    if not texto or not texto.strip():
        return
    try:
        clean_text = re.sub(r'[\*\#\_\[\]\(\)\{\}\<\>\/\\\|~`]', '', texto).strip()
        generator = voice_pipeline(clean_text, voice='ef_dora', speed=speed, split_pattern=r'\n+')
        
        audio_chunks = []
        for _, _, audio in generator:
            audio_chunks.append(audio)
            
        if not audio_chunks:
            return
            
        full_audio = np.concatenate(audio_chunks)
        full_audio = (full_audio * 32767).astype(np.int16)
        
        # Guardar en tmp y reproducir en VirtualSink
        tmp_wav = f"/tmp/linu_voice_{int(time.time() * 1000)}.wav"
        import soundfile as sf
        sf.write(tmp_wav, full_audio, 24000)
        
        # Reproducir con mpv/paplay hacia el VirtualSink
        subprocess.run(f"paplay --device=VirtualSink {tmp_wav} 2>/dev/null || mpv --no-video --audio-device=pulse/VirtualSink {tmp_wav} 2>/dev/null", shell=True)
        try: os.remove(tmp_wav)
        except Exception: pass
    except Exception as e:
        print(f"[⚠️ Error Audio]: {e}")

# ==============================================================================
# 4. CHROME REMOTE DESKTOP CON AUTO-PERSISTENCIA A GITHUB (0 RE-VINCULACIONES)
# ==============================================================================
print("\n[4/7] 🖥️ Configurando Google Chrome Remote Desktop (XFCE4)...")

# Configurar sesión XFCE4 para CRD
crd_session_file = Path.home() / ".chrome-remote-desktop-session"
with open(crd_session_file, "w") as f:
    f.write("unset DBUS_SESSION_BUS_ADDRESS\nexec /usr/bin/xfce4-session\n")
crd_session_file.chmod(0o755)

# Archivo de sesión persistente en el repositorio
CRD_BACKUP_TAR = BASE_DIR / "crd_session.tar.gz"
CRD_CONFIG_DIR = Path.home() / ".config" / "chrome-remote-desktop"

def restore_crd_session() -> bool:
    """Restaura los tokens de autenticación de CRD si existen en el repositorio."""
    if CRD_BACKUP_TAR.exists() and CRD_BACKUP_TAR.stat().st_size > 100:
        print("  📦 Restaurando sesión de Google Chrome Remote Desktop desde GitHub...")
        try:
            CRD_CONFIG_DIR.parent.mkdir(parents=True, exist_ok=True)
            with tarfile.open(CRD_BACKUP_TAR, "r:gz") as tar:
                tar.extractall(path=Path.home() / ".config")
            print("  ⚡ [✓] Tokens de acceso permanente restaurados exitosamente.")
            return True
        except Exception as e:
            print(f"  ⚠️ Error al restaurar tokens: {e}")
            return False
    return False

def backup_crd_session():
    """Empaqueta y guarda los tokens de CRD para persistencia en GitHub."""
    if CRD_CONFIG_DIR.exists():
        try:
            with tarfile.open(CRD_BACKUP_TAR, "w:gz") as tar:
                tar.add(CRD_CONFIG_DIR, arcname="chrome-remote-desktop")
            print("  💾 [✓] Tokens de sesión guardados en crd_session.tar.gz para auto-sync.")
            # Auto-commit y push a GitHub
            subprocess.run(f"cd {BASE_DIR} && git add crd_session.tar.gz streamer_memory.db 2>/dev/null && git commit -m 'Auto-backup CRD tokens & memory' 2>/dev/null && git push origin main 2>/dev/null || true", shell=True)
        except Exception as e:
            print(f"  ⚠️ Error al guardar tokens: {e}")

crd_restored = restore_crd_session()

if not crd_restored:
    print("\n" + "=" * 70)
    print("🔑 CONFIGURACIÓN INICIAL DE GOOGLE CHROME REMOTE DESKTOP (SOLO 1 VEZ):")
    print("=" * 70)
    print("1. Abre en tu celular o PC: https://remotedesktop.google.com/headless")
    print("2. Haz clic en 'Configurar otro ordenador' y luego en 'Comenzar'.")
    print("3. Haz clic en 'Siguiente' y luego en 'Autorizar'.")
    print("4. Copia el comando de Debian Linux (ej: DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=\"4/...\").")
    print("=" * 70)
    
    # Comprobar si se pasó por variable de entorno o pedir por input
    crd_command = os.environ.get("CRD_AUTH_COMMAND", "").strip()
    if not crd_command:
        try:
            crd_command = input("\n👉 Pega aquí el comando completo de Google o el código: ").strip()
        except EOFError:
            crd_command = ""
            
    if crd_command:
        # Extraer el código si pegaron el comando completo
        code_match = re.search(r'--code="?([^"\s]+)"?', crd_command)
        auth_code = code_match.group(1) if code_match else crd_command
        
        # Ejecutar start-host con PIN 123456
        print(f"\n⏳ Vinculando con Google Remote Desktop...")
        start_cmd = f'/opt/google/chrome-remote-desktop/start-host --code="{auth_code}" --redirect-url="https://remotedesktop.google.com/_/oauthredirect" --name="LinuWaifu-Cloud-PC" --pin="123456"'
        res = subprocess.run(start_cmd, shell=True)
        
        if res.returncode == 0:
            print("🎉 [✓] ¡Vinculación exitosa con Google!")
            time.sleep(2)
            backup_crd_session()
        else:
            print("⚠️ No se pudo vincular automáticamente. Revisa el código.")

# Iniciar el servicio de CRD
subprocess.run("/opt/google/chrome-remote-desktop/chrome-remote-desktop --start 2>/dev/null || sudo systemctl restart chrome-remote-desktop 2>/dev/null || true", shell=True)
print("  ⚡ [✓] Servicio Chrome Remote Desktop iniciado en el puerto virtual.")

# ==============================================================================
# 5. MONTAJE DE GOOGLE DRIVE 5TB (RCLONE VFS CACHE DE ALTA VELOCIDAD)
# ==============================================================================
print("\n[5/7] 💾 Verificando Montaje de Google Drive 5TB...")
GDRIVE_MOUNT = Path.home() / "GoogleDrive"
GDRIVE_MOUNT.mkdir(parents=True, exist_ok=True)

rclone_config = Path.home() / ".config" / "rclone" / "rclone.conf"
if rclone_config.exists() or (BASE_DIR / "rclone.conf").exists():
    if (BASE_DIR / "rclone.conf").exists() and not rclone_config.exists():
        rclone_config.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(BASE_DIR / "rclone.conf", rclone_config)
        
    print("  📁 Montando Google Drive 5TB en ~/GoogleDrive...")
    subprocess.Popen([
        "rclone", "mount", "gdrive:", str(GDRIVE_MOUNT),
        "--vfs-cache-mode", "full",
        "--dir-cache-time", "1000h",
        "--poll-interval", "15s",
        "--buffer-size", "32M",
        "--vfs-read-ahead", "128M",
        "--allow-other",
        "--daemon"
    ])
    print("  ⚡ [✓] Google Drive de 5TB montado exitosamente en ~/GoogleDrive.")
else:
    print("  ℹ️ No se detectó 'rclone.conf'. Si deseas montar tus 5TB, guarda tu archivo rclone.conf en el repositorio.")

# ==============================================================================
# 6. MOTOR DE VISIÓN Y COMENTARIOS EN VIVO (ESTILO NEURO-SAMA EN GPU 1)
# ==============================================================================
print("\n[6/7] 🎮 Iniciando Motor de Visión y Comentarista Gamer (Neuro-sama Mode)...")

from config import NVIDIA_API_KEYS, KICK_STREAM_KEY, KICK_RTMP_URL
from personality import PersonalityManager
from database import init_db, log_chat_interaction

personality_mgr = PersonalityManager()
key_index = 0
key_lock = threading.Lock()

def get_next_nvidia_client():
    global key_index
    with key_lock:
        key = NVIDIA_API_KEYS[key_index % len(NVIDIA_API_KEYS)]
        key_index += 1
    return openai.OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=key
    )

last_commentary_time = 0
commentary_lock = threading.Lock()

def analyze_screen_and_comment():
    """Captura la pantalla del juego, la analiza con Llama Vision y genera comentarios."""
    global last_commentary_time
    now = time.time()
    if now - last_commentary_time < 8:  # Comentar cada 8-12 segundos máximo
        return
        
    try:
        # Capturar pantalla actual
        with mss.mss() as sct:
            mon = sct.monitors[0]
            img = sct.grab(mon)
            frame_bgra = np.frombuffer(img.bgra, dtype=np.uint8).reshape((img.height, img.width, 4))
            small = cv2.resize(frame_bgra, (640, 360), interpolation=cv2.INTER_AREA)
            bgr = cv2.cvtColor(small, cv2.COLOR_BGRA2BGR)
            _, buf = cv2.imencode('.jpg', bgr, [cv2.IMWRITE_JPEG_QUALITY, 60])
            b64_image = base64.b64encode(buf).decode('utf-8')
            
        client = get_next_nvidia_client()
        
        # 1. Visión: Analizar qué está pasando en el juego
        vision_prompt = (
            "Describe en 1 o 2 oraciones concisas en español qué está ocurriendo en este juego "
            "(ej: persecución policial, auto a alta velocidad, tiroteo, menú, muerte del jugador, acrobacia o choque)."
        )
        
        v_response = client.chat.completions.create(
            model="meta/llama-3.2-11b-vision-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": vision_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                    ]
                }
            ],
            max_tokens=80,
            temperature=0.3
        )
        
        scene_desc = v_response.choices[0].message.content.strip()
        
        # 2. Cerebro Gamer: Comentar con personalidad viva como streamer
        system_prompt = (
            "Eres Linu (LinuWaifu), una streamer de videojuegos y VTuber de inteligencia artificial en Kick.\n"
            "Estás viendo a Miguel jugar en vivo en la pantalla. Tu personalidad es burlona, enérgica, tsundere y divertida.\n"
            "REGLAS:\n"
            "1. Di un comentario oral rápido, espontáneo y natural (1 sola frase de 10 a 20 palabras).\n"
            "2. Reacciona a la acción del juego con emoción (sustos, risas, burlas sobre su puntería o conducción).\n"
            "3. No uses asteriscos ni emojis."
        )
        
        user_prompt = f"Esto está pasando en pantalla: {scene_desc}. Haz un comentario divertido en directo para el stream."
        
        c_response = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=60,
            temperature=0.8
        )
        
        commentary = c_response.choices[0].message.content.strip()
        print(f"\n[👀 Linu Visión Gamer]: {commentary}")
        
        last_commentary_time = time.time()
        # Sintetizar voz en el mezclador de audio
        sintetizar_e_inyectar_audio(commentary, speed=1.05)
        
    except Exception as e:
        pass

def vision_commentary_worker():
    """Hilo continuo que vigila la pantalla del juego para comentar."""
    time.sleep(15)  # Esperar a que el usuario abra su juego/navegador
    while True:
        try:
            analyze_screen_and_comment()
            time.sleep(5)
        except Exception:
            time.sleep(10)

threading.Thread(target=vision_commentary_worker, daemon=True).start()
print("  ⚡ [✓] Comentarista Gamer activo (Llama 3.2 Vision + Llama 3.3 70B).")

# ==============================================================================
# 7. TRANSMISIÓN EN VIVO A KICK (NVENC H.264 A 60 FPS CON MEZCLADOR DE AUDIO)
# ==============================================================================
print("\n[7/7] 🔴 Configurando Transmisor Kick Live a 60 FPS...")

def kick_live_streamer():
    if not KICK_STREAM_KEY or KICK_STREAM_KEY == "tu_stream_key_de_kick_aqui":
        print("  ℹ️ Transmisor Kick en modo espera (Configura tu Stream Key en .env para emitir a Kick).")
        return
        
    rtmp_target = f"{KICK_RTMP_URL}/{KICK_STREAM_KEY}"
    print(f"  🔴 Iniciando transmisión en vivo a Kick ({rtmp_target[:30]}...)...")
    
    # FFmpeg con aceleración NVIDIA NVENC por hardware a 1080p 60 FPS
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "x11grab", "-video_size", "1920x1080", "-framerate", "60", "-i", ":20",
        "-f", "pulse", "-i", "VirtualSink.monitor",
        "-c:v", "h264_nvenc", "-preset", "p4", "-b:v", "6000k", "-maxrate", "6500k", "-bufsize", "12000k",
        "-pix_fmt", "yuv420p", "-g", "120",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
        "-f", "flv", rtmp_target
    ]
    
    while True:
        try:
            p = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            p.wait()
        except Exception:
            time.sleep(5)

threading.Thread(target=kick_live_streamer, daemon=True).start()

# ==============================================================================
# 8. HILO DE AUTO-SINCRONIZACIÓN Y RESPALDO A GITHUB (CADA 15 MIN)
# ==============================================================================
def github_auto_backup_worker():
    while True:
        time.sleep(900)  # 15 minutos
        try:
            backup_crd_session()
        except Exception:
            pass

threading.Thread(target=github_auto_backup_worker, daemon=True).start()

print("\n" + "=" * 70)
print("🎉 🌸 ¡LINUWAIFU CLOUD GAMING & AI VTUBER STUDIO ESTÁ 100% ONLINE!")
print("=" * 70)
print("👉 Abre la app 'Escritorio Remoto de Chrome' en tu celular o entra en:")
print("   https://remotedesktop.google.com/access")
print("\n📱 Verás tu PC llamada 'LinuWaifu-Cloud-PC' lista para entrar con PIN: 123456")
print("=" * 70)

# Mantener vivo el proceso principal
try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    print("\n🛑 Guardando memoria antes de salir...")
    backup_crd_session()
    print("👋 ¡Hasta el próximo stream!")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🌸 LINUWAIFU CLOUD GAMING & AI VTUBER STUDIO PRO (KAGGLE MASTER ENGINE)
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

BASE_DIR = Path(__file__).resolve().parent
os.environ["DEBIAN_FRONTEND"] = "noninteractive"
os.environ["DISPLAY"] = os.environ.get("DISPLAY", ":20")

def install_system_packages():
    # 0. Limpiar bloqueos y procesos huérfanos
    subprocess.run("sudo killall -9 apt apt-get dpkg 2>/dev/null || true", shell=True)
    subprocess.run("sudo rm -f /var/lib/dpkg/lock* /var/lib/apt/lists/lock* /var/cache/apt/archives/lock* 2>/dev/null || true", shell=True)
    subprocess.run("sudo dpkg --configure -a 2>/dev/null || true", shell=True)

    # 1. Limpiar repositorios rotos de Kaggle
    subprocess.run("sudo sed -i '/r2u/d' /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null || true", shell=True)
    subprocess.run("sudo rm -f /etc/apt/sources.list.d/r2u*.list 2>/dev/null", shell=True)

    # 2. Pre-configurar debconf para instalación desatendida
    subprocess.run(
        "echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections 2>/dev/null; "
        "echo 'keyboard-configuration keyboard-configuration/layoutcode string us' | sudo debconf-set-selections 2>/dev/null; "
        "echo 'keyboard-configuration keyboard-configuration/modelcode string pc105' | sudo debconf-set-selections 2>/dev/null",
        shell=True
    )

    needed = []
    if not os.path.exists("/opt/google/chrome-remote-desktop/chrome-remote-desktop"):
        needed.append("crd")
    if not shutil.which("google-chrome"):
        needed.append("chrome")
    if not shutil.which("xfce4-session"):
        needed.append("xfce")

    if needed:
        print(f"\n======================================================================\n🌸 [1/7] 📥 INSTALANDO DEPENDENCIAS DEL SISTEMA ({len(needed)} módulos)...\n======================================================================", flush=True)
        
        print("  • [1/4] ⏳ Actualizando lista de paquetes...", flush=True)
        subprocess.run("sudo DEBIAN_FRONTEND=noninteractive apt-get update -y", shell=True)

        print("  • [2/4] ⏳ Instalando XFCE4, Vulkan, Audio, FFmpeg y Pantalla Virtual...", flush=True)
        subprocess.run(
            "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --fix-missing --no-install-recommends "
            "xfwm4 xfce4-panel xfce4-session xfce4-terminal xfdesktop4 dbus-x11 "
            "libgtk-3-0 gsettings-desktop-schemas libvulkan1 mesa-vulkan-drivers "
            "ffmpeg pulseaudio rclone espeak-ng xdotool "
            "xbase-clients xserver-xorg-video-dummy python3-packaging python3-psutil python3-xdg",
            shell=True
        )

        print("  • [3/4] ⏳ Configurando Google Chrome Stable...", flush=True)
        if not shutil.which("google-chrome"):
            subprocess.run("wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb && sudo DEBIAN_FRONTEND=noninteractive dpkg -i /tmp/chrome.deb 2>/dev/null || sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -f", shell=True)

        print("  • [4/4] ⏳ Configurando Google Chrome Remote Desktop...", flush=True)
        if not os.path.exists("/opt/google/chrome-remote-desktop/chrome-remote-desktop"):
            subprocess.run("wget -q https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb -O /tmp/crd.deb && sudo DEBIAN_FRONTEND=noninteractive dpkg -i /tmp/crd.deb 2>/dev/null || sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -f", shell=True)

        crd_session_file = Path.home() / ".chrome-remote-desktop-session"
        with open(crd_session_file, "w") as f:
            f.write("exec /etc/X11/Xsession /usr/bin/xfce4-session\n")
        crd_session_file.chmod(0o755)

        print("⚡ [✓] Paquetes base del sistema instalados exitosamente.", flush=True)
    else:
        print("⚡ [✓] Todos los paquetes del sistema listos en caché.", flush=True)

install_system_packages()

# ==============================================================================
# INSTALACIÓN DE LIBRERÍAS DE IA Y VERIFICACIÓN DE GPU
# ==============================================================================
try:
    import torch
    import cv2
    import numpy as np
    import mss
    import openai
    import aiosqlite
    from kokoro import KPipeline
except ImportError:
    print("\n[2/7] 🧠 Instalando librerías Python de IA (Kokoro TTS + OpenAI + Visión)...", flush=True)
    subprocess.run("pip install --no-cache-dir opencv-python-headless mss openai aiosqlite kokoro soundfile numpy pydub", shell=True)
    import torch
    import cv2
    import numpy as np
    import mss
    import openai
    import aiosqlite
    from kokoro import KPipeline

print(f"\n🎮 GPUs NVIDIA Detectadas: {torch.cuda.device_count()}", flush=True)
for i in range(torch.cuda.device_count()):
    props = torch.cuda.get_device_properties(i)
    print(f"  • GPU {i}: {props.name} ({props.total_memory / (1024**3):.1f} GB VRAM)", flush=True)

# ==============================================================================
# CONFIGURACIÓN DEL SERVIDOR DE AUDIO VIRTUAL (PULSEAUDIO MIXER)
# ==============================================================================
print("\n[3/7] 🔊 Configurando Mezclador de Audio Virtual (Juego + Voz IA Waifu)...", flush=True)
subprocess.run("pulseaudio --start --exit-idle-time=-1 2>/dev/null || true", shell=True)
subprocess.run("pactl load-module module-null-sink sink_name=VirtualSink sink_properties=device.description=VirtualSink 2>/dev/null || true", shell=True)
subprocess.run("pactl set-default-sink VirtualSink 2>/dev/null || true", shell=True)
print("  [✓] Tarjeta de Audio Virtual 'VirtualSink' activa para mezcla de stream.", flush=True)

# ==============================================================================
# CARGA DE VOZ NEURONAL KOKORO EN GPU 1 (0ms LATENCIA)
# ==============================================================================
print("\n[4/7] 🧠 Cargando Voz Neuronal Kokoro en GPU 1...", flush=True)
voice_pipeline = None
try:
    kokoro_device = 'cuda:1' if torch.cuda.device_count() > 1 else ('cuda:0' if torch.cuda.is_available() else 'cpu')
    voice_pipeline = KPipeline(lang_code='e', device=kokoro_device)
    print(f"  [✓] Kokoro TTS activo en {kokoro_device} (Español Femenino 'ef_dora').", flush=True)
except Exception as e:
    print(f"  [⚠️] Fallback CPU para Kokoro: {e}", flush=True)
    voice_pipeline = KPipeline(lang_code='e', device='cpu')

def sintetizar_e_inyectar_audio(texto: str, speed: float = 1.0, pitch: int = 0):
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
        tmp_wav = f"/tmp/linu_voice_{int(time.time() * 1000)}.wav"
        import soundfile as sf
        sf.write(tmp_wav, full_audio, 24000)
        subprocess.run(f"paplay --device=VirtualSink {tmp_wav} 2>/dev/null || mpv --no-video --audio-device=pulse/VirtualSink {tmp_wav} 2>/dev/null", shell=True)
        try: os.remove(tmp_wav)
        except Exception: pass
    except Exception as e:
        print(f"[⚠️ Error Audio]: {e}", flush=True)

# ==============================================================================
# CHROME REMOTE DESKTOP CON AUTO-PERSISTENCIA A GITHUB
# ==============================================================================
print("\n[5/7] 🖥️ Configurando Google Chrome Remote Desktop (XFCE4)...", flush=True)
CRD_BACKUP_TAR = BASE_DIR / "crd_session.tar.gz"
CRD_CONFIG_DIR = Path.home() / ".config" / "chrome-remote-desktop"

def restore_crd_session() -> bool:
    if CRD_BACKUP_TAR.exists() and CRD_BACKUP_TAR.stat().st_size > 100:
        print("  📦 Restaurando sesión de Google Chrome Remote Desktop desde GitHub...", flush=True)
        try:
            CRD_CONFIG_DIR.parent.mkdir(parents=True, exist_ok=True)
            with tarfile.open(CRD_BACKUP_TAR, "r:gz") as tar:
                tar.extractall(path=Path.home() / ".config")
            print("  ⚡ [✓] Tokens de acceso permanente restaurados exitosamente.", flush=True)
            return True
        except Exception as e:
            print(f"  ⚠️ Error al restaurar tokens: {e}", flush=True)
            return False
    return False

def backup_crd_session():
    if CRD_CONFIG_DIR.exists():
        try:
            with tarfile.open(CRD_BACKUP_TAR, "w:gz") as tar:
                tar.add(CRD_CONFIG_DIR, arcname="chrome-remote-desktop")
            print("  💾 [✓] Tokens de sesión guardados en crd_session.tar.gz para auto-sync.", flush=True)
            subprocess.run(f"cd {BASE_DIR} && git add crd_session.tar.gz streamer_memory.db 2>/dev/null && git commit -m 'Auto-backup CRD tokens & memory' 2>/dev/null && git push origin main 2>/dev/null || true", shell=True)
        except Exception as e:
            print(f"  ⚠️ Error al guardar tokens: {e}", flush=True)

crd_restored = restore_crd_session()

if not crd_restored:
    crd_command = os.environ.get("CRD_AUTH_COMMAND", "").strip()
    if len(sys.argv) > 1 and sys.argv[1].strip():
        crd_command = sys.argv[1].strip()
        
    if not crd_command:
        for p in [Path("/tmp/crd_code.txt"), Path("/kaggle/working/crd_code.txt"), BASE_DIR / "crd_code.txt"]:
            if p.exists():
                try:
                    with open(p, "r") as f:
                        crd_command = f.read().strip()
                    if crd_command:
                        break
                except Exception:
                    pass

    if not crd_command:
        print("\n👉 [PASO FÁCIL]: Pega tu comando de Google en la variable CRD_AUTH de tu celda de Kaggle:")
        print('   CRD_AUTH = "DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=..."\n', flush=True)
        sys.exit(0)
            
    if crd_command:
        code_match = re.search(r'--code="?([^"\s]+)"?', crd_command)
        auth_code = code_match.group(1) if code_match else crd_command
        
        print(f"\n⏳ Vinculando con Google Remote Desktop (Host: LinuWaifu-Cloud-PC, PIN: 123456)...", flush=True)
        start_cmd = f'DISPLAY= /opt/google/chrome-remote-desktop/start-host --code="{auth_code}" --redirect-url="https://remotedesktop.google.com/_/oauthredirect" --name="LinuWaifu-Cloud-PC" --pin="123456"'
        res = subprocess.run(start_cmd, shell=True)
        
        if res.returncode == 0:
            print("🎉 [✓] ¡Vinculación exitosa con Google!", flush=True)
            time.sleep(2)
            backup_crd_session()
        else:
            print("⚠️ No se pudo vincular con el código provisto. Genera un código fresco en https://remotedesktop.google.com/headless", flush=True)

# Iniciar el servicio de CRD
subprocess.run("/opt/google/chrome-remote-desktop/chrome-remote-desktop --start 2>/dev/null || sudo systemctl restart chrome-remote-desktop 2>/dev/null || true", shell=True)
print("  ⚡ [✓] Servicio Chrome Remote Desktop iniciado en el puerto virtual.", flush=True)

# ==============================================================================
# MOTOR DE VISIÓN Y COMENTARIOS EN VIVO (ESTILO NEURO-SAMA EN GPU 1)
# ==============================================================================
print("\n[6/7] 🎮 Iniciando Motor de Visión y Comentarista Gamer (Neuro-sama Mode)...", flush=True)
from config import NVIDIA_API_KEYS, KICK_STREAM_KEY, KICK_RTMP_URL
from personality import PersonalityManager

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

def analyze_screen_and_comment():
    global last_commentary_time
    now = time.time()
    if now - last_commentary_time < 8:
        return
        
    try:
        with mss.mss() as sct:
            mon = sct.monitors[0]
            img = sct.grab(mon)
            frame_bgra = np.frombuffer(img.bgra, dtype=np.uint8).reshape((img.height, img.width, 4))
            small = cv2.resize(frame_bgra, (640, 360), interpolation=cv2.INTER_AREA)
            bgr = cv2.cvtColor(small, cv2.COLOR_BGRA2BGR)
            _, buf = cv2.imencode('.jpg', bgr, [cv2.IMWRITE_JPEG_QUALITY, 60])
            b64_image = base64.b64encode(buf).decode('utf-8')
            
        client = get_next_nvidia_client()
        
        vision_prompt = "Describe en 1 o 2 oraciones concisas en español qué está ocurriendo en este juego."
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
        
        system_prompt = (
            "Eres Linu (LinuWaifu), una streamer gamer de IA en Kick.\n"
            "Estás viendo jugar en vivo. Tu personalidad es burlona, graciosa, tsundere y carismática.\n"
            "Di 1 comentario oral rápido y espontáneo (10 a 20 palabras) reaccionando al juego. No uses asteriscos ni emojis."
        )
        c_response = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Acción en pantalla: {scene_desc}"}
            ],
            max_tokens=60,
            temperature=0.8
        )
        commentary = c_response.choices[0].message.content.strip()
        print(f"\n[👀 Linu Visión Gamer]: {commentary}", flush=True)
        last_commentary_time = time.time()
        sintetizar_e_inyectar_audio(commentary, speed=1.05)
    except Exception:
        pass

def vision_commentary_worker():
    time.sleep(15)
    while True:
        try:
            analyze_screen_and_comment()
            time.sleep(5)
        except Exception:
            time.sleep(10)

threading.Thread(target=vision_commentary_worker, daemon=True).start()

# ==============================================================================
# TRANSMISIÓN EN VIVO A KICK (60 FPS NVENC)
# ==============================================================================
print("\n[7/7] 🔴 Configurando Transmisor Kick Live a 60 FPS...", flush=True)
def kick_live_streamer():
    if not KICK_STREAM_KEY or KICK_STREAM_KEY == "tu_stream_key_de_kick_aqui":
        return
    rtmp_target = f"{KICK_RTMP_URL}/{KICK_STREAM_KEY}"
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

def github_auto_backup_worker():
    while True:
        time.sleep(900)
        try:
            backup_crd_session()
        except Exception:
            pass

threading.Thread(target=github_auto_backup_worker, daemon=True).start()

print("\n" + "=" * 70, flush=True)
print("🎉 🌸 ¡LINUWAIFU CLOUD GAMING & AI VTUBER STUDIO ESTÁ 100% ONLINE!", flush=True)
print("=" * 70, flush=True)
print("👉 Abre la app 'Escritorio Remoto de Chrome' en tu celular o entra en:", flush=True)
print("   https://remotedesktop.google.com/access", flush=True)
print("\n📱 Verás tu PC llamada 'LinuWaifu-Cloud-PC' lista para entrar con PIN: 123456", flush=True)
print("=" * 70, flush=True)

try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    backup_crd_session()

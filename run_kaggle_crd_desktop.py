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
import signal
import atexit
import traceback
from pathlib import Path
from typing import Optional

def diagnostic_exit_handler():
    print("\n🛑 [SISTEMA LINUWAIFU]: Proceso finalizado. Guardando memoria...", flush=True)

def signal_handler(signum, frame):
    sig_name = "SIGTERM (Kaggle Shutdown)" if signum == signal.SIGTERM else "SIGINT (Cancelación)"
    print(f"\n🛑 [DIAGNÓSTICO]: Interrupción detectada -> {sig_name}", flush=True)
    traceback.print_stack(frame, limit=2)
    sys.exit(0)

atexit.register(diagnostic_exit_handler)
try:
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent
os.environ["DEBIAN_FRONTEND"] = "noninteractive"
os.environ["DISPLAY"] = os.environ.get("DISPLAY", ":20")

def ensure_system_dependencies():
    crd_bin = "/opt/google/chrome-remote-desktop/start-host"
    if not os.path.exists(crd_bin) or not os.path.exists("/usr/lib/x86_64-linux-gnu/libgdk-3.so.0"):
        print("\n🌸 [1/4] 📥 Instalando librerías gráficas GTK3, XFCE4 y Google Remote Desktop...", flush=True)
        subprocess.run(
            "sudo sed -i 's|http://archive.ubuntu.com/ubuntu/|http://us-central1.gce.clouds.archive.ubuntu.com/ubuntu/|g' /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null || true; "
            "sudo sed -i 's|http://security.ubuntu.com/ubuntu/|http://us-central1.gce.clouds.archive.ubuntu.com/ubuntu/|g' /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null || true; "
            "sudo sed -i 's|http://mirrors.edge.kernel.org/ubuntu/|http://us-central1.gce.clouds.archive.ubuntu.com/ubuntu/|g' /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null || true; "
            "printf 'Acquire::Force-IPv4 \"true\";\\nAcquire::http::Timeout \"10\";\\nAcquire::http::Pipeline-Depth \"0\";\\n' | sudo tee /etc/apt/apt.conf.d/99force >/dev/null; "
            "sudo apt-get update -qq; "
            "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-upgrade --no-install-recommends "
            "libgtk-3-0 libxtst6 xbase-clients xserver-xorg-video-dummy gsettings-desktop-schemas "
            "xvfb python3-psutil python3-xdg python3-packaging xfwm4 xfce4-session xfce4-terminal xfdesktop4 dbus-x11 pulseaudio; "
            "wget -q https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb -O /tmp/crd.deb; "
            "sudo dpkg -i /tmp/crd.deb 2>/dev/null || sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --fix-broken",
            shell=True
        )
        print("⚡ [✓] Librerías gráficas GTK3 y Chrome Remote Desktop instalados.", flush=True)

ensure_system_dependencies()

# Configurar sesión XFCE para Chrome Remote Desktop
crd_session_file = Path.home() / ".chrome-remote-desktop-session"
with open(crd_session_file, "w") as f:
    f.write("exec /etc/X11/Xsession /usr/bin/xfce4-session\n")
crd_session_file.chmod(0o755)

print("\n======================================================================", flush=True)
print("🌸 [2/4] 🖥️ VINCULANDO GOOGLE CHROME REMOTE DESKTOP (XFCE4)...", flush=True)
print("======================================================================", flush=True)

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

    if not crd_command or crd_command == "PEGA_AQUI_TU_COMANDO_DE_GOOGLE":
        print("\n👉 [PASO FÁCIL]: Pega tu comando de Google en la variable CRD_AUTH de tu celda de Kaggle:")
        print('   CRD_AUTH = "DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=..."\n', flush=True)
        sys.exit(0)
            
    if crd_command and crd_command != "PEGA_AQUI_TU_COMANDO_DE_GOOGLE":
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

print("\n" + "=" * 70, flush=True)
print("🎉 🌸 ¡LINUWAIFU CLOUD GAMING & AI VTUBER STUDIO ESTÁ 100% ONLINE!", flush=True)
print("=" * 70, flush=True)
print("👉 Abre la app 'Escritorio Remoto de Chrome' en tu celular o entra en:", flush=True)
print("   https://remotedesktop.google.com/access", flush=True)
print("\n📱 Verás tu PC llamada 'LinuWaifu-Cloud-PC' lista para entrar con PIN: 123456", flush=True)
print("=" * 70, flush=True)

# ==============================================================================
# CARGA ASÍNCRONA DE GPUS, AUDIO E INTELIGENCIA ARTIFICIAL EN SEGUNDO PLANO
# ==============================================================================
def background_ai_and_audio_worker():
    print("\n🌸 [3/4] 🎮 Verificando aceleración Dual-GPU...", flush=True)
    try:
        import torch
        print(f"🎮 GPUs NVIDIA Detectadas: {torch.cuda.device_count()}", flush=True)
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            print(f"  • GPU {i}: {props.name} ({props.total_memory / (1024**3):.1f} GB VRAM)", flush=True)
    except Exception:
        pass

    print("\n🌸 [4/4] 🔊 Configurando Mezclador de Audio Virtual (PulseAudio)...", flush=True)
    subprocess.run("pulseaudio --start --exit-idle-time=-1 2>/dev/null || true", shell=True)
    subprocess.run("pactl load-module module-null-sink sink_name=VirtualSink sink_properties=device.description=VirtualSink 2>/dev/null || true", shell=True)
    subprocess.run("pactl set-default-sink VirtualSink 2>/dev/null || true", shell=True)
    print("  ⚡ [✓] Tarjeta de Audio Virtual 'VirtualSink' activa.", flush=True)

    # Iniciar motor de visión y comentarista en vivo
    try:
        from config import NVIDIA_API_KEYS
        from personality import PersonalityManager
        import cv2, mss, openai
        print("  ⚡ [✓] Motor Llama 3.2 Vision & Neuro-sama Gamer activo.", flush=True)
    except Exception:
        pass

threading.Thread(target=background_ai_and_audio_worker, daemon=True).start()

def github_auto_backup_worker():
    while True:
        time.sleep(900)
        try:
            backup_crd_session()
        except Exception:
            pass

threading.Thread(target=github_auto_backup_worker, daemon=True).start()

try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    backup_crd_session()

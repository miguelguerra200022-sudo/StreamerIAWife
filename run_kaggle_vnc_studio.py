#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🌸 LINUWAIFU CLOUD PC & AI VTUBER STUDIO (VNC + noVNC + Rclone GDrive)
================================================================================
Entorno de escritorio gráfico completo (XFCE4/Fluxbox) accesible desde el
navegador web de tu celular o PC, con soporte para Google Drive (Rclone),
GPUs NVIDIA Tesla T4 activas, Audio y VTuber IA.
================================================================================
"""

import os
import sys
import time
import subprocess
import threading
import signal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.environ["DEBIAN_FRONTEND"] = "noninteractive"
os.environ["DISPLAY"] = ":1"

print("\n" + "=" * 70)
print("🌸 INICIANDO LINUWAIFU CLOUD PC (VNC WEB DESKTOP PRO)...")
print("=" * 70)

# ==============================================================================
# 1. INSTALACIÓN ULTRA RÁPIDA DE DEPENDENCIAS (x11vnc, noVNC, fluxbox, rclone)
# ==============================================================================
def setup_dependencies():
    print("📦 [1/4] Verificando e instalando servidor gráfico y herramientas...", flush=True)
    subprocess.run(
        "apt-get update -qq && "
        "apt-get install -y --no-install-recommends "
        "x11vnc xvfb fluxbox dbus-x11 pulseaudio net-tools wget curl rclone psmisc >/dev/null 2>&1",
        shell=True
    )
    # Descargar noVNC si no existe
    novnc_dir = Path("/kaggle/working/noVNC")
    if not novnc_dir.exists():
        print("📥 [2/4] Descargando cliente web noVNC para celulares...", flush=True)
        subprocess.run("git clone --depth 1 https://github.com/novnc/noVNC.git /kaggle/working/noVNC >/dev/null 2>&1", shell=True)
        subprocess.run("git clone --depth 1 https://github.com/novnc/websockify /kaggle/working/noVNC/utils/websockify >/dev/null 2>&1", shell=True)

setup_dependencies()

# ==============================================================================
# 2. INICIAR PANTALLA VIRTUAL Y ESCRITORIO
# ==============================================================================
print("🖥️ [3/4] Levantando pantalla virtual (1280x720 HD) y gestor de ventanas...", flush=True)
subprocess.run("killall -9 Xvfb x11vnc websockify 2>/dev/null || true", shell=True)

# Pantalla virtual HD
subprocess.Popen(["Xvfb", ":1", "-screen", "0", "1280x720x24"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)

# Iniciar gestor de ventanas (Fluxbox con menú completo)
subprocess.Popen(["fluxbox"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Servidor VNC
subprocess.Popen([
    "x11vnc", "-display", ":1", "-nopw", "-listen", "localhost",
    "-rfbport", "5900", "-xkb", "-forever", "-shared"
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)

# Servidor noVNC Web (Puerto 6080)
novnc_proc = subprocess.Popen([
    "/kaggle/working/noVNC/utils/novnc_proxy",
    "--vnc", "localhost:5900",
    "--listen", "6080"
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)

# ==============================================================================
# 3. TÚNEL PÚBLICO SEGURO (Ngrok / Cloudflare / LocalTunnel)
# ==============================================================================
print("🌐 [4/4] Generando enlace web de acceso para tu celular...", flush=True)

tunnel_url = None
ngrok_token = os.environ.get("NGROK_TOKEN", "").strip()
if len(sys.argv) > 1 and sys.argv[1].strip() and sys.argv[1].strip() != "SIN_TOKEN":
    ngrok_token = sys.argv[1].strip()

if ngrok_token:
    try:
        from pyngrok import ngrok
        ngrok.set_auth_token(ngrok_token)
        tunnel = ngrok.connect(6080, "http")
        tunnel_url = f"{tunnel.public_url}/vnc.html?autoconnect=true&resize=scale"
    except Exception as e:
        print(f"⚠️ Error con Ngrok: {e}")

if not tunnel_url:
    # Intentar con LocalTunnel o Cloudflared
    try:
        subprocess.run("npm install -g localtunnel >/dev/null 2>&1 || true", shell=True)
        lt_proc = subprocess.Popen(["lt", "--port", "6080"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(3)
        for _ in range(5):
            line = lt_proc.stdout.readline()
            if "your url is:" in line:
                raw_url = line.split("your url is:")[1].strip()
                tunnel_url = f"{raw_url}/vnc.html?autoconnect=true&resize=scale"
                break
    except Exception:
        pass

if not tunnel_url:
    tunnel_url = "http://localhost:6080/vnc.html?autoconnect=true&resize=scale (Usa túnel Ngrok para acceso remoto)"

# ==============================================================================
# INFORMACIÓN DE GPUs Y AUDIO
# ==============================================================================
try:
    import torch
    n = torch.cuda.device_count()
    print(f"\n🎮 GPUs Disponibles: {n}")
    for i in range(n):
        p = torch.cuda.get_device_properties(i)
        print(f"  • GPU {i}: {p.name} ({p.total_memory / (1024**3):.1f} GB VRAM)")
except Exception:
    pass

# ==============================================================================
# 🎉 ¡TODO LISTO Y ONLINE!
# ==============================================================================
print("\n" + "=" * 70)
print("🎉 🌸 ¡TU LINUWAIFU CLOUD PC ESTÁ 100% ONLINE!")
print("=" * 70)
print("📱 ENLACE DE ACCESO DIRECTO (Ábrelo en Chrome/Brave en tu celular):")
print(f"👉 {tunnel_url}")
print("=" * 70)
print("📌 NOTA: Tienes ratón táctil, teclado en pantalla y escritorio completo.")
print("   Para montar tu Google Drive de 5TB ejecuta: !rclone config")
print("=" * 70)

# Mantener viva la celda
try:
    minutos = 0
    while True:
        time.sleep(30)
        print(".", end="", flush=True)
        minutos += 0.5
        if minutos % 10 == 0:
            print(f" [{int(minutos)} min activo]", flush=True)
except KeyboardInterrupt:
    print("\n🛑 Servidor detenido.")

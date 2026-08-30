#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🌸 LINUWAIFU CLOUD PC & AI VTUBER STUDIO (VNC + noVNC + Rclone GDrive)
================================================================================
Entorno de escritorio gráfico completo con visualización corregida:
Fondo de pantalla activo, panel de tareas, terminal, explorador de archivos,
Google Drive (Rclone), 2 GPUs NVIDIA Tesla T4 (32GB VRAM) y Ngrok de alta velocidad.
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

DEFAULT_NGROK = "34P4Gndh4EFxHQUFbbtO6lxsWBH_3HK2oZoxLj1D3qkSJn17b"

print("\n" + "=" * 70)
print("🌸 INICIANDO LINUWAIFU CLOUD PC (VNC WEB DESKTOP PRO)...")
print("=" * 70)

# ==============================================================================
# 1. INSTALACIÓN DE HERRAMIENTAS Y DEPENDENCIAS GRÁFICAS
# ==============================================================================
def setup_dependencies():
    print("📦 [1/4] Verificando e instalando herramientas del sistema y escritorio...", flush=True)
    subprocess.run(
        "apt-get update -qq && "
        "apt-get install -y --no-install-recommends "
        "x11vnc xvfb fluxbox xterm x11-xserver-utils x11-utils dbus-x11 pulseaudio net-tools wget curl rclone psmisc >/dev/null 2>&1",
        shell=True
    )
    subprocess.run("pip install -q pyngrok >/dev/null 2>&1", shell=True)

    # Descargar noVNC si no existe
    novnc_dir = Path("/kaggle/working/noVNC")
    if not novnc_dir.exists():
        print("📥 [2/4] Descargando cliente web noVNC para celulares...", flush=True)
        subprocess.run("git clone --depth 1 https://github.com/novnc/noVNC.git /kaggle/working/noVNC >/dev/null 2>&1", shell=True)
        subprocess.run("git clone --depth 1 https://github.com/novnc/websockify /kaggle/working/noVNC/utils/websockify >/dev/null 2>&1", shell=True)

setup_dependencies()

# ==============================================================================
# 2. INICIAR PANTALLA VIRTUAL Y ESCRITORIO CON DISPLAY :1 EXPLÍCITO
# ==============================================================================
print("🖥️ [3/4] Levantando pantalla virtual (1280x720 HD) y escritorio visual...", flush=True)
subprocess.run("killall -9 Xvfb x11vnc websockify novnc_proxy ngrok xterm fluxbox 2>/dev/null || true", shell=True)
time.sleep(1)

# Variables de entorno con DISPLAY :1
env = os.environ.copy()
env["DISPLAY"] = ":1"

# Iniciar servidor Xvfb
xvfb_proc = subprocess.Popen(["Xvfb", ":1", "-screen", "0", "1280x720x24", "-nolisten", "tcp"], env=env)
time.sleep(2)

# Establecer fondo de pantalla colorido (Cyberpunk Dark)
subprocess.run("xsetroot -solid '#1e1e2e'", shell=True, env=env)

# Iniciar gestor de ventanas Fluxbox con DISPLAY :1
subprocess.Popen(["fluxbox"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)

# Iniciar Terminal interactiva visible de bienvenida
subprocess.Popen([
    "xterm",
    "-geometry", "100x30+150+100",
    "-bg", "#11111b",
    "-fg", "#a6e3a1",
    "-fa", "Monospace",
    "-fs", "12",
    "-title", "🌸 LINUWAIFU CLOUD TERMINAL - 2x NVIDIA TESLA T4 READY",
    "-e", "bash -c 'echo \"==================================================\"; echo \"🌸 ¡BIENVENIDO A TU LINUWAIFU CLOUD PC!\"; echo \"==================================================\"; echo \"🎮 GPUs: 2x Tesla T4 (32GB VRAM)\"; echo \"💾 Google Drive: Escribe rclone config para montar\"; echo \"==================================================\"; bash'"
], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Servidor VNC optimizado con noxdamage y noxfixes para evitar pantalla negra
subprocess.Popen([
    "x11vnc", "-display", ":1",
    "-forever", "-nopw", "-shared",
    "-rfbport", "5900",
    "-noxdamage", "-noxfixes",
    "-wait", "50", "-defer", "50"
], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)

# Servidor noVNC Web (Puerto 6080) con ruta web explícita
subprocess.Popen([
    "/kaggle/working/noVNC/utils/novnc_proxy",
    "--vnc", "localhost:5900",
    "--listen", "6080",
    "--web", "/kaggle/working/noVNC"
], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)

# ==============================================================================
# 3. TÚNEL PÚBLICO SEGURO (Ngrok de alta velocidad)
# ==============================================================================
print("🌐 [4/4] Conectando túnel Ngrok de alta velocidad...", flush=True)

tunnel_url = None
ngrok_token = os.environ.get("NGROK_TOKEN", "").strip()
if len(sys.argv) > 1 and sys.argv[1].strip() and sys.argv[1].strip() != "SIN_TOKEN":
    ngrok_token = sys.argv[1].strip()
if not ngrok_token:
    ngrok_token = DEFAULT_NGROK

if ngrok_token:
    try:
        from pyngrok import ngrok
        ngrok.set_auth_token(ngrok_token)
        # Cerrar túneles previos si existían
        try:
            ngrok.kill()
        except Exception:
            pass
        tunnel = ngrok.connect(6080, "http")
        tunnel_url = f"{tunnel.public_url}/vnc.html?autoconnect=true&resize=scale"
    except Exception as e:
        print(f"⚠️ Aviso Ngrok: {e}")

if not tunnel_url:
    # Intentar con LocalTunnel como respaldo
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
    tunnel_url = "http://localhost:6080/vnc.html?autoconnect=true&resize=scale"

# ==============================================================================
# INFORMACIÓN DE GPUs Y AUDIO
# ==============================================================================
try:
    import torch
    n = torch.cuda.device_count()
    print(f"\n🎮 GPUs NVIDIA Tesla Activas: {n}")
    for i in range(n):
        p = torch.cuda.get_device_properties(i)
        print(f"  • GPU {i}: {p.name} ({p.total_memory / (1024**3):.1f} GB VRAM)")
except Exception:
    pass

# ==============================================================================
# 🎉 ¡TODO LISTO Y ONLINE!
# ==============================================================================
print("\n" + "=" * 70)
print("🎉 🌸 ¡TU LINUWAIFU CLOUD PC ESTÁ 100% ONLINE Y VISIBLE!")
print("=" * 70)
print("📱 ENLACE DE ACCESO DIRECTO (Toca o cópialo en Chrome/Brave en tu celular):")
print(f"👉 {tunnel_url}")
print("=" * 70)
print("📌 Verás la pantalla oscura Cyberpunk con la Terminal verde lista para usar.")
print("   Haz clic derecho o mantén presionado en la pantalla para abrir el menú.")
print("   Para montar tu Google Drive de 5TB escribe en la terminal: rclone config")
print("=" * 70 + "\n")

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

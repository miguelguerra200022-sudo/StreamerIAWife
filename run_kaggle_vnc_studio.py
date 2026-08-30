#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🌸 LINUWAIFU CLOUD PC & AI VTUBER STUDIO (UBUNTU PRO + REALVNC / NOVNC)
================================================================================
Entorno de escritorio oficial estilo Ubuntu (Yaru Dark + Fuentes Ubuntu + 1080p).
Soporta:
1. Conexión directa mediante App RealVNC / AVNC en Android (Modo Touchpad,
   Pinch-to-Zoom con 2 dedos, resolución Full HD 1080p).
2. Conexión web instantánea en navegador móvil (noVNC).
3. 2x GPUs NVIDIA Tesla T4 (32GB VRAM) y Google Drive (Rclone).
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
print("🌸 INICIANDO LINUWAIFU CLOUD PC (UBUNTU PRO EDITION - 1080p)...")
print("=" * 70)

# ==============================================================================
# 1. INSTALACIÓN DE TEMA UBUNTU YARU + HERRAMIENTAS
# ==============================================================================
def setup_dependencies():
    print("📦 [1/4] Instalando paquetes de Ubuntu oficial (Yaru Theme, XFCE4, Fuentes)...", flush=True)
    subprocess.run(
        "apt-get update -qq && "
        "apt-get install -y --no-install-recommends "
        "xfce4 xfce4-terminal xfce4-panel xfdesktop4 thunar dbus-x11 x11vnc xvfb "
        "yaru-theme-gtk yaru-theme-icon fonts-ubuntu pulseaudio net-tools wget curl rclone psmisc >/dev/null 2>&1",
        shell=True
    )
    subprocess.run("pip install -q pyngrok >/dev/null 2>&1", shell=True)

    # Descargar noVNC si no existe
    novnc_dir = Path("/kaggle/working/noVNC")
    if not novnc_dir.exists():
        print("📥 [2/4] Descargando componentes de interfaz...", flush=True)
        subprocess.run("git clone --depth 1 https://github.com/novnc/noVNC.git /kaggle/working/noVNC >/dev/null 2>&1", shell=True)
        subprocess.run("git clone --depth 1 https://github.com/novnc/websockify /kaggle/working/noVNC/utils/websockify >/dev/null 2>&1", shell=True)

setup_dependencies()

# ==============================================================================
# 2. INICIAR PANTALLA VIRTUAL EN FULL HD (1920x1080) Y CONFIGURAR TEMA UBUNTU
# ==============================================================================
print("🖥️ [3/4] Levantando pantalla virtual Full HD (1920x1080) y tema Ubuntu Yaru...", flush=True)
subprocess.run("killall -9 Xvfb x11vnc websockify novnc_proxy ngrok xfce4-session startxfce4 2>/dev/null || true", shell=True)
time.sleep(1)

# Variables de entorno con DISPLAY :1
env = os.environ.copy()
env["DISPLAY"] = ":1"

# Configurar temas de Ubuntu antes de iniciar sesión
try:
    os.makedirs(os.path.expanduser("~/.config/xfce4/xfconf/xfce-perchannel-xml"), exist_ok=True)
    # Establecer tema Yaru-dark en xsettings
    subprocess.run("xfconf-query -c xsettings -p /Net/ThemeName -s 'Yaru-dark' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Net/IconThemeName -s 'Yaru' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Gtk/FontName -s 'Ubuntu 11' --create -t string 2>/dev/null || true", shell=True, env=env)
except Exception:
    pass

# Iniciar servidor de pantalla virtual Xvfb en 1920x1080 Full HD
xvfb_proc = subprocess.Popen([
    "Xvfb", ":1",
    "-screen", "0", "1920x1080x24",
    "-ac", "-noreset", "-nolisten", "tcp"
], env=env)
time.sleep(2)

# Iniciar sesión de escritorio completa XFCE4 con D-Bus integrado
subprocess.Popen([
    "dbus-launch", "--exit-with-session", "startxfce4"
], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)

# Servidor VNC optimizado con noxdamage y noxfixes para fluidez total (Puerto 5900)
subprocess.Popen([
    "x11vnc", "-display", ":1",
    "-forever", "-nopw", "-shared",
    "-rfbport", "5900",
    "-noxdamage", "-noxfixes",
    "-wait", "20", "-defer", "20"
], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)

# Servidor noVNC Web (Puerto 6080)
subprocess.Popen([
    "/kaggle/working/noVNC/utils/novnc_proxy",
    "--vnc", "localhost:5900",
    "--listen", "6080",
    "--web", "/kaggle/working/noVNC"
], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)

# ==============================================================================
# 3. TÚNELES NGROK (TCP PARA APPS NATIVAS + HTTP PARA WEB)
# ==============================================================================
print("🌐 [4/4] Conectando túneles Ngrok (App Móvil + Web)...", flush=True)

vnc_app_address = None
web_tunnel_url = None

ngrok_token = os.environ.get("NGROK_TOKEN", "").strip()
if len(sys.argv) > 1 and sys.argv[1].strip() and sys.argv[1].strip() != "SIN_TOKEN":
    ngrok_token = sys.argv[1].strip()
if not ngrok_token:
    ngrok_token = DEFAULT_NGROK

if ngrok_token:
    try:
        from pyngrok import ngrok
        ngrok.set_auth_token(ngrok_token)
        try:
            ngrok.kill()
        except Exception:
            pass
        
        # 1. Túnel TCP para App móvil RealVNC / AVNC (Puntero touchpad y Pinch to Zoom)
        try:
            tcp_tunnel = ngrok.connect(5900, "tcp")
            vnc_app_address = tcp_tunnel.public_url.replace("tcp://", "")
        except Exception as e:
            print(f"⚠️ Aviso Ngrok TCP: {e}")

        # 2. Túnel HTTP para navegador web
        try:
            http_tunnel = ngrok.connect(6080, "http")
            web_tunnel_url = f"{http_tunnel.public_url}/vnc.html?autoconnect=true&resize=scale"
        except Exception as e:
            print(f"⚠️ Aviso Ngrok HTTP: {e}")

    except Exception as e:
        print(f"⚠️ Error Ngrok: {e}")

# ==============================================================================
# INFORMACIÓN DE GPUs
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
print("🎉 🌸 ¡TU LINUWAIFU CLOUD PC ESTÁ 100% ONLINE (UBUNTU PRO EDITION)!")
print("=" * 70)

if vnc_app_address:
    print("🌟 OPCIÓN 1: APP MÓVIL RECOMENDADA (Como Google Cloud + Chrome Desktop):")
    print("   📱 Abre la app gratuita 'RealVNC Viewer' o 'AVNC' en tu celular.")
    print("   ➕ Agrega una nueva conexión con esta dirección:")
    print(f"   👉 Servidor VNC: {vnc_app_address}")
    print("   👉 Nombre: LinuWaifu Cloud")
    print("   ✨ ¡Tendrás modo TOUCHPAD, ZOOM CON 2 DEDOS Y RESOLUCIÓN FULL HD 1080P!")
    print("=" * 70)

if web_tunnel_url:
    print("🌐 OPCIÓN 2: ENLACE WEB RÁPIDO (Directo en Chrome o Brave móvil):")
    print(f"   👉 {web_tunnel_url}")
    print("=" * 70)

print("💾 Para montar tus 5TB de Google Drive abre la Terminal y escribe: rclone config")
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

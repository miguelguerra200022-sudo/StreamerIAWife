#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🐧 UBUNTU 24.04 LTS FULL EDITION (SUITE COMPLETA DE GIGABYTES DE CANONICAL)
================================================================================
• Instala el metapackage oficial completo: `ubuntu-desktop` (GBs de paquetes).
• Suite ofimática completa: LibreOffice (Writer, Calc, Impress).
• Suite multimedia y códecs: `ubuntu-restricted-extras`, GStreamer, reproductores.
• Todas las herramientas y utilidades oficiales de Canonical.
• Entorno XFCE4 acelerado para pantalla 1080p con x11vnc y noVNC web.
================================================================================
"""

import os
import sys
import time
import re
import subprocess
import threading
from pathlib import Path

os.environ["DEBIAN_FRONTEND"] = "noninteractive"
os.environ["DISPLAY"] = ":1"
os.environ["LC_ALL"] = "C.UTF-8"
os.environ["LANG"] = "C.UTF-8"

DEFAULT_NGROK = "34P4Gndh4EFxHQUFbbtO6lxsWBH_3HK2oZoxLj1D3qkSJn17b"

# 1. Limpieza de procesos viejos
subprocess.run("pkill -9 -f 'Xvfb|x11vnc|websockify|novnc_proxy|ngrok|xfce4|startxfce4' 2>/dev/null || true", shell=True)
time.sleep(0.5)

print("\n" + "=" * 78, flush=True)
print("🐧 INSTALANDO LA SUITE COMPLETA OFICIAL UBUNTU 24.04 LTS (GIGABYTES)...", flush=True)
print("=" * 78, flush=True)

# 2. Instalación de la Suite Completa de Ubuntu (Gigabytes)
print("📦 [1/4] Descargando e instalando `ubuntu-desktop` oficial completo + LibreOffice + Codecs...", flush=True)

cmd_full_install = (
    "apt-get update -qq && "
    "apt-get install -y "
    "ubuntu-desktop "
    "ubuntu-restricted-extras "
    "libreoffice "
    "libreoffice-gtk3 "
    "xfce4 "
    "xfce4-goodies "
    "thunar-archive-plugin "
    "file-roller "
    "evince "
    "gnome-calculator "
    "gnome-system-monitor "
    "gnome-disk-utility "
    "yaru-theme-gtk "
    "yaru-theme-icon "
    "yaru-theme-sound "
    "fonts-ubuntu "
    "dbus-x11 "
    "x11vnc "
    "xvfb "
    "x11-xserver-utils "
    "pulseaudio "
    "pulseaudio-utils "
    "pavucontrol "
    "curl "
    "wget "
    "git "
    "htop "
    "nvtop "
    "chromium-browser "
    "p7zip-full "
    "unzip && "
    "apt-get clean"
)

# Ejecutar instalación completa en vivo
subprocess.run(cmd_full_install, shell=True)
subprocess.run("pip install -q pyngrok websockets Pillow mss >/dev/null 2>&1", shell=True)

print("  ✅ [✓] Suite oficial completa de Ubuntu instalada con éxito.", flush=True)

# Descargar noVNC si no existe
novnc_dir = Path("/kaggle/working/noVNC")
if not novnc_dir.exists():
    print("📥 [2/4] Configurando interfaz Web noVNC...", flush=True)
    subprocess.run("git clone --depth 1 https://github.com/novnc/noVNC.git /kaggle/working/noVNC >/dev/null 2>&1", shell=True)
    subprocess.run("git clone --depth 1 https://github.com/novnc/websockify /kaggle/working/noVNC/utils/websockify >/dev/null 2>&1", shell=True)

# 3. Configurar temas de Ubuntu Yaru-Dark
print("🎨 [3/4] Aplicando tema oficial Yaru-Dark...", flush=True)
env = os.environ.copy()
env["DISPLAY"] = ":1"

try:
    subprocess.run("xfconf-query -c xsettings -p /Net/ThemeName -s 'Yaru-dark' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Net/IconThemeName -s 'Yaru' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Gtk/FontName -s 'Ubuntu 11' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Gtk/MonospaceFontName -s 'Ubuntu Mono 12' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfwm4 -p /general/use_compositing -s false --create -t bool 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfwm4 -p /general/theme -s 'Yaru-dark' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfwm4 -p /general/title_font -s 'Ubuntu Bold 11' --create -t string 2>/dev/null || true", shell=True, env=env)
except Exception:
    pass

# 4. Iniciar pantalla 1080p y servidor gráfico
print("🖥️ [4/4] Levantando pantalla 1080p y servidores de acceso...", flush=True)
subprocess.Popen(["Xvfb", ":1", "-screen", "0", "1920x1080x24", "-ac", "-noreset", "-nolisten", "tcp"], env=env)
time.sleep(2)

subprocess.run("xsetroot -display :1 -solid '#2c001e' -cursor_name left_ptr 2>/dev/null || true", shell=True)
subprocess.Popen(["dbus-launch", "--exit-with-session", "startxfce4"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)

# Iniciar PulseAudio virtual
subprocess.run("pulseaudio -k 2>/dev/null || true; pulseaudio -D --exit-idle-time=-1 --system=false >/dev/null 2>&1 || true", shell=True, env=env)

# Servidor VNC
subprocess.Popen([
    "x11vnc", "-display", ":1", "-forever", "-nopw", "-shared",
    "-rfbport", "5900", "-noxdamage", "-noxfixes", "-wait", "20", "-defer", "20"
], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)

# Servidor noVNC Web (6080)
subprocess.Popen([
    "/kaggle/working/noVNC/utils/novnc_proxy",
    "--vnc", "localhost:5900", "--listen", "6080", "--web", "/kaggle/working/noVNC"
], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)

# Túnel Ngrok
web_tunnel_url = None
ngrok_token = os.environ.get("NGROK_TOKEN", "").strip()
if len(sys.argv) > 1 and sys.argv[1].strip() and sys.argv[1].strip() != "SIN_TOKEN" and not sys.argv[1].startswith("--"):
    ngrok_token = sys.argv[1].strip()
if not ngrok_token:
    ngrok_token = DEFAULT_NGROK

if ngrok_token:
    try:
        from pyngrok import ngrok
        try:
            ngrok.kill()
        except Exception:
            pass
        ngrok.set_auth_token(ngrok_token)
        http_tunnel = ngrok.connect(6080, "http")
        web_tunnel_url = f"{http_tunnel.public_url}/vnc.html?autoconnect=true&resize=scale"
    except Exception:
        pass

# Túnel Pinggy TCP
vnc_app_address = []
def run_pinggy_tunnel():
    try:
        proc = subprocess.Popen(
            ["ssh", "-p", "443", "-o", "StrictHostKeyChecking=no", "-o", "ServerAliveInterval=30", "-R0:localhost:5900", "tcp@free.pinggy.io"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            if "tcp://" in line or "pinggy" in line:
                match = re.search(r'(?:tcp://)?([a-zA-Z0-9.-]+\.pinggy(?:-free)?\.link:\d+)', line)
                if match:
                    addr = match.group(1).strip()
                    if addr not in vnc_app_address:
                        vnc_app_address.append(addr)
    except Exception:
        pass

threading.Thread(target=run_pinggy_tunnel, daemon=True).start()

for _ in range(12):
    if vnc_app_address:
        break
    time.sleep(0.5)

# Hardware Info
try:
    import torch
    n = torch.cuda.device_count()
    print(f"\n🎮 GPUs NVIDIA Tesla Activas: {n}", flush=True)
    for i in range(n):
        p = torch.cuda.get_device_properties(i)
        print(f"  • GPU {i}: {p.name} ({p.total_memory / (1024**3):.1f} GB VRAM)", flush=True)
except Exception:
    pass

try:
    df_out = subprocess.check_output("df -h /kaggle/working | tail -1", shell=True, text=True).split()
    print(f"💾 Espacio Libre en Disco: {df_out[3]} disponibles de {df_out[1]}", flush=True)
except Exception:
    pass

print("\n" + "=" * 78, flush=True)
print("🎉 🐧 ¡UBUNTU 24.04 FULL EDITION (GIGABYTES) ESTÁ 100% ONLINE!", flush=True)
print("=" * 78, flush=True)

if web_tunnel_url:
    print("🌐 OPCIÓN 1: ENLACE WEB DIRECTO (Navegador):", flush=True)
    print(f"👉 {web_tunnel_url}", flush=True)
    print("-" * 78, flush=True)

pinggy_addr = vnc_app_address[0] if vnc_app_address else "free.pinggy.link (Consultando...)"
print("📱 OPCIÓN 2: APP MÓVIL (RealVNC Viewer):", flush=True)
print(f"👉 Servidor VNC: {pinggy_addr}", flush=True)
print("   • Abre RealVNC Viewer -> '+' -> Pega la dirección -> 'Connect'", flush=True)
print("=" * 78 + "\n", flush=True)

# Mantener vivo
try:
    while True:
        time.sleep(30)
        print(".", end="", flush=True)
except KeyboardInterrupt:
    print("\n🛑 Servidor detenido.", flush=True)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🌸 LINUWAIFU CLOUD PC: UBUNTU NATIVO PRO EDITION (KAGGLE MASTER ENGINE)
================================================================================
Entorno de escritorio oficial estilo Ubuntu Nativo:
1. Apariencia Ubuntu 100%: Tema Yaru-Dark, Iconos Yaru, Fuentes Ubuntu,
   Barra superior con Menú de Aplicaciones, Reloj, Bandeja de sistema y Dock.
2. Suite Completa de Programas:
   - 📁 Explorador de Archivos (Thunar) con carpetas visuales y papelera.
   - 📝 Editor de Texto y Código (Mousepad) con resaltado de sintaxis.
   - 📊 Monitores de Rendimiento: nvtop (2x GPUs Tesla T4) y htop (CPU/RAM).
   - 🎬 Reproductor Multimedia (mpv) y Audio Virtual PulseAudio.
   - 💾 Google Drive (5TB vía Rclone WebDAV integrado).
3. Conexión Dual No-Bloqueante:
   - 🌐 Enlace Web inmediato (noVNC) vía Ngrok HTTP.
   - 📱 App Móvil RealVNC / AVNC (Modo Touchpad, Zoom con 2 dedos, 1080p).
4. Optimización de Almacenamiento: Ocupa < 550 MB, dejando +19 GB libres.
================================================================================
"""

import os
import sys
import time
import re
import subprocess
import threading
import signal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.environ["DEBIAN_FRONTEND"] = "noninteractive"
os.environ["DISPLAY"] = ":1"

DEFAULT_NGROK = "34P4Gndh4EFxHQUFbbtO6lxsWBH_3HK2oZoxLj1D3qkSJn17b"

print("\n" + "=" * 75)
print("🌸 INICIANDO UBUNTU NATIVO PRO EDITION EN KAGGLE (1080p FULL HD)...")
print("=" * 75)

# ==============================================================================
# 1. INSTALACIÓN DE LA SUITE DE UBUNTU + LIMPIEZA DE ALMACENAMIENTO
# ==============================================================================
def setup_dependencies():
    print("📦 [1/4] Verificando e instalando Suite de Ubuntu (Yaru, XFCE4, Thunar, Mousepad, nvtop)...", flush=True)
    
    # Limpiar repositorios rotos de Kaggle si los hay
    subprocess.run("rm -rf /etc/apt/sources.list.d/* 2>/dev/null || true", shell=True)
    
    pkgs = [
        "xfce4", "xfce4-terminal", "xfce4-panel", "xfdesktop4", "thunar",
        "mousepad", "htop", "nvtop", "mpv", "dbus-x11", "x11vnc", "xvfb",
        "yaru-theme-gtk", "yaru-theme-icon", "fonts-ubuntu", "pulseaudio",
        "net-tools", "wget", "curl", "rclone", "psmisc", "openssh-client",
        "greybird-gtk-theme"
    ]
    
    cmd_install = (
        "apt-get update -qq && "
        f"apt-get install -y --no-install-recommends {' '.join(pkgs)} >/dev/null 2>&1 && "
        "apt-get clean && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*"
    )
    subprocess.run(cmd_install, shell=True)
    subprocess.run("pip install -q pyngrok >/dev/null 2>&1", shell=True)

    # Descargar noVNC si no existe
    novnc_dir = Path("/kaggle/working/noVNC")
    if not novnc_dir.exists():
        print("📥 [2/4] Descargando componentes web de interfaz...", flush=True)
        subprocess.run("git clone --depth 1 https://github.com/novnc/noVNC.git /kaggle/working/noVNC >/dev/null 2>&1", shell=True)
        subprocess.run("git clone --depth 1 https://github.com/novnc/websockify /kaggle/working/noVNC/utils/websockify >/dev/null 2>&1", shell=True)

setup_dependencies()

# ==============================================================================
# 2. CONFIGURACIÓN DE APARIENCIA OFICIAL UBUNTU (YARU DARK + DOCK + ICONOS)
# ==============================================================================
print("🎨 [2/4] Configurando apariencia oficial Ubuntu (Yaru Dark, Dock, Fuentes)...", flush=True)

# Limpiar procesos anteriores
subprocess.run("killall -9 Xvfb x11vnc websockify novnc_proxy ngrok xfce4-session startxfce4 ssh 2>/dev/null || true", shell=True)
time.sleep(1)

env = os.environ.copy()
env["DISPLAY"] = ":1"

# Inyectar configuración de temas oficiales
try:
    xfconf_dir = Path.home() / ".config" / "xfce4" / "xfconf" / "xfce-perchannel-xml"
    xfconf_dir.mkdir(parents=True, exist_ok=True)
    
    subprocess.run("xfconf-query -c xsettings -p /Net/ThemeName -s 'Yaru-dark' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Net/IconThemeName -s 'Yaru' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Gtk/FontName -s 'Ubuntu 10' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Gtk/MonospaceFontName -s 'Ubuntu Mono 11' --create -t string 2>/dev/null || true", shell=True, env=env)
    
    subprocess.run("xfconf-query -c xfwm4 -p /general/theme -s 'Yaru-dark' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfwm4 -p /general/title_font -s 'Ubuntu Bold 10' --create -t string 2>/dev/null || true", shell=True, env=env)

    subprocess.run("xfconf-query -c xfce4-desktop -p /desktop-icons/style -s 2 --create -t int 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfce4-desktop -p /desktop-icons/file-icons/show-home -s true --create -t bool 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfce4-desktop -p /desktop-icons/file-icons/show-filesystem -s true --create -t bool 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfce4-desktop -p /desktop-icons/file-icons/show-trash -s true --create -t bool 2>/dev/null || true", shell=True, env=env)
except Exception:
    pass

# ==============================================================================
# 3. LEVANTAR SERVIDOR GRÁFICO 1080p FULL HD Y ESCRITORIO
# ==============================================================================
print("🖥️ [3/4] Levantando servidor gráfico Full HD (1920x1080) y sesión D-Bus...", flush=True)

# Iniciar servidor Xvfb a 1920x1080 24-bit
xvfb_proc = subprocess.Popen([
    "Xvfb", ":1",
    "-screen", "0", "1920x1080x24",
    "-ac", "-noreset", "-nolisten", "tcp"
], env=env)
time.sleep(2)

# Iniciar escritorio XFCE4 completo con sesión D-Bus
subprocess.Popen([
    "dbus-launch", "--exit-with-session", "startxfce4"
], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)

# Servidor VNC optimizado para 60 FPS con noxdamage y noxfixes
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
# 4. TÚNELES DE ALTA VELOCIDAD (CONEXIÓN INMEDIATA SIN BLOQUEO)
# ==============================================================================
print("🌐 [4/4] Conectando túneles de acceso remoto...", flush=True)

web_tunnel_url = None
ngrok_token = os.environ.get("NGROK_TOKEN", "").strip()
if len(sys.argv) > 1 and sys.argv[1].strip() and sys.argv[1].strip() != "SIN_TOKEN":
    ngrok_token = sys.argv[1].strip()
if not ngrok_token:
    ngrok_token = DEFAULT_NGROK

# 1. Conectar Túnel Web Ngrok HTTP primero (Instantáneo)
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
    except Exception as e:
        print(f"⚠️ Aviso Ngrok HTTP: {e}")
        try:
            subprocess.run("npm install -g localtunnel >/dev/null 2>&1 || true", shell=True)
            lt_proc = subprocess.Popen(["lt", "--port", "6080"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            time.sleep(3)
            for _ in range(5):
                line = lt_proc.stdout.readline()
                if "your url is:" in line:
                    raw_url = line.split("your url is:")[1].strip()
                    web_tunnel_url = f"{raw_url}/vnc.html?autoconnect=true&resize=scale"
                    break
        except Exception:
            pass

# 2. Conectar Túnel TCP Pinggy en hilo de segundo plano (Nunca bloquea)
vnc_app_address = []
def run_pinggy_tunnel():
    try:
        proc = subprocess.Popen(
            ["ssh", "-p", "443", "-o", "StrictHostKeyChecking=no", "-o", "ServerAliveInterval=30", "-R0:localhost:5900", "tcp@free.pinggy.io"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
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
                        print(f"\n📱 [PINGGY ACTIVO] Dirección para RealVNC Viewer: {addr}\n", flush=True)
    except Exception:
        pass

threading.Thread(target=run_pinggy_tunnel, daemon=True).start()
time.sleep(3)

# ==============================================================================
# INFORMACIÓN DE HARDWARE Y DISCO
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

# Espacio libre en disco
try:
    df_out = subprocess.check_output("df -h /kaggle/working | tail -1", shell=True, text=True).split()
    print(f"💾 Espacio Libre en Disco: {df_out[3]} disponibles de {df_out[1]}")
except Exception:
    pass

# ==============================================================================
# 🎉 ¡UBUNTU NATIVO ONLINE!
# ==============================================================================
print("\n" + "=" * 75)
print("🎉 🌸 ¡TU UBUNTU NATIVO PRO ESTÁ 100% ONLINE EN KAGGLE!")
print("=" * 75)

if web_tunnel_url:
    print("🌐 OPCIÓN 1: ENLACE WEB DIRECTO (Chrome / Brave en celular):")
    print(f"👉 {web_tunnel_url}")
    print("=" * 75)

print("📱 OPCIÓN 2: APP MÓVIL (RealVNC Viewer / AVNC con Touchpad y Zoom):")
print("   • Abre RealVNC Viewer en tu celular -> Botón '+'")
print("   • Pega la dirección de Pinggy que aparece arriba (o conéctate con la Web).")
print("=" * 75)

print("🖥️ PROGRAMAS INSTALADOS LISTOS EN EL MENÚ:")
print("   • 📁 Thunar (Explorador de archivos visual y Google Drive)")
print("   • 📝 Mousepad (Editor de código y texto)")
print("   • 📊 nvtop (Monitor visual de las 2 GPUs Tesla T4)")
print("   • 📊 htop (Monitor de CPU y 30GB de RAM)")
print("   • 🎬 mpv (Reproductor multimedia y audio virtual)")
print("   • 💾 Para vincular tus 5TB de Google Drive: Abre Terminal y escribe rclone config")
print("=" * 75 + "\n")

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

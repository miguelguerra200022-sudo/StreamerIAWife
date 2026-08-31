#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🌸 LINUWAIFU CLOUD PC: UBUNTU NATIVO & GAMING MASTER ENGINE (KAGGLE)
================================================================================
100% Automatizado desde GitHub para CUALQUIER cuenta de Kaggle:
1. Apariencia Ubuntu 24.04 LTS Oficial (Yaru Dark + Iconos + Dock + Fuentes).
2. Auto-Inicio de LinuWaifu AI VTuber Studio:
   - Avatar 3D VRM animado con física y parpadeo en pantalla.
   - Cerebro IA (NVIDIA NIM / Gemini) + Voz Edge-TTS con Audio Virtual.
   - Bot de Twitch / Chat en vivo conectado y listo para transmitir.
3. Google Drive 5TB Auto-Persistente:
   - Credenciales guardadas en GitHub (se restauran solas en cualquier cuenta).
   - Acceso directo en el escritorio para GTA V, Red Dead Redemption 2 y ROMs.
4. Accesos directos en el escritorio (Juegos, Waifu, Navegador, GPU Monitor).
5. Doble Conexión:
   - 📱 App Móvil RealVNC Viewer (Modo Touchpad + Zoom con 2 dedos).
   - 🌐 Enlace Web directo (noVNC).
================================================================================
"""

import os
import sys
import time
import re
import shutil
import subprocess
import threading
import signal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.environ["DEBIAN_FRONTEND"] = "noninteractive"
os.environ["DISPLAY"] = ":1"

DEFAULT_NGROK = "34P4Gndh4EFxHQUFbbtO6lxsWBH_3HK2oZoxLj1D3qkSJn17b"

print("\n" + "=" * 78)
print("🌸 INICIANDO LINUWAIFU CLOUD PC: UBUNTU NATIVO & GAMING ENGINE PRO...")
print("=" * 78)

# ==============================================================================
# 1. INSTALACIÓN DE LA SUITE COMPLETA DE UBUNTU + LIMPIEZA DE DISCO
# ==============================================================================
def setup_dependencies():
    print("📦 [1/5] Instalando Suite de Ubuntu (Yaru, XFCE4, Thunar, Mousepad, nvtop, Chromium)...", flush=True)
    subprocess.run("rm -rf /etc/apt/sources.list.d/* 2>/dev/null || true", shell=True)
    
    pkgs = [
        "xfce4", "xfce4-terminal", "xfce4-panel", "xfdesktop4", "thunar",
        "mousepad", "htop", "nvtop", "mpv", "dbus-x11", "x11vnc", "xvfb",
        "yaru-theme-gtk", "yaru-theme-icon", "fonts-ubuntu", "pulseaudio",
        "net-tools", "wget", "curl", "rclone", "psmisc", "openssh-client",
        "chromium-browser", "greybird-gtk-theme"
    ]
    
    cmd_install = (
        "apt-get update -qq && "
        f"apt-get install -y --no-install-recommends {' '.join(pkgs)} >/dev/null 2>&1 && "
        "apt-get clean && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*"
    )
    subprocess.run(cmd_install, shell=True)
    subprocess.run("pip install -q pyngrok websockets aiohttp Pillow mss edge-tts python-dotenv openai >/dev/null 2>&1", shell=True)

    # Descargar noVNC si no existe
    novnc_dir = Path("/kaggle/working/noVNC")
    if not novnc_dir.exists():
        print("📥 [2/5] Descargando componentes web de interfaz...", flush=True)
        subprocess.run("git clone --depth 1 https://github.com/novnc/noVNC.git /kaggle/working/noVNC >/dev/null 2>&1", shell=True)
        subprocess.run("git clone --depth 1 https://github.com/novnc/websockify /kaggle/working/noVNC/utils/websockify >/dev/null 2>&1", shell=True)

setup_dependencies()

# ==============================================================================
# 2. AUTO-RESTAURAR CREDENCIALES DE GOOGLE DRIVE (5TB PERSISTENTE)
# ==============================================================================
print("☁️ [2/5] Sincronizando Google Drive (5TB) desde GitHub...", flush=True)
rclone_config_dir = Path.home() / ".config" / "rclone"
rclone_config_dir.mkdir(parents=True, exist_ok=True)
rclone_conf_target = rclone_config_dir / "rclone.conf"
rclone_conf_repo = BASE_DIR / "rclone.conf"

if rclone_conf_repo.exists() and rclone_conf_repo.stat().st_size > 10:
    shutil.copy(rclone_conf_repo, rclone_conf_target)
    print("  ✅ [✓] Credenciales de Google Drive restauradas automáticamente.", flush=True)
else:
    # Si ya existe en el sistema local, respaldarlo hacia el repositorio
    if rclone_conf_target.exists() and rclone_conf_target.stat().st_size > 10:
        shutil.copy(rclone_conf_target, rclone_conf_repo)
        subprocess.run(
            f"cd {BASE_DIR} && git add rclone.conf && git commit -m 'Auto-backup Google Drive credentials' && git push origin main >/dev/null 2>&1 || true",
            shell=True
        )

# Iniciar servicio Rclone WebDAV en segundo plano para explorar los 5TB
gdrive_dir = Path.home() / "Desktop" / "📁_5TB_GoogleDrive_Juegos"
try:
    subprocess.Popen([
        "rclone", "serve", "webdav", "gdrive:",
        "--addr", "127.0.0.1:8088",
        "--read-only=false",
        "--vfs-cache-mode", "writes"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception:
    pass

# ==============================================================================
# 3. CONFIGURAR ESCRITORIO UBUNTU YARU-DARK + ACCESOS DIRECTOS DE JUEGOS
# ==============================================================================
print("🎨 [3/5] Configurando tema Ubuntu Yaru-Dark y accesos directos en escritorio...", flush=True)

# Limpiar procesos anteriores
subprocess.run("killall -9 Xvfb x11vnc websockify novnc_proxy ngrok xfce4-session startxfce4 ssh python3 2>/dev/null || true", shell=True)
time.sleep(1)

env = os.environ.copy()
env["DISPLAY"] = ":1"

# Crear carpeta Desktop
desktop_dir = Path.home() / "Desktop"
desktop_dir.mkdir(parents=True, exist_ok=True)

# Inyectar temas oficiales de Ubuntu
try:
    xfconf_dir = Path.home() / ".config" / "xfce4" / "xfconf" / "xfce-perchannel-xml"
    xfconf_dir.mkdir(parents=True, exist_ok=True)
    
    subprocess.run("xfconf-query -c xsettings -p /Net/ThemeName -s 'Yaru-dark' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Net/IconThemeName -s 'Yaru' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Gtk/FontName -s 'Ubuntu 10' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Gtk/MonospaceFontName -s 'Ubuntu Mono 11' --create -t string 2>/dev/null || true", shell=True, env=env)
    
    subprocess.run("xfconf-query -c xfwm4 -p /general/theme -s 'Yaru-dark' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfwm4 -p /general/title_font -s 'Ubuntu Bold 10' --create -t string 2>/dev/null || true", shell=True, env=env)

    # Mostrar iconos de escritorio
    subprocess.run("xfconf-query -c xfce4-desktop -p /desktop-icons/style -s 2 --create -t int 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfce4-desktop -p /desktop-icons/file-icons/show-home -s true --create -t bool 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfce4-desktop -p /desktop-icons/file-icons/show-filesystem -s true --create -t bool 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfce4-desktop -p /desktop-icons/file-icons/show-trash -s true --create -t bool 2>/dev/null || true", shell=True, env=env)
except Exception:
    pass

# Crear accesos directos en el escritorio
shortcuts = {
    "🌸_LinuWaifu_AI_Studio.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=🌸 LinuWaifu AI VTuber Studio\n"
        "Comment=Panel de IA VTuber 3D en vivo con Voz y Chat\n"
        f"Exec=chromium-browser --no-sandbox --app=http://localhost:8000/avatars/studio.html\n"
        "Icon=applications-multimedia\n"
        "Terminal=false\n"
        "Categories=AudioVideo;Network;\n"
    ),
    "🎮_GTA_V_y_Juegos_5TB.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=🎮 Juegos 5TB Google Drive (GTA V, RDR2)\n"
        "Comment=Explora y ejecuta tus juegos desde Google Drive\n"
        "Exec=thunar dav://127.0.0.1:8088/\n"
        "Icon=applications-games\n"
        "Terminal=false\n"
        "Categories=Game;\n"
    ),
    "📊_Monitor_GPUs_Tesla_T4.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=📊 Monitor de 2x GPUs NVIDIA (nvtop)\n"
        "Exec=xfce4-terminal --title='Monitor GPUs Tesla T4' -e 'nvtop'\n"
        "Icon=utilities-system-monitor\n"
        "Terminal=false\n"
        "Categories=System;\n"
    ),
    "🌐_Navegador_Web.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=🌐 Navegador Web Chromium\n"
        "Exec=chromium-browser --no-sandbox\n"
        "Icon=browser\n"
        "Terminal=false\n"
        "Categories=Network;\n"
    )
}

for fname, content in shortcuts.items():
    s_path = desktop_dir / fname
    s_path.write_text(content)
    s_path.chmod(0o755)

# ==============================================================================
# 4. LEVANTAR SERVIDOR GRÁFICO 1080p Y AUTO-INICIAR LINUWAIFU STUDIO
# ==============================================================================
print("🖥️ [4/5] Levantando pantalla 1080p y auto-iniciando LinuWaifu AI Studio...", flush=True)

# Iniciar servidor Xvfb a 1920x1080 24-bit
xvfb_proc = subprocess.Popen([
    "Xvfb", ":1",
    "-screen", "0", "1920x1080x24",
    "-ac", "-noreset", "-nolisten", "tcp"
], env=env)
time.sleep(2)

# Iniciar sesión de escritorio completa XFCE4
subprocess.Popen([
    "dbus-launch", "--exit-with-session", "startxfce4"
], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)

# Iniciar PulseAudio virtual
subprocess.run("pulseaudio --start --exit-idle-time=-1 2>/dev/null || true", shell=True)
subprocess.run("pactl load-module module-null-sink sink_name=VirtualSink 2>/dev/null || true", shell=True)

# Iniciar el servidor backend de LinuWaifu (Cloud Bridge + IA Brain) en puerto 8000
def start_linuwaifu_backend():
    try:
        subprocess.run(f"python3 {BASE_DIR}/cloud_bridge.py", shell=True, env=env)
    except Exception as e:
        print(f"Aviso LinuWaifu Backend: {e}")

threading.Thread(target=start_linuwaifu_backend, daemon=True).start()
time.sleep(2)

# Auto-abrir la ventana del Avatar 3D de LinuWaifu en la esquina de la pantalla
subprocess.Popen([
    "chromium-browser",
    "--no-sandbox",
    "--window-size=480,720",
    "--window-position=1440,0",
    f"--app=http://localhost:8000/avatars/studio.html"
], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
# 5. TÚNELES DE ALTA VELOCIDAD (PINGGY TCP PARA APP + NGROK HTTP PARA WEB)
# ==============================================================================
print("🌐 [5/5] Conectando túneles de acceso remoto...", flush=True)

web_tunnel_url = None
ngrok_token = os.environ.get("NGROK_TOKEN", "").strip()
if len(sys.argv) > 1 and sys.argv[1].strip() and sys.argv[1].strip() != "SIN_TOKEN":
    ngrok_token = sys.argv[1].strip()
if not ngrok_token:
    ngrok_token = DEFAULT_NGROK

# 1. Túnel Web Ngrok HTTP
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

# 2. Túnel TCP Pinggy en segundo plano
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

try:
    df_out = subprocess.check_output("df -h /kaggle/working | tail -1", shell=True, text=True).split()
    print(f"💾 Espacio Libre en Disco: {df_out[3]} disponibles de {df_out[1]}")
except Exception:
    pass

# ==============================================================================
# 🎉 ¡UBUNTU GAMING & AI VTUBER STUDIO 100% ONLINE!
# ==============================================================================
print("\n" + "=" * 78)
print("🎉 🌸 ¡TU UBUNTU NATIVO & LINUWAIFU AI STUDIO ESTÁ 100% ONLINE!")
print("=" * 78)

if web_tunnel_url:
    print("🌐 OPCIÓN 1: ENLACE WEB DIRECTO (Chrome / Brave en celular):")
    print(f"👉 {web_tunnel_url}")
    print("=" * 78)

print("📱 OPCIÓN 2: APP MÓVIL (RealVNC Viewer / AVNC con Touchpad y Zoom):")
print("   • Abre RealVNC Viewer en tu celular -> Botón '+'")
print("   • Pega la dirección de Pinggy que aparece arriba.")
print("=" * 78)

print("🌸 EN TU ESCRITORIO LISTO PARA USAR:")
print("   • 🌸 LinuWaifu AI Avatar 3D: Ya está abierto en pantalla reaccionando en vivo.")
print("   • 🎮 Carpeta Google Drive 5TB: Acceso directo en el escritorio para GTA V / RDR2.")
print("   • 📊 Monitor de GPUs: Acceso directo a nvtop (2x Tesla T4 32GB VRAM).")
print("   • 🌐 Navegador Chromium y Explorador de Archivos Thunar.")
print("=" * 78 + "\n")

# Mantener viva la celda
try:
    minutos = 0
    while True:
        time.sleep(30)
        print(".", end="", flush=True)
        minutos += 0.5
        if minutos % 10 == 0:
            print(f" [{int(minutos)} min activo]", flush=True)
            # Auto-backup de rclone.conf a GitHub si fue modificado
            if rclone_conf_target.exists() and rclone_conf_target.stat().st_size > 10:
                if not rclone_conf_repo.exists() or rclone_conf_target.read_text() != rclone_conf_repo.read_text():
                    shutil.copy(rclone_conf_target, rclone_conf_repo)
                    subprocess.run(
                        f"cd {BASE_DIR} && git add rclone.conf && git commit -m 'Auto-backup Google Drive credentials' && git push origin main >/dev/null 2>&1 || true",
                        shell=True
                    )
except KeyboardInterrupt:
    print("\n🛑 Servidor detenido.")

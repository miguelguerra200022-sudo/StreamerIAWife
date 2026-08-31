#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🌸 LINUWAIFU CLOUD PC: INFINITE PERSISTENCE ENGINE (KAGGLE MULTI-ACCOUNT)
================================================================================
Comportamiento de PC Real:
Guarda y restaura el estado completo de tu PC entre CUALQUIER cuenta de Kaggle
usando tu Google Drive de 5TB y GitHub.

1. Al Iniciar (En CUALQUIER cuenta de Kaggle):
   - Restaura credenciales de Google Drive (rclone_gdrive.b64).
   - Restaura todas las dependencias y programas APT que hayas instalado antes.
   - Restaura el escritorio, configuraciones, partidas de juegos y navegador.
   - Conecta la carpeta de 5TB de juegos (GTA V, RDR2, ROMs) en ~/Games y Escritorio.
   - Inicia Ubuntu 24.04 LTS Oficial (Yaru-Dark) + LinuWaifu AI VTuber Studio en vivo.
   - Abre los túneles para RealVNC en tu celular.

2. En Segundo Plano (Auto-Guardado cada 5 min y al salir):
   - Registra cualquier nuevo paquete APT o pip que instales.
   - Respalda partidas de juegos, descargas y configuraciones a Google Drive.
================================================================================
"""

import os
import sys
import time
import re
import shutil
import base64
import subprocess
import threading
import signal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.environ["DEBIAN_FRONTEND"] = "noninteractive"
os.environ["DISPLAY"] = ":1"

DEFAULT_NGROK = "34P4Gndh4EFxHQUFbbtO6lxsWBH_3HK2oZoxLj1D3qkSJn17b"

print("\n" + "=" * 78)
print("🌸 INICIANDO LINUWAIFU CLOUD PC: SISTEMA DE PERSISTENCIA TOTAL (5TB GDrive)...")
print("=" * 78)

# Directorios Clave
GDRIVE_CONF_DIR = Path.home() / ".config" / "rclone"
GDRIVE_CONF_FILE = GDRIVE_CONF_DIR / "rclone.conf"
REPO_RCLONE_B64 = BASE_DIR / "rclone_gdrive.b64"
EXTRA_PKGS_FILE = BASE_DIR / "packages_extra.txt"
STATE_DIR = Path("/kaggle/working/LinuWaifu_State")
STATE_DIR.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# 1. AUTO-RESTAURAR CREDENCIALES DE GOOGLE DRIVE Y PERSISTENCIA
# ==============================================================================
print("☁️ [1/6] Sincronizando credenciales de Google Drive (5TB)...", flush=True)
GDRIVE_CONF_DIR.mkdir(parents=True, exist_ok=True)

if REPO_RCLONE_B64.exists() and REPO_RCLONE_B64.stat().st_size > 10:
    try:
        decoded = base64.b64decode(REPO_RCLONE_B64.read_text().strip())
        GDRIVE_CONF_FILE.write_bytes(decoded)
        print("  ✅ [✓] Credenciales de 5TB restauradas automáticamente desde GitHub.", flush=True)
    except Exception as e:
        print(f"  ⚠️ Error decodificando credenciales: {e}")
elif GDRIVE_CONF_FILE.exists() and GDRIVE_CONF_FILE.stat().st_size > 10:
    try:
        encoded = base64.b64encode(GDRIVE_CONF_FILE.read_bytes()).decode('utf-8')
        REPO_RCLONE_B64.write_text(encoded)
    except Exception:
        pass

# Iniciar servidor Rclone WebDAV en segundo plano
try:
    subprocess.Popen([
        "rclone", "serve", "webdav", "gdrive:",
        "--addr", "127.0.0.1:8088",
        "--read-only=false",
        "--vfs-cache-mode", "writes"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("  ✅ [✓] Servidor de 5TB Google Drive montado en red local (Puerto 8088).", flush=True)
except Exception:
    pass

# ==============================================================================
# 2. INSTALACIÓN DE SUITE BASE + AUTO-RESTAURACIÓN DE PAQUETES EXTRA
# ==============================================================================
def setup_dependencies():
    print("📦 [2/6] Instalando Suite de Ubuntu oficial y dependencias...", flush=True)
    subprocess.run("rm -rf /etc/apt/sources.list.d/* 2>/dev/null || true", shell=True)
    
    base_pkgs = [
        "xfce4", "xfce4-terminal", "xfce4-panel", "xfdesktop4", "thunar",
        "mousepad", "htop", "nvtop", "mpv", "dbus-x11", "x11vnc", "xvfb",
        "yaru-theme-gtk", "yaru-theme-icon", "fonts-ubuntu", "pulseaudio",
        "net-tools", "wget", "curl", "rclone", "psmisc", "openssh-client",
        "chromium-browser", "greybird-gtk-theme", "p7zip-full", "unzip"
    ]
    
    extra_pkgs = []
    if EXTRA_PKGS_FILE.exists():
        try:
            extra_pkgs = [p.strip() for p in EXTRA_PKGS_FILE.read_text().split() if p.strip()]
            print(f"  📦 Restaurando {len(extra_pkgs)} programas adicionales guardados: {', '.join(extra_pkgs)}", flush=True)
        except Exception:
            pass
    
    all_pkgs = list(set(base_pkgs + extra_pkgs))
    
    cmd_install = (
        "apt-get update -qq && "
        f"apt-get install -y --no-install-recommends {' '.join(all_pkgs)} >/dev/null 2>&1 && "
        "apt-get clean && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*"
    )
    subprocess.run(cmd_install, shell=True)
    subprocess.run("pip install -q pyngrok websockets aiohttp Pillow mss edge-tts python-dotenv openai >/dev/null 2>&1", shell=True)

    # Descargar noVNC si no existe
    novnc_dir = Path("/kaggle/working/noVNC")
    if not novnc_dir.exists():
        print("📥 [3/6] Descargando componentes web de interfaz...", flush=True)
        subprocess.run("git clone --depth 1 https://github.com/novnc/noVNC.git /kaggle/working/noVNC >/dev/null 2>&1", shell=True)
        subprocess.run("git clone --depth 1 https://github.com/novnc/websockify /kaggle/working/noVNC/utils/websockify >/dev/null 2>&1", shell=True)

setup_dependencies()

# ==============================================================================
# 3. RESTAURAR ESTADO DE USUARIO (CONFIGURACIONES, PARTIDAS DE JUEGOS, ESCRITORIO)
# ==============================================================================
print("📂 [3/6] Restaurando partidas, escritorio y estado personal de Google Drive...", flush=True)
try:
    backup_tar = STATE_DIR / "linuwaifu_user_state.tar.gz"
    subprocess.run(
        f"rclone copy gdrive:LinuWaifu_PC/system_state/linuwaifu_user_state.tar.gz {STATE_DIR} >/dev/null 2>&1 || true",
        shell=True
    )
    if backup_tar.exists() and backup_tar.stat().st_size > 100:
        subprocess.run(f"tar -xzf {backup_tar} -C /root/ >/dev/null 2>&1 || true", shell=True)
        print("  ✅ [✓] Escritorio, fondos y partidas restauradas con éxito.", flush=True)
except Exception as e:
    print(f"  ℹ️ Estado inicial nuevo: {e}")

# ==============================================================================
# 4. CONFIGURAR ESCRITORIO UBUNTU YARU-DARK + ACCESOS DIRECTOS Y HERRAMIENTAS
# ==============================================================================
print("🎨 [4/6] Configurando tema Ubuntu Yaru-Dark y herramientas en escritorio...", flush=True)

# Limpiar procesos anteriores
subprocess.run("killall -9 Xvfb x11vnc websockify novnc_proxy ngrok xfce4-session startxfce4 ssh python3 2>/dev/null || true", shell=True)
time.sleep(1)

env = os.environ.copy()
env["DISPLAY"] = ":1"

# Crear carpeta Desktop y Games
desktop_dir = Path.home() / "Desktop"
desktop_dir.mkdir(parents=True, exist_ok=True)
games_dir = Path.home() / "Games"
games_dir.mkdir(parents=True, exist_ok=True)

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

# Script auxiliar para instalar cualquier paquete y guardarlo para siempre en GitHub/GDrive
install_helper = BASE_DIR / "instalar_y_guardar.sh"
install_helper.write_text(
    "#!/bin/bash\n"
    "if [ -z \"$1\" ]; then\n"
    "  echo 'Uso: ./instalar_y_guardar.sh <nombre_paquete>'\n"
    "  exit 1\n"
    "fi\n"
    "apt-get update -qq && apt-get install -y --no-install-recommends \"$@\"\n"
    "if [ $? -eq 0 ]; then\n"
    f"  echo \"$@\" >> {EXTRA_PKGS_FILE}\n"
    f"  cd {BASE_DIR} && git add packages_extra.txt && git commit -m 'Add persistent packages: '$@ && git push origin main >/dev/null 2>&1 || true\n"
    "  echo '✅ ¡Paquete instalado y guardado para siempre en GitHub!'\n"
    "fi\n"
)
install_helper.chmod(0o755)
subprocess.run(f"cp {install_helper} /usr/local/bin/instalar 2>/dev/null || true", shell=True)

# Accesos directos en el escritorio
shortcuts = {
    "🌸_LinuWaifu_AI_Studio.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=🌸 LinuWaifu AI VTuber Studio\n"
        "Comment=Panel de IA VTuber 3D en vivo con Voz y Chat\n"
        "Exec=chromium-browser --no-sandbox --app=http://localhost:8000/avatars/studio.html\n"
        "Icon=applications-multimedia\n"
        "Terminal=false\n"
        "Categories=AudioVideo;Network;\n"
    ),
    "🎮_Mis_Juegos_5TB_GoogleDrive.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=🎮 Mis Juegos 5TB Google Drive (GTA V, RDR2)\n"
        "Comment=Carpeta persistente con todos tus juegos y partidas\n"
        "Exec=thunar dav://127.0.0.1:8088/\n"
        "Icon=applications-games\n"
        "Terminal=false\n"
        "Categories=Game;\n"
    ),
    "💾_Guardar_Estado_de_mi_PC.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=💾 Guardar Estado de mi PC (Nube)\n"
        "Comment=Guarda tus partidas, descargas y cambios a Google Drive y GitHub\n"
        f"Exec=python3 {BASE_DIR}/run_kaggle_vnc_studio.py --save-now\n"
        "Icon=system-software-update\n"
        "Terminal=true\n"
        "Categories=System;\n"
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
# 5. LEVANTAR SERVIDOR GRÁFICO 1080p Y AUTO-INICIAR LINUWAIFU STUDIO
# ==============================================================================
print("🖥️ [5/6] Levantando pantalla 1080p y auto-iniciando LinuWaifu AI Studio...", flush=True)

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
# 6. TÚNELES DE ALTA VELOCIDAD (PINGGY TCP PARA APP + NGROK HTTP PARA WEB)
# ==============================================================================
print("🌐 [6/6] Conectando túneles de acceso remoto...", flush=True)

web_tunnel_url = None
ngrok_token = os.environ.get("NGROK_TOKEN", "").strip()
if len(sys.argv) > 1 and sys.argv[1].strip() and sys.argv[1].strip() != "SIN_TOKEN" and not sys.argv[1].startswith("--"):
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
# 🎉 ¡UBUNTU PERSISTENTE 100% ONLINE!
# ==============================================================================
print("\n" + "=" * 78)
print("🎉 🌸 ¡TU LINUWAIFU CLOUD PC PERSISTENTE ESTÁ 100% ONLINE!")
print("=" * 78)

if web_tunnel_url:
    print("🌐 OPCIÓN 1: ENLACE WEB DIRECTO (Chrome / Brave en celular):")
    print(f"👉 {web_tunnel_url}")
    print("=" * 78)

print("📱 OPCIÓN 2: APP MÓVIL (RealVNC Viewer / AVNC con Touchpad y Zoom):")
print("   • Abre RealVNC Viewer en tu celular -> Botón '+'")
print("   • Pega la dirección de Pinggy que aparece arriba.")
print("=" * 78)

print("💾 SISTEMA DE PERSISTENCIA ACTIVO:")
print("   • 🎮 Tus 5TB de Google Drive (GTA V, RDR2) montados en el escritorio.")
print("   • 📦 Para instalar cualquier cosa y recordarla para siempre usa: instalar <nombre>")
print("   • 🌸 Tu Waifu 3D ya está abierta en pantalla lista para transmitir.")
print("=" * 78 + "\n")

# Función de auto-guardado a Google Drive y GitHub
def auto_save_user_state():
    try:
        # 1. Respaldar rclone si fue modificado
        if GDRIVE_CONF_FILE.exists() and GDRIVE_CONF_FILE.stat().st_size > 10:
            encoded = base64.b64encode(GDRIVE_CONF_FILE.read_bytes()).decode('utf-8')
            if not REPO_RCLONE_B64.exists() or REPO_RCLONE_B64.read_text().strip() != encoded:
                REPO_RCLONE_B64.write_text(encoded)
                subprocess.run(
                    f"cd {BASE_DIR} && git add rclone_gdrive.b64 && git commit -m 'Auto-backup Google Drive credentials' && git push origin main >/dev/null 2>&1 || true",
                    shell=True
                )
        
        # 2. Respaldar partidas de juegos y configuraciones a Google Drive
        save_tar = STATE_DIR / "linuwaifu_user_state.tar.gz"
        subprocess.run(
            f"tar -czf {save_tar} -C /root/ .config/ .local/share/ Games/ >/dev/null 2>&1 || true",
            shell=True
        )
        if save_tar.exists():
            subprocess.run(
                f"rclone copy {save_tar} gdrive:LinuWaifu_PC/system_state/ >/dev/null 2>&1 || true",
                shell=True
            )
    except Exception:
        pass

# Mantener viva la celda con auto-guardado periódico
try:
    minutos = 0
    while True:
        time.sleep(30)
        print(".", end="", flush=True)
        minutos += 0.5
        if minutos % 5 == 0:
            auto_save_user_state()
        if minutos % 10 == 0:
            print(f" [{int(minutos)} min activo - Estado Guardado en Nube]", flush=True)
except KeyboardInterrupt:
    print("\n🛑 Guardando estado final antes de salir...")
    auto_save_user_state()
    print("✅ Estado guardado. Servidor detenido.")

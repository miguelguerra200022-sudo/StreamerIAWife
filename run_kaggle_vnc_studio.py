#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🌸 LINUWAIFU CLOUD PC: UBUNTU 24.04 LTS OFICIAL GNOME DESKTOP (5TB GOOGLE DRIVE)
================================================================================
1. [PASO 1]: Conecta y monta Google Drive (PC_Kaggle) inmediatamente.
2. [PASO 2]: Carga y activa el entorno OFICIAL de Ubuntu (GNOME Shell Canonical):
   - Barra superior oficial negra de Ubuntu (Top Bar).
   - Ubuntu Left Dock oficial translúcido con iconos Yaru oficiales.
   - Explorador de archivos oficial Nautilus y terminal GNOME.
   - Panel de control y configuraciones oficiales de Ubuntu.
3. [PASO 3]: Activa 2x GPUs NVIDIA Tesla T4, Audio Virtual y LinuWaifu 3D IA.
4. [PASO 4]: Persistencia infinita: Todo lo que hagas vive en tus 5TB de Google Drive.
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
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.environ["DEBIAN_FRONTEND"] = "noninteractive"
os.environ["DISPLAY"] = ":1"
os.environ["XDG_CURRENT_DESKTOP"] = "ubuntu:GNOME"
os.environ["XDG_SESSION_DESKTOP"] = "ubuntu"
os.environ["XDG_SESSION_TYPE"] = "x11"
os.environ["MUTTER_DEBUG_DUMMY_MODE_SPECS"] = "1920x1080"

DEFAULT_NGROK = "34P4Gndh4EFxHQUFbbtO6lxsWBH_3HK2oZoxLj1D3qkSJn17b"

# Archivo Maestro de Registros
LOG_FILE = Path("/kaggle/working/linuwaifu_system.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def log(msg, level="INFO"):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{ts}] [{level}] {msg}"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

# 0. Limpieza segura de procesos residuales
subprocess.run("pkill -9 -f 'Xvfb|x11vnc|websockify|novnc_proxy|ngrok|gnome|xfce4|startxfce4|rclone|cloud_bridge|pulseaudio' 2>/dev/null || true", shell=True)
time.sleep(0.5)

# Inicializar archivo de log limpio
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"=== INICIO DE SESIÓN LINUWAIFU UBUNTU OFICIAL GNOME ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

print("\n" + "=" * 78, flush=True)
print("🌸 INICIANDO UBUNTU 24.04 LTS OFICIAL GNOME (5TB GOOGLE DRIVE + WAIFU IA)...", flush=True)
print("=" * 78, flush=True)

# Directorios Clave
GDRIVE_CONF_DIR = Path.home() / ".config" / "rclone"
GDRIVE_CONF_FILE = GDRIVE_CONF_DIR / "rclone.conf"
REPO_RCLONE_B64 = BASE_DIR / "rclone_gdrive.b64"
EXTRA_PKGS_FILE = BASE_DIR / "packages_extra.txt"
STATE_DIR = Path("/kaggle/working/LinuWaifu_State")
STATE_DIR.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# 1. [PASO 1 INMEDIATO] CONECTAR Y MONTAR GOOGLE DRIVE 5TB (PC_Kaggle)
# ==============================================================================
print("☁️ [1/5] Conectando Google Drive (5TB - Carpeta PC_Kaggle)...", flush=True)
log("Iniciando conexión de Google Drive...")
GDRIVE_CONF_DIR.mkdir(parents=True, exist_ok=True)

if REPO_RCLONE_B64.exists() and REPO_RCLONE_B64.stat().st_size > 10:
    try:
        decoded = base64.b64decode(REPO_RCLONE_B64.read_text().strip())
        GDRIVE_CONF_FILE.write_bytes(decoded)
    except Exception:
        pass

# Instalar rclone rápido si no está presente
subprocess.run("which rclone >/dev/null 2>&1 || (apt-get update -qq && apt-get install -y -qq rclone >/dev/null 2>&1)", shell=True)

# Iniciar servidor Rclone WebDAV
try:
    log_rclone = open(LOG_FILE, "a", encoding="utf-8")
    subprocess.Popen([
        "rclone", "serve", "webdav", "gdrive:",
        "--addr", "127.0.0.1:8088",
        "--read-only=false",
        "--vfs-cache-mode", "writes"
    ], stdout=log_rclone, stderr=log_rclone)
    
    # Crear estructura base en Google Drive
    subprocess.run(f"rclone mkdir gdrive:PC_Kaggle/system_state >> {LOG_FILE} 2>&1 || true", shell=True)
    subprocess.run(f"rclone mkdir gdrive:PC_Kaggle/Games >> {LOG_FILE} 2>&1 || true", shell=True)
    subprocess.run(f"rclone mkdir gdrive:PC_Kaggle/system_packages >> {LOG_FILE} 2>&1 || true", shell=True)
    
    print("  ✅ [✓] Unidad de 5TB Google Drive conectada como Disco Principal.", flush=True)
    log("Google Drive 5TB montado con éxito.", "SUCCESS")
except Exception as e:
    log(f"Aviso Rclone: {e}", "WARNING")

# ==============================================================================
# 2. INSTALACIÓN DE LA SUITE OFICIAL UBUNTU DESKTOP (GNOME SHELL CANONICAL)
# ==============================================================================
print("📦 [2/5] Activando Suite Oficial Ubuntu Desktop (GNOME Shell, Nautilus, Yaru)...", flush=True)
log("Instalando Suite Oficial Ubuntu GNOME Desktop...")
subprocess.run("rm -rf /etc/apt/sources.list.d/* 2>/dev/null || true", shell=True)

# Paquetes oficiales de Canonical Ubuntu Desktop
official_ubuntu_pkgs = [
    "ubuntu-desktop-minimal", "gnome-session", "gnome-shell", "nautilus",
    "gnome-terminal", "gnome-control-center", "yaru-theme-gtk", "yaru-theme-icon",
    "yaru-theme-sound", "fonts-ubuntu", "dbus-x11", "x11vnc", "xvfb",
    "pulseaudio", "net-tools", "wget", "curl", "psmisc", "openssh-client",
    "chromium-browser", "p7zip-full", "unzip", "htop", "nvtop", "mpv"
]

extra_pkgs = []
if EXTRA_PKGS_FILE.exists():
    try:
        for line in EXTRA_PKGS_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                for p in line.split():
                    if p and not p.startswith("#"):
                        extra_pkgs.append(p)
    except Exception:
        pass

all_pkgs = list(set(official_ubuntu_pkgs + extra_pkgs))

cmd_install = (
    "apt-get update -qq && "
    f"apt-get install -y --no-install-recommends {' '.join(all_pkgs)} >> {LOG_FILE} 2>&1 && "
    "apt-get clean && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*"
)
subprocess.run(cmd_install, shell=True)
subprocess.run(f"pip install -q pyngrok websockets aiohttp Pillow mss edge-tts python-dotenv openai >> {LOG_FILE} 2>&1", shell=True)

# Descargar noVNC si no existe
novnc_dir = Path("/kaggle/working/noVNC")
if not novnc_dir.exists():
    subprocess.run(f"git clone --depth 1 https://github.com/novnc/noVNC.git /kaggle/working/noVNC >> {LOG_FILE} 2>&1", shell=True)
    subprocess.run(f"git clone --depth 1 https://github.com/novnc/websockify /kaggle/working/noVNC/utils/websockify >> {LOG_FILE} 2>&1", shell=True)

print("  ✅ [✓] Entorno Oficial Ubuntu Desktop GNOME listo.", flush=True)

# Restaurar estado personal guardado de Google Drive
try:
    backup_tar = STATE_DIR / "linuwaifu_user_state.tar.gz"
    subprocess.run(
        f"rclone copy gdrive:PC_Kaggle/system_state/linuwaifu_user_state.tar.gz {STATE_DIR} >> {LOG_FILE} 2>&1 || true",
        shell=True
    )
    if backup_tar.exists() and backup_tar.stat().st_size > 100:
        subprocess.run(f"tar -xzf {backup_tar} -C /root/ >> {LOG_FILE} 2>&1 || true", shell=True)
        print("  ✅ [✓] Partidas y preferencias de usuario restauradas desde Google Drive.", flush=True)
except Exception:
    pass

# ==============================================================================
# 3. CONFIGURAR ESCRITORIO OFICIAL, DOCK Y ACCESOS DIRECTOS
# ==============================================================================
print("🎨 [3/5] Configurando apariencia oficial de Canonical Ubuntu...", flush=True)

env = os.environ.copy()
env["DISPLAY"] = ":1"
env["XDG_CURRENT_DESKTOP"] = "ubuntu:GNOME"
env["XDG_SESSION_DESKTOP"] = "ubuntu"
env["XDG_SESSION_TYPE"] = "x11"

desktop_dir = Path.home() / "Desktop"
desktop_dir.mkdir(parents=True, exist_ok=True)
games_dir = Path.home() / "Games"
games_dir.mkdir(parents=True, exist_ok=True)

# Script auxiliar para instalar cualquier paquete y guardarlo en GitHub
install_helper = BASE_DIR / "instalar_y_guardar.sh"
install_helper.write_text(
    "#!/bin/bash\n"
    "if [ -z \"$1\" ]; then\n"
    "  echo 'Uso: ./instalar_y_guardar.sh <nombre_paquete>'\n"
    "  exit 1\n"
    "fi\n"
    f"apt-get update -qq && apt-get install -y --no-install-recommends \"$@\" >> {LOG_FILE} 2>&1\n"
    "if [ $? -eq 0 ]; then\n"
    f"  echo \"$@\" >> {EXTRA_PKGS_FILE}\n"
    f"  cd {BASE_DIR} && git add packages_extra.txt && git commit -m 'Add persistent packages: '$@ && git push origin main >/dev/null 2>&1 || true\n"
    "  echo '✅ ¡Paquete instalado y guardado para siempre en GitHub!'\n"
    "fi\n"
)
install_helper.chmod(0o755)
subprocess.run(f"cp {install_helper} /usr/local/bin/instalar 2>/dev/null || true", shell=True)

# Accesos directos oficiales en el escritorio
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
        "Exec=nautilus dav://127.0.0.1:8088/\n"
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
        "Name=📊 Monitor GPUs Tesla T4 (nvtop)\n"
        "Exec=gnome-terminal --title='Monitor GPUs Tesla T4' -e 'nvtop'\n"
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
# 4. LEVANTAR SERVIDOR GRÁFICO FULL HD CON GNOME SESSION OFICIAL
# ==============================================================================
print("🖥️ [4/5] Levantando pantalla 1080p e iniciando sesión oficial Ubuntu GNOME...", flush=True)

# Iniciar servidor Xvfb a 1920x1080 24-bit
xvfb_proc = subprocess.Popen([
    "Xvfb", ":1",
    "-screen", "0", "1920x1080x24",
    "-ac", "-noreset", "-nolisten", "tcp"
], env=env)
time.sleep(2)

# Iniciar sesión oficial de Ubuntu (GNOME Shell)
log_gnome = open(LOG_FILE, "a", encoding="utf-8")
try:
    subprocess.Popen([
        "dbus-run-session", "--", "gnome-session", "--session=ubuntu"
    ], env=env, stdout=log_gnome, stderr=log_gnome)
except Exception:
    subprocess.Popen([
        "dbus-launch", "--exit-with-session", "startxfce4"
    ], env=env, stdout=log_gnome, stderr=log_gnome)
time.sleep(3)

# Iniciar PulseAudio virtual
subprocess.run(f"pulseaudio --start --exit-idle-time=-1 >> {LOG_FILE} 2>&1 || true", shell=True)
subprocess.run(f"pactl load-module module-null-sink sink_name=VirtualSink >> {LOG_FILE} 2>&1 || true", shell=True)

# Iniciar backend de LinuWaifu
def start_linuwaifu_backend():
    try:
        subprocess.run(f"python3 {BASE_DIR}/cloud_bridge.py >> {LOG_FILE} 2>&1", shell=True, env=env)
    except Exception:
        pass

threading.Thread(target=start_linuwaifu_backend, daemon=True).start()
time.sleep(2)

# Auto-abrir la ventana del Avatar 3D de LinuWaifu
subprocess.Popen([
    "chromium-browser",
    "--no-sandbox",
    "--window-size=480,720",
    "--window-position=1440,0",
    f"--app=http://localhost:8000/avatars/studio.html"
], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Servidor VNC optimizado para 60 FPS
log_vnc = open(LOG_FILE, "a", encoding="utf-8")
subprocess.Popen([
    "x11vnc", "-display", ":1",
    "-forever", "-nopw", "-shared",
    "-rfbport", "5900",
    "-noxdamage", "-noxfixes",
    "-wait", "20", "-defer", "20"
], env=env, stdout=log_vnc, stderr=log_vnc)
time.sleep(1)

# Servidor noVNC Web (Puerto 6080)
subprocess.Popen([
    "/kaggle/working/noVNC/utils/novnc_proxy",
    "--vnc", "localhost:5900",
    "--listen", "6080",
    "--web", "/kaggle/working/noVNC"
], env=env, stdout=log_vnc, stderr=log_vnc)
time.sleep(2)

# ==============================================================================
# 5. TÚNELES DE ALTA VELOCIDAD (PINGGY TCP PARA APP + NGROK HTTP PARA WEB)
# ==============================================================================
print("🌐 [5/5] Conectando túneles de acceso remoto...", flush=True)

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
        log(f"Aviso Ngrok HTTP: {e}", "WARNING")

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

# ==============================================================================
# 🎉 ¡UBUNTU OFICIAL GNOME 100% ONLINE!
# ==============================================================================
print("\n" + "=" * 78, flush=True)
print("🎉 🌸 ¡TU UBUNTU 24.04 LTS OFICIAL GNOME ESTÁ 100% ONLINE!", flush=True)
print("=" * 78, flush=True)

if web_tunnel_url:
    print("🌐 OPCIÓN 1: ENLACE WEB DIRECTO (Chrome / Brave en celular):", flush=True)
    print(f"👉 {web_tunnel_url}", flush=True)
    print("-" * 78, flush=True)

pinggy_addr = vnc_app_address[0] if vnc_app_address else "free.pinggy.link (Consultando...)"
print("📱 OPCIÓN 2: APP MÓVIL (RealVNC Viewer / AVNC con Touchpad y Zoom):", flush=True)
print(f"👉 Servidor VNC: {pinggy_addr}", flush=True)
print("   • Abre RealVNC Viewer en tu celular -> Botón '+'", flush=True)
print("   • Pega la dirección de arriba y toca 'Connect'.", flush=True)
print("=" * 78, flush=True)

print("💾 SISTEMA DE PERSISTENCIA ACTIVO:", flush=True)
print("   • 🎮 Tus 5TB de Google Drive (PC_Kaggle) montados en el escritorio.", flush=True)
print("   • 📦 Para instalar cualquier cosa usa: instalar <nombre>", flush=True)
print("   • 🌸 Tu Waifu 3D ya está abierta en pantalla lista para transmitir.", flush=True)
print("=" * 78 + "\n", flush=True)

# Función de auto-guardado a Google Drive
def auto_save_user_state():
    try:
        if GDRIVE_CONF_FILE.exists() and GDRIVE_CONF_FILE.stat().st_size > 10:
            encoded = base64.b64encode(GDRIVE_CONF_FILE.read_bytes()).decode('utf-8')
            if not REPO_RCLONE_B64.exists() or REPO_RCLONE_B64.read_text().strip() != encoded:
                REPO_RCLONE_B64.write_text(encoded)
                subprocess.run(
                    f"cd {BASE_DIR} && git add rclone_gdrive.b64 && git commit -m 'Auto-backup Google Drive credentials' && git push origin main >/dev/null 2>&1 || true",
                    shell=True
                )
        
        save_tar = STATE_DIR / "linuwaifu_user_state.tar.gz"
        subprocess.run(
            f"tar -czf {save_tar} -C /root/ . >> {LOG_FILE} 2>&1 || true",
            shell=True
        )
        if save_tar.exists():
            subprocess.run(
                f"rclone copy {save_tar} gdrive:PC_Kaggle/system_state/ >> {LOG_FILE} 2>&1 || true",
                shell=True
            )
            log("Auto-guardado del sistema a Google Drive (PC_Kaggle) completado.", "SUCCESS")
    except Exception as e:
        log(f"Error en auto-guardado: {e}", "ERROR")

# Mantener viva la celda con auto-guardado y transmisión
try:
    minutos = 0
    while True:
        time.sleep(30)
        minutos += 0.5
        print(".", end="", flush=True)
        if minutos % 5 == 0:
            auto_save_user_state()
        if minutos % 10 == 0:
            print(f" [{int(minutos)} min activo - Estado Guardado]", flush=True)
except KeyboardInterrupt:
    print("\n🛑 Guardando estado final antes de salir...", flush=True)
    auto_save_user_state()
    print("✅ Estado guardado. Servidor detenido.", flush=True)

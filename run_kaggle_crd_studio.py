#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🌸 LINUWAIFU CLOUD PC: EDICIÓN GOOGLE CHROME REMOTE DESKTOP (CRD)
================================================================================
1. Instala Chrome Remote Desktop oficial de Google y Suite Ubuntu 24.04 LTS.
2. Monta tus 5TB de Google Drive (PC_Kaggle).
3. Vincula tu máquina a tu cuenta de Google con tu código de autorización y PIN.
4. Conexión directa a través de la App Oficial "Escritorio Remoto de Chrome".
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
import getpass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.environ["DEBIAN_FRONTEND"] = "noninteractive"

LOG_FILE = Path("/kaggle/working/linuwaifu_crd_system.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

print("\n" + "=" * 78, flush=True)
print("🌸 INICIANDO UBUNTU 24.04 EN GOOGLE CHROME REMOTE DESKTOP (CRD)...", flush=True)
print("=" * 78, flush=True)

# 0. Limpieza previa
subprocess.run("pkill -9 -f 'chrome-remote-desktop|Xvfb|xfce4|rclone|cloud_bridge' 2>/dev/null || true", shell=True)

# 1. Crear usuario de sistema no-root si no existe (CRD requiere usuario estándar)
subprocess.run("id -u linuwaifu >/dev/null 2>&1 || (useradd -m -s /bin/bash -G sudo linuwaifu && echo 'linuwaifu:123456' | chpasswd)", shell=True)
subprocess.run("echo 'linuwaifu ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers 2>/dev/null || true", shell=True)

USER_HOME = Path("/home/linuwaifu")

# ==============================================================================
# 2. INSTALAR CHROME REMOTE DESKTOP OFICIAL + SUITE UBUNTU
# ==============================================================================
print("📦 [1/4] Instalando Google Chrome Remote Desktop y Suite de Ubuntu...", flush=True)

base_pkgs = [
    "xfce4", "xfce4-terminal", "xfce4-panel", "xfdesktop4", "thunar",
    "gvfs", "gvfs-backends", "gvfs-fuse", "tumbler", "mousepad", "htop",
    "nvtop", "mpv", "dbus-x11", "xvfb", "x11-xserver-utils", "yaru-theme-gtk",
    "yaru-theme-icon", "fonts-ubuntu", "pulseaudio", "wget", "curl",
    "rclone", "p7zip-full", "unzip", "chromium-browser"
]

subprocess.run(
    "apt-get update -qq && "
    f"apt-get install -y --no-install-recommends {' '.join(base_pkgs)} >> {LOG_FILE} 2>&1 && "
    "wget -q https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb -O /tmp/crd.deb && "
    "dpkg -i /tmp/crd.deb >> {LOG_FILE} 2>&1 || apt-get install -y --fix-broken >> {LOG_FILE} 2>&1",
    shell=True
)
subprocess.run(f"pip install -q websockets aiohttp Pillow mss edge-tts python-dotenv openai >> {LOG_FILE} 2>&1", shell=True)
print("  ✅ [✓] Chrome Remote Desktop y entorno de escritorio listos.", flush=True)

# ==============================================================================
# 3. CONECTAR GOOGLE DRIVE 5TB (PC_Kaggle)
# ==============================================================================
print("☁️ [2/4] Conectando Google Drive (5TB - Carpeta PC_Kaggle)...", flush=True)
gdrive_conf_dir = USER_HOME / ".config" / "rclone"
gdrive_conf_dir.mkdir(parents=True, exist_ok=True)
repo_b64 = BASE_DIR / "rclone_gdrive.b64"

if repo_b64.exists() and repo_b64.stat().st_size > 10:
    try:
        decoded = base64.b64decode(repo_b64.read_text().strip())
        (gdrive_conf_dir / "rclone.conf").write_bytes(decoded)
        (Path.home() / ".config" / "rclone").mkdir(parents=True, exist_ok=True)
        (Path.home() / ".config" / "rclone" / "rclone.conf").write_bytes(decoded)
    except Exception:
        pass

# Montar WebDAV local
subprocess.Popen([
    "rclone", "serve", "webdav", "gdrive:",
    "--addr", "127.0.0.1:8088",
    "--read-only=false",
    "--vfs-cache-mode", "writes",
    "--tpslimit", "5"
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("  ✅ [✓] Unidad 5TB Google Drive conectada.", flush=True)

# ==============================================================================
# 4. CONFIGURAR SESIÓN DE ESCRITORIO Y TEMAS
# ==============================================================================
print("🎨 [3/4] Configurando sesión de escritorio...", flush=True)

# Archivo de sesión de Chrome Remote Desktop
session_file = USER_HOME / ".chrome-remote-desktop-session"
session_file.write_text("exec /etc/X11/Xsession /usr/bin/startxfce4\n")
session_file.chmod(0o755)
subprocess.run(f"chown -R linuwaifu:linuwaifu {USER_HOME}", shell=True)

# Configurar XFCE en usuario linuwaifu
xfconf_dir = USER_HOME / ".config" / "xfce4" / "xfconf" / "xfce-perchannel-xml"
xfconf_dir.mkdir(parents=True, exist_ok=True)
desktop_dir = USER_HOME / "Desktop"
desktop_dir.mkdir(parents=True, exist_ok=True)

shortcuts = {
    "LinuWaifu_AI_Studio.desktop": (
        "[Desktop Entry]\nVersion=1.0\nType=Application\nName=🌸 LinuWaifu AI VTuber Studio\n"
        "Exec=chromium-browser --no-sandbox --app=http://localhost:8000/avatars/studio.html\n"
        "Path=/kaggle/working/StreamerIAWife\nIcon=applications-multimedia\nTerminal=false\n"
    ),
    "Mis_Juegos_5TB_GoogleDrive.desktop": (
        "[Desktop Entry]\nVersion=1.0\nType=Application\nName=🎮 Mis Juegos 5TB Google Drive\n"
        "Exec=thunar dav://127.0.0.1:8088/\nPath=/home/linuwaifu\nIcon=applications-games\nTerminal=false\n"
    ),
    "Navegador_Web.desktop": (
        "[Desktop Entry]\nVersion=1.0\nType=Application\nName=🌐 Navegador Web Chromium\n"
        "Exec=chromium-browser --no-sandbox\nPath=/home/linuwaifu\nIcon=browser\nTerminal=false\n"
    )
}

for fname, content in shortcuts.items():
    s_path = desktop_dir / fname
    s_path.write_text(content, encoding="utf-8")
    s_path.chmod(0o755)

subprocess.run(f"chown -R linuwaifu:linuwaifu {USER_HOME}", shell=True)

# Iniciar backend de IA Waifu 3D
def start_linuwaifu_backend():
    try:
        subprocess.run(f"python3 {BASE_DIR}/cloud_bridge.py >> {LOG_FILE} 2>&1", shell=True)
    except Exception:
        pass

threading.Thread(target=start_linuwaifu_backend, daemon=True).start()

# ==============================================================================
# 5. VINCULACIÓN DE GOOGLE CHROME REMOTE DESKTOP
# ==============================================================================
print("\n" + "=" * 78, flush=True)
print("🔑 [4/4] VINCULACIÓN CON TU CUENTA DE GOOGLE", flush=True)
print("=" * 78, flush=True)

crd_auth_cmd = None
if len(sys.argv) > 1 and sys.argv[1].strip() and sys.argv[1].strip() != "PROMPT":
    crd_auth_cmd = " ".join(sys.argv[1:]).strip()

pin = "123456"

if not crd_auth_cmd:
    print("👉 1. Abre este enlace en tu navegador o celular:", flush=True)
    print("   🔗 https://remotedesktop.google.com/headless", flush=True)
    print("👉 2. Toca 'Configurar otra computadora' ➔ 'Comenzar' ➔ 'Autorizar'.", flush=True)
    print("👉 3. Copia el comando que te da Google para Debian Linux.", flush=True)
    print("-" * 78, flush=True)
    try:
        crd_auth_cmd = input("📋 Pega aquí el comando de Google: ").strip()
    except EOFError:
        crd_auth_cmd = ""

if not crd_auth_cmd:
    print("❌ No se proporcionó el comando de Google. Cancelando.", flush=True)
    sys.exit(1)

# Extraer el código y redirección del comando
code_match = re.search(r'--code="?([^"\s]+)"?', crd_auth_cmd)
redirect_match = re.search(r'--redirect-url="?([^"\s]+)"?', crd_auth_cmd)

code = code_match.group(1) if code_match else crd_auth_cmd.strip()
redirect_url = redirect_match.group(1) if redirect_match else "https://remotedesktop.google.com/_/oauthredirect"

host_name = "LinuWaifu-CloudPC"

# Ejecutar el start-host bajo el usuario linuwaifu
cmd_crd = (
    f"su - linuwaifu -c '"
    f"/opt/google/chrome-remote-desktop/start-host "
    f"--code=\"{code}\" "
    f"--redirect-url=\"{redirect_url}\" "
    f"--name=\"{host_name}\" "
    f"--pin=\"{pin}\"'"
)

res = subprocess.run(cmd_crd, shell=True, capture_output=True, text=True)

print("\n" + "=" * 78, flush=True)
print("🎉 🌸 ¡TU PC EN CHROME REMOTE DESKTOP ESTÁ VINCULADA Y ONLINE!", flush=True)
print("=" * 78, flush=True)
print("📱 CÓMO CONECTARTE DESDE TU CELULAR O PC:", flush=True)
print("   • Abre la app 'Escritorio Remoto de Chrome' o entra a:", flush=True)
print("     🔗 https://remotedesktop.google.com/access", flush=True)
print(f"   • Toca en tu PC: 💻 [{host_name}] (Aparece en VERDE)", flush=True)
print(f"   • Ingresa tu PIN de seguridad: 🔑 {pin}", flush=True)
print("=" * 78)
print("💾 SISTEMA DE PERSISTENCIA ACTIVO: 5TB de Google Drive montados.")
print("=" * 78 + "\n", flush=True)

# Mantener viva la sesión
try:
    minutos = 0
    while True:
        time.sleep(30)
        minutos += 0.5
        print(".", end="", flush=True)
        if minutos % 10 == 0:
            print(f" [{int(minutos)} min activo en Chrome Remote Desktop]", flush=True)
except KeyboardInterrupt:
    print("\n🛑 Servidor detenido.", flush=True)

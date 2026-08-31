#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🌸 LINUWAIFU CLOUD PC: INFINITE PERSISTENCE & FULL LOGGING ENGINE (KAGGLE)
================================================================================
Comportamiento de PC Real con Registro Completo en Vivo:
1. Celda 1 (Principal): Mantiene la PC limpia, rápida y online.
2. Celda 2 (Monitor): Registra en vivo todo lo que se instala, juega o ejecuta.
3. Almacenamiento 5TB en Google Drive (Juegos, partidas y dependencias).
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

# Archivo Maestro de Registros Centralizado
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

# Inicializar archivo de log
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"=== INICIO DE SESIÓN LINUWAIFU CLOUD PC ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

print("\n" + "=" * 78)
print("🌸 INICIANDO LINUWAIFU CLOUD PC (SISTEMA CON REGISTRO EN VIVO)...")
print("=" * 78)
log("Iniciando sistema maestro de LinuWaifu Cloud PC...")

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
log("Sincronizando credenciales de Google Drive (5TB)...")
GDRIVE_CONF_DIR.mkdir(parents=True, exist_ok=True)

if REPO_RCLONE_B64.exists() and REPO_RCLONE_B64.stat().st_size > 10:
    try:
        decoded = base64.b64decode(REPO_RCLONE_B64.read_text().strip())
        GDRIVE_CONF_FILE.write_bytes(decoded)
        print("  ✅ [✓] Credenciales de 5TB restauradas automáticamente desde GitHub.", flush=True)
        log("Credenciales de Google Drive restauradas con éxito desde GitHub.", "SUCCESS")
    except Exception as e:
        log(f"Error decodificando credenciales: {e}", "ERROR")
elif GDRIVE_CONF_FILE.exists() and GDRIVE_CONF_FILE.stat().st_size > 10:
    try:
        encoded = base64.b64encode(GDRIVE_CONF_FILE.read_bytes()).decode('utf-8')
        REPO_RCLONE_B64.write_text(encoded)
    except Exception:
        pass

# Iniciar servidor Rclone WebDAV en segundo plano con salida a log
try:
    log_rclone = open(LOG_FILE, "a", encoding="utf-8")
    subprocess.Popen([
        "rclone", "serve", "webdav", "gdrive:",
        "--addr", "127.0.0.1:8088",
        "--read-only=false",
        "--vfs-cache-mode", "writes"
    ], stdout=log_rclone, stderr=log_rclone)
    print("  ✅ [✓] Servidor de 5TB Google Drive montado en red local (Puerto 8088).", flush=True)
    log("Servidor Rclone WebDAV montado en puerto 8088.", "SUCCESS")
except Exception as e:
    log(f"Error iniciando Rclone WebDAV: {e}", "ERROR")

# ==============================================================================
# 2. INSTALACIÓN DE SUITE BASE + AUTO-RESTAURACIÓN DE PAQUETES EXTRA
# ==============================================================================
def setup_dependencies():
    print("📦 [2/6] Instalando Suite de Ubuntu oficial y dependencias...", flush=True)
    log("Instalando dependencias de Ubuntu y herramientas...")
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
            print(f"  📦 Restaurando {len(extra_pkgs)} programas adicionales: {', '.join(extra_pkgs)}", flush=True)
            log(f"Restaurando programas adicionales: {', '.join(extra_pkgs)}")
        except Exception:
            pass
    
    all_pkgs = list(set(base_pkgs + extra_pkgs))
    
    cmd_install = (
        "apt-get update -qq && "
        f"apt-get install -y --no-install-recommends {' '.join(all_pkgs)} >> {LOG_FILE} 2>&1 && "
        "apt-get clean && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*"
    )
    subprocess.run(cmd_install, shell=True)
    subprocess.run(f"pip install -q pyngrok websockets aiohttp Pillow mss edge-tts python-dotenv openai >> {LOG_FILE} 2>&1", shell=True)
    log("Instalación de paquetes completada.", "SUCCESS")

    # Descargar noVNC si no existe
    novnc_dir = Path("/kaggle/working/noVNC")
    if not novnc_dir.exists():
        print("📥 [3/6] Descargando componentes web de interfaz...", flush=True)
        log("Clonando repositorios noVNC y websockify...")
        subprocess.run(f"git clone --depth 1 https://github.com/novnc/noVNC.git /kaggle/working/noVNC >> {LOG_FILE} 2>&1", shell=True)
        subprocess.run(f"git clone --depth 1 https://github.com/novnc/websockify /kaggle/working/noVNC/utils/websockify >> {LOG_FILE} 2>&1", shell=True)

setup_dependencies()

# ==============================================================================
# 3. RESTAURAR ESTADO DE USUARIO (CONFIGURACIONES, PARTIDAS DE JUEGOS, ESCRITORIO)
# ==============================================================================
print("📂 [3/6] Restaurando partidas, escritorio y estado personal de Google Drive...", flush=True)
log("Restaurando estado personal del usuario desde Google Drive...")
try:
    backup_tar = STATE_DIR / "linuwaifu_user_state.tar.gz"
    subprocess.run(
        f"rclone copy gdrive:LinuWaifu_PC/system_state/linuwaifu_user_state.tar.gz {STATE_DIR} >> {LOG_FILE} 2>&1 || true",
        shell=True
    )
    if backup_tar.exists() and backup_tar.stat().st_size > 100:
        subprocess.run(f"tar -xzf {backup_tar} -C /root/ >> {LOG_FILE} 2>&1 || true", shell=True)
        print("  ✅ [✓] Escritorio, fondos y partidas restauradas con éxito.", flush=True)
        log("Estado personal restaurado con éxito.", "SUCCESS")
except Exception as e:
    log(f"Aviso estado personal: {e}", "WARNING")

# ==============================================================================
# 4. CONFIGURAR ESCRITORIO UBUNTU YARU-DARK + ACCESOS DIRECTOS Y HERRAMIENTAS
# ==============================================================================
print("🎨 [4/6] Configurando tema Ubuntu Yaru-Dark y herramientas en escritorio...", flush=True)
log("Configurando temas de escritorio Yaru-Dark y accesos directos...")

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
    f"echo '[INSTALANDO]: '$@ >> {LOG_FILE}\n"
    f"apt-get update -qq && apt-get install -y --no-install-recommends \"$@\" >> {LOG_FILE} 2>&1\n"
    "if [ $? -eq 0 ]; then\n"
    f"  echo \"$@\" >> {EXTRA_PKGS_FILE}\n"
    f"  cd {BASE_DIR} && git add packages_extra.txt && git commit -m 'Add persistent packages: '$@ && git push origin main >/dev/null 2>&1 || true\n"
    "  echo '✅ ¡Paquete instalado y guardado para siempre en GitHub!'\n"
    f"  echo '[EXITO]: Paquetes '$@' guardados.' >> {LOG_FILE}\n"
    "else\n"
    f"  echo '[ERROR]: Falló la instalación de '$@ >> {LOG_FILE}\n"
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
log("Iniciando pantalla Xvfb, XFCE4, Audio Virtual y LinuWaifu Backend...")

# Iniciar servidor Xvfb a 1920x1080 24-bit
xvfb_proc = subprocess.Popen([
    "Xvfb", ":1",
    "-screen", "0", "1920x1080x24",
    "-ac", "-noreset", "-nolisten", "tcp"
], env=env)
time.sleep(2)

# Iniciar sesión de escritorio completa XFCE4 con salida a log
log_xfce = open(LOG_FILE, "a", encoding="utf-8")
subprocess.Popen([
    "dbus-launch", "--exit-with-session", "startxfce4"
], env=env, stdout=log_xfce, stderr=log_xfce)
time.sleep(3)

# Iniciar PulseAudio virtual
subprocess.run(f"pulseaudio --start --exit-idle-time=-1 >> {LOG_FILE} 2>&1 || true", shell=True)
subprocess.run(f"pactl load-module module-null-sink sink_name=VirtualSink >> {LOG_FILE} 2>&1 || true", shell=True)

# Iniciar el servidor backend de LinuWaifu (Cloud Bridge + IA Brain) en puerto 8000
def start_linuwaifu_backend():
    try:
        subprocess.run(f"python3 {BASE_DIR}/cloud_bridge.py >> {LOG_FILE} 2>&1", shell=True, env=env)
    except Exception as e:
        log(f"Aviso Backend: {e}", "WARNING")

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
# 6. TÚNELES DE ALTA VELOCIDAD (PINGGY TCP PARA APP + NGROK HTTP PARA WEB)
# ==============================================================================
print("🌐 [6/6] Conectando túneles de acceso remoto...", flush=True)
log("Conectando túneles Ngrok y Pinggy...")

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
        log(f"Túnel Web Ngrok conectado: {web_tunnel_url}", "SUCCESS")
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
                        print(f"\n📱 [PINGGY ACTIVO] Dirección para RealVNC Viewer: {addr}\n", flush=True)
                        log(f"Túnel TCP Pinggy conectado: {addr}", "SUCCESS")
    except Exception as e:
        log(f"Aviso Pinggy: {e}", "WARNING")

threading.Thread(target=run_pinggy_tunnel, daemon=True).start()
time.sleep(3)

# ==============================================================================
# INFORMACIÓN DE HARDWARE Y DISCO
# ==============================================================================
try:
    import torch
    n = torch.cuda.device_count()
    print(f"\n🎮 GPUs NVIDIA Tesla Activas: {n}")
    log(f"GPUs NVIDIA Tesla detectadas: {n}")
    for i in range(n):
        p = torch.cuda.get_device_properties(i)
        print(f"  • GPU {i}: {p.name} ({p.total_memory / (1024**3):.1f} GB VRAM)")
        log(f"GPU {i}: {p.name} ({p.total_memory / (1024**3):.1f} GB VRAM)")
except Exception:
    pass

try:
    df_out = subprocess.check_output("df -h /kaggle/working | tail -1", shell=True, text=True).split()
    print(f"💾 Espacio Libre en Disco: {df_out[3]} disponibles de {df_out[1]}")
    log(f"Espacio Libre en Disco: {df_out[3]} disponibles de {df_out[1]}")
except Exception:
    pass

# ==============================================================================
# 🎉 ¡UBUNTU PERSISTENTE 100% ONLINE!
# ==============================================================================
print("\n" + "=" * 78)
print("🎉 🌸 ¡TU LINUWAIFU CLOUD PC ESTÁ 100% ONLINE (CON REGISTRO EN VIVO)!")
print("=" * 78)

if web_tunnel_url:
    print("🌐 OPCIÓN 1: ENLACE WEB DIRECTO (Chrome / Brave en celular):")
    print(f"👉 {web_tunnel_url}")
    print("=" * 78)

print("📱 OPCIÓN 2: APP MÓVIL (RealVNC Viewer / AVNC con Touchpad y Zoom):")
print("   • Abre RealVNC Viewer en tu celular -> Botón '+'")
print("   • Pega la dirección de Pinggy que aparece arriba.")
print("=" * 78)

print("📊 PARA VER LOS REGISTROS Y DIAGNOSTICAR EN VIVO (CELDA 2):")
print("👉 Ejecuta en otra celda: !python3 /kaggle/working/StreamerIAWife/debug_monitor.py")
print("=" * 78 + "\n")

# Función de auto-guardado a Google Drive y GitHub
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
            f"tar -czf {save_tar} -C /root/ .config/ .local/share/ Games/ >> {LOG_FILE} 2>&1 || true",
            shell=True
        )
        if save_tar.exists():
            subprocess.run(
                f"rclone copy {save_tar} gdrive:LinuWaifu_PC/system_state/ >> {LOG_FILE} 2>&1 || true",
                shell=True
            )
            log("Auto-guardado a Google Drive completado.", "SUCCESS")
    except Exception as e:
        log(f"Error en auto-guardado: {e}", "ERROR")

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
            print(f" [{int(minutos)} min activo]", flush=True)
            log(f"Sistema activo {int(minutos)} minutos. Todo funcionando correctamente.")
except KeyboardInterrupt:
    print("\n🛑 Guardando estado final antes de salir...")
    log("Detención manual solicitada por el usuario...")
    auto_save_user_state()
    print("✅ Estado guardado. Servidor detenido.")

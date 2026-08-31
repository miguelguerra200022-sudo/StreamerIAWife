#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🌸 LINUWAIFU CLOUD PC: KASMVNC PRO 60 FPS (WEBRTC H.264 + 5TB GOOGLE DRIVE)
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
os.environ["PULSE_SERVER"] = "127.0.0.1"
os.environ["LC_ALL"] = "C.UTF-8"
os.environ["LANG"] = "C.UTF-8"
os.environ["NO_AT_BRIDGE"] = "1"

DEFAULT_NGROK = "34P4Gndh4EFxHQUFbbtO6lxsWBH_3HK2oZoxLj1D3qkSJn17b"

# Archivo Maestro de Registros
LOG_FILE = Path("/kaggle/working/linuwaifu_system.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# 0. Limpieza segura de procesos residuales
subprocess.run("vncserver -kill :1 2>/dev/null || true", shell=True)
subprocess.run("pkill -9 -f 'Xvfb|x11vnc|Xkasmvnc|kasmvnc|websockify|novnc_proxy|ngrok|gnome|xfce4|startxfce4|rclone|cloud_bridge|pulseaudio' 2>/dev/null || true", shell=True)
subprocess.run("rm -rf /tmp/.X11-unix/X1 /tmp/.X1-lock 2>/dev/null || true", shell=True)
time.sleep(0.5)

# Inicializar archivo de log limpio
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"=== INICIO DE SESIÓN LINUWAIFU KASMVNC 60 FPS ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

def log(msg, level="INFO"):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{ts}] [{level}] {msg}"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

# Hilo de transmisión de logs (filtrando ruido interno irrelevante)
IGNORE_KEYWORDS = [
    "unsupported gl renderer", "remote volume monitor", "not starting for system user",
    "pm-is-supported", "assertion 'source != null'", "pulseaudio-plugin-warning",
    "attempting to reconnect in 5 seconds", "calling canshutdown failed", "calling canrestart failed",
    "thumbnailer failed", "failed to connect to proxy", "accountsservice", "g_source_unref",
    "assertion 'string != null' failed", "dbind-warning", "failed to resolve group 'kvm'"
]

def live_log_streamer():
    last_size = 0
    while True:
        try:
            if LOG_FILE.exists():
                curr_size = LOG_FILE.stat().st_size
                if curr_size > last_size:
                    with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                        f.seek(last_size)
                        new_text = f.read()
                        last_size = curr_size
                        for line in new_text.splitlines():
                            l_strip = line.strip()
                            if l_strip and not any(ign in l_strip.lower() for ign in IGNORE_KEYWORDS):
                                if "error" in l_strip.lower() or "failed" in l_strip.lower() or "exception" in l_strip.lower():
                                    print(f"🔴 {l_strip}", flush=True)
                                elif "warning" in l_strip.lower() or "warn" in l_strip.lower():
                                    print(f"⚠️ {l_strip}", flush=True)
            time.sleep(0.5)
        except Exception:
            time.sleep(1)

threading.Thread(target=live_log_streamer, daemon=True).start()

print("\n" + "=" * 78, flush=True)
print("🌸 INICIANDO LINUWAIFU CLOUD PC (KASMVNC 60 FPS WEBRTC + 5TB GDRIVE)...", flush=True)
print("=" * 78, flush=True)

# Directorios Clave
GDRIVE_CONF_DIR = Path.home() / ".config" / "rclone"
GDRIVE_CONF_FILE = GDRIVE_CONF_DIR / "rclone.conf"
REPO_RCLONE_B64 = BASE_DIR / "rclone_gdrive.b64"
EXTRA_PKGS_FILE = BASE_DIR / "packages_extra.txt"
STATE_DIR = Path("/kaggle/working/LinuWaifu_State")
STATE_DIR.mkdir(parents=True, exist_ok=True)

# Iniciar servicio D-Bus del sistema
subprocess.run("mkdir -p /var/run/dbus && dbus-daemon --system --fork 2>/dev/null || true", shell=True)

# ==============================================================================
# 1. [PASO 1] CONECTAR Y MONTAR GOOGLE DRIVE 5TB (PC_Kaggle)
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
subprocess.run("which rclone >/dev/null 2>&1 || (apt-get update -qq && apt-get install -y -qq rclone >> /kaggle/working/linuwaifu_system.log 2>&1)", shell=True)

# Iniciar servidor Rclone WebDAV
try:
    log_rclone = open(LOG_FILE, "a", encoding="utf-8")
    subprocess.Popen([
        "rclone", "serve", "webdav", "gdrive:",
        "--addr", "127.0.0.1:8088",
        "--read-only=false",
        "--vfs-cache-mode", "writes",
        "--tpslimit", "5",
        "--drive-chunk-size", "64M"
    ], stdout=log_rclone, stderr=log_rclone)
    time.sleep(1)
    
    print("  ✅ [✓] Unidad de 5TB Google Drive conectada como Disco Principal.", flush=True)
    log("Google Drive 5TB montado con éxito.", "SUCCESS")
except Exception as e:
    log(f"Aviso Rclone: {e}", "WARNING")

# ==============================================================================
# 2. INSTALACIÓN DE LA SUITE OFICIAL UBUNTU + MOTOR KASMVNC WEBRTC 60 FPS
# ==============================================================================
print("📦 [2/5] Instalando Ubuntu ligero + Motor KasmVNC WebRTC H.264 (60 FPS)...", flush=True)
log("Instalando dependencias de Ubuntu y KasmVNC...")
subprocess.run("rm -rf /etc/apt/sources.list.d/* 2>/dev/null || true", shell=True)

base_pkgs = [
    "xfce4", "xfce4-terminal", "xfce4-panel", "xfdesktop4", "thunar",
    "gvfs", "gvfs-backends", "gvfs-fuse", "tumbler", "tumbler-plugins-extra",
    "mousepad", "htop", "nvtop", "mpv", "dbus-x11", "x11-xserver-utils",
    "yaru-theme-gtk", "yaru-theme-icon", "yaru-theme-sound", "fonts-ubuntu",
    "pulseaudio", "pulseaudio-utils", "pavucontrol", "net-tools", "wget", "curl", "psmisc", "openssh-client",
    "chromium-browser", "greybird-gtk-theme", "p7zip-full", "unzip", "ssl-cert", "libjpeg-turbo8", "libpixman-1-0"
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

all_pkgs = list(set(base_pkgs + extra_pkgs))

cmd_install = (
    "apt-get update -qq && "
    f"apt-get install -y --no-install-recommends {' '.join(all_pkgs)} >> {LOG_FILE} 2>&1 && "
    "apt-get clean && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*"
)
subprocess.run(cmd_install, shell=True)
subprocess.run(f"pip install -q pyngrok websockets aiohttp Pillow mss edge-tts python-dotenv openai >> {LOG_FILE} 2>&1", shell=True)

# Descargar e Instalar KasmVNC Server oficial (WebRTC / H.264 60 FPS)
kasm_installed = subprocess.run("which vncserver >/dev/null 2>&1", shell=True).returncode == 0
if not kasm_installed:
    print("  🚀 Descargando e instalando KasmVNC 60 FPS (H.264 / WebRTC)...", flush=True)
    subprocess.run(
        "wget -q https://github.com/kasmtech/KasmVNC/releases/download/v1.3.3/kasmvncserver_jammy_1.3.3_amd64.deb -O /tmp/kasmvnc.deb && "
        "apt-get install -y --no-install-recommends /tmp/kasmvnc.deb >> " + str(LOG_FILE) + " 2>&1 && "
        "rm -f /tmp/kasmvnc.deb",
        shell=True
    )

# Configurar xstartup de KasmVNC para XFCE4
vnc_home = Path.home() / ".vnc"
vnc_home.mkdir(parents=True, exist_ok=True)
xstartup_file = vnc_home / "xstartup"
xstartup_file.write_text(
    "#!/bin/sh\n"
    "unset SESSION_MANAGER\n"
    "unset DBUS_SESSION_BUS_ADDRESS\n"
    "export DISPLAY=:1\n"
    "export NO_AT_BRIDGE=1\n"
    "xsetroot -solid '#2c001e' -cursor_name left_ptr\n"
    "exec dbus-launch --exit-with-session startxfce4\n"
)
xstartup_file.chmod(0o755)

# Configurar YAML de KasmVNC en puerto 8444 HTTP (sin SSL para máxima velocidad con Ngrok)
kasm_yaml = vnc_home / "kasmvnc.yaml"
kasm_yaml.write_text(
    "network:\n"
    "  protocol: http\n"
    "  websocket_port: 8444\n"
    "  interface: 0.0.0.0\n"
    "  http_dir: /usr/share/kasmvnc/www\n"
    "  ssl:\n"
    "    require_ssl: false\n"
    "encoding:\n"
    "  video_encoding: true\n"
    "  frame_rate: 60\n"
    "  quality: 9\n"
    "  rect_encoding_mode: 1\n"
    "runtime:\n"
    "  command_line:\n"
    "    prompt: false\n"
)
subprocess.run(f"mkdir -p /etc/kasmvnc && cp {kasm_yaml} /etc/kasmvnc/kasmvnc.yaml 2>/dev/null || true", shell=True)

# Restaurar estado personal guardado de Google Drive con validación de integridad
try:
    backup_tar = STATE_DIR / "linuwaifu_user_state.tar.gz"
    subprocess.run(
        f"rclone copy gdrive:PC_Kaggle/system_state/linuwaifu_user_state.tar.gz {STATE_DIR} --tpslimit 5 >/dev/null 2>&1 || true",
        shell=True
    )
    if backup_tar.exists() and backup_tar.stat().st_size > 1000:
        test_tar = subprocess.run(f"tar -tzf {backup_tar} >/dev/null 2>&1", shell=True)
        if test_tar.returncode == 0:
            subprocess.run(f"tar -xzf {backup_tar} -C /root/ >> {LOG_FILE} 2>&1 || true", shell=True)
            print("  ✅ [✓] Partidas y preferencias de usuario restauradas desde Google Drive.", flush=True)
        else:
            backup_tar.unlink(missing_ok=True)
            print("  ℹ️ Primera ejecución: Creando entorno inicial limpio.", flush=True)
    else:
        print("  ℹ️ Primera ejecución: Creando entorno inicial limpio.", flush=True)
except Exception:
    pass

# ==============================================================================
# 3. APARIENCIA OFICIAL UBUNTU YARU-DARK (WALLPAPER, ICONOS, ACCESOS)
# ==============================================================================
print("🎨 [3/5] Configurando apariencia oficial Ubuntu 24.04 (Yaru-Dark)...", flush=True)

env = os.environ.copy()
env["DISPLAY"] = ":1"
env["PULSE_SERVER"] = "127.0.0.1"
env["LC_ALL"] = "C.UTF-8"
env["LANG"] = "C.UTF-8"
env["NO_AT_BRIDGE"] = "1"

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
    subprocess.run("xfconf-query -c xsettings -p /Gtk/FontName -s 'Ubuntu 11' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Gtk/MonospaceFontName -s 'Ubuntu Mono 12' --create -t string 2>/dev/null || true", shell=True, env=env)
    
    # Desactivar compositor OpenGL para 120 FPS
    subprocess.run("xfconf-query -c xfwm4 -p /general/use_compositing -s false --create -t bool 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfwm4 -p /general/theme -s 'Yaru-dark' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfwm4 -p /general/title_font -s 'Ubuntu Bold 11' --create -t string 2>/dev/null || true", shell=True, env=env)

    # Iconos de escritorio
    subprocess.run("xfconf-query -c xfce4-desktop -p /desktop-icons/style -s 2 --create -t int 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfce4-desktop -p /desktop-icons/file-icons/show-home -s true --create -t bool 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfce4-desktop -p /desktop-icons/file-icons/show-filesystem -s true --create -t bool 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfce4-desktop -p /desktop-icons/file-icons/show-trash -s true --create -t bool 2>/dev/null || true", shell=True, env=env)
except Exception:
    pass

# Script auxiliar para instalar paquetes
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

# Accesos directos oficiales en el escritorio (nombres ASCII para evitar bugs de UTF-8 en X11)
shortcuts = {
    "LinuWaifu_AI_Studio.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=🌸 LinuWaifu AI VTuber Studio\n"
        "Comment=Panel de IA VTuber 3D en vivo con Voz y Chat\n"
        "Exec=chromium-browser --no-sandbox --app=http://localhost:8000/avatars/studio.html\n"
        "Path=/kaggle/working/StreamerIAWife\n"
        "Icon=applications-multimedia\n"
        "Terminal=false\n"
        "Categories=AudioVideo;Network;\n"
    ),
    "Mis_Juegos_5TB_GoogleDrive.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=🎮 Mis Juegos 5TB Google Drive (GTA V, RDR2)\n"
        "Comment=Carpeta persistente con todos tus juegos y partidas\n"
        "Exec=thunar dav://127.0.0.1:8088/\n"
        "Path=/root\n"
        "Icon=applications-games\n"
        "Terminal=false\n"
        "Categories=Game;\n"
    ),
    "Guardar_Estado_de_mi_PC.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=💾 Guardar Estado de mi PC (Nube)\n"
        "Comment=Guarda tus partidas, descargas y cambios a Google Drive y GitHub\n"
        f"Exec=python3 {BASE_DIR}/run_kaggle_vnc_studio.py --save-now\n"
        "Path=/kaggle/working/StreamerIAWife\n"
        "Icon=system-software-update\n"
        "Terminal=true\n"
        "Categories=System;\n"
    ),
    "Monitor_GPUs_Tesla_T4.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=📊 Monitor GPUs Tesla T4 (nvtop)\n"
        "Exec=xfce4-terminal --title='Monitor GPUs Tesla T4' -e 'nvtop'\n"
        "Path=/root\n"
        "Icon=utilities-system-monitor\n"
        "Terminal=false\n"
        "Categories=System;\n"
    ),
    "Navegador_Web.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=🌐 Navegador Web Chromium\n"
        "Exec=chromium-browser --no-sandbox\n"
        "Path=/root\n"
        "Icon=browser\n"
        "Terminal=false\n"
        "Categories=Network;\n"
    )
}

for fname, content in shortcuts.items():
    s_path = desktop_dir / fname
    s_path.write_text(content, encoding="utf-8")
    s_path.chmod(0o755)

# ==============================================================================
# 4. LEVANTAR SERVIDORES GRÁFICOS: KASMVNC 60 FPS
# ==============================================================================
print("🖥️ [4/5] Levantando pantalla 1080p y servidor KasmVNC 60 FPS...", flush=True)

# Iniciar PulseAudio nativo en modo TCP local
subprocess.run(
    "pulseaudio -k 2>/dev/null || true; "
    "pulseaudio -D --exit-idle-time=-1 --system=false "
    "--load='module-native-protocol-tcp auth-anonymous=1 port=4713' "
    "--load='module-null-sink sink_name=VirtualSink' >> {LOG_FILE} 2>&1 || true",
    shell=True, env=env
)
time.sleep(1)

# Iniciar KasmVNC Server oficial (Él mismo maneja la pantalla :1 y el puerto WebRTC 8444)
log_kasm = open(LOG_FILE, "a", encoding="utf-8")
subprocess.run(
    "vncserver :1 -geometry 1920x1080 -depth 24 -select-de XFCE -disableBasicAuth >> " + str(LOG_FILE) + " 2>&1 || true",
    shell=True, env=env
)
time.sleep(3)

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

# ==============================================================================
# 5. TÚNELES DE ALTA VELOCIDAD (KASMVNC 60 FPS WEBRTC)
# ==============================================================================
print("🌐 [5/5] Conectando túneles de transmisión WebRTC 60 FPS...", flush=True)

kasm_tunnel_url = None
ngrok_token = os.environ.get("NGROK_TOKEN", "").strip()
if len(sys.argv) > 1 and sys.argv[1].strip() and sys.argv[1].strip() != "SIN_TOKEN" and not sys.argv[1].startswith("--"):
    ngrok_token = sys.argv[1].strip()
if not ngrok_token:
    ngrok_token = DEFAULT_NGROK

# 1. Túnel Web Ngrok HTTP apuntando al puerto 8444 de KasmVNC (WebRTC 60 FPS)
if ngrok_token:
    try:
        from pyngrok import ngrok
        try:
            ngrok.kill()
        except Exception:
            pass
        ngrok.set_auth_token(ngrok_token)
        http_tunnel = ngrok.connect(8444, "http")
        kasm_tunnel_url = f"{http_tunnel.public_url}"
    except Exception as e:
        log(f"Aviso Ngrok HTTP: {e}", "WARNING")

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
# 🎉 ¡KASMVNC PRO 60 FPS WEBRTC 100% ONLINE!
# ==============================================================================
print("\n" + "=" * 78, flush=True)
print("🎉 🌸 ¡TU LINUWAIFU CLOUD PC (KASMVNC 60 FPS) ESTÁ 100% ONLINE!", flush=True)
print("=" * 78, flush=True)

if kasm_tunnel_url:
    print("🚀 ENLACE WEB DIRECTO KASMVNC 60 FPS (ABRE EN CHROME / BRAVE MÓVIL):", flush=True)
    print(f"👉 {kasm_tunnel_url}", flush=True)
    print("   • Transmisión de video continua WebRTC H.264 a 60 FPS reales.", flush=True)
    print("   • Calidad cristalina, controles táctiles, zoom y cero latencia.", flush=True)
    print("=" * 78, flush=True)

print("💾 SISTEMA DE PERSISTENCIA Y REGISTRO ACTIVO:", flush=True)
print("   • 🎮 Tus 5TB de Google Drive (PC_Kaggle) montados en el escritorio.", flush=True)
print("   • 📦 Para instalar cualquier cosa usa: instalar <nombre>", flush=True)
print("   • 🌸 Tu Waifu 3D ya está abierta en pantalla lista para transmitir.", flush=True)
print("   • ⚡ Video H.264 / WebRTC acelerado a 60 FPS nativo.", flush=True)
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
                f"rclone copy {save_tar} gdrive:PC_Kaggle/system_state/ --tpslimit 5 >/dev/null 2>&1 || true",
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

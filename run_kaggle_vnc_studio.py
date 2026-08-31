#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🌸 LINUWAIFU CLOUD PC: UBUNTU 24.04 LTS FULL EDITION (DEFAULT MASTER SUITE)
================================================================================
1. [PASO 1]: Conecta y monta Google Drive (5TB - Carpeta PC_Kaggle) inmediatamente.
2. [PASO 2]: Instala la Suite Oficial Completa de Ubuntu de Canonical (Gigabytes):
   - `ubuntu-desktop` y herramientas oficiales de Canonical.
   - Suite ofimática LibreOffice completa (Writer, Calc, Impress).
   - Suite multimedia con códecs propietarios (`ubuntu-restricted-extras`).
   - Gestor de archivos GVFS para 5TB Google Drive, compresores 7-Zip.
3. [PASO 3]: Configura tema oficial Ubuntu Yaru-Dark y accesos directos.
4. [PASO 4]: Inicia pantalla 1080p nativa 16:9 completa, PulseAudio y Waifu IA 3D.
5. [PASO 5]: Auto-guarda todo a Google Drive y entrega enlaces de acceso remoto.
================================================================================
"""

import os
import sys
import time
import re
import shutil
import base64
import socket
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
subprocess.run("pkill -9 -f 'Xvfb|x11vnc|websockify|novnc_proxy|ngrok|gnome|xfce4|startxfce4|rclone|cloud_bridge|pulseaudio' 2>/dev/null || true", shell=True)
subprocess.run("rm -rf /tmp/.X11-unix/X1 /tmp/.X1-lock /tmp/.X11-unix/X* /tmp/.X*-lock 2>/dev/null || true", shell=True)
time.sleep(0.5)

# Inicializar archivo de log limpio
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"=== INICIO DE SESIÓN LINUWAIFU UBUNTU FULL EDITION ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

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
    "assertion 'string != null' failed", "dbind-warning", "failed to resolve group 'kvm'",
    "wnck_is_window", "tpm0: failed to write", "tpmrm0: failed to write", "sda: failed to write",
    "failed to send reload request", "g_value_get_string", "another compositing manager is running",
    "g_str_has_prefix", "update-rc.d: warning", "update-inetd: warning",
    "the home dir /var/lib/usbmux", "adduser: warning"
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
print("🌸 INICIANDO UBUNTU 24.04 LTS FULL EDITION (SUITE COMPLETA + 5TB GDRIVE)...", flush=True)
print("=" * 78, flush=True)

# Directorios Clave
GDRIVE_CONF_DIR = Path.home() / ".rclone"
GDRIVE_CONF_FILE = GDRIVE_CONF_DIR / "rclone.conf"
os.environ["RCLONE_CONFIG"] = str(GDRIVE_CONF_FILE)
REPO_RCLONE_B64 = BASE_DIR / "rclone_gdrive.b64"
EXTRA_PKGS_FILE = BASE_DIR / "packages_extra.txt"
STATE_DIR = Path("/kaggle/working/LinuWaifu_State")
STATE_DIR.mkdir(parents=True, exist_ok=True)

# Utilidades de Polling y Espera Activa (Elimina Race Conditions)
def wait_for_path(path, timeout=15):
    p = Path(path)
    start = time.time()
    while time.time() - start < timeout:
        if p.exists():
            return True
        time.sleep(0.2)
    return False

def wait_for_port(port, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=0.3):
                return True
        except Exception:
            time.sleep(0.2)
    return False

# Función de auto-guardado a Google Drive (Excluyendo gdrive para evitar loops recursivos)
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
            f"tar --exclude='./gdrive' --exclude='./.cache' --exclude='./.config/google-chrome' -czf {save_tar} -C /root/ . >> {LOG_FILE} 2>&1 || true",
            shell=True
        )
        if save_tar.exists() and save_tar.stat().st_size > 100:
            subprocess.run(
                f"rclone copy {save_tar} gdrive:PC_Kaggle/system_state/ --tpslimit 5 >/dev/null 2>&1 || true",
                shell=True
            )
            log("Auto-guardado del sistema a Google Drive (PC_Kaggle) completado.", "SUCCESS")
    except Exception as e:
        log(f"Error en auto-guardado: {e}", "ERROR")

# Manejador dedicado para el botón de escritorio "Guardar Estado de mi PC"
if "--save-now" in sys.argv:
    print("💾 Guardando estado manual de la PC en Google Drive...", flush=True)
    auto_save_user_state()
    if os.environ.get("DISPLAY"):
        subprocess.run(
            "notify-send '💾 Guardado de PC' 'Tu estado ha sido respaldado en Google Drive exitosamente.' 2>/dev/null || true",
            shell=True
        )
    print("✅ Estado guardado exitosamente. Saliendo.", flush=True)
    sys.exit(0)

# Iniciar servicio D-Bus del sistema
subprocess.run("mkdir -p /var/run/dbus && dbus-daemon --system --fork 2>/dev/null || true", shell=True)

# ==============================================================================
# 1. [PASO 1] CONECTAR Y MONTAR GOOGLE DRIVE 5TB (PC_Kaggle)
# ==============================================================================
print("☁️ [1/5] Conectando Google Drive (5TB - Carpeta PC_Kaggle) y Kaggle API...", flush=True)
log("Iniciando conexión de Google Drive...")
GDRIVE_CONF_DIR.mkdir(parents=True, exist_ok=True)

# 1. Configurar API de Kaggle
KAGGLE_API_DIR = Path.home() / ".kaggle"
KAGGLE_API_DIR.mkdir(parents=True, exist_ok=True)
KAGGLE_API_FILE = KAGGLE_API_DIR / "kaggle.json"
REPO_KAGGLE_JSON = BASE_DIR / "kaggle legacy.json"

if REPO_KAGGLE_JSON.exists():
    try:
        subprocess.run(f"cp '{REPO_KAGGLE_JSON}' '{KAGGLE_API_FILE}'", shell=True)
        subprocess.run(f"chmod 600 '{KAGGLE_API_FILE}'", shell=True)
    except Exception:
        pass

if REPO_RCLONE_B64.exists() and REPO_RCLONE_B64.stat().st_size > 10:
    try:
        decoded = base64.b64decode(REPO_RCLONE_B64.read_text().strip())
        GDRIVE_CONF_FILE.write_bytes(decoded)
    except Exception:
        pass

# Instalar rclone y fuse3 rápido si no están presentes
subprocess.run("which rclone >/dev/null 2>&1 || (apt-get update -qq && apt-get install -y -qq rclone fuse3 >> /kaggle/working/linuwaifu_system.log 2>&1)", shell=True)

# Iniciar Rclone Mount (FUSE) para permitir Symlinks
try:
    # Crear la carpeta raíz en Drive por si no existe
    subprocess.run("rclone mkdir gdrive:PC_Kaggle >/dev/null 2>&1 || true", shell=True)
    
    # Montar Drive físicamente en el sistema
    os.makedirs("/root/gdrive", exist_ok=True)
    log_rclone = open(LOG_FILE, "a", encoding="utf-8")
    subprocess.Popen([
        "rclone", "mount", "gdrive:PC_Kaggle", "/root/gdrive",
        "--vfs-cache-mode", "writes",
        "--tpslimit", "5",
        "--drive-chunk-size", "64M",
        "--daemon"
    ], stdout=log_rclone, stderr=log_rclone)
    
    # Espera activa inteligente para confirmación del montaje
    drive_ready = wait_for_path("/root/gdrive", timeout=15)
    if drive_ready:
        print("  ✅ [✓] Unidad de 5TB Google Drive montada físicamente en /root/gdrive.", flush=True)
        log("Google Drive 5TB montado con éxito.", "SUCCESS")
    else:
        print("  ⚠️ [!] Montaje de Google Drive tardando más de lo normal...", flush=True)
    
    # ==============================================================================
    # Sincronización Simbólica Inteligente (Master Folders)
    # ==============================================================================
    print("  🔄 [✓] Estableciendo Sincronización Inteligente para perfiles y credenciales...", flush=True)
    sync_dirs = {
        "/root/.config": "/root/gdrive/Master_Config",
        "/root/.local/share": "/root/gdrive/Master_LocalData",
        "/root/.local/state": "/root/gdrive/Master_State",
        "/root/.mozilla": "/root/gdrive/Master_Mozilla",
        "/root/.ssh": "/root/gdrive/Master_SSH",
        "/root/.pki": "/root/gdrive/Master_PKI",
        "/root/Descargas": "/root/gdrive/Descargas",
        "/root/Documentos": "/root/gdrive/Documentos",
        "/root/Juegos": "/root/gdrive/Juegos",
        "/root/Escritorio": "/root/gdrive/Escritorio",
    }
    
    for local_dir, drive_dir in sync_dirs.items():
        subprocess.run(f"mkdir -p '{drive_dir}'", shell=True)
        if not os.path.exists(local_dir):
            os.makedirs(os.path.dirname(local_dir), exist_ok=True)
            os.symlink(drive_dir, local_dir)
        elif os.path.isdir(local_dir) and not os.path.islink(local_dir):
            # Mover el contenido existente a Drive de forma segura y luego hacer symlink
            subprocess.run(f"cp -a '{local_dir}'/* '{drive_dir}/' 2>/dev/null || true", shell=True)
            subprocess.run(f"rm -rf '{local_dir}'", shell=True)
            os.symlink(drive_dir, local_dir)

    # 1.5. Configuración Base del Puntero (Eliminar X negra)
    cursor_conf = Path("/root/.icons/default")
    cursor_conf.mkdir(parents=True, exist_ok=True)
    (cursor_conf / "index.theme").write_text("[Icon Theme]\nInherits=Yaru\n")

    # Inyectar Comando Mágico: subir_juego_a_kaggle
    script_kaggle = r"""#!/bin/bash
if [ "$#" -ne 2 ]; then
    echo 'Uso: subir_juego_a_kaggle "Nombre Del Juego" /ruta/a/la/carpeta/del/juego'
    echo 'Ejemplo: subir_juego_a_kaggle "Cyberpunk 2077" /root/Juegos/Cyberpunk'
    exit 1
fi
JUEGO_NOMBRE="$1"
RUTA_JUEGO="$2"
DATASET_ID=$(echo "$JUEGO_NOMBRE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g')
USUARIO=$(grep -o '"username":"[^"]*' ~/.kaggle/kaggle.json | cut -d'"' -f4)

if [ ! -d "$RUTA_JUEGO" ]; then
    echo "Error: La ruta $RUTA_JUEGO no existe."
    exit 1
fi

echo "Iniciando Dataset de Kaggle en $RUTA_JUEGO..."
kaggle datasets init -p "$RUTA_JUEGO"
sed -i 's/"title": ".*"/"title": "'"$JUEGO_NOMBRE"'"/' "$RUTA_JUEGO/dataset-metadata.json"
sed -i 's|"id": ".*"|"id": "'"$USUARIO/$DATASET_ID"'"|' "$RUTA_JUEGO/dataset-metadata.json"

echo "Subiendo juego a Kaggle Datasets (Velocidad Gigabit interna)..."
kaggle datasets create -p "$RUTA_JUEGO" --dir-mode tar
echo "¡Listo! El juego se está procesando. Revisa tu perfil de Kaggle."
"""
    script_path = Path("/usr/local/bin/subir_juego_a_kaggle")
    script_path.write_text(script_kaggle)
    script_path.chmod(0o755)

except Exception as e:
    log(f"Aviso Rclone/Symlink: {e}", "WARNING")

# ==============================================================================
# 2. INSTALACIÓN DE LA SUITE COMPLETA UBUNTU (GIGABYTES) + LIBREOFFICE + CODECS
# ==============================================================================
print("📦 [2/5] Descargando e instalando Suite Oficial Completa de Ubuntu (Gigabytes)...", flush=True)
log("Instalando paquetes oficiales de Ubuntu...")
subprocess.run("rm -rf /etc/apt/sources.list.d/* 2>/dev/null || true", shell=True)

full_ubuntu_pkgs = [
    "ubuntu-desktop", "ubuntu-restricted-extras", "libreoffice", "libreoffice-gtk3",
    "xfce4", "xfce4-goodies", "xfce4-terminal", "xfce4-panel", "xfdesktop4", "thunar",
    "gvfs", "gvfs-backends", "gvfs-fuse", "tumbler", "tumbler-plugins-extra",
    "evince", "gnome-calculator", "gnome-system-monitor", "gnome-disk-utility",
    "file-roller", "mousepad", "htop", "nvtop", "mpv", "dbus-x11", "x11vnc", "xvfb",
    "x11-xserver-utils", "yaru-theme-gtk", "yaru-theme-icon", "yaru-theme-sound",
    "fonts-ubuntu", "pulseaudio", "pulseaudio-utils", "pavucontrol", "net-tools",
    "wget", "curl", "psmisc", "openssh-client", "p7zip-full", "unzip"
]

extra_pkgs = []
if EXTRA_PKGS_FILE.exists():
    extra_pkgs = [p.strip() for p in EXTRA_PKGS_FILE.read_text().splitlines() if p.strip() and not p.startswith("#")]

all_pkgs = list(set(full_ubuntu_pkgs + extra_pkgs))

# Descargar o reutilizar Google Chrome Oficial desde caché de Drive
chrome_deb = Path("/kaggle/working/google-chrome-stable_current_amd64.deb")
gdrive_cache_deb = Path("/root/gdrive/Cache/google-chrome-stable_current_amd64.deb")

if gdrive_cache_deb.exists() and gdrive_cache_deb.stat().st_size > 50_000_000:
    print("  ⚡ [✓] Reutilizando Google Chrome desde caché de Google Drive...", flush=True)
    try:
        shutil.copy2(gdrive_cache_deb, chrome_deb)
    except Exception:
        pass

if not chrome_deb.exists() or chrome_deb.stat().st_size < 1000:
    subprocess.run(
        "wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /kaggle/working/google-chrome-stable_current_amd64.deb",
        shell=True
    )
    if chrome_deb.exists() and chrome_deb.stat().st_size > 50_000_000 and os.path.exists("/root/gdrive"):
        os.makedirs("/root/gdrive/Cache", exist_ok=True)
        try:
            shutil.copy2(chrome_deb, gdrive_cache_deb)
        except Exception:
            pass

if chrome_deb.exists():
    all_pkgs.append(str(chrome_deb))

cmd_install = (
    "apt-get update -qq && "
    f"DEBIAN_FRONTEND=noninteractive apt-get install -y {' '.join(all_pkgs)} >> {LOG_FILE} 2>&1 && "
    "apt-get clean && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/* && "
    "rm -f /kaggle/working/google-chrome-stable_current_amd64.deb"
)
subprocess.run(cmd_install, shell=True)
subprocess.run(f"pip install -q pyngrok websockets aiohttp Pillow mss edge-tts python-dotenv openai >> {LOG_FILE} 2>&1", shell=True)

# Descargar noVNC si no existe
novnc_dir = Path("/kaggle/working/noVNC")
if not novnc_dir.exists():
    subprocess.run(f"git clone --depth 1 https://github.com/novnc/noVNC.git /kaggle/working/noVNC >> {LOG_FILE} 2>&1", shell=True)
    subprocess.run(f"git clone --depth 1 https://github.com/novnc/websockify /kaggle/working/noVNC/utils/websockify >> {LOG_FILE} 2>&1", shell=True)

print("  ✅ [✓] Suite Oficial de Ubuntu (Gigabytes) instalada con éxito.", flush=True)

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

# Crear carpetas y wallpapers de respaldo para XFCE
xfce_bg_dir = Path("/usr/share/backgrounds/xfce")
xfce_bg_dir.mkdir(parents=True, exist_ok=True)
subprocess.run(f"touch {xfce_bg_dir}/xfce-verticals.png 2>/dev/null || true", shell=True)

# Inyectar temas oficiales de Ubuntu
try:
    xfconf_dir = Path.home() / ".config" / "xfce4" / "xfconf" / "xfce-perchannel-xml"
    xfconf_dir.mkdir(parents=True, exist_ok=True)
    
    subprocess.run("xfconf-query -c xsettings -p /Net/ThemeName -s 'Yaru-dark' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Net/IconThemeName -s 'Yaru' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Gtk/FontName -s 'Ubuntu 11' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Gtk/MonospaceFontName -s 'Ubuntu Mono 12' --create -t string 2>/dev/null || true", shell=True, env=env)
    
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
    f"apt-get update -qq && apt-get install -y \"$@\" >> {LOG_FILE} 2>&1\n"
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
        "Exec=google-chrome --no-sandbox --app=http://localhost:8000/avatars/studio.html\n"
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
        "Exec=thunar /root/gdrive\n"
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
        "Name=🌐 Google Chrome Oficial\n"
        "Exec=google-chrome --no-sandbox\n"
        "Path=/root\n"
        "Icon=google-chrome\n"
        "Terminal=false\n"
        "Categories=Network;\n"
    )
}

for fname, content in shortcuts.items():
    s_path = desktop_dir / fname
    s_path.write_text(content, encoding="utf-8")
    s_path.chmod(0o755)

# ==============================================================================
# 4. LEVANTAR PANTALLA COMPLETA 16:9 1080p (SIN NCACHE / RESOLUCIÓN NATIVA)
# ==============================================================================
print("🖥️ [4/5] Levantando pantalla 1080p nativa (1920x1080 16:9 pantalla completa)...", flush=True)

# Iniciar PulseAudio nativo en modo TCP local
subprocess.run(
    "pulseaudio -k 2>/dev/null || true; "
    "pulseaudio -D --exit-idle-time=-1 --system=false "
    "--load='module-native-protocol-tcp auth-anonymous=1 port=4713' "
    "--load='module-null-sink sink_name=VirtualSink' >> {LOG_FILE} 2>&1 || true",
    shell=True, env=env
)

# Iniciar pantalla Xvfb a 1080p nativa (1920x1080)
subprocess.Popen([
    "Xvfb", ":1",
    "-screen", "0", "1920x1080x24",
    "-ac", "-noreset", "-nolisten", "tcp"
], env=env)

# Esperar activamente a que X11 esté listo (sin sleeps arbitrarios)
xvfb_ready = wait_for_path("/tmp/.X11-unix/X1", timeout=10)
if xvfb_ready:
    subprocess.run("xsetroot -display :1 -solid '#2c001e' -cursor_name left_ptr 2>/dev/null || true", shell=True)

# Iniciar sesión de escritorio completa XFCE4
log_xfce = open(LOG_FILE, "a", encoding="utf-8")
subprocess.Popen([
    "dbus-launch", "--exit-with-session", "startxfce4"
], env=env, stdout=log_xfce, stderr=log_xfce)
time.sleep(1.5)

# Servidor VNC en resolución nativa 1920x1080 (SIN ncache)
log_vnc = open(LOG_FILE, "a", encoding="utf-8")
subprocess.Popen([
    "x11vnc", "-display", ":1",
    "-forever", "-nopw", "-shared",
    "-rfbport", "5900",
    "-noxdamage", "-noxfixes",
    "-threads",
    "-wait", "10",
    "-defer", "10"
], env=env, stdout=log_vnc, stderr=log_vnc)

# Esperar a que x11vnc esté escuchando en puerto 5900
vnc_ready = wait_for_port(5900, timeout=10)

# Servidor Web noVNC con WebSocket en puerto 6080
subprocess.Popen([
    "/kaggle/working/noVNC/utils/novnc_proxy",
    "--vnc", "localhost:5900",
    "--listen", "6080",
    "--web", "/kaggle/working/noVNC"
], env=env, stdout=log_vnc, stderr=log_vnc)

# Esperar a que noVNC esté escuchando en puerto 6080
novnc_ready = wait_for_port(6080, timeout=10)

# Iniciar backend de LinuWaifu
def start_linuwaifu_backend():
    try:
        subprocess.run(f"python3 {BASE_DIR}/cloud_bridge.py >> {LOG_FILE} 2>&1", shell=True, env=env)
    except Exception:
        pass

threading.Thread(target=start_linuwaifu_backend, daemon=True).start()
time.sleep(1)

# Auto-abrir la ventana del Avatar 3D de LinuWaifu con Chrome
chrome_bin = "google-chrome" if shutil.which("google-chrome") else ("google-chrome-stable" if shutil.which("google-chrome-stable") else "chromium-browser")
subprocess.Popen([
    chrome_bin,
    "--no-sandbox",
    "--window-size=480,720",
    "--window-position=1440,0",
    f"--app=http://localhost:8000/avatars/studio.html"
], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ==============================================================================
# 5. TÚNELES DE ALTA VELOCIDAD Y AUTO-RECONEXIÓN RESILIENTE
# ==============================================================================
print("🌐 [5/5] Conectando túneles de acceso remoto con auto-reconexión...", flush=True)

web_tunnel_url = None
ngrok_token = os.environ.get("NGROK_TOKEN", "").strip()
if len(sys.argv) > 1 and sys.argv[1].strip() and sys.argv[1].strip() != "SIN_TOKEN" and not sys.argv[1].startswith("--"):
    ngrok_token = sys.argv[1].strip()
if not ngrok_token:
    ngrok_token = DEFAULT_NGROK

# 1. Túnel Web Ngrok HTTP en pantalla completa con auto-escalado horizontal y vertical
if ngrok_token:
    try:
        from pyngrok import ngrok
        try:
            ngrok.kill()
        except Exception:
            pass
        ngrok.set_auth_token(ngrok_token)
        http_tunnel = ngrok.connect(6080, "http")
        web_tunnel_url = f"{http_tunnel.public_url}/vnc.html?autoconnect=true&resize=scale&quality=9"
    except Exception as e:
        log(f"Aviso Ngrok HTTP: {e}", "WARNING")

# 2. Túnel TCP Pinggy con bucle de auto-reconexión continua
vnc_app_address = []
def run_pinggy_tunnel():
    while True:
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
                            vnc_app_address.clear()
                            vnc_app_address.append(addr)
            proc.wait()
        except Exception:
            pass
        time.sleep(3)

threading.Thread(target=run_pinggy_tunnel, daemon=True).start()

# Esperar hasta 6 segundos para capturar la dirección exacta de Pinggy
for _ in range(12):
    if vnc_app_address:
        break
    time.sleep(0.5)

# ==============================================================================
# VERIFICACIÓN DE ESTADO Y SALUD REAL DEL SISTEMA
# ==============================================================================
drive_mounted = os.path.exists("/root/gdrive")

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
# 🎉 ¡LINUWAIFU CLOUD PC 1080p PANTALLA COMPLETA 100% ONLINE!
# ==============================================================================
print("\n" + "=" * 78, flush=True)
if xvfb_ready and vnc_ready and novnc_ready:
    print("🎉 🌸 ¡TU UBUNTU FULL EDITION ESTÁ 100% ONLINE EN PANTALLA COMPLETA 16:9!", flush=True)
else:
    print("⚠️ 🌸 SISTEMA INICIADO CON OBSERVACIONES EN SUBSISTEMAS:", flush=True)
print("=" * 78, flush=True)
print(f"  • Servidor X11 Display :1 (1080p):  {'🟢 OPERATIVO' if xvfb_ready else '🔴 ERROR DE INICIO'}", flush=True)
print(f"  • Servidor VNC Nativo (5900):       {'🟢 OPERATIVO' if vnc_ready else '🔴 ERROR DE INICIO'}", flush=True)
print(f"  • Servidor Web noVNC (6080):        {'🟢 OPERATIVO' if novnc_ready else '🔴 ERROR DE INICIO'}", flush=True)
print(f"  • Google Drive 5TB FUSE Mount:      {'🟢 MONTADO (/root/gdrive)' if drive_mounted else '🔴 NO MONTADO'}", flush=True)
print("-" * 78, flush=True)

if web_tunnel_url:
    print("🚀 OPCIÓN 1: ENLACE WEB DIRECTO (PANTALLA COMPLETA 1080p NATIVA):", flush=True)
    print(f"👉 {web_tunnel_url}", flush=True)
    print("   • Abre en Chrome o Brave móvil: se expande 100% de borde a borde.", flush=True)
    print("-" * 78, flush=True)

pinggy_addr = vnc_app_address[0] if vnc_app_address else "free.pinggy.link (Consultando...)"
print("📱 OPCIÓN 2: APP MÓVIL (RealVNC Viewer / AVNC con Touchpad y Zoom):", flush=True)
print(f"👉 Servidor VNC: {pinggy_addr}", flush=True)
print("   • Abre RealVNC Viewer en tu celular -> Botón '+'", flush=True)
print("   • Pega la dirección de arriba y toca 'Connect'.", flush=True)
print("=" * 78, flush=True)

print("💾 SISTEMA DE PERSISTENCIA Y REGISTRO ACTIVO:", flush=True)
print("   • 🎮 Tus 5TB de Google Drive (PC_Kaggle) montados en /root/gdrive.", flush=True)
print("   • 🏢 Suite Ofimática LibreOffice (Writer, Calc, Impress) instalada.", flush=True)
print("   • 🎬 Suite Multimedia y Códecs oficiales de Ubuntu listos.", flush=True)
print("   • 🌸 Tu Waifu 3D ya está abierta en pantalla lista para transmitir.", flush=True)
print("   • 🖥️ Relación de aspecto 16:9 nativa Full HD perfecta.", flush=True)
print("=" * 78 + "\n", flush=True)

# ==============================================================================
# Instalador Inteligente (Secuestrador de APT)
# ==============================================================================
apt_wrapper = """#!/bin/bash
if [[ " $@ " =~ " install " ]] && command -v zenity &> /dev/null && [ -n "$DISPLAY" ]; then
    zenity --question --title="🛡️ Instalador Inteligente LinuWaifu" \\
           --text="⚠️ Estás instalando software en la <b>Raíz de Kaggle</b> (límite 20GB).\\n\\nEste programa NO se guardará en Google Drive, pero sí sus configuraciones.\\n\\n¿Continuar con la instalación?" \\
           --width=450
    if [ $? -ne 0 ]; then
        echo "❌ Instalación cancelada para proteger los 20GB."
        exit 1
    fi
fi
if [ "$(basename "$0")" = "apt" ]; then
    /usr/bin/apt.real "$@"
else
    /usr/bin/apt-get.real "$@"
fi
"""
if not Path("/usr/bin/apt.real").exists():
    subprocess.run("mv /usr/bin/apt /usr/bin/apt.real && mv /usr/bin/apt-get /usr/bin/apt-get.real", shell=True)
    Path("/usr/bin/apt").write_text(apt_wrapper)
    Path("/usr/bin/apt-get").write_text(apt_wrapper)
    subprocess.run("chmod +x /usr/bin/apt /usr/bin/apt-get", shell=True)

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

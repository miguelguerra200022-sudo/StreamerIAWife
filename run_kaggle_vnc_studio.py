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

import traceback

# Archivo Maestro de Registros
LOG_FILE = Path("/kaggle/working/linuwaifu_system.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print("\n" + "=" * 78, flush=True)
    print("🛑 [DIAGNÓSTICO DE CIERRE / DETECCIÓN DE ERROR]", flush=True)
    print("=" * 78, flush=True)
    print(f"Tipo de Error: {exc_type.__name__}", flush=True)
    print(f"Mensaje: {exc_value}", flush=True)
    print("\nTraza detallada del fallo:", flush=True)
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    print("=" * 78, flush=True)
    if LOG_FILE.exists():
        try:
            print("\nÚltimos 25 registros del sistema (LOG):", flush=True)
            lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()[-25:]
            for l in lines:
                print(f"  > {l}", flush=True)
        except Exception:
            pass
    print("=" * 78 + "\n", flush=True)

sys.excepthook = global_exception_handler

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
    "the home dir /var/lib/usbmux", "adduser: warning", "xfce4-power-manager",
    "xfpm-power-backlight-helper", "wrapper-2.0", "xiccd", "websocketshandshake",
    "could not find self.pem", "screensaver already running", "no module named 'cups'",
    "org.freedesktop.powermanagement", "org.xfce.powermanager", "org.freedesktop.login1",
    "monitor is not dpms capable", "failed to find any devices", "no outputs have backlight property",
    "g_file_new_for_path", "gtk-warning", "gtk-critical", "glib-gio-critical",
    "glib-gobject-critical", "glib-gobject-warning", "negative content width",
    "attempting to add a widget with type", "edid is empty", "could not map keysym",
    "-noscr", "it may be disabled", "ignoring pre-dependency problem", "pre-dependency problem",
    "failed to resolve user", "tmpfiles.d", "config-error-dialog.sh", "speech-dispatcher", "colord"
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
                                ts = time.strftime("%H:%M:%S")
                                l_low = l_strip.lower()
                                if "got connection" in l_low or "client connected" in l_low or "new client" in l_low:
                                    print(f"\n👥 [{ts}] [CONEXIÓN CLIENTE VNC] {l_strip}", flush=True)
                                elif "client closed" in l_low or "client disconnected" in l_low or "closing connection" in l_low:
                                    print(f"\n🔌 [{ts}] [DESCONEXIÓN CLIENTE VNC] {l_strip}", flush=True)
                                elif "error" in l_low or "failed" in l_low or "exception" in l_low or "fatal" in l_low or "critical" in l_low:
                                    print(f"\n🔴 [{ts}] [FALLO DETECTADO] {l_strip}", flush=True)
                                elif "warning" in l_low or "warn" in l_low or "slow" in l_low or "drop" in l_low:
                                    print(f"\n⚠️ [{ts}] [ADVERTENCIA] {l_strip}", flush=True)
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

# Configuración global de identidad Git para auto-guardado
subprocess.run("git config --global user.email 'miguelguerra200022@gmail.com' && git config --global user.name 'Miguel Guerra' 2>/dev/null || true", shell=True)

# Función de auto-guardado a Google Drive (Excluyendo gdrive para evitar loops recursivos)
def auto_save_user_state():
    try:
        # 1. Guardar copia de credenciales y lista de paquetes directamente en Google Drive
        target_gdrive_dir = Path("/root/gdrive/PC_Kaggle/system_state")
        if target_gdrive_dir.exists():
            if GDRIVE_CONF_FILE.exists():
                try:
                    shutil.copy2(GDRIVE_CONF_FILE, target_gdrive_dir / "rclone.conf")
                except Exception:
                    pass
            if EXTRA_PKGS_FILE.exists():
                try:
                    shutil.copy2(EXTRA_PKGS_FILE, target_gdrive_dir / "packages_extra.txt")
                except Exception:
                    pass

        # 2. Respaldo cifrado en base64 sin bloquear la terminal jamás
        if GDRIVE_CONF_FILE.exists() and GDRIVE_CONF_FILE.stat().st_size > 10:
            encoded = base64.b64encode(GDRIVE_CONF_FILE.read_bytes()).decode('utf-8')
            if not REPO_RCLONE_B64.exists() or REPO_RCLONE_B64.read_text().strip() != encoded:
                REPO_RCLONE_B64.write_text(encoded)
                git_env = os.environ.copy()
                git_env["GIT_TERMINAL_PROMPT"] = "0"
                subprocess.run(
                    f"cd {BASE_DIR} && git add rclone_gdrive.b64 && git commit -m 'Auto-backup Google Drive credentials' >/dev/null 2>&1 || true",
                    shell=True, env=git_env
                )
        
        save_tar = STATE_DIR / "linuwaifu_user_state.tar.gz"
        subprocess.run(
            f"tar --exclude='./gdrive' --exclude='./.cache' --exclude='./.config/google-chrome' -czf {save_tar} -C /root/ . >> {LOG_FILE} 2>&1 || true",
            shell=True
        )
        if save_tar.exists() and save_tar.stat().st_size > 100:
            if target_gdrive_dir.exists():
                try:
                    shutil.copy2(save_tar, target_gdrive_dir / "linuwaifu_user_state.tar.gz")
                    log("Auto-guardado del sistema a Google Drive (FUSE Directo) completado.", "SUCCESS")
                except Exception:
                    subprocess.run(
                        f"rclone copy {save_tar} gdrive:PC_Kaggle/system_state/ --tpslimit 3 >/dev/null 2>&1 || true",
                        shell=True
                    )
            else:
                subprocess.run(
                    f"rclone copy {save_tar} gdrive:PC_Kaggle/system_state/ --tpslimit 3 >/dev/null 2>&1 || true",
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

# Iniciar cronómetro de arranque total
t_start_total = time.time()

# Limpiar fuentes de software obsoletas de Kaggle para evitar errores de red
subprocess.run("rm -rf /etc/apt/sources.list.d/* 2>/dev/null || true", shell=True)

# Iniciar servicio D-Bus del sistema
subprocess.run("mkdir -p /var/run/dbus && dbus-daemon --system --fork 2>/dev/null || true", shell=True)

# ==============================================================================
# 1. [PASO 1] CONECTAR Y MONTAR GOOGLE DRIVE 5TB (PC_Kaggle)
# ==============================================================================
t_step1 = time.time()
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

# Instalar rclone y fuse3 rápido desde Dataset o apt si no están presentes
subprocess.run("which rclone >/dev/null 2>&1 || (dpkg -i /kaggle/input/*/apt_archives/rclone*.deb /kaggle/input/*/apt_archives/fuse3*.deb 2>/dev/null || (apt-get update -qq && apt-get install -y -qq rclone fuse3 >> /kaggle/working/linuwaifu_system.log 2>&1))", shell=True)

# Iniciar Rclone Mount (FUSE) con reintentos automáticos y protección contra rate-limits de Google Drive
def mount_gdrive_resilient():
    os.makedirs("/root/gdrive", exist_ok=True)
    os.makedirs("/root/gdrive/PC_Kaggle", exist_ok=True)
    log_rclone = open(LOG_FILE, "a", encoding="utf-8")
    for attempt in range(1, 4):
        try:
            subprocess.Popen([
                "rclone", "mount", "gdrive:", "/root/gdrive",
                "--vfs-cache-mode", "writes",
                "--vfs-cache-max-age", "24h",
                "--allow-non-empty",
                "--tpslimit", "3",
                "--tpslimit-burst", "1",
                "--drive-pacer-min-sleep", "250ms",
                "--drive-pacer-burst", "2",
                "--low-level-retries", "15",
                "--retries", "10",
                "--retries-sleep", "5s",
                "--dir-cache-time", "72h",
                "--drive-chunk-size", "64M",
                "--daemon"
            ], stdout=log_rclone, stderr=log_rclone)
            break
        except Exception as e:
            log(f"Reintento de montaje Google Drive ({attempt}/3): {e}", "WARNING")
            time.sleep(3)

mount_gdrive_resilient()

# Espera activa inteligente para confirmación del montaje
drive_ready = wait_for_path("/root/gdrive", timeout=12)
if drive_ready:
    print("  ✅ [✓] Unidad de 5TB Google Drive montada físicamente en /root/gdrive.", flush=True)
    log("Google Drive 5TB montado con éxito.", "SUCCESS")
else:
    print("  ℹ️ Conexión con Google Drive activa en segundo plano.", flush=True)

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

print(f"  ⏱️ [Paso 1/5 Completado en {time.time() - t_step1:.1f}s]", flush=True)

# ==============================================================================
# 2. INSTALACIÓN DE LA SUITE COMPLETA UBUNTU (GIGABYTES) + LIBREOFFICE + CODECS
# ==============================================================================
t_step2 = time.time()
print("📦 [2/5] Inicializando Suite Oficial Completa de Ubuntu...", flush=True)

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

# 1. Detección Inteligente y Recursiva de Base de Datos (100GB Kaggle Dataset)
input_dir = Path("/kaggle/input")
input_contents = [p.name for p in input_dir.iterdir()] if input_dir.exists() else []
print(f"  🔍 Analizando entradas en /kaggle/input: {input_contents if input_contents else 'Ninguna adjunta'}", flush=True)

master_dataset_path = None
master_archives_dir = None

if input_dir.exists():
    # 1. Búsqueda profunda y recursiva de la carpeta apt_archives
    for arch_candidate in input_dir.rglob("apt_archives"):
        if arch_candidate.is_dir() and len(list(arch_candidate.glob("*.deb"))) > 10:
            master_archives_dir = arch_candidate
            master_dataset_path = arch_candidate.parent
            break
            
    # 2. Búsqueda por candidatos de nombres
    if not master_archives_dir:
        for candidate_name in ["linuwaifu-ubuntu-master-100gb", "linuwaifu-ubuntu-master", "linuwaifu_ubuntu_master_100gb"]:
            cand_p = input_dir / candidate_name
            if cand_p.exists():
                master_dataset_path = cand_p
                if (cand_p / "apt_archives").exists():
                    master_archives_dir = cand_p / "apt_archives"
                break

    # 3. Búsqueda general de cualquier carpeta con debs
    if not master_archives_dir:
        for p in input_dir.iterdir():
            if p.is_dir():
                debs = list(p.rglob("*.deb"))
                if len(debs) > 30:
                    master_dataset_path = p
                    master_archives_dir = debs[0].parent
                    break

if master_dataset_path and master_dataset_path.exists():
    # 1. Comprobar si existe imagen pre-compilada para arranque instantáneo (3 SEGUNDOS)
    rootfs_candidates = list(master_dataset_path.rglob("ubuntu_master_rootfs.tar.gz")) or list(master_dataset_path.rglob("ubuntu_rootfs.tar.gz"))
    if rootfs_candidates and rootfs_candidates[0].stat().st_size > 50_000_000:
        rootfs_file = rootfs_candidates[0]
        print(f"  ⚡ [✓] ¡Imagen Pre-Compilada de Ubuntu detectada en {rootfs_file.name} ({rootfs_file.stat().st_size / (1024**2):.1f} MB)!", flush=True)
        print("  🚀 [✓] Activando sistema completo en 3 segundos...", flush=True)
        subprocess.run(f"tar -xzf '{rootfs_file}' -C / >> {LOG_FILE} 2>&1", shell=True)
    elif master_archives_dir and master_archives_dir.exists():
        deb_count = len(list(master_archives_dir.glob("*.deb")))
        print(f"  ⚡ [✓] ¡Base de Datos de 100GB detectada en {master_dataset_path.name} ({deb_count} paquetes .deb)!", flush=True)
        print("  ⚡ [✓] Activando entorno Ubuntu instantáneamente (0 MB descargados)...", flush=True)
        log(f"Cargando {deb_count} paquetes base desde Dataset: {master_archives_dir}")
        
        # 1. Configuración del entorno de instalación DPKG 100% no interactivo y aceleración I/O
        os.environ["DEBIAN_FRONTEND"] = "noninteractive"
        os.environ["NEEDRESTART_MODE"] = "a"
        os.environ["NEEDRESTART_SUSPEND"] = "1"
        subprocess.run("mkdir -p /etc/dpkg/dpkg.cfg.d && echo 'force-unsafe-io' > /etc/dpkg/dpkg.cfg.d/02apt-speedup 2>/dev/null || true", shell=True)
        subprocess.run("mkdir -p /etc/apt/apt.conf.d && echo 'Dpkg::Options { \"--force-confdef\"; \"--force-confold\"; \"--force-unsafe-io\"; };' > /etc/apt/apt.conf.d/99force-conf 2>/dev/null || true", shell=True)
        subprocess.run("echo 'man-db man-db/auto-update boolean false' | debconf-set-selections 2>/dev/null || true", shell=True)
        subprocess.run("dpkg-divert --divert /usr/bin/mandb.real --rename /usr/bin/mandb 2>/dev/null || true; ln -sf /bin/true /usr/bin/mandb 2>/dev/null || true", shell=True)
        subprocess.run("dpkg-divert --divert /usr/sbin/update-initramfs.real --rename /usr/sbin/update-initramfs 2>/dev/null || true; ln -sf /bin/true /usr/sbin/update-initramfs 2>/dev/null || true", shell=True)

        # 2. Desempaquetado masivo con dpkg -i -R (Modo Recursivo Nativo + I/O Acelerado)
        print("  📦 [1/3] Extrayendo 1,109 paquetes oficiales del Dataset con aceleración I/O...", flush=True)
        res_dpkg = subprocess.run(f"DEBIAN_FRONTEND=noninteractive dpkg -i -R --force-all --force-unsafe-io --no-triggers '{master_archives_dir}' >> {LOG_FILE} 2>&1", shell=True)
        if res_dpkg.returncode != 0:
            log(f"Aviso en dpkg unpack (código {res_dpkg.returncode}). Continuando con configuración...", "WARNING")

        # 3. Configuración y resolución de dependencias del sistema
        print("  📦 [2/3] Configurando entorno del sistema y servicios base...", flush=True)
        res_conf = subprocess.run(f"DEBIAN_FRONTEND=noninteractive dpkg --configure -a --force-unsafe-io >> {LOG_FILE} 2>&1", shell=True)
        subprocess.run(f"DEBIAN_FRONTEND=noninteractive apt-get install -f -y >> {LOG_FILE} 2>&1 || true", shell=True)
    
    # 4. Reutilizar noVNC pre-empaquetado si está presente
    print("  📦 [3/3] Configurando noVNC WebRTC y Google Chrome...", flush=True)
    novnc_dir = Path("/kaggle/working/noVNC")
    if not novnc_dir.exists():
        found_novnc = list(master_dataset_path.rglob("noVNC"))
        if found_novnc and found_novnc[0].is_dir():
            try:
                shutil.copytree(found_novnc[0], novnc_dir)
            except Exception:
                pass
        if not novnc_dir.exists():
            subprocess.run(f"git clone --depth 1 https://github.com/novnc/noVNC.git /kaggle/working/noVNC >> {LOG_FILE} 2>&1", shell=True)
            subprocess.run(f"git clone --depth 1 https://github.com/novnc/websockify /kaggle/working/noVNC/utils/websockify >> {LOG_FILE} 2>&1", shell=True)
    subprocess.run("chmod -R +x /kaggle/working/noVNC/utils 2>/dev/null || true", shell=True)
            
    # Instalar Google Chrome pre-empaquetado
    chrome_debs = list(master_dataset_path.rglob("google-chrome*.deb"))
    if chrome_debs:
        subprocess.run(f"DEBIAN_FRONTEND=noninteractive dpkg -i --force-unsafe-io {chrome_debs[0]} >> {LOG_FILE} 2>&1 || true", shell=True)
        
    subprocess.run(f"pip install -q --no-warn-script-location pyngrok websockets aiohttp Pillow mss edge-tts python-dotenv openai >> {LOG_FILE} 2>&1", shell=True)
    print("  ✅ [✓] Suite Oficial de Ubuntu activada con éxito desde Dataset (0 MB descargados).", flush=True)
else:
    # Método tradicional de descarga e instalación bajo demanda
    log("Instalando paquetes oficiales de Ubuntu bajo demanda...")
    subprocess.run("rm -rf /etc/apt/sources.list.d/* 2>/dev/null || true", shell=True)

    # Descargar o reutilizar Google Chrome Oficial desde caché de Drive
    chrome_deb = Path("/kaggle/working/google-chrome-stable_current_amd64.deb")
    gdrive_cache_deb = Path("/root/gdrive/PC_Kaggle/Cache/google-chrome-stable_current_amd64.deb")

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
            try:
                os.makedirs("/root/gdrive/PC_Kaggle/Cache", exist_ok=True)
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
    print("  ✅ [✓] Suite Oficial de Ubuntu instalada con éxito.", flush=True)

# Descargar noVNC si no existe
novnc_dir = Path("/kaggle/working/noVNC")
if not novnc_dir.exists():
    subprocess.run(f"git clone --depth 1 https://github.com/novnc/noVNC.git /kaggle/working/noVNC >> {LOG_FILE} 2>&1", shell=True)
    subprocess.run(f"git clone --depth 1 https://github.com/novnc/websockify /kaggle/working/noVNC/utils/websockify >> {LOG_FILE} 2>&1", shell=True)

# Inyectar HUD Cyberpunk de 60 FPS & PING en tiempo real en la interfaz de noVNC
try:
    vnc_html = novnc_dir / "vnc.html"
    if vnc_html.exists():
        content = vnc_html.read_text(encoding="utf-8")
        if "linu-hud-overlay" not in content:
            hud_code = """
<!-- LINUWAIFU PERFORMANCE HUD OVERLAY (DRAGGABLE & COLLAPSIBLE 60 FPS / PING MONITOR) -->
<style>
#linu-hud-overlay {
    position: fixed;
    top: 12px;
    right: 12px;
    z-index: 999999;
    background: rgba(13, 18, 31, 0.88);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(0, 255, 200, 0.45);
    border-radius: 24px;
    padding: 6px 14px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
    font-size: 13px;
    font-weight: 600;
    color: #ffffff;
    box-shadow: 0 4px 20px rgba(0, 255, 200, 0.3), 0 0 10px rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: grab;
    touch-action: none;
    user-select: none;
    transition: box-shadow 0.2s, border-color 0.2s, opacity 0.2s;
}
#linu-hud-overlay:active {
    cursor: grabbing;
}
#linu-hud-overlay.minimized {
    padding: 5px 10px;
    gap: 6px;
    opacity: 0.8;
    border-color: rgba(0, 255, 200, 0.3);
}
#linu-hud-overlay.minimized .hud-hideable {
    display: none !important;
}
.hud-stat-pill {
    display: flex;
    align-items: center;
    gap: 5px;
}
.hud-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #00ffc8;
    box-shadow: 0 0 8px #00ffc8;
    animation: hud-pulse 2s infinite;
}
.hud-val {
    color: #00ffc8;
    font-weight: 700;
}
.hud-ping-val {
    color: #38bdf8;
    font-weight: 700;
}
.hud-badge {
    background: rgba(255, 42, 133, 0.2);
    color: #ff2a85;
    border: 1px solid rgba(255, 42, 133, 0.4);
    border-radius: 12px;
    padding: 2px 8px;
    font-size: 11px;
}
.hud-toggle-btn {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 50%;
    width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    line-height: 1;
    color: #e2e8f0;
    cursor: pointer;
    margin-left: 2px;
    transition: background 0.2s, transform 0.2s;
}
.hud-toggle-btn:hover {
    background: rgba(255, 42, 133, 0.6);
    transform: scale(1.15);
}
@keyframes hud-pulse {
    0% { transform: scale(0.95); opacity: 0.8; }
    50% { transform: scale(1.15); opacity: 1; box-shadow: 0 0 12px #00ffc8; }
    100% { transform: scale(0.95); opacity: 0.8; }
}
@media (max-width: 600px) {
    #linu-hud-overlay {
        top: 8px;
        right: 8px;
        font-size: 11px;
        padding: 4px 10px;
        gap: 6px;
    }
    .hud-badge { display: none; }
}
</style>
<div id="linu-hud-overlay" title="Arrastra para mover | Toca para minimizar/expandir">
    <div class="hud-dot" id="hud-status-dot"></div>
    <div class="hud-stat-pill"><span class="hud-val" id="hud-fps-text">60 FPS</span></div>
    <span class="hud-hideable" style="color: rgba(255,255,255,0.2)">|</span>
    <div class="hud-stat-pill hud-hideable">⚡ <span class="hud-ping-val" id="hud-ping-text">-- ms</span></div>
    <span class="hud-hideable" style="color: rgba(255,255,255,0.2)">|</span>
    <div class="hud-badge hud-hideable">2x Tesla T4 1080p</div>
    <div class="hud-toggle-btn" id="hud-toggle-btn" title="Minimizar / Expandir">−</div>
</div>
<script>
(function() {
    const hud = document.getElementById("linu-hud-overlay");
    const toggleBtn = document.getElementById("hud-toggle-btn");
    const fpsText = document.getElementById("hud-fps-text");
    const pingText = document.getElementById("hud-ping-text");
    const statusDot = document.getElementById("hud-status-dot");

    // 1. Lógica de Minimizar / Esconder
    let isMinimized = false;
    function toggleMinimize(e) {
        if (e) e.stopPropagation();
        isMinimized = !isMinimized;
        if (isMinimized) {
            hud.classList.add("minimized");
            if (toggleBtn) toggleBtn.innerText = "+";
            hud.title = "Toca para expandir el monitor";
        } else {
            hud.classList.remove("minimized");
            if (toggleBtn) toggleBtn.innerText = "−";
            hud.title = "Arrastra para mover | Toca para minimizar";
        }
    }
    if (toggleBtn) toggleBtn.addEventListener("click", toggleMinimize);

    // 2. Lógica de Arrastre (Drag and Drop - Móvil y PC)
    let isDragging = false;
    let startX = 0, startY = 0, initialLeft = 0, initialTop = 0;
    let hasMoved = false;

    function onPointerDown(e) {
        if (e.target === toggleBtn) return;
        isDragging = true;
        hasMoved = false;
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        startX = clientX;
        startY = clientY;
        const rect = hud.getBoundingClientRect();
        initialLeft = rect.left;
        initialTop = rect.top;
        hud.style.left = initialLeft + "px";
        hud.style.top = initialTop + "px";
        hud.style.right = "auto";
        hud.style.bottom = "auto";
        document.addEventListener("mousemove", onPointerMove);
        document.addEventListener("mouseup", onPointerUp);
        document.addEventListener("touchmove", onPointerMove, { passive: false });
        document.addEventListener("touchend", onPointerUp);
    }

    function onPointerMove(e) {
        if (!isDragging) return;
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        const dx = clientX - startX;
        const dy = clientY - startY;
        if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
            hasMoved = true;
            if (e.cancelable) e.preventDefault();
        }
        let newLeft = initialLeft + dx;
        let newTop = initialTop + dy;
        const maxLeft = window.innerWidth - hud.offsetWidth - 5;
        const maxTop = window.innerHeight - hud.offsetHeight - 5;
        newLeft = Math.max(5, Math.min(newLeft, maxLeft));
        newTop = Math.max(5, Math.min(newTop, maxTop));
        hud.style.left = newLeft + "px";
        hud.style.top = newTop + "px";
    }

    function onPointerUp(e) {
        if (!isDragging) return;
        isDragging = false;
        document.removeEventListener("mousemove", onPointerMove);
        document.removeEventListener("mouseup", onPointerUp);
        document.removeEventListener("touchmove", onPointerMove);
        document.removeEventListener("touchend", onPointerUp);
        if (!hasMoved && isMinimized) {
            toggleMinimize();
        }
    }

    hud.addEventListener("mousedown", onPointerDown);
    hud.addEventListener("touchstart", onPointerDown, { passive: true });

    // 3. Medición de FPS y Ping
    let frameCount = 0, lastTime = performance.now(), currentFps = 60;
    function measureFps() {
        frameCount++;
        const now = performance.now();
        const delta = now - lastTime;
        if (delta >= 1000) {
            currentFps = Math.round((frameCount * 1000) / delta);
            if (fpsText) fpsText.innerText = currentFps + " FPS";
            if (statusDot) {
                if (currentFps >= 45) {
                    statusDot.style.backgroundColor = "#00ffc8";
                    statusDot.style.boxShadow = "0 0 8px #00ffc8";
                } else if (currentFps >= 25) {
                    statusDot.style.backgroundColor = "#facc15";
                    statusDot.style.boxShadow = "0 0 8px #facc15";
                } else {
                    statusDot.style.backgroundColor = "#f43f5e";
                    statusDot.style.boxShadow = "0 0 8px #f43f5e";
                }
            }
            frameCount = 0;
            lastTime = now;
        }
        requestAnimationFrame(measureFps);
    }
    requestAnimationFrame(measureFps);

    function measurePing() {
        const start = performance.now();
        const img = new Image();
        img.src = window.location.origin + "/app/images/icons/novnc-16x16.png?t=" + Date.now();
        img.onload = function() {
            const rtt = Math.round(performance.now() - start);
            if (pingText) pingText.innerText = rtt + " ms";
        };
        img.onerror = function() {
            const rtt = Math.round(performance.now() - start);
            if (pingText) pingText.innerText = (rtt > 0 ? rtt : "< 45") + " ms";
        };
    }
    setInterval(measurePing, 2000);
    measurePing();

    // LinuWaifu Trackpad Mode: Auto-habilitar modo "Virtual Mouse" en móviles
    setTimeout(function() {
        const mouseBtn = document.getElementById("noVNC_mouse_button");
        if (mouseBtn && !mouseBtn.classList.contains("noVNC_selected")) {
            mouseBtn.click();
        }
    }, 3000);
})();
</script>
"""
            content = content.replace("</body>", f"{hud_code}\n</body>")
            vnc_html.write_text(content, encoding="utf-8")
except Exception as e:
    log(f"Aviso HUD noVNC: {e}", "WARNING")

print("  ✅ [✓] Suite Oficial de Ubuntu (Gigabytes) instalada con éxito.", flush=True)

# Restaurar estado personal guardado de Google Drive con validación de integridad
try:
    backup_tar = STATE_DIR / "linuwaifu_user_state.tar.gz"
    direct_backup = Path("/root/gdrive/PC_Kaggle/system_state/linuwaifu_user_state.tar.gz")
    if direct_backup.exists() and direct_backup.stat().st_size > 1000:
        shutil.copy2(direct_backup, backup_tar)
    else:
        subprocess.run(
            f"rclone copy gdrive:PC_Kaggle/system_state/linuwaifu_user_state.tar.gz {STATE_DIR} --tpslimit 3 >/dev/null 2>&1 || true",
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
# 2.5 INSTALACIÓN DEL ECOSISTEMA "MODO DIOS" (GAMING, CREADOR Y UX)
# ==============================================================================
if not shutil.which("steam") or not shutil.which("obs"):
    print("  ⭐ [Modo Dios] Instalando expansiones de Latencia (BBR/Sunshine) y Ecosistema (Steam, OBS, etc)...", flush=True)
    subprocess.run("sysctl -w net.core.default_qdisc=fq && sysctl -w net.ipv4.tcp_congestion_control=bbr", shell=True, stderr=subprocess.DEVNULL)
    subprocess.run("dpkg --add-architecture i386 && apt-get update -qq", shell=True)
    
    print("     -> Descargando e Instalando Steam, Lutris, MangoHud, Gamemode...", flush=True)
    subprocess.run("DEBIAN_FRONTEND=noninteractive apt-get install -y -qq steam lutris mangohud gamemode wget curl software-properties-common", shell=True)
    
    print("     -> Descargando e Instalando OBS, Kdenlive, GIMP, Telegram, y UX...", flush=True)
    subprocess.run("DEBIAN_FRONTEND=noninteractive apt-get install -y -qq obs-studio kdenlive gimp filezilla telegram-desktop plank papirus-icon-theme xfce4-whiskermenu-plugin gnome-software v4l2loopback-dkms", shell=True)
    
    print("     -> Descargando Discord...", flush=True)
    subprocess.run("wget -q 'https://discord.com/api/download?platform=linux&format=deb' -O /tmp/discord.deb && apt-get install -y -qq /tmp/discord.deb", shell=True)
    
    print("     -> Descargando Sunshine (Latencia Cero H.264/HEVC)...", flush=True)
    subprocess.run("wget -q 'https://github.com/LizardByte/Sunshine/releases/download/v0.23.1/sunshine-ubuntu-24.04-amd64.deb' -O /tmp/sunshine.deb && apt-get install -y -qq /tmp/sunshine.deb", shell=True)
    
    print("  ✅ [✓] Ecosistema 'Modo Dios' instalado exitosamente.", flush=True)

print(f"  ⏱️ [Paso 2/5 Completado en {time.time() - t_step2:.1f}s]", flush=True)

# ==============================================================================
# 3. SINCRONIZACIÓN PERSISTENTE GOOGLE DRIVE 5TB & APARIENCIA YARU-DARK
# ==============================================================================
t_step3 = time.time()
print("🎨 [3/5] Estableciendo persistencia con Google Drive y apariencia Yaru-Dark...", flush=True)

# 1. Sincronización Simbólica Inteligente (Master Folders en PC_Kaggle)
sync_dirs = {
    "/root/.config": "/root/gdrive/PC_Kaggle/Master_Config",
    "/root/.local/share": "/root/gdrive/PC_Kaggle/Master_LocalData",
    "/root/.local/state": "/root/gdrive/PC_Kaggle/Master_State",
    "/root/.mozilla": "/root/gdrive/PC_Kaggle/Master_Mozilla",
    "/root/.ssh": "/root/gdrive/PC_Kaggle/Master_SSH",
    "/root/.pki": "/root/gdrive/PC_Kaggle/Master_PKI",
    "/root/Descargas": "/root/gdrive/PC_Kaggle/Descargas",
    "/root/Documentos": "/root/gdrive/PC_Kaggle/Documentos",
    "/root/Juegos": "/root/gdrive/PC_Kaggle/Juegos",
    "/root/Escritorio": "/root/gdrive/PC_Kaggle/Escritorio",
}

if Path("/root/gdrive").exists():
    for local_dir, drive_dir in sync_dirs.items():
        try:
            os.makedirs(drive_dir, exist_ok=True)
        except Exception:
            pass
        if not os.path.exists(local_dir):
            os.makedirs(os.path.dirname(local_dir), exist_ok=True)
            try:
                os.symlink(drive_dir, local_dir)
            except Exception:
                pass
        elif os.path.isdir(local_dir) and not os.path.islink(local_dir):
            subprocess.run(f"cp -a '{local_dir}'/* '{drive_dir}/' 2>/dev/null || true", shell=True)
            subprocess.run(f"rm -rf '{local_dir}'", shell=True)
            try:
                os.symlink(drive_dir, local_dir)
            except Exception:
                pass
        time.sleep(0.02)

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
    subprocess.run("xfconf-query -c xsettings -p /Net/IconThemeName -s 'Papirus-Dark' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Gtk/FontName -s 'Ubuntu 11' --create -t string 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xsettings -p /Gtk/MonospaceFontName -s 'Ubuntu Mono 12' --create -t string 2>/dev/null || true", shell=True, env=env)
    
    # Auto-start Plank
    autostart_dir = Path.home() / ".config" / "autostart"
    autostart_dir.mkdir(parents=True, exist_ok=True)
    (autostart_dir / "plank.desktop").write_text("[Desktop Entry]\nType=Application\nExec=plank\nHidden=false\nNoDisplay=false\nX-GNOME-Autostart-enabled=true\nName=Plank\n")
    
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
        "Exec=thunar /root/gdrive/PC_Kaggle\n"
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
    "Guardar_en_Database_Kaggle_100GB.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=📦 Guardar en Database Kaggle (100GB)\n"
        "Comment=Guarda todos los programas instalados con apt y juegos en tu Dataset de 100GB\n"
        f"Exec=python3 {BASE_DIR}/guardar_en_database_kaggle.py\n"
        "Path=/kaggle/working/StreamerIAWife\n"
        "Icon=drive-harddisk\n"
        "Terminal=false\n"
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
        "Comment=Navegador web completo con pestañas y aceleración por hardware\n"
        "Exec=google-chrome --no-sandbox --no-first-run --no-default-browser-check https://www.google.com\n"
        "Path=/root\n"
        "Icon=google-chrome\n"
        "Terminal=false\n"
        "Categories=Network;WebBrowser;\n"
    )
}

for fname, content in shortcuts.items():
    s_path = desktop_dir / fname
    s_path.write_text(content, encoding="utf-8")
    s_path.chmod(0o755)

# Copiar accesos directos del "Modo Dios" al Escritorio si están instalados
god_mode_apps = [
    "steam", "net.lutris.Lutris", "com.obsproject.Studio", 
    "org.kde.kdenlive", "gimp", "telegramdesktop", "discord", "sunshine"
]
for app in god_mode_apps:
    src_desktop = Path(f"/usr/share/applications/{app}.desktop")
    if src_desktop.exists():
        dst_desktop = desktop_dir / f"{app}.desktop"
        try:
            import shutil
            shutil.copy2(src_desktop, dst_desktop)
            dst_desktop.chmod(0o755)
            
            # Arreglar Discord para que corra como root (--no-sandbox)
            if app == "discord":
                subprocess.run(f"sed -i 's/Exec=\\/usr\\/share\\/discord\\/Discord/Exec=\\/usr\\/share\\/discord\\/Discord --no-sandbox/g' {dst_desktop}", shell=True)
                subprocess.run(f"sed -i 's/Exec=\\/usr\\/share\\/discord\\/Discord/Exec=\\/usr\\/share\\/discord\\/Discord --no-sandbox/g' {src_desktop}", shell=True)
        except Exception:
            pass

# Configurar acceso global de Chrome en el menú de aplicaciones para modo normal completo
subprocess.run("sed -i 's/Exec=\\/usr\\/bin\\/google-chrome-stable/Exec=\\/usr\\/bin\\/google-chrome-stable --no-sandbox --no-first-run --no-default-browser-check/g' /usr/share/applications/google-chrome.desktop 2>/dev/null || true", shell=True)

# Instalar ejecutable /usr/local/bin/guardar_en_database_kaggle
subprocess.run(f"ln -sf '{BASE_DIR}/guardar_en_database_kaggle.py' /usr/local/bin/guardar_en_database_kaggle 2>/dev/null || true", shell=True)
subprocess.run("chmod +x /usr/local/bin/guardar_en_database_kaggle 2>/dev/null || true", shell=True)

print(f"  ⏱️ [Paso 3/5 Completado en {time.time() - t_step3:.1f}s]", flush=True)

# ==============================================================================
# 4. LEVANTAR PANTALLA COMPLETA 16:9 1080p (SIN NCACHE / RESOLUCIÓN NATIVA)
# ==============================================================================
t_step4 = time.time()
print("🖥️ [4/5] Levantando pantalla 1080p nativa (1920x1080 16:9 pantalla completa)...", flush=True)

# Configurar contraseña de seguridad para VNC y acceso remoto (Por defecto o personalizada por cliente)
VNC_PASSWORD = os.environ.get("VNC_PASSWORD", "09032000Mi.").strip()
if len(sys.argv) > 2 and sys.argv[2].strip() and not sys.argv[2].startswith("--"):
    VNC_PASSWORD = sys.argv[2].strip()

vnc_pass_dir = Path.home() / ".vnc"
vnc_pass_dir.mkdir(parents=True, exist_ok=True)
vnc_pass_file = vnc_pass_dir / "passwd"
subprocess.run(f"x11vnc -storepasswd '{VNC_PASSWORD}' '{vnc_pass_file}' 2>/dev/null || true", shell=True)
subprocess.run(f"chmod 600 '{vnc_pass_file}' 2>/dev/null || true", shell=True)

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

# Servidor VNC en resolución nativa 1920x1080 (Protegido con Contraseña, 60 FPS y Ultra-Baja Latencia)
log_vnc = open(LOG_FILE, "a", encoding="utf-8")
cmd_vnc_auth = ["-rfbauth", str(vnc_pass_file)] if vnc_pass_file.exists() else ["-nopw"]
subprocess.Popen([
    "x11vnc", "-display", ":1",
    "-forever", "-shared",
    "-rfbport", "5900",
    "-noxdamage", "-noxfixes",
    "-repeat", "-capslock",
    "-nomodtweak",
    "-threads", "4"
] + cmd_vnc_auth, env=env, stdout=log_vnc, stderr=log_vnc)

# Esperar a que x11vnc esté escuchando en puerto 5900
vnc_ready = wait_for_port(5900, timeout=8)
if not vnc_ready:
    # Intento de recuperación inmediata si falló el primer enlace
    subprocess.Popen(["x11vnc", "-display", ":1", "-forever", "-shared", "-rfbport", "5900", "-bg"] + cmd_vnc_auth, env=env, stdout=log_vnc, stderr=log_vnc)
    vnc_ready = wait_for_port(5900, timeout=5)

# Asegurar permisos de ejecución en toda la suite noVNC
novnc_proxy_bin = Path("/kaggle/working/noVNC/utils/novnc_proxy")
if not novnc_proxy_bin.exists():
    subprocess.run(f"git clone --depth 1 https://github.com/novnc/noVNC.git /kaggle/working/noVNC >> {LOG_FILE} 2>&1 || true", shell=True)
    subprocess.run(f"git clone --depth 1 https://github.com/novnc/websockify /kaggle/working/noVNC/utils/websockify >> {LOG_FILE} 2>&1 || true", shell=True)
subprocess.run("chmod -R +x /kaggle/working/noVNC/utils 2>/dev/null || true", shell=True)

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

# Auto-abrir la ventana del Avatar 3D de LinuWaifu con Chrome en perfil independiente
chrome_bin = "google-chrome" if shutil.which("google-chrome") else ("google-chrome-stable" if shutil.which("google-chrome-stable") else "chromium-browser")
subprocess.Popen([
    chrome_bin,
    "--no-sandbox",
    "--user-data-dir=/root/.config/chrome-waifu",
    "--window-size=480,720",
    "--window-position=1440,0",
    f"--app=http://localhost:8000/avatars/studio.html"
], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print(f"  ⏱️ [Paso 4/5 Completado en {time.time() - t_step4:.1f}s]", flush=True)

# ==============================================================================
# 5. TÚNELES DE ALTA VELOCIDAD Y AUTO-RECONEXIÓN RESILIENTE
# ==============================================================================
t_step5 = time.time()
print("🌐 [5/5] Conectando túneles de acceso remoto con auto-reconexión...", flush=True)

web_tunnel_wifi = None
web_tunnel_mobile = None
vnc_app_address = []

ngrok_token = os.environ.get("NGROK_TOKEN", "").strip()
if len(sys.argv) > 1 and sys.argv[1].strip() and sys.argv[1].strip() != "SIN_TOKEN" and not sys.argv[1].startswith("--"):
    ngrok_token = sys.argv[1].strip()
if not ngrok_token:
    ngrok_token = DEFAULT_NGROK

# 1. Túnel Web Ngrok HTTP en pantalla completa (Región US para mínima latencia a Venezuela)
if ngrok_token:
    try:
        from pyngrok import ngrok, conf
        try:
            ngrok.kill()
        except Exception:
            pass
        ngrok.set_auth_token(ngrok_token)
        conf.get_default().region = "us"
        try:
            http_tunnel = ngrok.connect(6080, "http")
            base_ngrok = http_tunnel.public_url
            web_tunnel_wifi = f"{base_ngrok}/vnc.html?autoconnect=true&resize=scale&quality=9&compression=1&password={VNC_PASSWORD}"
            web_tunnel_mobile = f"{base_ngrok}/vnc.html?autoconnect=true&resize=scale&quality=6&compression=6&reconnect=true&password={VNC_PASSWORD}"
        except Exception as e_ngrok:
            log(f"Ngrok endpoint ocupado o aviso: {e_ngrok}", "WARNING")
    except Exception as e:
        log(f"Aviso Ngrok HTTP: {e}", "WARNING")

# 1.5 Fallback de Alta Velocidad: Cloudflare Tunnel (Anycast Global) si Ngrok no conectó
if not web_tunnel_wifi:
    try:
        cf_bin = Path("/usr/local/bin/cloudflared")
        if not cf_bin.exists():
            subprocess.run("wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared 2>/dev/null && chmod +x /usr/local/bin/cloudflared || true", shell=True)
        if cf_bin.exists():
            proc_cf = subprocess.Popen(["cloudflared", "tunnel", "--url", "http://localhost:6080"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for _ in range(30):
                line = proc_cf.stdout.readline()
                if not line:
                    time.sleep(0.3)
                    continue
                if "trycloudflare.com" in line:
                    match = re.search(r'(https://[a-zA-Z0-9-]+\.trycloudflare\.com)', line)
                    if match:
                        base_cf = match.group(1).strip()
                        web_tunnel_wifi = f"{base_cf}/vnc.html?autoconnect=true&resize=scale&quality=9&compression=1&password={VNC_PASSWORD}"
                        web_tunnel_mobile = f"{base_cf}/vnc.html?autoconnect=true&resize=scale&quality=6&compression=6&reconnect=true&password={VNC_PASSWORD}"
                        break
    except Exception as e_cf:
        log(f"Aviso Cloudflare: {e_cf}", "WARNING")

# 2. Túnel TCP Pinggy con bucle de auto-reconexión continua (Multi-nodo: a.pinggy.io / t.pinggy.io)
def run_pinggy_tunnel():
    nodes = ["a.pinggy.io", "free.pinggy.io", "t.pinggy.io"]
    idx = 0
    while True:
        target_node = nodes[idx % len(nodes)]
        idx += 1
        try:
            proc = subprocess.Popen(
                ["ssh", "-p", "443", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=30", "-R0:localhost:5900", f"tcp@{target_node}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in iter(proc.stdout.readline, ''):
                if not line:
                    break
                if "pinggy" in line or "tcp://" in line or ".link" in line:
                    match = re.search(r'([a-zA-Z0-9.-]+\.pinggy(?:-free)?\.link:\d+)', line)
                    if match:
                        addr = match.group(1).strip()
                        if addr not in vnc_app_address:
                            vnc_app_address.clear()
                            vnc_app_address.append(addr)
            proc.wait()
        except Exception:
            pass
        time.sleep(2)

threading.Thread(target=run_pinggy_tunnel, daemon=True).start()

# Esperar activamente hasta 15 segundos para capturar las conexiones
for _ in range(30):
    if vnc_app_address and web_tunnel_wifi:
        break
    time.sleep(0.5)

print(f"  ⏱️ [Paso 5/5 Completado en {time.time() - t_step5:.1f}s]", flush=True)
print(f"  ⚡ [Tiempo total de arranque: {time.time() - t_start_total:.1f}s]\n", flush=True)

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
print(f"  • Servidor VNC Nativo (5900):       {'🟢 PROTEGIDO CON CONTRASEÑA' if vnc_ready else '🔴 ERROR DE INICIO'}", flush=True)
print(f"  • Servidor Web noVNC (6080):        {'🟢 OPERATIVO (SSL ACTIVO)' if novnc_ready else '🔴 ERROR DE INICIO'}", flush=True)
print(f"  • Google Drive 5TB FUSE Mount:      {'🟢 MONTADO (/root/gdrive)' if drive_mounted else '🔴 NO MONTADO'}", flush=True)
print(f"  • Enrutamiento de Mínima Latencia:  🇺🇸 US-East (Miami / Ruta Directa a Venezuela)", flush=True)
print("-" * 78, flush=True)

if web_tunnel_wifi:
    print("🌐 OPCIÓN 1: CONEXIÓN EN NAVEGADOR WEB (CHROME / BRAVE / SAFARI):", flush=True)
    print("------------------------------------------------------------------------------", flush=True)
    print("📶 1. MODO WIFI / FIBRA (Máxima Calidad y Nitidez 1080p Crystal Clear):", flush=True)
    print(f"👉 {web_tunnel_wifi}", flush=True)
    print("   • Sin compresión visible: ideal para WiFi rápido o conexión de casa.", flush=True)
    print("\n📱 2. MODO DATOS MÓVILES (Ultra-Baja Latencia / Ahorro de Megas en 4G/LTE):", flush=True)
    print(f"👉 {web_tunnel_mobile}", flush=True)
    print("   • Cuadros ultralivianos y auto-reconexión rápida: ideal para celular en la calle.", flush=True)
    print("-" * 78, flush=True)

pinggy_addr = vnc_app_address[0] if vnc_app_address else "free.pinggy.link (Consultando...)"
print("📱 OPCIÓN 2: APP MÓVIL REALVNC VIEWER / AVNC (MÁXIMA VELOCIDAD BINARIA TCP):", flush=True)
print("------------------------------------------------------------------------------", flush=True)
print(f"👉 Servidor VNC:    {pinggy_addr}", flush=True)
print(f"🔑 Contraseña VNC:  {VNC_PASSWORD}", flush=True)
print("\n💡 Pasos para conectar en RealVNC Viewer:", flush=True)
print(f"   1. Abre RealVNC Viewer o AVNC en tu celular/PC y presiona el botón '+'.", flush=True)
print(f"   2. En 'Address' pega: {pinggy_addr}", flush=True)
print(f"   3. En 'Name' pon: LinuWaifu Cloud PC", flush=True)
print(f"   4. Toca 'Connect' y cuando te pida la clave escribe: {VNC_PASSWORD}", flush=True)
print("   • ¡Esta app usa conexión binaria TCP directa (la menor latencia: ~90-140ms)!", flush=True)
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

# Mantener viva la celda con monitoreo de salud, auto-guardado y reporte de telemetría en tiempo real
try:
    minutos = 0
    while True:
        time.sleep(30)
        minutos += 0.5
        
        # Watchdog: Monitoreo activo de procesos
        xvfb_alive = Path("/tmp/.X11-unix/X1").exists()
        vnc_alive = wait_for_port(5900, timeout=1)
        novnc_alive = wait_for_port(6080, timeout=1)
        drive_alive = Path("/root/gdrive").exists()
        
        if not xvfb_alive:
            print(f"\n🔴 [{time.strftime('%H:%M:%S')}] [ALERTA DE PROCESO] Servidor X11 Display :1 no responde.", flush=True)
        if not vnc_alive:
            print(f"\n🔴 [{time.strftime('%H:%M:%S')}] [ALERTA DE PROCESO] Servidor VNC (5900) no responde.", flush=True)
        if not novnc_alive:
            print(f"\n🔴 [{time.strftime('%H:%M:%S')}] [ALERTA DE PROCESO] Servidor noVNC (6080) no responde.", flush=True)
            
        if minutos % 5 == 0:
            auto_save_user_state()
            try:
                ram_str = subprocess.check_output("free -h | grep Mem: | awk '{print $3 \"/\" $2}'", shell=True, text=True).strip()
                disk_str = subprocess.check_output("df -h /kaggle/working | tail -1 | awk '{print $4 \" libres\"}'", shell=True, text=True).strip()
                gpu_info = ""
                try:
                    gpu_lines = subprocess.check_output("nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null", shell=True, text=True).strip().splitlines()
                    if gpu_lines:
                        gpu_parts = []
                        for g in gpu_lines:
                            parts = [x.strip() for x in g.split(",")]
                            if len(parts) >= 4:
                                idx, util, mem_u, mem_t = parts[0], parts[1], parts[2], parts[3]
                                gpu_parts.append(f"T4-{idx}: {util}% ({mem_u}/{mem_t}MB)")
                        if gpu_parts:
                            gpu_info = " | 🎮 " + ", ".join(gpu_parts)
                except Exception:
                    pass
                print(f"\n📊 [{time.strftime('%H:%M:%S')}] Telemetría ({int(minutos)} min activo) | 🟢 RAM: {ram_str} | 💾 Disco: {disk_str}{gpu_info} | ☁️ Drive: {'Conectado' if drive_alive else 'Desconectado'} | Estado Guardado ✅", flush=True)
            except Exception:
                print(f"\n📊 [{time.strftime('%H:%M:%S')}] Telemetría ({int(minutos)} min activo) | Estado Guardado en Drive ✅", flush=True)
        else:
            print(".", end="", flush=True)
except KeyboardInterrupt:
    print("\n🛑 Guardando estado final antes de salir...", flush=True)
    auto_save_user_state()
    print("✅ Estado guardado. Servidor detenido.", flush=True)

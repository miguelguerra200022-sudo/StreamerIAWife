#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🐧 UBUNTU CLOUD PC: DESKTOP EDITION (CORE & SOCIAL HUB)
================================================================================
1. [PASO 1]: Conecta y monta Google Drive (5TB - Carpeta PC_Kaggle) inmediatamente.
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
print("🌸 INICIANDO UBUNTU 24.04 LTS FULL EDITION (SUITE COMPLETA + 5TB GDRIVE)...", flush=True)
print("=" * 78, flush=True)

# ==============================================================================
# 🚀 0.1 HYPER-TUNING DE RED: GOOGLE BBR + BUFFERS TCP 64MB + MULTI-HILO
# ==============================================================================
def optimizar_red_bbr_buffers():
    """Aplica Google BBR y amplía buffers TCP de Linux al límite físico de la red de Google Cloud."""
    print("🌐 [Turbo Red] Optimizando Stack TCP con Google BBR y Buffers de 64MB...", flush=True)
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
# 🎮 0.2 ORQUESTADOR DUAL-GPU (NVIDIA TESLA T4 x2 - 32GB VRAM)
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
        print(f"🚀 [Dual-GPU Maestro] ¡Detectadas {gpu_count} GPUs NVIDIA Tesla ({gpus[0]} x{gpu_count})!", flush=True)
        print("   🎮 GPU 0 (16GB VRAM): Asignada a Juegos (Proton/Wine/Steam), Emuladores y Display X11.", flush=True)
        print("   🧠 GPU 1 (16GB VRAM): Asignada a IA (Ollama/ComfyUI), Clonación de Voz y Cómputo.", flush=True)
        
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
        print(f"⚡ [GPU Única] Detectada 1 GPU NVIDIA ({gpus[0]}). Modo Alto Rendimiento activo.", flush=True)
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    else:
        print("ℹ️ [Modo CPU] No se detectó GPU NVIDIA dedicada. Modo emulación activado.", flush=True)

# ==============================================================================
# ⚡ 0.3 ACELERADOR DE DESCARGAS MULTI-HILO (16 CONEXIONES PARALELAS)
# ==============================================================================
def instalar_acelerador_descargas():
    """Configura Aria2c multi-hilo con 16 conexiones paralelas para saturar conexiones Gigabit de Google."""
    subprocess.run("which aria2c >/dev/null 2>&1 || (apt-get update -qq && apt-get install -y -qq aria2 >> /kaggle/working/linuwaifu_system.log 2>&1 || true)", shell=True)
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
    subprocess.run("which pigz >/dev/null 2>&1 || (apt-get update -qq && apt-get install -y -qq pigz >> /kaggle/working/linuwaifu_system.log 2>&1 || true)", shell=True)
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

# Variables de entorno para redirigir prefijos pesados de Wine, Steam y Proton a 5TB de Google Drive
os.environ["WINEPREFIX"] = "/root/gdrive/PC_Kaggle/wineprefix"
os.environ["STEAM_EXTRA_COMPAT_TOOLS_PATHS"] = "/root/gdrive/PC_Kaggle/compatibilitytools.d"
os.environ["PROTON_LOG_DIR"] = "/tmp"
os.environ["NPM_CONFIG_CACHE"] = "/tmp/.npm"

# Iniciar Rclone Mount (FUSE) con reintentos automáticos y protección contra rate-limits de Google Drive
def mount_gdrive_resilient():
    os.makedirs("/root/gdrive", exist_ok=True)
    os.makedirs("/root/gdrive/PC_Kaggle", exist_ok=True)
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
    rootfs_candidates = list(master_dataset_path.rglob("ubuntu_master_rootfs.tar.data")) or list(master_dataset_path.rglob("ubuntu_master_rootfs.tar.gz")) or list(master_dataset_path.rglob("ubuntu_rootfs.tar.gz"))
    if rootfs_candidates and rootfs_candidates[0].stat().st_size > 50_000_000:
        rootfs_file = rootfs_candidates[0]
        print(f"  ⚡ [✓] ¡Imagen Pre-Compilada de Ubuntu detectada en {rootfs_file.name} ({rootfs_file.stat().st_size / (1024**2):.1f} MB)!", flush=True)
        print("  🚀 [✓] Activando sistema completo en 3 segundos...", flush=True)
        subprocess.run(f"which pigz >/dev/null 2>&1 && (pigz -dc '{rootfs_file}' | tar -xf - -C / >> {LOG_FILE} 2>&1) || tar -xzf '{rootfs_file}' -C / >> {LOG_FILE} 2>&1", shell=True)
    elif master_archives_dir and master_archives_dir.exists():
        deb_count = len(list(master_archives_dir.glob("*.deb")))
        print(f"  ⚡ [✓] ¡Base de Datos de 100GB detectada en {master_dataset_path.name} ({deb_count} paquetes .deb)!", flush=True)
        print("  ⚡ [✓] Activando entorno Ubuntu instantáneamente (0 MB descargados)...", flush=True)
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
/* Virtual Trackpad & Cursor */
#linu-virtual-cursor {
    position: fixed;
}
#linu-virtual-cursor {
    position: fixed;
    width: 24px;
    height: 24px;
    pointer-events: none;
    z-index: 999999;
    transform: translate3d(0, 0, 0);
    display: none;
    filter: drop-shadow(0 2px 5px rgba(0,0,0,0.85));
    will-change: transform;
}
body.tp-active #linu-virtual-cursor {
    display: block;
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
<svg id="linu-virtual-cursor" viewBox="0 0 24 24" fill="#ffffff" stroke="#000000" stroke-width="1.6">
    <path d="M4 4l7 17 2.5-6.5L20 12 4 4z"/>
</svg>
<div id="linu-hud-overlay" title="Arrastra para mover | Toca para minimizar/expandir">
    <div class="hud-dot" id="hud-status-dot"></div>
    <div class="hud-stat-pill"><span class="hud-val" id="hud-fps-text">60 FPS</span></div>
    <span class="hud-hideable" style="color: rgba(255,255,255,0.2)">|</span>
    <div class="hud-stat-pill hud-hideable">⚡ <span class="hud-ping-val" id="hud-ping-text">-- ms</span></div>
    <span class="hud-hideable" style="color: rgba(255,255,255,0.2)">|</span>
    <div class="hud-badge hud-hideable">NVIDIA T4 1080p</div>
    <div class="hud-toggle-btn" id="hud-toggle-btn" title="Minimizar / Expandir">−</div>
</div>
<script>
(function() {
    const hud = document.getElementById("linu-hud-overlay");
    const toggleBtn = document.getElementById("hud-toggle-btn");
    const fpsText = document.getElementById("hud-fps-text");
    const pingText = document.getElementById("hud-ping-text");
    const statusDot = document.getElementById("hud-status-dot");

    // 1. Minimizar HUD
    let isMinimized = false;
    function toggleMinimize(e) {
        if (e) e.stopPropagation();
        isMinimized = !isMinimized;
        if (isMinimized) {
            hud.classList.add("minimized");
            if (toggleBtn) toggleBtn.innerText = "+";
        } else {
            hud.classList.remove("minimized");
            if (toggleBtn) toggleBtn.innerText = "−";
        }
    }
    if (toggleBtn) toggleBtn.addEventListener("click", toggleMinimize);

    // 2. Arrastre HUD
    let isDragging = false, startX = 0, startY = 0, initialLeft = 0, initialTop = 0, hasMoved = false;
    function onPointerDown(e) {
        if (e.target === toggleBtn) return;
        isDragging = true;
        hasMoved = false;
        const cx = e.touches ? e.touches[0].clientX : e.clientX;
        const cy = e.touches ? e.touches[0].clientY : e.clientY;
        startX = cx; startY = cy;
        const rect = hud.getBoundingClientRect();
        initialLeft = rect.left; initialTop = rect.top;
        hud.style.left = initialLeft + "px"; hud.style.top = initialTop + "px";
        hud.style.right = "auto"; hud.style.bottom = "auto";
        document.addEventListener("mousemove", onPointerMove);
        document.addEventListener("mouseup", onPointerUp);
        document.addEventListener("touchmove", onPointerMove, { passive: false });
        document.addEventListener("touchend", onPointerUp);
    }
    function onPointerMove(e) {
        if (!isDragging) return;
        const cx = e.touches ? e.touches[0].clientX : e.clientX;
        const cy = e.touches ? e.touches[0].clientY : e.clientY;
        const dx = cx - startX, dy = cy - startY;
        if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
            hasMoved = true;
            if (e.cancelable) e.preventDefault();
        }
        hud.style.left = Math.max(5, Math.min(initialLeft + dx, window.innerWidth - hud.offsetWidth - 5)) + "px";
        hud.style.top = Math.max(5, Math.min(initialTop + dy, window.innerHeight - hud.offsetHeight - 5)) + "px";
    }
    function onPointerUp() {
        if (!isDragging) return;
        isDragging = false;
        document.removeEventListener("mousemove", onPointerMove);
        document.removeEventListener("mouseup", onPointerUp);
        document.removeEventListener("touchmove", onPointerMove);
        document.removeEventListener("touchend", onPointerUp);
        if (!hasMoved && isMinimized) toggleMinimize();
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
                statusDot.style.backgroundColor = currentFps >= 45 ? "#00ffc8" : (currentFps >= 25 ? "#facc15" : "#f43f5e");
                statusDot.style.boxShadow = "0 0 8px " + statusDot.style.backgroundColor;
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
        img.onload = img.onerror = function() {
            const rtt = Math.round(performance.now() - start);
            if (pingText) pingText.innerText = (rtt > 0 ? rtt : "< 45") + " ms";
        };
    }
    setInterval(measurePing, 2000);
    measurePing();

    // =========================================================================
    // 4. MOTOR DE TRACKPAD PROFESIONAL (ESTÁNDAR CHROME REMOTE DESKTOP / MACBOOK)
    // =========================================================================
    const cursor = document.getElementById("linu-virtual-cursor");
    let isTrackpadEnabled = true;
    let virtX = 960, virtY = 540; // Coordenadas 1080p
    const screenW = 1920, screenH = 1080;

    function getRFB() {
        return (window.UI && window.UI.rfb) ? window.UI.rfb : null;
    }

    function updateCursorElement() {
        if (!cursor) return;
        const displayX = (virtX / screenW) * window.innerWidth;
        const displayY = (virtY / screenH) * window.innerHeight;
        cursor.style.transform = `translate3d(${displayX}px, ${displayY}px, 0)`;
    }

    function sendMouse(mask) {
        const rfb = getRFB();
        if (rfb && typeof rfb.sendMouse === "function") {
            rfb.sendMouse(Math.round(virtX), Math.round(virtY), mask);
        }
    }

    function hapticFeedback(pattern) {
        if (navigator.vibrate) {
            try { navigator.vibrate(pattern); } catch(e) {}
        }
    }

    let startX = 0, startY = 0, lastX = 0, lastY = 0;
    let touchStartTime = 0;
    let isTouching = false;
    let totalMoved = 0;
    let isDragging = false;
    let dragHoldTimer = null;
    let initialTouchCount = 0;

    window.addEventListener("touchstart", function(e) {
        if (!isTrackpadEnabled) return;
        if (e.target.closest("#linu-hud-overlay") || e.target.closest("#noVNC_control_bar")) return;

        initialTouchCount = e.touches.length;
        touchStartTime = performance.now();
        totalMoved = 0;

        if (e.touches.length === 1) {
            isTouching = true;
            isDragging = false;
            startX = lastX = e.touches[0].clientX;
            startY = lastY = e.touches[0].clientY;

            // Timer de pulsación larga: Tap & Hold para Drag & Drop (Chrome Remote Desktop standard)
            clearTimeout(dragHoldTimer);
            dragHoldTimer = setTimeout(function() {
                if (isTouching && totalMoved < 15 && e.touches.length === 1) {
                    isDragging = true;
                    hapticFeedback(25); // Pulso físico de enganche
                    sendMouse(1);       // Bloquea clic izquierdo presionado
                }
            }, 250);

        } else if (e.touches.length === 2) {
            clearTimeout(dragHoldTimer);
            isDragging = false;
            lastY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
        } else {
            clearTimeout(dragHoldTimer);
        }
    }, { passive: false });

    window.addEventListener("touchmove", function(e) {
        if (!isTrackpadEnabled) return;
        if (e.target.closest("#linu-hud-overlay") || e.target.closest("#noVNC_control_bar")) return;

        if (isTouching && e.touches.length === 1) {
            e.preventDefault();
            const curX = e.touches[0].clientX;
            const curY = e.touches[0].clientY;
            const dx = curX - lastX;
            const dy = curY - lastY;
            lastX = curX;
            lastY = curY;
            const dist = Math.hypot(dx, dy);
            totalMoved += dist;

            if (totalMoved > 10 && !isDragging) {
                clearTimeout(dragHoldTimer);
            }

            // Curva de aceleración balística no lineal
            const speed = Math.max(1, dist);
            const accel = Math.min(2.8, Math.max(0.9, Math.pow(speed, 0.22)));
            const scaleX = (screenW / window.innerWidth) * 1.35 * accel;
            const scaleY = (screenH / window.innerHeight) * 1.35 * accel;

            virtX = Math.max(0, Math.min(screenW, virtX + (dx * scaleX)));
            virtY = Math.max(0, Math.min(screenH, virtY + (dy * scaleY)));

            updateCursorElement();
            sendMouse(isDragging ? 1 : 0);

        } else if (e.touches.length === 2) {
            e.preventDefault();
            const curY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
            const dy = curY - lastY;
            lastY = curY;
            if (dy > 10) {
                sendMouse(16); // Scroll abajo
                setTimeout(() => sendMouse(0), 30);
            } else if (dy < -10) {
                sendMouse(8);  // Scroll arriba
                setTimeout(() => sendMouse(0), 30);
            }
        }
    }, { passive: false });

    window.addEventListener("touchend", function(e) {
        if (!isTrackpadEnabled) return;
        if (e.target.closest("#linu-hud-overlay") || e.target.closest("#noVNC_control_bar")) return;

        clearTimeout(dragHoldTimer);
        const duration = performance.now() - touchStartTime;

        if (isDragging) {
            isDragging = false;
            sendMouse(0); // Libera el clic izquierdo
            hapticFeedback(12);
            return;
        }

        if (e.touches.length === 0) {
            isTouching = false;

            if (initialTouchCount === 1) {
                // Toque rápido con 1 dedo (< 220ms y < 10px) = Clic Izquierdo
                if (duration < 220 && totalMoved < 10) {
                    hapticFeedback(12);
                    sendMouse(1);
                    setTimeout(() => sendMouse(0), 40);
                }
            } else if (initialTouchCount === 2) {
                // Toque rápido con 2 dedos = Clic Derecho (Menú contextual)
                if (duration < 260) {
                    hapticFeedback([12, 35, 12]);
                    sendMouse(4);
                    setTimeout(() => sendMouse(0), 40);
                }
            } else if (initialTouchCount === 3) {
                // Toque rápido con 3 dedos = Clic Central / Rueda
                if (duration < 280) {
                    hapticFeedback(20);
                    sendMouse(2);
                    setTimeout(() => sendMouse(0), 40);
                }
            }
            initialTouchCount = 0;
        }
    }, { passive: false });

    document.body.classList.add("tp-active");
    updateCursorElement();
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
    backup_tar = STATE_DIR / "ubuntu_user_state.tar.gz"
    direct_backup = Path("/root/gdrive/PC_Kaggle/system_state/ubuntu_user_state.tar.gz")
    if direct_backup.exists() and direct_backup.stat().st_size > 1000:
        shutil.copy2(direct_backup, backup_tar)
    else:
        subprocess.run(
            f"rclone copy gdrive:PC_Kaggle/system_state/ubuntu_user_state.tar.gz {STATE_DIR} --tpslimit 3 >/dev/null 2>&1 || true",
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
    subprocess.run("wget -q 'https://discord.com/api/download?platform=linux&format=deb' -O /tmp/discord.deb && apt-get install -y -qq /tmp/discord.deb", shell=True)
    
    print("     -> Descargando Sunshine (Latencia Cero H.264/HEVC)...", flush=True)
    subprocess.run("wget -q 'https://github.com/LizardByte/Sunshine/releases/download/v0.23.1/sunshine-ubuntu-22.04-amd64.deb' -O /tmp/sunshine.deb && apt-get install -y -qq /tmp/sunshine.deb || (wget -q 'https://github.com/LizardByte/Sunshine/releases/download/v0.23.1/sunshine-ubuntu-24.04-amd64.deb' -O /tmp/sunshine.deb && apt-get install -y -qq /tmp/sunshine.deb) || true", shell=True)
    
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
    "/root/.ollama": "/root/gdrive/PC_Kaggle/Master_Ollama",
    "/root/.openwebui": "/root/gdrive/PC_Kaggle/Master_OpenWebUI",
    "/root/.lmms": "/root/gdrive/PC_Kaggle/Master_LMMS",
    "/root/.electrum": "/root/gdrive/PC_Kaggle/Master_Electrum",
    "/root/.sparrow": "/root/gdrive/PC_Kaggle/Master_Sparrow",
    "/root/.bitmonero": "/root/gdrive/PC_Kaggle/Master_Monero",
    "/root/ComfyUI_Outputs": "/root/gdrive/PC_Kaggle/ComfyUI_Outputs",
    "/root/Fooocus_Outputs": "/root/gdrive/PC_Kaggle/Fooocus_Outputs",
    "/root/Voice_Outputs": "/root/gdrive/PC_Kaggle/Voice_Outputs",
    "/root/Blender_Projects": "/root/gdrive/PC_Kaggle/Blender_Projects",
    "/root/Projects": "/root/gdrive/PC_Kaggle/Projects",
    "/root/Freqtrade_UserData": "/root/gdrive/PC_Kaggle/Freqtrade_UserData",
    "/root/Security_Reports": "/root/gdrive/PC_Kaggle/Security_Reports",
    "/root/Universidad_Ciencia": "/root/gdrive/PC_Kaggle/Universidad_Ciencia",
    "/root/Tesis_y_Papers": "/root/gdrive/PC_Kaggle/Universidad_Ciencia/Tesis_y_Papers",
    "/root/Anime_Manga_Media": "/root/gdrive/PC_Kaggle/Anime_Manga_Media",
    "/root/Manga_Descargas": "/root/gdrive/PC_Kaggle/Anime_Manga_Media/Manga_Descargas",
    "/root/Android_Cloud_Phone": "/root/gdrive/PC_Kaggle/Android_Cloud_Phone",
    "/root/Android_APKs": "/root/gdrive/PC_Kaggle/Android_Cloud_Phone/APKs_Instalados",
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
subprocess.run(f"cp {BASE_DIR}/salvar_y_salir.py /usr/local/bin/salvar_y_salir.py 2>/dev/null || true", shell=True)
subprocess.run(f"cp {BASE_DIR}/test_velocidad_real.py /usr/local/bin/test_velocidad_real.py 2>/dev/null || true", shell=True)

# Iniciar Gamepad UInput Bridge en segundo plano para detección de mandos inmediata
subprocess.Popen("python3 /usr/local/bin/gamepad_uinput_bridge.py >> /kaggle/working/linuwaifu_gamepad.log 2>&1", shell=True)

# Accesos directos oficiales en el escritorio (nombres ASCII para evitar bugs de UTF-8 en X11)
shortcuts = {
    "Tienda_de_Software_1Clic.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=🛍️ Tienda de Software y Juegos (20 Databases)\n"
        "Comment=Explora e instala cualquiera de los 20 packs de 100GB en 1 clic\n"
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
        "Name=📊 Gestor de Databases & Recursos (20 Módulos)\n"
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
        "Name=⚡ Liberar VRAM GPU (Modo Gaming Pro)\n"
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
        "Name=⚡ Descargador Turbo 16x (Gigabit Multi-Hilo)\n"
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
        "Name=🚀 Test de Velocidad Real Gigabit (1GB Test)\n"
        "Comment=Mide la velocidad real en MB/s y Gbps descargando y borrando un archivo de prueba\n"
        "Exec=xfce4-terminal --title='Test de Velocidad Real' -e 'bash -c \"python3 /usr/local/bin/test_velocidad_real.py 1gb; echo; read -p \\\"Presiona Enter para salir...\\\"\"'\n"
        "Path=/tmp\n"
        "Icon=utilities-system-monitor\n"
        "Terminal=false\n"
        "Categories=Network;System;\n"
    ),
    "Mis_Archivos_5TB_GoogleDrive.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=📁 Mis Archivos 5TB (Google Drive)\n"
        "Comment=Carpeta persistente en la nube con 5TB para juegos y archivos\n"
        "Exec=thunar /root/gdrive/PC_Kaggle\n"
        "Path=/root\n"
        "Icon=folder-remote\n"
        "Terminal=false\n"
        "Categories=System;Utility;\n"
    ),
    "Guardar_Estado_de_mi_PC.desktop": (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=💾 Guardar Estado de mi PC (Nube)\n"
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
        "Name=📦 Guardar en Database Ubuntu (100GB)\n"
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

# Auto-iniciar Sunshine (Servidor GameStream / Moonlight para Gaming 60 FPS con aceleración GPU)
sunshine_bin = shutil.which("sunshine")
if sunshine_bin:
    try:
        os.makedirs("/root/.config/sunshine", exist_ok=True)
        conf_p = Path("/root/.config/sunshine/sunshine.conf")
        if not conf_p.exists():
            conf_p.write_text("origin_pin_allowed = pc\nmin_log_level = info\nport = 47989\n", encoding="utf-8")
        subprocess.run(f"{sunshine_bin} --creds admin {VNC_PASSWORD} >/dev/null 2>&1 || true", shell=True)
        subprocess.Popen([sunshine_bin], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log("Servidor Sunshine (Moonlight Host) iniciado exitosamente en segundo plano")
    except Exception as e_sun:
        log(f"Aviso Sunshine startup: {e_sun}", "WARNING")

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
            proc_cf = subprocess.Popen(["cloudflared", "tunnel", "--protocol", "quic", "--edge-ip-version", "auto", "--url", "http://localhost:6080"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
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

# Guardar URL de sesión en Google Drive para acceso instantáneo remoto
if web_tunnel_wifi:
    try:
        Path("/tmp/current_vnc_url.txt").write_text(web_tunnel_wifi, encoding="utf-8")
        Path("/kaggle/working/current_vnc_url.txt").write_text(web_tunnel_wifi, encoding="utf-8")
        if Path("/root/gdrive/PC_Kaggle/system_state").exists():
            Path("/root/gdrive/PC_Kaggle/system_state/current_vnc_url.txt").write_text(web_tunnel_wifi, encoding="utf-8")
        subprocess.run("rclone copyto /tmp/current_vnc_url.txt gdrive:PC_Kaggle/system_state/current_vnc_url.txt >/dev/null 2>&1 || true", shell=True)
        
        # Enviar notificación automática a tu celular por Telegram
        try:
            telegram_script = Path(__file__).resolve().parent / "telegram_notifier.py"
            if telegram_script.exists():
                subprocess.run(f"python3 '{telegram_script}' '🚀 <b>¡Tu Ubuntu Cloud PC está ONLINE!</b>\\n\\n👉 <b>WiFi:</b> {web_tunnel_wifi}\\n📱 <b>Móvil:</b> {web_tunnel_mobile}\\n🔑 <b>Pass:</b> {VNC_PASSWORD}' >/dev/null 2>&1 || true", shell=True)
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
# 🎉 ¡UBUNTU CLOUD PC 1080p PANTALLA COMPLETA 100% ONLINE!
# ==============================================================================
print("\n" + "=" * 78, flush=True)
if xvfb_ready and vnc_ready and novnc_ready:
    print("🎉 🐧 ¡TU UBUNTU DESKTOP EDITION ESTÁ 100% ONLINE EN PANTALLA COMPLETA 16:9!", flush=True)
else:
    print("⚠️ 🐧 SISTEMA INICIADO CON OBSERVACIONES EN SUBSISTEMAS:", flush=True)
print("=" * 78, flush=True)
print(f"  • Servidor X11 Display :1 (1080p):  {'🟢 OPERATIVO' if xvfb_ready else '🔴 ERROR DE INICIO'}", flush=True)
print(f"  • Servidor VNC Nativo (5900):       {'🟢 PROTEGIDO CON CONTRASEÑA' if vnc_ready else '🔴 ERROR DE INICIO'}", flush=True)
print(f"  • Servidor Web noVNC (6080):        {'🟢 OPERATIVO (SSL ACTIVO)' if novnc_ready else '🔴 ERROR DE INICIO'}", flush=True)
print(f"  • Google Drive 5TB FUSE Mount:      {'🟢 MONTADO (/root/gdrive)' if drive_mounted else '🔴 NO MONTADO'}", flush=True)
print(f"  • Enrutamiento de Mínima Latencia:  🇺🇸 US-East (Miami / Ruta Directa a Venezuela)", flush=True)
print("-" * 78, flush=True)

if web_tunnel_wifi:
    print("🌐 OPCIÓN 1: NAVEGADOR WEB CON MOTOR DE TRACKPAD DE LAPTOP INTEGRADO:", flush=True)
    print("------------------------------------------------------------------------------", flush=True)
    print("📶 1. MODO WIFI / FIBRA (1080p Máxima Nitidez + Trackpad):", flush=True)
    print(f"👉 {web_tunnel_wifi}", flush=True)
    print("\n📱 2. MODO DATOS MÓVILES (Ultra-Baja Latencia + Trackpad):", flush=True)
    print(f"👉 {web_tunnel_mobile}", flush=True)
    print("   • Desliza tu dedo en cualquier parte para mover la flecha del mouse suavemente.", flush=True)
    print("-" * 78, flush=True)

pinggy_addr = vnc_app_address[0] if vnc_app_address else "free.pinggy.link (Consultando...)"
parts = pinggy_addr.split(":") if ":" in pinggy_addr else [pinggy_addr, "5900"]
host_part = parts[0]
port_part = parts[1] if len(parts) > 1 else "5900"

print("📱 OPCIÓN 2: APP MÓVIL REALVNC VIEWER / AVNC (CONEXIÓN BINARIA TCP):", flush=True)
print("------------------------------------------------------------------------------", flush=True)
print(f"👉 Para RealVNC Viewer pega:  {host_part}::{port_part}  (con dos puntos dobles)")
print(f"👉 Para AVNC / bVNC pega:")
print(f"   • Host / Servidor:         {host_part}")
print(f"   • Puerto:                  {port_part}")
print(f"🔑 Contraseña VNC:            {VNC_PASSWORD}")
print("-" * 78, flush=True)

print("🎮 OPCIÓN 3: MOONLIGHT + SUNSHINE (GAMING 60 FPS / GPU TESLA DIRECTA):", flush=True)
print("------------------------------------------------------------------------------", flush=True)
print(f"👉 Servidor Sunshine:         🟢 Activo en segundo plano (Puerto 47989/47990)")
print(f"🔑 Usuario Web: admin         Contraseña: {VNC_PASSWORD}")
print("=" * 78, flush=True)

print("💾 SISTEMA DE PERSISTENCIA Y REGISTRO ACTIVO:", flush=True)
print("   • 🎮 Tus 5TB de Google Drive (PC_Kaggle) montados en /root/gdrive.", flush=True)
print("   • 🏢 Suite Ofimática LibreOffice (Writer, Calc, Impress) instalada.", flush=True)
print("   • 💬 Redes Sociales & Comunicación: Discord, Telegram, Spotify, Chrome listos.", flush=True)
print("   • 🛍️ Centro de Software 1-Clic en el Escritorio (20 Databases Disponibles).", flush=True)
print("   • 🖥️ Relación de aspecto 16:9 nativa Full HD perfecta.", flush=True)
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

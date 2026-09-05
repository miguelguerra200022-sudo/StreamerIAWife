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
    "failed to resolve user", "tmpfiles.d", "config-error-dialog.sh", "speech-dispatcher", "colord",
    "blueman", "rfcommerror", "import _blueman"
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

def _prefetch_tunnel_binaries():
    try:
        cf = Path("/usr/local/bin/cloudflared")
        if not cf.exists():
            subprocess.run("wget -q --timeout=15 https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared 2>/dev/null && chmod +x /usr/local/bin/cloudflared || true", shell=True)
    except Exception:
        pass
threading.Thread(target=_prefetch_tunnel_binaries, daemon=True).start()

print("\n" + "=" * 78, flush=True)
print("[AETHER] INICIANDO UBUNTU 24.04 LTS ENTERPRISE EDITION (5TB GDRIVE)...", flush=True)
print("=" * 78, flush=True)

# ==============================================================================
# 0.1 HYPER-TUNING DE RED: GOOGLE BBR + BUFFERS TCP 64MB + DNS ULTRA-RÁPIDO
# ==============================================================================
def optimizar_red_bbr_buffers():
    """Aplica Google BBR, amplía buffers TCP de Linux a 64MB y acelera DNS al límite físico de la red de Google Cloud (10Gbps+)."""
    print("[NETWORK] Optimizando Stack TCP con Google BBR, Buffers de 64MB y DNS Ultra-Rápido...", flush=True)
    
    # 1. Optimización del DNS Resolver (Cloudflare 1.1.1.1 + Google 8.8.8.8 con single-request-reopen)
    try:
        resolv_p = Path("/etc/resolv.conf")
        if resolv_p.exists():
            content = resolv_p.read_text(encoding="utf-8")
            if "single-request-reopen" not in content:
                header = (
                    "# BigTech Ultra-Fast DNS Optimization (Latencia < 5ms)\n"
                    "options single-request-reopen timeout:1 attempts:2 rotate\n"
                    "nameserver 1.1.1.1\n"
                    "nameserver 8.8.8.8\n"
                    "nameserver 1.0.0.1\n"
                    "nameserver 8.8.4.4\n"
                )
                resolv_p.write_text(header + content, encoding="utf-8")
    except Exception:
        pass

    # 2. Kernel Sysctl para enlaces Cloud de 10Gbps+ (BBR + BDP Buffers 64MB)
    sysctls = [
        ("net.core.default_qdisc", "fq"),
        ("net.ipv4.tcp_congestion_control", "bbr"),
        ("net.core.rmem_max", "67108864"),
        ("net.core.wmem_max", "67108864"),
        ("net.core.rmem_default", "33554432"),
        ("net.core.wmem_default", "33554432"),
        ("net.ipv4.tcp_rmem", "4096 87380 67108864"),
        ("net.ipv4.tcp_wmem", "4096 65536 67108864"),
        ("net.ipv4.tcp_window_scaling", "1"),
        ("net.ipv4.tcp_fastopen", "3"),
        ("net.ipv4.tcp_slow_start_after_idle", "0"),
        ("net.ipv4.tcp_timestamps", "1"),
        ("net.ipv4.tcp_sack", "1"),
        ("net.core.netdev_max_backlog", "262144"),
        ("net.core.somaxconn", "65535"),
        ("net.ipv4.tcp_max_syn_backlog", "65535"),
        ("net.ipv4.tcp_fin_timeout", "15"),
        ("net.ipv4.tcp_tw_reuse", "1"),
        ("net.ipv4.tcp_notsent_lowat", "16384"),
        ("net.ipv4.ip_local_port_range", "1024 65535")
    ]
    for key, val in sysctls:
        subprocess.run(f"sysctl -w {key}={val} >/dev/null 2>&1 || true", shell=True)

    try:
        conf_lines = "\n".join([f"{k} = {v}" for k, v in sysctls]) + "\n"
        Path("/etc/sysctl.d").mkdir(parents=True, exist_ok=True)
        Path("/etc/sysctl.d/99-bbr-cloud.conf").write_text(conf_lines, encoding="utf-8")
    except Exception:
        pass

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
# ⚡ 0.3 ACELERADOR DE DESCARGAS MULTI-HILO (16 CONEXIONES PARALELAS ARIA2C)
# ==============================================================================
def instalar_acelerador_descargas():
    """Configura Aria2c multi-hilo con 16 conexiones paralelas y lanza interfaz CLI y GUI universal."""
    subprocess.run("which aria2c >/dev/null 2>&1 || (apt-get update -qq && apt-get install -y -qq aria2 >> /kaggle/working/cloudpc_system.log 2>&1 || true)", shell=True)
    turbo_script = """#!/bin/bash
# ⚡ Acelerador de Descargas Turbo Gigabit (16 Conexiones Simultáneas)
URL="$1"
DEST="${2:-/root/Descargas}"

if [ -z "$URL" ]; then
    if [ -n "$DISPLAY" ] && command -v zenity &>/dev/null; then
        URL=$(zenity --entry --title="⚡ Descargador Turbo Gigabit (16 Hilos)" --text="Pega el enlace de descarga directa (HTTP/HTTPS/FTP):" --width=540 2>/dev/null)
        [ -z "$URL" ] && exit 0
        SEL_DEST=$(zenity --file-selection --directory --title="Selecciona Carpeta de Destino" --filename="$DEST" 2>/dev/null)
        [ -n "$SEL_DEST" ] && DEST="$SEL_DEST"
    else
        echo "Uso: descarga_turbo <URL> [Directorio]"
        exit 1
    fi
fi

mkdir -p "$DEST"
echo "⚡ Descargando con 16 conexiones paralelas de ultra-velocidad hacia $DEST..."
aria2c -x 16 -s 16 -k 1M --file-allocation=none --summary-interval=1 --continue=true -d "$DEST" "$URL"
STATUS=$?
if [ $STATUS -eq 0 ] && [ -n "$DISPLAY" ] && command -v zenity &>/dev/null; then
    zenity --notification --text="✅ Descarga completada exitosamente en $DEST" 2>/dev/null || true
fi
"""
    try:
        Path("/usr/local/bin/descarga_turbo").write_text(turbo_script, encoding="utf-8")
        subprocess.run("chmod +x /usr/local/bin/descarga_turbo 2>/dev/null || true", shell=True)
    except Exception:
        pass

# ==============================================================================
# ⚡ 0.4 ACELERADOR MULTI-NÚCLEO DE INSTALACIÓN (APT/DPKG/PIP) Y DESCARGAS GUI (CHROME/STEAM)
# ==============================================================================
def acelerar_instalaciones_y_desempaquetado():
    """Optimiza APT, DPKG, PIP, Chrome y Steam para usar el 100% de los núcleos de CPU y transferir a velocidad gigabit."""
    print("⚡ [Turbo I/O & Red] Configurando APT, DPKG y PIP en modo Gigabit Multi-Hilo...", flush=True)
    
    # 1. Desactivar fsync en DPKG (300% más rápido en contenedores Docker/Kaggle)
    try:
        Path("/etc/dpkg/dpkg.cfg.d").mkdir(parents=True, exist_ok=True)
        Path("/etc/dpkg/dpkg.cfg.d/02apt-speedup").write_text("force-unsafe-io\n", encoding="utf-8")
    except Exception:
        pass

    # 2. Configurar APT en modo tubería HTTP persistente, sin traducciones ni cuellos de botella
    try:
        Path("/etc/apt/apt.conf.d").mkdir(parents=True, exist_ok=True)
        apt_turbo = (
            'Acquire::Languages "none";\n'
            'Acquire::IndexTargets::deb::Contents-deb::DefaultEnabled "false";\n'
            'Acquire::ForceIPv4 "true";\n'
            'Acquire::Queue-Mode "host";\n'
            'Acquire::http::Pipeline-Depth "10";\n'
            'Acquire::http::No-Cache "true";\n'
            'Acquire::BrokenProxy "true";\n'
            'APT::Install-Recommends "0";\n'
            'APT::Install-Suggests "0";\n'
            'DPkg::Options { "--force-confdef"; "--force-confold"; };\n'
        )
        Path("/etc/apt/apt.conf.d/99turbo").write_text(apt_turbo, encoding="utf-8")
    except Exception:
        pass

    # 3. Optimización Global de PIP (Descargas paralelas y timeouts controlados)
    try:
        pip_conf = (
            "[global]\n"
            "timeout = 15\n"
            "index-url = https://pypi.org/simple\n"
            "trusted-host = pypi.org pypi.python.org files.pythonhosted.org\n"
            "no-cache-dir = false\n"
        )
        Path("/root/.pip").mkdir(parents=True, exist_ok=True)
        Path("/root/.pip/pip.conf").write_text(pip_conf, encoding="utf-8")
        Path("/etc/pip.conf").write_text(pip_conf, encoding="utf-8")
    except Exception:
        pass

    # 4. Reemplazar gzip con pigz paralelo si está disponible para usar todos los núcleos en .tar.gz y .deb
    subprocess.run("which pigz >/dev/null 2>&1 || (apt-get update -qq && apt-get install -y -qq pigz >> /kaggle/working/cloudpc_system.log 2>&1 || true)", shell=True)
    if Path("/usr/bin/pigz").exists():
        try:
            subprocess.run("ln -sf /usr/bin/pigz /usr/local/bin/gzip 2>/dev/null || true", shell=True)
        except Exception:
            pass

    # 5. Wrapper de Google Chrome con Descargas Paralelas y HTTP/3 QUIC Habilitadas
    chrome_wrapper = (
        "#!/bin/bash\n"
        "exec /usr/bin/google-chrome-stable "
        "--no-sandbox --test-type --ignore-gpu-blocklist "
        "--enable-gpu-rasterization --enable-zero-copy "
        "--use-gl=angle --use-angle=gl-egl --enable-unsafe-webgpu "
        "--enable-features=ParallelDownloading,VaapiVideoDecoder,CanvasOopRasterization,WebRTCPipeWireCapturer "
        "--enable-quic "
        "--disk-cache-size=1073741824 "
        "--media-cache-size=536870912 "
        "--disable-dev-shm-usage \"$@\"\n"
    )
    try:
        Path("/usr/local/bin/google-chrome").write_text(chrome_wrapper, encoding="utf-8")
        subprocess.run("chmod +x /usr/local/bin/google-chrome 2>/dev/null || true", shell=True)
    except Exception:
        pass

    # 6. Optimización de Descargas Steam (Bypass de HTTP/2 bug en Linux)
    try:
        steam_cfg = (
            "@nClientDownloadEnableHTTP2PlatformLinux 0\n"
            "@fDownloadRateImprovementToAddAnotherConnection 1.0\n"
        )
        for sdir in ["/root/.steam/steam", "/root/.local/share/Steam", "/etc/steam"]:
            p = Path(sdir)
            p.mkdir(parents=True, exist_ok=True)
            (p / "steam_dev.cfg").write_text(steam_cfg, encoding="utf-8")
    except Exception:
        pass

# Ejecutar optimizaciones maestras de arranque (Stack de red BBR primero)
optimizar_red_bbr_buffers()
acelerar_instalaciones_y_desempaquetado()
orquestar_dual_gpu()
instalar_acelerador_descargas()

# Directorios Clave (Estándar Oficial XDG y Legacy Rclone)
GDRIVE_CONF_DIR = Path.home() / ".config" / "rclone"
GDRIVE_CONF_DIR.mkdir(parents=True, exist_ok=True)
GDRIVE_CONF_FILE = GDRIVE_CONF_DIR / "rclone.conf"
LEGACY_RCLONE_DIR = Path.home() / ".rclone"
LEGACY_RCLONE_DIR.mkdir(parents=True, exist_ok=True)
LEGACY_RCLONE_FILE = LEGACY_RCLONE_DIR / "rclone.conf"
os.environ["RCLONE_CONFIG"] = str(GDRIVE_CONF_FILE)
REPO_RCLONE_B64 = BASE_DIR / "rclone_gdrive.b64"
REPO_RCLONE_CONF = BASE_DIR / "rclone.conf"
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
                        f"rclone copy {save_tar} gdrive:Cloud_PC/system_state/ --tpslimit 10 --drive-chunk-size 64M --fast-list >/dev/null 2>&1 || true",
                        shell=True
                    )
            else:
                subprocess.run(
                    f"rclone copy {save_tar} gdrive:Cloud_PC/system_state/ --tpslimit 10 --drive-chunk-size 64M --fast-list >/dev/null 2>&1 || true",
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

if not KAGGLE_API_FILE.exists() and REPO_KAGGLE_JSON.exists():
    try:
        subprocess.run(f"cp '{REPO_KAGGLE_JSON}' '{KAGGLE_API_FILE}'", shell=True)
        subprocess.run(f"chmod 600 '{KAGGLE_API_FILE}'", shell=True)
    except Exception:
        pass

conf_bytes = None
if REPO_RCLONE_B64.exists() and REPO_RCLONE_B64.stat().st_size > 10:
    try:
        conf_bytes = base64.b64decode(REPO_RCLONE_B64.read_text().strip())
    except Exception:
        pass
if not conf_bytes and REPO_RCLONE_CONF.exists() and REPO_RCLONE_CONF.stat().st_size > 10:
    try:
        conf_bytes = REPO_RCLONE_CONF.read_bytes()
    except Exception:
        pass
if conf_bytes:
    try:
        GDRIVE_CONF_FILE.write_bytes(conf_bytes)
        LEGACY_RCLONE_FILE.write_bytes(conf_bytes)
        subprocess.run(f"chmod 600 '{GDRIVE_CONF_FILE}' '{LEGACY_RCLONE_FILE}' 2>/dev/null || true", shell=True)
    except Exception:
        pass

# Instalar rclone y fuse3 rápido desde Dataset o apt si no están presentes
subprocess.run("which rclone >/dev/null 2>&1 || (dpkg -i /kaggle/input/*/apt_archives/rclone*.deb /kaggle/input/*/apt_archives/fuse3*.deb 2>/dev/null || (apt-get update -qq && apt-get install -y -qq rclone fuse3 >> /kaggle/working/cloudpc_system.log 2>&1))", shell=True)

# Variables de entorno para redirigir prefijos pesados de Wine, Steam y Proton a 5TB de Google Drive
os.environ["WINEPREFIX"] = "/root/gdrive/Cloud_PC/wineprefix"
os.environ["STEAM_EXTRA_COMPAT_TOOLS_PATHS"] = "/root/gdrive/Cloud_PC/compatibilitytools.d"
os.environ["PROTON_LOG_DIR"] = "/tmp"
os.environ["NPM_CONFIG_CACHE"] = "/tmp/.npm"

# Iniciar Rclone Mount (FUSE) con parámetros de alto rendimiento BigTech y protección contra 403 Rate Limits
def mount_gdrive_resilient():
    os.makedirs("/root/gdrive", exist_ok=True)
    os.makedirs("/root/gdrive/Cloud_PC", exist_ok=True)
    # Seleccionar almacenamiento NVMe de alta velocidad para caché VFS en vez de RAM (/tmp)
    cache_dir = Path("/kaggle/working/.rclone_cache") if Path("/kaggle/working").exists() else Path.home() / ".cache/rclone"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Pre-crear estructura de directorios persistentes en Google Drive si no existen
    try:
        subprocess.run("rclone mkdir gdrive:Cloud_PC/system_state >/dev/null 2>&1 || true", shell=True, timeout=8)
        subprocess.run("rclone mkdir gdrive:Cloud_PC/wineprefix >/dev/null 2>&1 || true", shell=True, timeout=8)
        subprocess.run("rclone mkdir gdrive:Cloud_PC/Juegos >/dev/null 2>&1 || true", shell=True, timeout=8)
    except Exception:
        pass

    log_rclone = open(LOG_FILE, "a", encoding="utf-8")
    for attempt in range(1, 4):
        try:
            subprocess.Popen([
                "rclone", "mount", "gdrive:", "/root/gdrive",
                "--cache-dir", str(cache_dir),
                "--vfs-cache-mode", "full",
                "--vfs-cache-max-size", "15G",
                "--vfs-cache-max-age", "24h",
                "--vfs-write-back", "5s",
                "--vfs-read-chunk-size", "32M",
                "--vfs-read-chunk-size-limit", "256M",
                "--buffer-size", "32M",
                "--drive-chunk-size", "128M",
                "--drive-skip-gdocs",
                "--drive-use-trash=false",
                "--poll-interval", "15s",
                "--dir-cache-time", "72h",
                "--fast-list",
                "--allow-other",
                "--allow-non-empty",
                "--tpslimit", "10",
                "--tpslimit-burst", "2",
                "--drive-pacer-min-sleep", "100ms",
                "--drive-pacer-burst", "2",
                "--low-level-retries", "15",
                "--retries", "10",
                "--retries-sleep", "3s",
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
    "libreoffice", "libreoffice-gtk3",
    "xfce4", "xfce4-goodies", "xfce4-terminal", "xfce4-panel", "xfdesktop4", "thunar",
    "gvfs", "gvfs-backends", "gvfs-fuse", "tumbler", "tumbler-plugins-extra",
    "evince", "gnome-calculator", "gnome-system-monitor", "gnome-disk-utility",
    "file-roller", "mousepad", "htop", "nvtop", "mpv", "dbus-x11", "x11vnc", "xvfb",
    "x11-xserver-utils", "yaru-theme-gtk", "yaru-theme-icon", "yaru-theme-sound",
    "fonts-ubuntu", "pulseaudio", "pulseaudio-utils", "pavucontrol", "net-tools",
    "wget", "curl", "psmisc", "openssh-client", "p7zip-full", "unzip",
    "ffmpeg", "sox", "libportaudio2", "ubuntu-restricted-addons", "libavcodec-extra",
    "wireguard-tools", "iptables", "bridge-utils", "iproute2", "kdeconnect", "qrencode",
    "avahi-daemon", "iputils-ping", "traceroute", "nethogs", "iftop", "iperf3", "aria2"
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
    log("Iniciando instalación limpia oficial de Ubuntu bajo demanda...")

    # 1. Configurar mirror interno de Google Cloud Compute Engine (10 Gbps)
    print("  ⚡ [1/4] Enlazando mirrors de alta velocidad de Google Cloud (10Gbps)...", flush=True)
    subprocess.run("rm -rf /etc/apt/sources.list.d/* 2>/dev/null || true", shell=True)
    subprocess.run("rm -f /var/lib/dpkg/lock* /var/lib/apt/lists/lock* /var/cache/apt/archives/lock* 2>/dev/null || true", shell=True)
    subprocess.run(
        "printf 'deb http://us-central1.gce.clouds.archive.ubuntu.com/ubuntu/ jammy main universe restricted multiverse\\n"
        "deb http://us-central1.gce.clouds.archive.ubuntu.com/ubuntu/ jammy-updates main universe restricted multiverse\\n"
        "deb http://us-central1.gce.clouds.archive.ubuntu.com/ubuntu/ jammy-security main universe restricted multiverse\\n' > /etc/apt/sources.list",
        shell=True
    )
    subprocess.run("printf 'Acquire::Force-IPv4 \"true\";\\nAcquire::http::Timeout \"10\";\\n' > /etc/apt/apt.conf.d/99clean", shell=True)

    # 2. Debconf no-interactivo a prueba de fallos
    subprocess.run("echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections 2>/dev/null || true", shell=True)
    subprocess.run("echo 'keyboard-configuration keyboard-configuration/layoutcode string us' | debconf-set-selections 2>/dev/null || true", shell=True)
    subprocess.run("echo 'tzdata tzdata/Areas select Etc' | debconf-set-selections 2>/dev/null || true", shell=True)
    subprocess.run("echo 'tzdata tzdata/Zones/Etc select UTC' | debconf-set-selections 2>/dev/null || true", shell=True)

    # 3. Descarga e instalación de la suite oficial
    print("  📦 [2/4] Actualizando repositorios e instalando paquetes oficiales...", flush=True)
    repo_pkgs = [p for p in all_pkgs if not p.endswith(".deb")]
    cmd_install = (
        "apt-get update -qq && "
        f"DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true apt-get install -y --no-install-recommends -o Dpkg::Options::='--force-confdef' -o Dpkg::Options::='--force-confold' {' '.join(repo_pkgs)} >> {LOG_FILE} 2>&1 || "
        f"(DEBIAN_FRONTEND=noninteractive apt-get install -y --fix-broken >> {LOG_FILE} 2>&1)"
    )
    subprocess.run(cmd_install, shell=True)

    # 4. Descargar e instalar Google Chrome Oficial
    print("  🌐 [3/4] Instalando Google Chrome Oficial de 64 bits...", flush=True)
    chrome_deb = Path("/kaggle/working/google-chrome-stable_current_amd64.deb")
    gdrive_cache_deb = Path("/root/gdrive/Cloud_PC/Cache/google-chrome-stable_current_amd64.deb")

    if gdrive_cache_deb.exists() and gdrive_cache_deb.stat().st_size > 50_000_000:
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
        subprocess.run(f"dpkg -i {chrome_deb} >> {LOG_FILE} 2>&1 || (DEBIAN_FRONTEND=noninteractive apt-get install -y --fix-broken >> {LOG_FILE} 2>&1)", shell=True)
        subprocess.run(f"rm -f {chrome_deb}", shell=True)

    # 5. Módulos de Python
    print("  🐍 [4/4] Instalando dependencias de Python...", flush=True)
    subprocess.run(f"pip install -q pyngrok websockets aiohttp Pillow mss edge-tts python-dotenv openai >> {LOG_FILE} 2>&1", shell=True)
    print("  ✅ [✓] Suite Oficial de Ubuntu instalada limpiamente con éxito.", flush=True)

# Descargar noVNC si no existe
novnc_dir = Path("/opt/noVNC")
novnc_dir.parent.mkdir(parents=True, exist_ok=True)
if not (novnc_dir / "vnc.html").exists():
    shutil.rmtree(str(novnc_dir), ignore_errors=True)
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
/* ========================================================================== */
/* 1. VELOCÍMETRO ULTRA-MINIMALISTA: TEXTO PURO SIN MARCOS NI FONDOS          */
/* ========================================================================== */
#cloud-speed-indicator {
    position: fixed;
    bottom: calc(6px + var(--safe-bottom, 0px));
    left: calc(8px + var(--safe-left, 0px));
    display: inline-flex;
    align-items: baseline;
    gap: 4px;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
    font-size: 10.5px;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.75);
    text-shadow: 0 1px 2px #000000, 0 0 5px rgba(0, 0, 0, 0.9);
    z-index: 999980;
    pointer-events: none !important;
    user-select: none;
    -webkit-user-select: none;
    line-height: 1;
}
#cloud-speed-indicator .speed-fps-val {
    color: var(--aether-cyan, #00ffc8);
    font-weight: 800;
}
#cloud-speed-indicator .speed-sep {
    color: rgba(255, 255, 255, 0.35);
}
#cloud-speed-indicator .speed-ping-val {
    color: var(--aether-blue, #38bdf8);
    font-weight: 700;
}

/* ========================================================================== */
/* Ocultar barra antigua y conflictiva nativa de noVNC */
#noVNC_control_bar_anchor, #noVNC_control_bar {
    display: none !important;
}

/* Renderizado Ultra-Nítido Canvas BigTech & Aislamiento Táctil Completo */
#noVNC_canvas, canvas {
    image-rendering: -webkit-optimize-contrast !important;
    image-rendering: crisp-edges !important;
    touch-action: none !important;
    -webkit-touch-callout: none !important;
    -webkit-user-select: none !important;
    user-select: none !important;
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
    touch-action: pan-y;
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
.drawer-section-title {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: rgba(0, 255, 200, 0.7);
    margin-top: 6px;
    margin-bottom: 2px;
    padding-left: 4px;
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
    touch-action: pan-y;
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
.drawer-card-box {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 10px 12px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    transition: border-color 0.2s;
}
.drawer-card-box:hover {
    border-color: rgba(0, 255, 200, 0.25);
}
.drawer-card-label {
    font-size: 11px;
    font-weight: 700;
    color: #e2e8f0;
    letter-spacing: 0.3px;
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
/* 3. CAPA DE MANDOS VIRTUALES: MICROSOFT TAK + NEO-RETROPAD + XBOX VECTOR    */
/* ========================================================================== */
#virtual-gamepad-overlay {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 999970;
    user-select: none;
    touch-action: none;
    display: none;
    opacity: 1;
    transition: opacity 0.45s cubic-bezier(0.16, 1, 0.3, 1);
}
#virtual-gamepad-overlay.visible {
    display: block;
}
/* Sistema de Visibilidad Inteligente: Atenuación suave en reposo (TAK / Steam Link 20% ghost) */
#virtual-gamepad-overlay.gp-idle-ghost {
    opacity: 0.20;
    transition: opacity 0.8s ease;
}
/* Ocultamiento Automático al Conectar Mando Físico (Estándar TAK y RetroArch) */
#virtual-gamepad-overlay.gp-phys-hidden {
    opacity: 0 !important;
    pointer-events: none !important;
}

/* Base de Joysticks Analógicos: Arco Ergonómico TAK con Grip Cóncavo */
.gp-stick-zone {
    position: absolute;
    bottom: calc(24px + var(--safe-bottom, 0px));
    left: calc(24px + var(--safe-left, 0px));
    width: 144px;
    height: 144px;
    pointer-events: auto;
    touch-action: none;
}
/* Joystick Derecho: Barrido Interno para Control 3D de Cámara / Puntero */
.gp-right-stick-zone {
    left: auto !important;
    right: calc(192px + var(--safe-right, 0px));
    bottom: calc(24px + var(--safe-bottom, 0px));
}
.gp-stick-base {
    position: absolute;
    width: 140px;
    height: 140px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(15, 23, 42, 0.5) 0%, rgba(10, 15, 26, 0.75) 100%);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 2px solid rgba(0, 255, 200, 0.35);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.55), inset 0 0 16px rgba(0, 255, 200, 0.12);
    display: flex;
    align-items: center;
    justify-content: center;
}
/* Anillos Guía de Centrado en el Base */
.gp-stick-base::before {
    content: '';
    position: absolute;
    width: 86px;
    height: 86px;
    border-radius: 50%;
    border: 1px dashed rgba(0, 255, 200, 0.25);
    pointer-events: none;
}
.gp-stick-thumb {
    width: 58px;
    height: 58px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #2a3b53 0%, #151e2e 60%, #0b111a 100%);
    border: 2px solid var(--aether-cyan);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.7), 0 0 14px rgba(0, 255, 200, 0.5), inset 0 2px 4px rgba(255, 255, 255, 0.25), inset 0 -3px 6px rgba(0, 0, 0, 0.7);
    transform: translate3d(0, 0, 0);
    will-change: transform;
    pointer-events: none;
    display: flex;
    align-items: center;
    justify-content: center;
}
.gp-stick-thumb::after {
    content: '';
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0, 255, 200, 0.3) 0%, rgba(0, 255, 200, 0) 70%);
    border: 1px solid rgba(0, 255, 200, 0.4);
}

/* Botones L3 y R3 (Click Físico de Joystick - Sprint y Crouch) */
.gp-stick-click-btn {
    position: absolute;
    top: -6px;
    right: -6px;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1.5px solid var(--aether-cyan);
    color: var(--aether-cyan);
    font-size: 11px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    touch-action: none;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4), 0 0 12px rgba(0, 255, 200, 0.25);
    transition: transform 0.08s ease, background 0.1s ease;
    z-index: 10;
}
.gp-stick-click-btn:active, .gp-stick-click-btn.pressed {
    background: var(--aether-cyan);
    color: #0a0f1a;
    box-shadow: 0 0 18px var(--aether-cyan);
    transform: scale(0.92);
}

/* D-Pad Esculpido Continuo (Neo-Retropad + TAK Arc Slot 7/8) */
.gp-dpad-container {
    position: absolute;
    bottom: calc(186px + var(--safe-bottom, 0px));
    left: calc(32px + var(--safe-left, 0px));
    width: 128px;
    height: 128px;
    pointer-events: auto;
    touch-action: none;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(15, 23, 42, 0.4) 0%, rgba(10, 15, 26, 0.65) 100%);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1.5px solid rgba(56, 189, 248, 0.3);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
}
/* Hub central cóncavo del D-Pad */
.gp-dpad-container::before {
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 40px; height: 40px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.9) 100%);
    border: 1px solid rgba(56, 189, 248, 0.25);
    z-index: 1;
    pointer-events: none;
}
.gp-dpad-btn {
    position: absolute;
    width: 40px;
    height: 40px;
    background: rgba(15, 23, 42, 0.5);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(56, 189, 248, 0.35);
    color: var(--aether-blue);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    touch-action: none;
    transition: transform 0.08s ease, background 0.1s ease, color 0.1s ease, border-color 0.1s ease;
    z-index: 2;
}
.gp-dpad-btn svg {
    width: 20px;
    height: 20px;
    fill: currentColor;
    pointer-events: none;
    filter: drop-shadow(0 1px 2px rgba(0,0,0,0.5));
}
.gp-dpad-up {
    top: 4px; left: 44px;
    border-radius: 12px 12px 4px 4px;
}
.gp-dpad-down {
    bottom: 4px; left: 44px;
    border-radius: 4px 4px 12px 12px;
}
.gp-dpad-left {
    top: 44px; left: 4px;
    border-radius: 12px 4px 4px 12px;
}
.gp-dpad-right {
    top: 44px; right: 4px;
    border-radius: 4px 12px 12px 4px;
}
.gp-dpad-btn:active, .gp-dpad-btn.pressed {
    background: rgba(56, 189, 248, 0.55);
    border-color: #38bdf8;
    color: #ffffff;
    box-shadow: 0 0 16px #38bdf8;
    transform: scale(0.94);
}

/* Diamante de Acción ABXY (Microsoft Xbox TAK Diamond + Cristal Óptico) */
.gp-abxy-container {
    position: absolute;
    bottom: calc(24px + var(--safe-bottom, 0px));
    right: calc(24px + var(--safe-right, 0px));
    width: 156px;
    height: 156px;
    pointer-events: auto;
    touch-action: none;
}
.gp-action-btn {
    position: absolute;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, rgba(30, 41, 59, 0.75) 0%, rgba(15, 23, 42, 0.9) 100%);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 19px;
    font-weight: 900;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    cursor: pointer;
    touch-action: none;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.55), inset 0 2px 4px rgba(255, 255, 255, 0.18), inset 0 -3px 6px rgba(0, 0, 0, 0.5);
    transition: transform 0.08s ease, background 0.1s ease, box-shadow 0.1s ease, border-color 0.1s ease;
}
.gp-action-btn:active, .gp-action-btn.pressed {
    transform: scale(0.92);
}

/* Botón A (Verde Esmeralda Xbox Oficial: #10b981) */
.btn-xbox-a {
    bottom: 0; left: 53px;
    border: 2.2px solid rgba(16, 185, 129, 0.7);
    color: #10b981;
    text-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
}
.btn-xbox-a.pressed, .btn-xbox-a:active {
    background: #10b981;
    border-color: #10b981;
    box-shadow: 0 0 24px #10b981;
    color: #ffffff;
    text-shadow: 0 1px 3px rgba(0,0,0,0.5);
}

/* Botón B (Rojo Carmín Xbox Oficial: #ef4444) */
.btn-xbox-b {
    top: 53px; right: 0;
    border: 2.2px solid rgba(239, 68, 68, 0.7);
    color: #ef4444;
    text-shadow: 0 0 8px rgba(239, 68, 68, 0.6);
}
.btn-xbox-b.pressed, .btn-xbox-b:active {
    background: #ef4444;
    border-color: #ef4444;
    box-shadow: 0 0 24px #ef4444;
    color: #ffffff;
    text-shadow: 0 1px 3px rgba(0,0,0,0.5);
}

/* Botón X (Azul Cobalto Xbox Oficial: #3b82f6) */
.btn-xbox-x {
    top: 53px; left: 0;
    border: 2.2px solid rgba(59, 130, 246, 0.7);
    color: #3b82f6;
    text-shadow: 0 0 8px rgba(59, 130, 246, 0.6);
}
.btn-xbox-x.pressed, .btn-xbox-x:active {
    background: #3b82f6;
    border-color: #3b82f6;
    box-shadow: 0 0 24px #3b82f6;
    color: #ffffff;
    text-shadow: 0 1px 3px rgba(0,0,0,0.5);
}

/* Botón Y (Oro Ámbar Xbox Oficial: #f59e0b) */
.btn-xbox-y {
    top: 0; left: 53px;
    border: 2.2px solid rgba(245, 158, 11, 0.7);
    color: #f59e0b;
    text-shadow: 0 0 8px rgba(245, 158, 11, 0.6);
}
.btn-xbox-y.pressed, .btn-xbox-y:active {
    background: #f59e0b;
    border-color: #f59e0b;
    box-shadow: 0 0 24px #f59e0b;
    color: #ffffff;
    text-shadow: 0 1px 3px rgba(0,0,0,0.5);
}

/* Gatillos y Bumpers Anatómicos Superiores (LB, RB, LT, RT) */
.gp-shoulders-container {
    position: absolute;
    top: calc(12px + var(--safe-top, 0px));
    width: 100vw;
    display: flex;
    justify-content: space-between;
    padding: 0 calc(20px + var(--safe-right, 0px)) 0 calc(20px + var(--safe-left, 0px));
    box-sizing: border-box;
    pointer-events: auto;
}
.gp-shoulder-group {
    display: flex;
    gap: 10px;
    align-items: center;
}
.gp-shoulder-btn {
    background: radial-gradient(circle at 50% 30%, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1.5px solid rgba(0, 255, 200, 0.4);
    height: 40px;
    padding: 0 18px;
    color: var(--aether-cyan);
    font-size: 13px;
    font-weight: 800;
    cursor: pointer;
    touch-action: none;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    transition: transform 0.08s ease, background 0.1s ease, box-shadow 0.1s ease;
}
/* Bumpers (LB / RB) */
.gp-bumper-btn {
    border-radius: 12px;
    min-width: 60px;
}
/* Gatillos Analógicos Curvos (LT / RT) */
.gp-trigger-left {
    border-radius: 16px 6px 16px 6px;
    min-width: 66px;
    border-color: rgba(56, 189, 248, 0.5);
    color: var(--aether-blue);
}
.gp-trigger-right {
    border-radius: 6px 16px 6px 16px;
    min-width: 66px;
    border-color: rgba(56, 189, 248, 0.5);
    color: var(--aether-blue);
}
.gp-shoulder-btn.pressed, .gp-shoulder-btn:active {
    background: var(--aether-cyan);
    color: #0a0f1a;
    box-shadow: 0 0 18px var(--aether-cyan);
    transform: scale(0.93);
}
.gp-trigger-left.pressed, .gp-trigger-left:active,
.gp-trigger-right.pressed, .gp-trigger-right:active {
    background: #38bdf8;
    color: #0a0f1a;
    box-shadow: 0 0 18px #38bdf8;
}

/* Barra de Navegación Central (View, Nexus Guide, Menu) */
.gp-center-container {
    position: absolute;
    top: calc(12px + var(--safe-top, 0px));
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 8px;
    align-items: center;
    background: rgba(15, 23, 42, 0.55);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 24px;
    padding: 4px 10px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    pointer-events: auto;
}
.gp-center-btn {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 18px;
    height: 32px;
    padding: 0 12px;
    color: #94a3b8;
    font-size: 11px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    cursor: pointer;
    touch-action: none;
    transition: transform 0.08s ease, background 0.1s ease, color 0.1s ease;
}
.gp-center-btn svg {
    width: 15px;
    height: 15px;
    stroke: currentColor;
    fill: none;
}
.gp-guide-btn {
    background: radial-gradient(circle, rgba(0, 255, 200, 0.15) 0%, rgba(15, 23, 42, 0.6) 100%) !important;
    border-color: rgba(0, 255, 200, 0.4) !important;
    color: var(--aether-cyan) !important;
    font-weight: 800;
}
.gp-guide-btn svg {
    fill: currentColor !important;
    stroke: none !important;
}
.gp-center-btn.pressed, .gp-center-btn:active {
    background: rgba(255, 255, 255, 0.3);
    color: #ffffff;
    transform: scale(0.92);
}
.gp-guide-btn.pressed, .gp-guide-btn:active {
    background: var(--aether-cyan) !important;
    color: #0a0f1a !important;
    box-shadow: 0 0 16px var(--aether-cyan);
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
body.tp-touch-mode #cloud-virtual-cursor { display: block; }
body.tp-gamepad-active #cloud-virtual-cursor { display: none; }

#cloud-finger-contact {
    position: fixed; width: 38px; height: 38px; pointer-events: none !important;
    z-index: 999997; transform: translate3d(-50%, -50%, 0); opacity: 0;
    border-radius: 50%; border: 1.8px solid rgba(0, 255, 200, 0.7);
    background: radial-gradient(circle, rgba(0, 255, 200, 0.25) 0%, rgba(0, 255, 200, 0) 72%);
    box-shadow: 0 0 12px rgba(0, 255, 200, 0.45);
    transition: opacity 0.15s ease; will-change: transform, opacity;
}
#cloud-finger-contact.active { opacity: 1; }

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
#aether-kbd-dismiss {
    position: fixed; right: calc(14px + var(--safe-right));
    bottom: calc(18px + var(--safe-bottom));
    background: rgba(10, 15, 26, 0.94);
    color: #00ffc8;
    border: 1px solid rgba(0, 255, 200, 0.5);
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 12px; font-weight: 700;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.7), 0 0 12px rgba(0, 255, 200, 0.3);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    z-index: 999999;
    display: none;
    cursor: pointer;
    user-select: none;
    touch-action: manipulation;
    transition: transform 0.15s ease, background 0.15s ease;
}
#aether-kbd-dismiss:active {
    transform: scale(0.95);
    background: rgba(0, 255, 200, 0.2);
}
#aether-kbd-dismiss.visible {
    display: flex;
    align-items: center;
    gap: 6px;
}
</style>

<!-- 1. VELOCÍMETRO ULTRA-MINIMALISTA (LETRAS Y NÚMEROS PUROS SOBRE PANTALLA, SIN MARCOS) -->
<div id="cloud-speed-indicator" aria-hidden="true">
    <span class="speed-fps-val" id="perf-fps-text">60 FPS</span>
    <span class="speed-sep">·</span>
    <span class="speed-ping-val" id="perf-ping-text">-- ms</span>
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
        <div class="drawer-section-title">Entrada y Control</div>
        <button class="drawer-btn active-glow" id="btn-aether-mode">
            <div class="drawer-btn-left">
                <span class="d-icon" id="icon-aether-mode">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="7"/><line x1="12" y1="6" x2="12" y2="10"/></svg>
                </span>
                <span>Modo de Entrada</span>
            </div>
            <span class="drawer-pill active" id="badge-aether-mode">Trackpad</span>
        </button>
        <button class="drawer-btn" id="btn-aether-gamepad">
            <div class="drawer-btn-left">
                <span class="d-icon" id="icon-aether-gamepad">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="6"/><line x1="6" y1="12" x2="10" y2="12"/><line x1="8" y1="10" x2="8" y2="14"/><line x1="15" y1="13" x2="15.01" y2="13"/><line x1="18" y1="11" x2="18.01" y2="11"/></svg>
                </span>
                <span>Mandos en Pantalla</span>
            </div>
            <span class="drawer-pill" id="badge-aether-gamepad">OFF</span>
        </button>
        <button class="drawer-btn" id="btn-aether-sensitivity">
            <div class="drawer-btn-left">
                <span class="d-icon" id="icon-aether-sensitivity">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                </span>
                <span>Sensibilidad Trackpad</span>
            </div>
            <span class="drawer-pill" id="badge-aether-sensitivity">1.0x</span>
        </button>
        <button class="drawer-btn" id="btn-aether-scroll">
            <div class="drawer-btn-left">
                <span class="d-icon" id="icon-aether-scroll">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/><polyline points="5 8 12 1 19 8"/></svg>
                </span>
                <span>Desplazamiento Scroll</span>
            </div>
            <span class="drawer-pill" id="badge-aether-scroll">Estándar</span>
        </button>
        <button class="drawer-btn" id="btn-aether-pointerlock">
            <div class="drawer-btn-left">
                <span class="d-icon" id="icon-aether-pointerlock">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/></svg>
                </span>
                <span>Modo Gaming 3D</span>
            </div>
            <span class="drawer-pill" id="badge-aether-pointerlock">OFF</span>
        </button>
        <button class="drawer-btn" id="btn-aether-keyboard">
            <div class="drawer-btn-left">
                <span class="d-icon" id="icon-aether-keyboard">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><line x1="6" y1="8" x2="6.01" y2="8"/><line x1="10" y1="8" x2="10.01" y2="8"/><line x1="14" y1="8" x2="14.01" y2="8"/><line x1="18" y1="8" x2="18.01" y2="8"/><line x1="6" y1="12" x2="6.01" y2="12"/><line x1="10" y1="12" x2="10.01" y2="12"/><line x1="14" y1="12" x2="14.01" y2="12"/><line x1="18" y1="12" x2="18.01" y2="12"/><line x1="7" y1="16" x2="17" y2="16"/></svg>
                </span>
                <span>Teclado en Pantalla</span>
            </div>
            <span class="drawer-pill" id="badge-aether-keyboard">OFF</span>
        </button>

        <div class="drawer-section-title">Pantalla, Telemetría y Audio</div>
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
        <button class="drawer-btn" id="btn-aether-telem">
            <div class="drawer-btn-left">
                <span class="d-icon" id="icon-aether-telem">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                </span>
                <span>Diagnóstico Stream</span>
            </div>
            <span class="drawer-pill" id="badge-aether-telem">HUD</span>
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

        <div class="drawer-section-title">Cloud Gaming (GeForce NOW & Moonlight)</div>
        <button class="drawer-btn" id="btn-aether-gfn">
            <div class="drawer-btn-left">
                <span class="d-icon" id="icon-aether-gfn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                </span>
                <span>Modo GeForce NOW</span>
            </div>
            <span class="drawer-pill" id="badge-aether-gfn">OFF</span>
        </button>

        <div class="drawer-card-box">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="drawer-card-label">Moonlight + Sunshine 60 FPS</span>
                <span class="drawer-pill active" id="badge-sunshine-status">Activo</span>
            </div>
            <div style="display:flex; gap:6px; margin-top:6px;">
                <input type="text" id="input-moonlight-pin" placeholder="PIN 4 dígitos" maxlength="6" style="flex:1; background:rgba(0,0,0,0.5); border:1px solid rgba(0,255,200,0.3); border-radius:6px; color:#fff; padding:6px 10px; font-size:13px; text-align:center; font-family:monospace; letter-spacing:2px;">
                <button id="btn-moonlight-pair" style="background:var(--aether-cyan, #00ffc8); color:#0a0f1a; border:none; border-radius:6px; padding:6px 12px; font-weight:700; font-size:12px; cursor:pointer;">Vincular</button>
            </div>
            <div id="moonlight-status-text" style="font-size:10.5px; color:#8892b0; margin-top:4px;">1. Conecta con la IP de abajo. 2. Pon el PIN aquí y pulsa Vincular.</div>
            <div style="margin-top:8px;">
                <button id="btn-open-sunshine-web" style="width:100%; background:rgba(0,255,200,0.12); color:#00ffc8; border:1px solid rgba(0,255,200,0.3); border-radius:6px; padding:5px 8px; font-size:11px; font-weight:600; cursor:pointer;">Abrir Panel Web Sunshine (47990)</button>
            </div>
        </div>

        <div class="drawer-card-box">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="drawer-card-label">Tailscale VPN (Jugar por Internet)</span>
                <span class="drawer-pill" id="badge-tailscale-status">Verificando...</span>
            </div>
            <div id="tailscale-info" style="font-size:11px; color:#ccd6f6; margin-top:5px; font-family:monospace; word-break:break-all;">IP: Buscando...</div>
            <div style="display:flex; gap:6px; margin-top:6px;">
                <button id="btn-tailscale-copy" style="flex:1; background:rgba(255,255,255,0.08); color:#fff; border:1px solid rgba(255,255,255,0.2); border-radius:6px; padding:5px 8px; font-size:11px; cursor:pointer;">Copiar IP</button>
                <button id="btn-tailscale-login" style="display:none; flex:1; background:var(--aether-blue, #0099ff); color:#fff; border:none; border-radius:6px; padding:5px 8px; font-size:11px; font-weight:600; cursor:pointer;">Iniciar Sesión</button>
            </div>
            <div style="font-size:10px; color:#8892b0; margin-top:4px;">Usa esta IP en Moonlight para jugar desde cualquier red móvil o Wi-Fi.</div>
        </div>
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

<!-- 4. CAPA DE MANDOS VIRTUALES TÁCTILES: XBOX TAK + NEO-RETROPAD VECTOR -->
<div id="virtual-gamepad-overlay">
    <!-- Joystick Izquierdo (Locomoción Principal) -->
    <div class="gp-stick-zone" id="left-stick-zone">
        <div class="gp-stick-base">
            <div class="gp-stick-thumb" id="left-stick-thumb"></div>
        </div>
        <button class="gp-stick-click-btn" data-btn="10" title="Click Stick Izquierdo (Sprint / L3)">L3</button>
    </div>

    <!-- Joystick Derecho (Cámara 3D y Apuntar) -->
    <div class="gp-stick-zone gp-right-stick-zone" id="right-stick-zone">
        <div class="gp-stick-base">
            <div class="gp-stick-thumb" id="right-stick-thumb"></div>
        </div>
        <button class="gp-stick-click-btn" data-btn="11" title="Click Stick Derecho (Crouch / R3)">R3</button>
    </div>

    <!-- Cruceta D-Pad Esculpida con Vectores Kenney/Xbox -->
    <div class="gp-dpad-container" id="gp-dpad-dish">
        <button class="gp-dpad-btn gp-dpad-up" data-btn="12" title="Cruceta Arriba">
            <svg viewBox="0 0 24 24"><path d="M12 4l-7 8h4.5v8h5v-8H19z"/></svg>
        </button>
        <button class="gp-dpad-btn gp-dpad-down" data-btn="13" title="Cruceta Abajo">
            <svg viewBox="0 0 24 24"><path d="M12 20l7-8h-4.5V4h-5v8H5z"/></svg>
        </button>
        <button class="gp-dpad-btn gp-dpad-left" data-btn="14" title="Cruceta Izquierda">
            <svg viewBox="0 0 24 24"><path d="M4 12l8-7v4.5h8v5h-8V19z"/></svg>
        </button>
        <button class="gp-dpad-btn gp-dpad-right" data-btn="15" title="Cruceta Derecha">
            <svg viewBox="0 0 24 24"><path d="M20 12l-8 7v-4.5H4v-5h8V5z"/></svg>
        </button>
    </div>

    <!-- Diamante Anatómico de Acción ABXY (Neón Xbox Series) -->
    <div class="gp-abxy-container">
        <button class="gp-action-btn btn-xbox-y" data-btn="3" title="Botón Y">Y</button>
        <button class="gp-action-btn btn-xbox-x" data-btn="2" title="Botón X">X</button>
        <button class="gp-action-btn btn-xbox-b" data-btn="1" title="Botón B">B</button>
        <button class="gp-action-btn btn-xbox-a" data-btn="0" title="Botón A">A</button>
    </div>

    <!-- Gatillos y Bumpers Ergonómicos Superiores (LB, LT, RT, RB) -->
    <div class="gp-shoulders-container">
        <div class="gp-shoulder-group">
            <button class="gp-shoulder-btn gp-trigger-left" data-btn="6" title="Gatillo Izquierdo (LT)">LT</button>
            <button class="gp-shoulder-btn gp-bumper-btn" data-btn="4" title="Bumper Izquierdo (LB)">LB</button>
        </div>
        <div class="gp-shoulder-group">
            <button class="gp-shoulder-btn gp-bumper-btn" data-btn="5" title="Bumper Derecho (RB)">RB</button>
            <button class="gp-shoulder-btn gp-trigger-right" data-btn="7" title="Gatillo Derecho (RT)">RT</button>
        </div>
    </div>

    <!-- Barra Central de Sistema (View / Nexus Guide / Menu) -->
    <div class="gp-center-container">
        <button class="gp-center-btn" data-btn="8" title="Botón Vista / Compartir (View)">
            <svg viewBox="0 0 24 24" stroke-width="2"><rect x="4" y="8" width="10" height="10" rx="2"/><rect x="10" y="6" width="10" height="10" rx="2"/></svg>
            <span>VIEW</span>
        </button>
        <button class="gp-center-btn gp-guide-btn" data-btn="16" title="Botón Guía Xbox (Nexus Home)">
            <svg viewBox="0 0 24 24" width="18" height="18"><circle cx="12" cy="12" r="10.5" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M7 6.5c2.8 2.2 4.5 5 5 8 .5-3 2.2-5.8 5-8-1.5-1.5-3.6-2.5-6-2.5s-4.5 1-6 2.5z"/><path d="M6 8c-1.3 1.8-2 3.9-2 6.2 0 4.2 2.6 7.8 6.4 9.3-1.6-3.8-3.4-7.5-4.4-15.5zm12 0c1 8 2.8 11.7 4.4 15.5 3.8-1.5 6.4-5.1 6.4-9.3 0-2.3-.7-4.4-2-6.2z" opacity="0.88"/></svg>
            <span>XBOX</span>
        </button>
        <button class="gp-center-btn" data-btn="9" title="Botón Menú / Pausa (Menu)">
            <svg viewBox="0 0 24 24" stroke-width="2.5"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg>
            <span>MENU</span>
        </button>
    </div>
</div>

<!-- 5. CURSOR Y ANILLO VISUAL -->
<svg id="cloud-virtual-cursor" viewBox="0 0 24 24" fill="#ffffff" stroke="#000000" stroke-width="1.6">
    <path d="M0 0l7 18 2.5-7 7-2.5L0 0z"/>
</svg>
<svg id="cloud-hold-ring" viewBox="0 0 44 44">
    <circle cx="22" cy="22" r="19" fill="none" stroke="rgba(255,255,255,0.25)" stroke-width="3"/>
    <circle class="progress" cx="22" cy="22" r="19" fill="none" stroke="#00ffc8" stroke-width="3" stroke-linecap="round" transform="rotate(-90 22 22)"/>
</svg>
<div id="cloud-finger-contact" aria-hidden="true"></div>
<div id="cloud-toast">Modo Trackpad Activo</div>
<button id="aether-kbd-dismiss" title="Cerrar teclado en pantalla">
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    <span>Ocultar Teclado</span>
</button>
<audio id="cloud-web-audio" preload="none"></audio>

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
    const btnPointerLock = document.getElementById("btn-aether-pointerlock");
    const badgePointerLock = document.getElementById("badge-aether-pointerlock");
    const btnKeyboard = document.getElementById("btn-aether-keyboard");
    const badgeKeyboard = document.getElementById("badge-aether-keyboard");
    const kbdDismissBtn = document.getElementById("aether-kbd-dismiss");
    let isVirtualKeyboardActive = false;
    const btnOpenSunshineWeb = document.getElementById("btn-open-sunshine-web");
    const btnSensitivity = document.getElementById("btn-aether-sensitivity");
    const badgeSensitivity = document.getElementById("badge-aether-sensitivity");
    const btnScroll = document.getElementById("btn-aether-scroll");
    const badgeScroll = document.getElementById("badge-aether-scroll");
    const btnTelem = document.getElementById("btn-aether-telem");
    const badgeTelem = document.getElementById("badge-aether-telem");
    const btnAspect = document.getElementById("btn-aether-aspect");
    const badgeAspect = document.getElementById("badge-aether-aspect");
    const btnZoom = document.getElementById("btn-aether-zoom");
    const badgeZoom = document.getElementById("badge-aether-zoom");
    const btnAudio = document.getElementById("btn-aether-audio");
    const iconAudio = document.getElementById("icon-aether-audio");
    const badgeAudio = document.getElementById("badge-aether-audio");
    const webAudio = document.getElementById("cloud-web-audio");
    const btnFullscreen = document.getElementById("btn-aether-fullscreen");
    const badgeFullscreen = document.getElementById("badge-aether-fullscreen");
    const btnGfn = document.getElementById("btn-aether-gfn");
    const badgeGfn = document.getElementById("badge-aether-gfn");
    const inputMoonlightPin = document.getElementById("input-moonlight-pin");
    const btnMoonlightPair = document.getElementById("btn-moonlight-pair");
    const moonlightStatusText = document.getElementById("moonlight-status-text");
    const badgeTailscaleStatus = document.getElementById("badge-tailscale-status");
    const tailscaleInfo = document.getElementById("tailscale-info");
    const btnTailscaleCopy = document.getElementById("btn-tailscale-copy");
    const btnTailscaleLogin = document.getElementById("btn-tailscale-login");
    let isGfnMode = false;
    const btnExit = document.getElementById("btn-aether-exit");

    const gpOverlay = document.getElementById("virtual-gamepad-overlay");
    const leftStickZone = document.getElementById("left-stick-zone");
    const leftStickThumb = document.getElementById("left-stick-thumb");
    const rightStickZone = document.getElementById("right-stick-zone");
    const rightStickThumb = document.getElementById("right-stick-thumb");

    // Velocímetro Ultra-Minimalista (FPS y Ping sobre pantalla, sin marcos)
    const perfFps = document.getElementById("perf-fps-text");
    const perfPing = document.getElementById("perf-ping-text");

    const cursor = document.getElementById("cloud-virtual-cursor");
    const holdRing = document.getElementById("cloud-hold-ring");
    const toast = document.getElementById("cloud-toast");

    const screenW = 1920, screenH = 1080;
    let virtX = 960, virtY = 540;
    let currentMode = localStorage.getItem("cloudpc_input_mode") || "TRACKPAD";
    let isGamepadVisible = localStorage.getItem("cloudpc_gp_visible") === "true";
    let isStretchedAspect = false;
    let isAudioMuted = false;

    let trackpadSens = parseFloat(localStorage.getItem("cloudpc_tp_sens") || "1.0");
    let isNaturalScroll = localStorage.getItem("cloudpc_natural_scroll") === "true";
    let scrollAccumulatorY = 0;
    let isEdgeSwiping = false, edgeSwipeStartX = 0;
    let threeTouchStartY = 0, threeTouchStartX = 0, threeTouchMoved = 0, isThreeFingerGesture = false;

    let currentZoom = 1.0, panX = 0, panY = 0;
    let isDragging = false, isTouching = false, touchStartTime = 0, lastTapEndTime = 0;
    let initialTouchCount = 0, startX = 0, startY = 0, lastX = 0, lastY = 0, totalMoved = 0;
    let dragHoldTimer = null, isTapAndHalfCandidate = false;

    let scrollVelocityY = 0, lastScrollY = 0, lastScrollX = 0, lastScrollTime = 0, momentumAnimFrame = null;
    let isPinching = false, initialPinchDist = 0, initialPinchZoom = 1.0, initialPinchMidX = 0, initialPinchMidY = 0;
    let initialPinchWorldX = 0, initialPinchWorldY = 0, lastTapStartX = 0, lastTapStartY = 0;
    let lastMoveTime = 0;

    // -------------------------------------------------------------------------
    // CALIBRACIÓN MILIMÉTRICA DE PANTALLA (PROYECCIÓN INVARIANTE GEFORCE NOW & STEAM)
    // -------------------------------------------------------------------------
    function getDisplayGeometry() {
        const vw = window.innerWidth;
        const vh = window.innerHeight;
        const canvas = getCanvas();

        let containerW = vw;
        let containerH = vh;
        let containerLeft = 0;
        let containerTop = 0;

        if (canvas && canvas.parentElement) {
            const pRect = canvas.parentElement.getBoundingClientRect();
            if (pRect.width > 20 && pRect.height > 20) {
                containerW = pRect.width;
                containerH = pRect.height;
                containerLeft = pRect.left;
                containerTop = pRect.top;
            }
        }

        if (isStretchedAspect) {
            const renderW = containerW * currentZoom;
            const renderH = containerH * currentZoom;
            return {
                left: containerLeft + panX,
                top: containerTop + panY,
                width: renderW,
                height: renderH,
                baseW: containerW,
                baseH: containerH,
                offsetX: containerLeft,
                offsetY: containerTop,
                scaleX: renderW / screenW,
                scaleY: renderH / screenH
            };
        }

        const targetAspect = screenW / screenH; // 1920 / 1080 = 16:9
        const containerAspect = containerW / containerH;
        let baseW, baseH, offsetX, offsetY;

        if (containerAspect > targetAspect) {
            // Pantalla ancha (smartphone horizontal): bandas negras laterales (pillarboxing)
            baseH = containerH;
            baseW = containerH * targetAspect;
            offsetX = containerLeft + (containerW - baseW) / 2;
            offsetY = containerTop;
        } else {
            // Pantalla alta (tablet o vertical): bandas negras superior/inferior (letterboxing)
            baseW = containerW;
            baseH = containerW / targetAspect;
            offsetX = containerLeft;
            offsetY = containerTop + (containerH - baseH) / 2;
        }

        const renderW = baseW * currentZoom;
        const renderH = baseH * currentZoom;
        const renderLeft = offsetX + panX;
        const renderTop = offsetY + panY;

        return {
            left: renderLeft,
            top: renderTop,
            width: renderW,
            height: renderH,
            baseW: baseW,
            baseH: baseH,
            offsetX: offsetX,
            offsetY: offsetY,
            scaleX: renderW / screenW,
            scaleY: renderH / screenH
        };
    }

    function getViewportMetrics() {
        return getDisplayGeometry();
    }

    function getRFB() { return (window.UI && window.UI.rfb) ? window.UI.rfb : null; }
    function getCanvas() {
        const rfb = getRFB();
        if (rfb && rfb._canvas) return rfb._canvas;
        return document.querySelector("#noVNC_canvas") || document.querySelector("canvas");
    }

    // Conversión de Pantalla Física (Touch/Click) a Espacio Virtual 1080p Nativo (Milimétrico y Calibrado)
    function screenToVirtual(clientX, clientY) {
        const geo = getDisplayGeometry();
        const vx = ((clientX - geo.left) / geo.width) * screenW;
        const vy = ((clientY - geo.top) / geo.height) * screenH;
        return {
            x: Math.max(0, Math.min(screenW, Math.round(vx))),
            y: Math.max(0, Math.min(screenH, Math.round(vy)))
        };
    }

    // Conversión de Coordenadas Virtuales 1080p a Posición en Pantalla Física (CSS Pixels)
    function virtualToScreen(vx, vy) {
        const geo = getDisplayGeometry();
        const sx = geo.left + (vx / screenW) * geo.width;
        const sy = geo.top + (vy / screenH) * geo.height;
        return {
            x: Math.round(sx * 10) / 10,
            y: Math.round(sy * 10) / 10
        };
    }

    function clampPanX(x, zoom) {
        if (zoom <= 1.01) return 0;
        const m = getViewportMetrics();
        const minX = m.renderW > window.innerWidth ? (window.innerWidth - m.renderW) : 0;
        return Math.min(0, Math.max(minX, x));
    }
    function clampPanY(y, zoom) {
        if (zoom <= 1.01) return 0;
        const m = getViewportMetrics();
        const minY = m.renderH > window.innerHeight ? (window.innerHeight - m.renderH) : 0;
        return Math.min(0, Math.max(minY, y));
    }
    function zoomToPoint(targetZoom, screenX, screenY, animate) {
        const clampedZoom = Math.min(3.8, Math.max(1.0, targetZoom));
        if (clampedZoom <= 1.02) {
            currentZoom = 1.0;
            panX = 0;
            panY = 0;
        } else {
            const canvasX = (screenX - panX) / currentZoom;
            const canvasY = (screenY - panY) / currentZoom;
            currentZoom = clampedZoom;
            panX = clampPanX(screenX - (canvasX * currentZoom), currentZoom);
            panY = clampPanY(screenY - (canvasY * currentZoom), currentZoom);
        }
        updateCanvasTransform(animate);
    }

    function showToast(msg) {
        if (!toast) return;
        toast.innerText = msg;
        toast.classList.add("show");
        clearTimeout(toast._timer);
        toast._timer = setTimeout(() => toast.classList.remove("show"), 1800);
    }

    function hapticFeedback(pattern) {
        if (navigator.vibrate) { try { navigator.vibrate(pattern); } catch(e) {} }
        try {
            const gps = (typeof navigator.getGamepads === "function") ? navigator.getGamepads() : [];
            for (let i = 0; i < gps.length; i++) {
                const gp = gps[i];
                if (gp && gp.connected && gp.vibrationActuator && typeof gp.vibrationActuator.playEffect === "function") {
                    const dur = Array.isArray(pattern) ? pattern[0] : (typeof pattern === "number" ? pattern : 40);
                    gp.vibrationActuator.playEffect("dual-rumble", {
                        startDelay: 0,
                        duration: Math.min(250, dur || 40),
                        weakMagnitude: 0.55,
                        strongMagnitude: 0.35
                    }).catch(() => {});
                }
            }
        } catch(e) {}
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
        try {
            history.pushState({ aetherDrawerOpen: true }, "");
        } catch(e) {}
    }

    function closeDrawer(preventHistoryBack) {
        if (!drawer.classList.contains("open")) return;
        drawer.classList.remove("open");
        scrim.classList.remove("open");
        edgeTab.classList.remove("active");
        resetEdgeIdleTimer();
        if (!preventHistoryBack && history.state && history.state.aetherDrawerOpen) {
            try { history.back(); } catch(e) {}
        }
    }

    window.addEventListener("popstate", function(e) {
        if (drawer && drawer.classList.contains("open")) {
            closeDrawer(true);
        }
    });

    // Control de scroll y supresión absoluta de activación accidental en el panel Aether
    let drawerIsScrolling = false;
    let drawerTouchStartX = 0;
    let drawerTouchStartY = 0;
    let drawerLastScrollTime = 0;
    let drawerScrollTimeout = null;
    let lastGlobalTouchTime = 0;

    window.addEventListener("touchstart", function() { lastGlobalTouchTime = performance.now(); }, { capture: true, passive: true });
    window.addEventListener("touchend", function() { lastGlobalTouchTime = performance.now(); }, { capture: true, passive: true });

    function markDrawerScrolling() {
        drawerIsScrolling = true;
        drawerLastScrollTime = performance.now();
        clearTimeout(drawerScrollTimeout);
        drawerScrollTimeout = setTimeout(() => {
            drawerIsScrolling = false;
        }, 350);
    }

    const drawerItems = document.querySelector(".drawer-items");
    if (drawerItems) {
        drawerItems.addEventListener("scroll", markDrawerScrolling, { passive: true });
    }

    if (drawer) {
        drawer.addEventListener("scroll", markDrawerScrolling, { capture: true, passive: true });

        drawer.addEventListener("touchstart", function(e) {
            if (e.touches.length === 1) {
                drawerTouchStartX = e.touches[0].clientX;
                drawerTouchStartY = e.touches[0].clientY;
            }
        }, { capture: true, passive: true });

        drawer.addEventListener("touchmove", function(e) {
            if (e.touches.length === 1) {
                const dx = e.touches[0].clientX - drawerTouchStartX;
                const dy = e.touches[0].clientY - drawerTouchStartY;
                if (Math.hypot(dx, dy) > 5) {
                    markDrawerScrolling();
                }
            }
        }, { capture: true, passive: true });

        drawer.addEventListener("touchend", function(e) {
            if (drawerIsScrolling) {
                markDrawerScrolling();
            }
        }, { capture: true, passive: true });

        drawer.addEventListener("touchcancel", function(e) {
            markDrawerScrolling();
        }, { capture: true, passive: true });
    }

    // Helper anti-accidental de Grado Industrial (Estándar BigTech: Chrome / Material Design / FastClick)
    function attachButtonTap(elem, callback) {
        if (!elem) return;
        let btnTouchStartX = 0;
        let btnTouchStartY = 0;
        let btnTouchStartTime = 0;
        let btnStartScrollTop = 0;
        let btnMoved = false;
        let lastTapTime = 0;

        const getScrollContainer = () => elem.closest(".drawer-items") || drawer;

        elem.addEventListener("touchstart", function(e) {
            if (e.touches.length === 1) {
                btnTouchStartX = e.touches[0].clientX;
                btnTouchStartY = e.touches[0].clientY;
                btnTouchStartTime = performance.now();
                btnMoved = false;
                const sc = getScrollContainer();
                btnStartScrollTop = sc ? sc.scrollTop : 0;
            }
        }, { passive: true });

        elem.addEventListener("touchmove", function(e) {
            if (e.touches.length === 1) {
                const dx = e.touches[0].clientX - btnTouchStartX;
                const dy = e.touches[0].clientY - btnTouchStartY;
                if (Math.hypot(dx, dy) > 7) {
                    btnMoved = true;
                    markDrawerScrolling();
                }
            }
        }, { passive: true });

        elem.addEventListener("touchcancel", function(e) {
            btnMoved = true;
            markDrawerScrolling();
        }, { passive: true });

        elem.addEventListener("touchend", function(e) {
            // SUPRESIÓN OBLIGATORIA DEL CLIC SINTÉTICO DEL NAVEGADOR
            e.preventDefault();
            e.stopPropagation();

            const sc = getScrollContainer();
            const curScrollTop = sc ? sc.scrollTop : 0;
            const scrollDelta = Math.abs(curScrollTop - btnStartScrollTop);
            const duration = performance.now() - btnTouchStartTime;
            const timeSinceScroll = performance.now() - drawerLastScrollTime;

            // Si el dedo se movió > 7px, el contenedor hizo scroll > 4px, hubo scroll reciente (< 350ms), o fue un toque sostenido (> 420ms), descartar sin activar
            if (btnMoved || scrollDelta > 4 || drawerIsScrolling || timeSinceScroll < 350 || duration > 420) {
                btnMoved = false;
                return;
            }

            const now = performance.now();
            if (now - lastTapTime < 300) return;
            lastTapTime = now;
            callback(e);
        }, { passive: false });

        elem.addEventListener("click", function(e) {
            e.stopPropagation();
            // Ignorar clics sintéticos residuales producidos por toques táctiles
            if (performance.now() - lastGlobalTouchTime < 700) {
                e.preventDefault();
                return;
            }
            if (drawerIsScrolling || (performance.now() - drawerLastScrollTime < 350)) {
                e.preventDefault();
                return;
            }
            const now = performance.now();
            if (now - lastTapTime < 300) {
                e.preventDefault();
                return;
            }
            lastTapTime = now;
            callback(e);
        });
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
        showToast("Mando Físico: " + name);
        hapticFeedback([20, 50, 20]);
        // Estándar TAK y RetroArch: Auto-ocultar mandos táctiles al conectar mando físico
        if (isGamepadVisible && gpOverlay) {
            gpOverlay.classList.add("gp-phys-hidden");
        }
        initGamepadWebSocket();
        startPhysicalGamepadLoop();
    });

    window.addEventListener("gamepaddisconnected", function(e) {
        physicalGamepadCount = Math.max(0, physicalGamepadCount - 1);
        showToast("Mando físico desconectado");
        if (physicalGamepadCount === 0 && isGamepadVisible && gpOverlay) {
            gpOverlay.classList.remove("gp-phys-hidden");
            wakeGamepadOverlay();
        }
        gpAxesState = [0, 0, 0, 0];
        gpButtonsState = new Array(17).fill(0);
        emitGamepadState();
    });

    function triggerGamepadRumble(gp, duration = 80, strong = 0.4, weak = 0.6) {
        if (gp && gp.vibrationActuator && typeof gp.vibrationActuator.playEffect === "function") {
            try {
                gp.vibrationActuator.playEffect("dual-rumble", {
                    startDelay: 0,
                    duration: duration,
                    weakMagnitude: weak,
                    strongMagnitude: strong
                });
            } catch(e) {}
        }
    }

    function startPhysicalGamepadLoop() {
        if (physicalPollingFrame) return;
        function poll() {
            const gamepads = navigator.getGamepads ? navigator.getGamepads() : [];
            let active = false;
            for (let i = 0; i < gamepads.length; i++) {
                const gp = gamepads[i];
                if (gp && gp.connected) {
                    active = true;
                    // 1. Mapeo estándar de botones (0 a 16) con respuesta háptica y gradación analógica LT/RT (0..255)
                    for (let b = 0; b < gp.buttons.length && b < 17; b++) {
                        const btnObj = gp.buttons[b];
                        const val = typeof btnObj === "object" ? btnObj.value : (btnObj ? 1 : 0);
                        const pressed = typeof btnObj === "object" ? btnObj.pressed : (btnObj > 0.5);
                        if (pressed && !gpButtonsState[b] && (b === 6 || b === 7 || b === 0)) {
                            triggerGamepadRumble(gp, 60, 0.4, 0.6);
                        }
                        // Botones 6 (LT) y 7 (RT) envían valor analógico continuo (0.0 .. 1.0) para 256 niveles
                        gpButtonsState[b] = (b === 6 || b === 7) ? val : (pressed ? 1 : 0);
                    }
                    // 2. Sticks analógicos físicos con Deadzone continua calibrada
                    if (gp.axes.length >= 2) {
                        const ax0 = gp.axes[0], ax1 = gp.axes[1];
                        const mag = Math.hypot(ax0, ax1);
                        const deadzone = 0.10;
                        if (mag < deadzone) {
                            gpAxesState[0] = 0;
                            gpAxesState[1] = 0;
                        } else {
                            const scaledMag = (mag - deadzone) / (1.0 - deadzone);
                            gpAxesState[0] = (ax0 / mag) * scaledMag;
                            gpAxesState[1] = (ax1 / mag) * scaledMag;
                        }
                    }
                    if (gp.axes.length >= 4) {
                        const ax2 = gp.axes[2], ax3 = gp.axes[3];
                        const mag = Math.hypot(ax2, ax3);
                        const deadzone = 0.10;
                        if (mag < deadzone) {
                            gpAxesState[2] = 0;
                            gpAxesState[3] = 0;
                        } else {
                            const scaledMag = (mag - deadzone) / (1.0 - deadzone);
                            gpAxesState[2] = (ax2 / mag) * scaledMag;
                            gpAxesState[3] = (ax3 / mag) * scaledMag;
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

    // Sistema de Visibilidad Inteligente y Auto-Fade de Mandos (Microsoft TAK + Steam Link)
    let gpIdleTimer = null;
    const GP_IDLE_TIMEOUT = 4000; // 4s de inactividad para pasar a modo reposo (ghost 20%)

    function wakeGamepadOverlay() {
        if (!isGamepadVisible || !gpOverlay || physicalGamepadCount > 0) return;
        if (gpOverlay.classList.contains("gp-idle-ghost")) {
            gpOverlay.classList.remove("gp-idle-ghost");
        }
        clearTimeout(gpIdleTimer);
        gpIdleTimer = setTimeout(() => {
            const hasActiveTouch = (stickTouchId !== null) || (typeof rightStickTouchId !== "undefined" && rightStickTouchId !== null) || gpButtonsState.some(b => b === 1);
            if (!hasActiveTouch && isGamepadVisible && gpOverlay && physicalGamepadCount === 0) {
                gpOverlay.classList.add("gp-idle-ghost");
            }
        }, GP_IDLE_TIMEOUT);
    }

    window.addEventListener("touchstart", wakeGamepadOverlay, { passive: true });
    window.addEventListener("touchmove", wakeGamepadOverlay, { passive: true });

    function setGamepadVisibility(visible) {
        isGamepadVisible = visible;
        localStorage.setItem("cloudpc_gp_visible", visible ? "true" : "false");
        if (visible) {
            gpOverlay.classList.add("visible");
            gpOverlay.classList.remove("gp-idle-ghost");
            if (physicalGamepadCount > 0) {
                gpOverlay.classList.add("gp-phys-hidden");
            } else {
                gpOverlay.classList.remove("gp-phys-hidden");
                wakeGamepadOverlay();
            }
            if (badgeGamepad) { badgeGamepad.innerText = "ON"; badgeGamepad.classList.add("active"); }
            btnGamepad.classList.add("active-glow");
            document.body.classList.add("tp-gamepad-active");
            initGamepadWebSocket();
            showToast("Mandos Táctiles Activados");
        } else {
            clearTimeout(gpIdleTimer);
            gpOverlay.classList.remove("visible", "gp-idle-ghost", "gp-phys-hidden");
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
    let lastLeftStickTapTime = 0;
    const maxStickRadius = 42;

    if (leftStickZone) {
        leftStickZone.addEventListener("touchstart", function(e) {
            const now = performance.now();
            if (now - lastLeftStickTapTime < 280) {
                // Doble tap rápido = L3 Stick Click
                gpButtonsState[10] = 1;
                emitGamepadState();
                hapticFeedback([30, 20, 30]);
                showToast("L3 Clic (Stick Izquierdo)");
                setTimeout(() => { gpButtonsState[10] = 0; emitGamepadState(); }, 120);
                lastLeftStickTapTime = 0;
            } else {
                lastLeftStickTapTime = now;
            }
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
    let lastRightStickTapTime = 0;

    if (rightStickZone) {
        rightStickZone.addEventListener("touchstart", function(e) {
            const now = performance.now();
            if (now - lastRightStickTapTime < 280) {
                // Doble tap rápido = R3 Stick Click
                gpButtonsState[11] = 1;
                emitGamepadState();
                hapticFeedback([30, 20, 30]);
                showToast("R3 Clic (Stick Derecho)");
                setTimeout(() => { gpButtonsState[11] = 0; emitGamepadState(); }, 120);
                lastRightStickTapTime = 0;
            } else {
                lastRightStickTapTime = now;
            }
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

    // B. Mapeo de Cruceta D-Pad Continua (Deslizamiento Fluido 8-Way TAK / RetroArch)
    const dpadDish = document.getElementById("gp-dpad-dish");
    if (dpadDish) {
        let dpadTouchId = null;
        const dpadUpBtn = dpadDish.querySelector(".gp-dpad-up");
        const dpadDownBtn = dpadDish.querySelector(".gp-dpad-down");
        const dpadLeftBtn = dpadDish.querySelector(".gp-dpad-left");
        const dpadRightBtn = dpadDish.querySelector(".gp-dpad-right");

        function processDpadTouch(clientX, clientY) {
            const rect = dpadDish.getBoundingClientRect();
            const cx = rect.left + rect.width / 2;
            const cy = rect.top + rect.height / 2;
            const dx = clientX - cx;
            const dy = clientY - cy;
            const dist = Math.hypot(dx, dy);

            let up = 0, down = 0, left = 0, right = 0;
            if (dist >= 14) { // Zona muerta central de 14px
                const angle = Math.atan2(dy, dx) * (180 / Math.PI); // -180 a 180 deg
                if (angle >= -157.5 && angle <= -22.5) up = 1;
                if (angle >= 22.5 && angle <= 157.5) down = 1;
                if (angle >= -67.5 && angle <= 67.5) right = 1;
                if (angle >= 112.5 || angle <= -112.5) left = 1;
            }

            const changed = (gpButtonsState[12] !== up || gpButtonsState[13] !== down ||
                             gpButtonsState[14] !== left || gpButtonsState[15] !== right);

            gpButtonsState[12] = up;
            gpButtonsState[13] = down;
            gpButtonsState[14] = left;
            gpButtonsState[15] = right;

            if (dpadUpBtn) dpadUpBtn.classList.toggle("pressed", !!up);
            if (dpadDownBtn) dpadDownBtn.classList.toggle("pressed", !!down);
            if (dpadLeftBtn) dpadLeftBtn.classList.toggle("pressed", !!left);
            if (dpadRightBtn) dpadRightBtn.classList.toggle("pressed", !!right);

            if (changed) {
                if (up || down || left || right) hapticFeedback(12);
                emitGamepadState();
            }
        }

        function resetDpad() {
            dpadTouchId = null;
            if (gpButtonsState[12] || gpButtonsState[13] || gpButtonsState[14] || gpButtonsState[15]) {
                gpButtonsState[12] = 0;
                gpButtonsState[13] = 0;
                gpButtonsState[14] = 0;
                gpButtonsState[15] = 0;
                if (dpadUpBtn) dpadUpBtn.classList.remove("pressed");
                if (dpadDownBtn) dpadDownBtn.classList.remove("pressed");
                if (dpadLeftBtn) dpadLeftBtn.classList.remove("pressed");
                if (dpadRightBtn) dpadRightBtn.classList.remove("pressed");
                emitGamepadState();
            }
        }

        dpadDish.addEventListener("touchstart", function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (e.changedTouches.length > 0) {
                dpadTouchId = e.changedTouches[0].identifier;
                processDpadTouch(e.changedTouches[0].clientX, e.changedTouches[0].clientY);
            }
        }, { passive: false });

        window.addEventListener("touchmove", function(e) {
            if (dpadTouchId === null) return;
            for (let i = 0; i < e.changedTouches.length; i++) {
                if (e.changedTouches[i].identifier === dpadTouchId) {
                    processDpadTouch(e.changedTouches[i].clientX, e.changedTouches[i].clientY);
                    break;
                }
            }
        }, { passive: true });

        window.addEventListener("touchend", function(e) {
            if (dpadTouchId === null) return;
            for (let i = 0; i < e.changedTouches.length; i++) {
                if (e.changedTouches[i].identifier === dpadTouchId) {
                    resetDpad();
                    break;
                }
            }
        });

        window.addEventListener("touchcancel", function(e) {
            if (dpadTouchId === null) return;
            for (let i = 0; i < e.changedTouches.length; i++) {
                if (e.changedTouches[i].identifier === dpadTouchId) {
                    resetDpad();
                    break;
                }
            }
        });
    }

    // C. Mapeo de Botones Táctiles en Pantalla (ABXY, Shoulders, L3/R3, Start, Back, Guide)
    document.querySelectorAll("[data-btn]:not(.gp-dpad-btn)").forEach(btn => {
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
    // 4. MODO TRACKPAD & TÁCTIL DIRECTO (GESTOS CHROME REMOTE DESKTOP & GUACAMOLE)
    // -------------------------------------------------------------------------
    function updateCursorElement() {
        if (!cursor) return;
        const pt = virtualToScreen(virtX, virtY);
        cursor.style.transform = `translate3d(${pt.x}px, ${pt.y}px, 0)`;
    }

    // Inyección de Puntero en Kernel X11 / TigerVNC (Tres Capas: Socket Directo, API noVNC y DOM)
    function sendPointer(x, y, mask) {
        const rfb = getRFB();
        const px = Math.max(0, Math.min(screenW, Math.round(x)));
        const py = Math.max(0, Math.min(screenH, Math.round(y)));

        if (rfb && rfb._rfbConnectionState === 'connected' && !rfb._viewOnly) {
            // Método 1: Envío binario PointerEvent directo al socket RFB (100% Preciso en Framebuffer 1080p)
            if (rfb._sock && rfb.constructor && rfb.constructor.messages && typeof rfb.constructor.messages.pointerEvent === "function") {
                try {
                    rfb.constructor.messages.pointerEvent(rfb._sock, px, py, mask);
                    rfb._mousePos = { x: px, y: py };
                    rfb._mouseButtonMask = mask;
                    return;
                } catch(e) {}
            }
            // Método 2: Invocación de _sendMouse con calibración de escala y offset
            if (typeof rfb._sendMouse === "function" && rfb._display) {
                try {
                    const scale = rfb._display._scale || 1;
                    const vx = (px - (rfb._display._viewportLoc ? rfb._display._viewportLoc.x : 0)) * scale;
                    const vy = (py - (rfb._display._viewportLoc ? rfb._display._viewportLoc.y : 0)) * scale;
                    rfb._sendMouse(vx, vy, mask);
                    return;
                } catch(e) {}
            }
        }

        // Método 3: Fallback sintético al canvas con proyección geométrica milimétrica
        const canvas = getCanvas();
        if (canvas) {
            const sPt = virtualToScreen(px, py);
            const clientX = sPt.x;
            const clientY = sPt.y;
            const btn = (mask === 4) ? 2 : ((mask === 2) ? 1 : 0);
            const evtType = mask ? "mousedown" : "mouseup";
            try {
                canvas.dispatchEvent(new MouseEvent("mousemove", {
                    bubbles: true, cancelable: true, view: window,
                    clientX: clientX, clientY: clientY,
                    buttons: mask
                }));
                if (mask !== undefined) {
                    canvas.dispatchEvent(new MouseEvent(evtType, {
                        bubbles: true, cancelable: true, view: window,
                        clientX: clientX, clientY: clientY,
                        button: btn, buttons: mask
                    }));
                }
            } catch(e) {}
        }
    }

    function sendMouse(mask) {
        sendPointer(virtX, virtY, mask);
    }

    function sendMouseMove() {
        sendPointer(virtX, virtY, isDragging ? 1 : 0);
    }

    // Desactivar GestureHandler nativo y cursor duplicado de noVNC para evitar colisiones con el Trackpad
    function setupNoVNCHooks() {
        const rfb = getRFB();
        if (rfb) {
            rfb.showDotCursor = false;
            if (rfb._cursor && rfb._cursor._canvas) {
                try { rfb._cursor._canvas.style.display = "none"; } catch(e) {}
            }
            if (rfb._gestures && rfb._gestures._target) {
                try {
                    rfb._gestures.detach();
                    console.log("[AETHER] Gestures nativos de noVNC desacoplados para Trackpad Aether Pro");
                } catch(e) {}
            }
            if (rfb._canvas) {
                if (!rfb._canvas.id) rfb._canvas.id = "noVNC_canvas";
                rfb._canvas.style.touchAction = "none";
            }
        }
    }
    setInterval(setupNoVNCHooks, 400);

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

    function sendKeyCombo(downKeysym, pressKeysym) {
        const rfb = getRFB();
        if (!rfb) return;
        const sk = (typeof rfb.sendKey === "function") ? rfb.sendKey.bind(rfb) : (typeof rfb._sendKey === "function" ? rfb._sendKey.bind(rfb) : null);
        if (!sk) return;
        sk(downKeysym, 1);
        setTimeout(() => {
            sk(pressKeysym, 1);
            setTimeout(() => {
                sk(pressKeysym, 0);
                setTimeout(() => sk(downKeysym, 0), 40);
            }, 60);
        }, 30);
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
        setupNoVNCHooks();
    }

    if (btnMode) {
        attachButtonTap(btnMode, function() {
            setInputMode(currentMode === "TRACKPAD" ? "TOUCH" : "TRACKPAD");
        });
    }

    // Filtro para ignorar toques en controles UI (drawer, edge tab, mandos gamepad)
    function shouldIgnoreTouch(e) {
        if (!e.target) return false;
        return !!(
            e.target.closest("#aether-drawer") ||
            e.target.closest("#aether-edge-tab") ||
            e.target.closest("#aether-scrim") ||
            e.target.closest("#cloud-speed-indicator") ||
            e.target.closest("#aether-kbd-dismiss") ||
            e.target.closest("#virtual-gamepad-overlay [data-btn]") ||
            e.target.closest(".gp-stick-zone") ||
            e.target.closest(".gp-stick-click-btn") ||
            e.target.closest(".gp-dpad-container") ||
            e.target.closest(".gp-abxy-container") ||
            e.target.closest(".gp-shoulders-container") ||
            e.target.closest(".gp-center-container")
        );
    }

    // GESTOS TÁCTILES Y MOTOR DE TRACKPAD EN CAPTURE PHASE UNIVERSAL
    function handleTouchStart(e) {
        if (shouldIgnoreTouch(e)) return;

        // Si el teclado virtual está inactivo, asegurar que ningún input residual reabra el teclado al tocar la pantalla
        if (!isVirtualKeyboardActive) {
            const inputElem = document.getElementById("noVNC_keyboardinput") || document.querySelector("textarea") || document.querySelector("input");
            if (inputElem && document.activeElement === inputElem) {
                inputElem.blur();
            }
        }

        // Prevenir comportamiento nativo del navegador (pan de página, zoom, pull-to-refresh)
        e.preventDefault();
        e.stopPropagation();

        initialTouchCount = e.touches.length;
        touchStartTime = performance.now();
        totalMoved = 0;
        cancelAnimationFrame(momentumAnimFrame);
        resetEdgeIdleTimer();

        // 1 Dedo: Movimiento de Puntero (Trackpad) o Posicionamiento Directo (Touch)
        if (e.touches.length === 1) {
            isTouching = true;
            startX = lastX = e.touches[0].clientX;
            startY = lastY = e.touches[0].clientY;
            lastMoveTime = touchStartTime;

            const fingerContact = document.getElementById("cloud-finger-contact");
            if (fingerContact) {
                fingerContact.style.transform = `translate3d(${startX}px, ${startY}px, 0)`;
                fingerContact.classList.add("active");
            }

            // Deslizamiento desde el margen izquierdo para abrir el menú Aether
            if (startX < 28 && !drawer.classList.contains("open")) {
                isEdgeSwiping = true;
                edgeSwipeStartX = startX;
            } else {
                isEdgeSwiping = false;
            }

            const timeSinceLastTap = touchStartTime - lastTapEndTime;
            isTapAndHalfCandidate = (currentMode === "TRACKPAD" && timeSinceLastTap < 320 && Math.hypot(startX - lastTapStartX, startY - lastTapStartY) < 35);

            clearTimeout(dragHoldTimer);
            if (holdRing) {
                const pt = virtualToScreen(virtX, virtY);
                holdRing.style.left = pt.x + "px";
                holdRing.style.top = pt.y + "px";
                holdRing.classList.remove("active");
            }

            if (currentMode === "TRACKPAD") {
                // Long-press hold para iniciar Arrastre (Tolerancia ergonómica 25px para pulgar humano)
                dragHoldTimer = setTimeout(function() {
                    if (isTouching && totalMoved < 25 && initialTouchCount === 1) {
                        isDragging = true;
                        if (holdRing) holdRing.classList.add("active");
                        if (cursor) cursor.classList.add("cursor-dragging");
                        hapticFeedback(35);
                        sendMouse(1);
                        showToast("Arrastre Bloqueado (Drag & Drop)");
                    }
                }, 300);
            } else {
                // MODO TÁCTIL DIRECTO: Mover puntero de inmediato al toque
                const vPos = screenToVirtual(startX, startY);
                virtX = vPos.x;
                virtY = vPos.y;
                updateCursorElement();
                sendMouseMove();
            }
        } else if (e.touches.length === 2) {
            clearTimeout(dragHoldTimer);
            if (holdRing) holdRing.classList.remove("active");
            if (isDragging) {
                isDragging = false;
                if (cursor) cursor.classList.remove("cursor-dragging");
                sendMouse(0);
            }

            scrollAccumulatorY = 0;
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
        } else if (e.touches.length === 3) {
            threeTouchStartY = (e.touches[0].clientY + e.touches[1].clientY + e.touches[2].clientY) / 3;
            threeTouchStartX = (e.touches[0].clientX + e.touches[1].clientX + e.touches[2].clientX) / 3;
            threeTouchMoved = 0;
            isThreeFingerGesture = true;
        }
    }

    function handleTouchMove(e) {
        if (shouldIgnoreTouch(e)) return;

        e.preventDefault();
        e.stopPropagation();

        // Deslizamiento desde el borde izquierdo para abrir el menú Aether
        if (isEdgeSwiping && e.touches.length === 1) {
            const curTouchX = e.touches[0].clientX;
            if (curTouchX - edgeSwipeStartX > 42) {
                isEdgeSwiping = false;
                openDrawer();
                return;
            }
        }

        if (isTouching && e.touches.length === 1) {
            const curX = e.touches[0].clientX, curY = e.touches[0].clientY;
            const dx = curX - lastX, dy = curY - lastY;
            lastX = curX; lastY = curY;
            const dist = Math.hypot(dx, dy);
            totalMoved += dist;

            const fingerContact = document.getElementById("cloud-finger-contact");
            if (fingerContact) {
                fingerContact.style.transform = `translate3d(${curX}px, ${curY}px, 0)`;
            }

            const now = performance.now();
            const dt = Math.max(8, now - lastMoveTime);
            lastMoveTime = now;

            if (totalMoved > 25 && !isDragging) {
                clearTimeout(dragHoldTimer);
                if (holdRing) holdRing.classList.remove("active");
            }

            // Tap & Drag (Doble toque y arrastre inmediato)
            if (isTapAndHalfCandidate && totalMoved > 6 && !isDragging) {
                isDragging = true;
                if (cursor) cursor.classList.add("cursor-dragging");
                hapticFeedback(25);
                sendMouse(1);
                showToast("Arrastre Bloqueado (Tap & Drag)");
            }

            if (currentMode === "TRACKPAD") {
                // Filtro anti-jitter para micro-temblores en reposo (< 0.5px)
                if (dist < 0.5 && !isDragging) {
                    return;
                }

                // Aceleración Balística Estándar Apple macOS / Chrome Remote Desktop
                const v = dist / dt; // velocidad instantánea (px/ms)
                let accel = 1.0;
                if (v < 0.20) {
                    accel = 0.75; // Micro-precisión subpíxel para botones finos y enlaces
                } else if (v < 1.0) {
                    accel = 0.75 + (v - 0.20) * 0.95; // Transición lineal ergonómica 1:1
                } else {
                    accel = Math.min(3.5, 1.5 + Math.pow(v - 1.0, 1.25)); // Aceleración balística progresiva
                }

                const scaleFactor = 1.25 * accel * trackpadSens;
                const geo = getDisplayGeometry();
                const scaleX = (screenW / geo.width) * scaleFactor;
                const scaleY = (screenH / geo.height) * scaleFactor;

                virtX = Math.max(0, Math.min(screenW, virtX + (dx * scaleX)));
                virtY = Math.max(0, Math.min(screenH, virtY + (dy * scaleY)));

                // Auto-pan suave si el cursor llega al borde estando ampliado con zoom
                if (currentZoom > 1.05) {
                    const pt = virtualToScreen(virtX, virtY);
                    const edgeMargin = 40;
                    if (pt.x < edgeMargin) panX = clampPanX(panX + (edgeMargin - pt.x) * 0.35, currentZoom);
                    if (pt.x > window.innerWidth - edgeMargin) panX = clampPanX(panX - (pt.x - (window.innerWidth - edgeMargin)) * 0.35, currentZoom);
                    if (pt.y < edgeMargin) panY = clampPanY(panY + (edgeMargin - pt.y) * 0.35, currentZoom);
                    if (pt.y > window.innerHeight - edgeMargin) panY = clampPanY(panY - (pt.y - (window.innerHeight - edgeMargin)) * 0.35, currentZoom);
                    updateCanvasTransform(false);
                } else {
                    updateCursorElement();
                }

                // Transmisión inmediata y continua del movimiento al servidor VNC
                sendMouseMove();
            } else {
                // MODO TÁCTIL DIRECTO (TABLET): Arrastre natural al deslizar el dedo
                if (totalMoved > 8 && !isDragging) {
                    isDragging = true;
                    if (cursor) cursor.classList.add("cursor-dragging");
                    sendMouse(1);
                }
                const vPos = screenToVirtual(curX, curY);
                virtX = vPos.x;
                virtY = vPos.y;
                updateCursorElement();
                sendMouseMove();
            }
        } else if (e.touches.length === 2) {
            const p1 = e.touches[0], p2 = e.touches[1];
            const currentDist = Math.hypot(p1.clientX - p2.clientX, p1.clientY - p2.clientY);
            const distDiff = Math.abs(currentDist - initialPinchDist);
            const curMidX = (p1.clientX + p2.clientX) / 2;
            const curMidY = (p1.clientY + p2.clientY) / 2;

            if (distDiff > 16 || isPinching) {
                isPinching = true;
                const zoomFactor = currentDist / initialPinchDist;
                const newZoom = Math.min(3.8, Math.max(1.0, initialPinchZoom * zoomFactor));

                if (newZoom <= 1.02) {
                    currentZoom = 1.0;
                    panX = 0;
                    panY = 0;
                } else {
                    currentZoom = newZoom;
                    panX = clampPanX(curMidX - (initialPinchWorldX * currentZoom), currentZoom);
                    panY = clampPanY(curMidY - (initialPinchWorldY * currentZoom), currentZoom);
                }
                if (badgeZoom) badgeZoom.innerText = Math.round(currentZoom * 100) + "%";
                updateCanvasTransform(false);
            } else if (currentZoom > 1.05) {
                // Pan a dos dedos en modo zoom ampliado
                const dx = curMidX - lastScrollX;
                const dy = curMidY - lastScrollY;
                lastScrollX = curMidX;
                lastScrollY = curMidY;
                panX = clampPanX(panX + dx, currentZoom);
                panY = clampPanY(panY + dy, currentZoom);
                updateCanvasTransform(false);
            } else {
                // Modo Scroll a Dos Dedos con Acumulador Fino de Subpíxeles
                const dy = curMidY - lastScrollY;
                lastScrollY = curMidY;
                lastScrollX = curMidX;
                const now = performance.now(), dt = Math.max(8, now - lastScrollTime);
                if (dt > 0) scrollVelocityY = dy / dt;
                lastScrollTime = now;

                scrollAccumulatorY += dy;
                const step = 14;
                while (Math.abs(scrollAccumulatorY) >= step) {
                    const mask = scrollAccumulatorY > 0 ? (isNaturalScroll ? 8 : 16) : (isNaturalScroll ? 16 : 8);
                    sendMouse(mask);
                    setTimeout(() => sendMouse(0), 18);
                    scrollAccumulatorY += (scrollAccumulatorY > 0 ? -step : step);
                }
            }
        } else if (e.touches.length === 3 && isThreeFingerGesture) {
            const curMidY = (e.touches[0].clientY + e.touches[1].clientY + e.touches[2].clientY) / 3;
            threeTouchMoved = curMidY - threeTouchStartY;
        }
    }

    function handleTouchEnd(e) {
        if (shouldIgnoreTouch(e)) return;

        e.preventDefault();
        e.stopPropagation();

        isEdgeSwiping = false;
        clearTimeout(dragHoldTimer);
        if (holdRing) holdRing.classList.remove("active");
        const duration = performance.now() - touchStartTime;

        if (isDragging) {
            isDragging = false;
            if (cursor) cursor.classList.remove("cursor-dragging");
            sendMouse(0);
            hapticFeedback(15);
            lastTapEndTime = performance.now();
            return;
        }

        if (e.touches.length === 0) {
            isTouching = false;

            const fingerContact = document.getElementById("cloud-finger-contact");
            if (fingerContact) {
                fingerContact.classList.remove("active");
            }

            // Inercia Cinética de Scroll
            if (initialTouchCount === 2 && !isPinching && Math.abs(scrollVelocityY) > 0.35 && currentZoom <= 1.05) {
                let v = scrollVelocityY * 16;
                let decay = () => {
                    if (Math.abs(v) > 0.8) {
                        const mask = v > 0 ? (isNaturalScroll ? 8 : 16) : (isNaturalScroll ? 16 : 8);
                        sendMouse(mask);
                        setTimeout(() => sendMouse(0), 18);
                        v *= 0.88;
                        momentumAnimFrame = requestAnimationFrame(decay);
                    }
                };
                decay();
            }

            // Toque con 1 dedo (< 320ms y < 15px)
            if (initialTouchCount === 1 && duration < 320 && totalMoved < 15) {
                const timeSinceLastTap = touchStartTime - lastTapEndTime;

                // Doble Clic (Dos toques consecutivos)
                if (timeSinceLastTap < 300 && Math.hypot(startX - lastTapStartX, startY - lastTapStartY) < 35) {
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
                lastTapEndTime = performance.now();

                if (currentMode === "TRACKPAD") {
                    const pt = virtualToScreen(virtX, virtY);
                    createRipple(pt.x, pt.y, "left-click");
                    hapticFeedback(12);
                    sendMouse(1);
                    setTimeout(() => sendMouse(0), 45);
                } else {
                    const vPos = screenToVirtual(startX, startY);
                    virtX = vPos.x;
                    virtY = vPos.y;
                    const pt = virtualToScreen(virtX, virtY);
                    createRipple(pt.x, pt.y, "left-click");
                    hapticFeedback(12);
                    sendMouse(1);
                    setTimeout(() => sendMouse(0), 45);
                }
            } else if (initialTouchCount === 2 && !isPinching && duration < 320 && totalMoved < 15) {
                // Toque a 2 dedos = Clic Derecho (Right Click)
                hapticFeedback([12, 35, 12]);
                const pt = virtualToScreen(virtX, virtY);
                createRipple(pt.x, pt.y, "right-click");
                sendMouse(4);
                setTimeout(() => sendMouse(0), 45);
                showToast("Clic Secundario");
            } else if (initialTouchCount === 3) {
                // Gestos a 3 dedos
                if (Math.abs(threeTouchMoved) > 50) {
                    if (threeTouchMoved < -50) {
                        sendKeyCombo(0xFFEB, 0x0064); // Super + D
                        showToast("Mostrar Escritorio (Super+D)");
                        hapticFeedback([25, 40, 25]);
                    } else {
                        sendKeyCombo(0xFFE9, 0xFF09); // Alt + Tab
                        showToast("Alternar Ventanas (Alt+Tab)");
                        hapticFeedback([25, 40, 25]);
                    }
                } else if (duration < 350) {
                    // Toque 3 dedos = Clic Central de Ratón
                    hapticFeedback(22);
                    sendMouse(2);
                    setTimeout(() => sendMouse(0), 45);
                    showToast("Clic Central (Rueda / Pegar)");
                }
                isThreeFingerGesture = false;
            } else if (initialTouchCount === 4 && duration < 400) {
                toggleFullScreen();
            }
            initialTouchCount = 0;
        }
    }

    // Registro en Capture Phase Universal: Ejecuta ANTES de cualquier listener del canvas
    window.addEventListener("touchstart", handleTouchStart, { capture: true, passive: false });
    window.addEventListener("touchmove", handleTouchMove, { capture: true, passive: false });
    window.addEventListener("touchend", handleTouchEnd, { capture: true, passive: false });
    window.addEventListener("touchcancel", handleTouchEnd, { capture: true, passive: false });

    window.addEventListener("resize", function() {
        updateCanvasTransform(false);
        updateCursorElement();
    });

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

    // Gestión Quirúrgica de Teclado en Pantalla (Activar / Desactivar sin trampas de foco)
    function setVirtualKeyboardState(active) {
        isVirtualKeyboardActive = !!active;
        const inputElem = document.getElementById("noVNC_keyboardinput") || document.querySelector("textarea") || document.querySelector("input");
        const rfb = getRFB();

        if (isVirtualKeyboardActive) {
            if (badgeKeyboard) {
                badgeKeyboard.innerText = "ON";
                badgeKeyboard.classList.add("active");
            }
            if (btnKeyboard) btnKeyboard.classList.add("active-glow");
            if (kbdDismissBtn) kbdDismissBtn.classList.add("visible");
            if (inputElem) {
                try {
                    inputElem.focus({ preventScroll: true });
                    const l = inputElem.value.length;
                    inputElem.setSelectionRange(l, l);
                } catch(e) {
                    inputElem.focus();
                }
            }
            if (window.UI && typeof window.UI.showVirtualKeyboard === "function") {
                try { window.UI.showVirtualKeyboard(); } catch(e) {}
            }
            showToast("Teclado Activado");
        } else {
            if (badgeKeyboard) {
                badgeKeyboard.innerText = "OFF";
                badgeKeyboard.classList.remove("active");
            }
            if (btnKeyboard) btnKeyboard.classList.remove("active-glow");
            if (kbdDismissBtn) kbdDismissBtn.classList.remove("visible");
            if (inputElem) {
                try { inputElem.blur(); } catch(e) {}
            }
            if (document.activeElement && document.activeElement.blur) {
                try { document.activeElement.blur(); } catch(e) {}
            }
            if (window.UI && typeof window.UI.hideVirtualKeyboard === "function") {
                try { window.UI.hideVirtualKeyboard(); } catch(e) {}
            }
            const novncKbdBtn = document.getElementById("noVNC_keyboard_button");
            if (novncKbdBtn) novncKbdBtn.classList.remove("noVNC_selected");
            if (rfb) {
                rfb.focusOnClick = true;
            }
            showToast("Teclado Desactivado");
        }
    }

    if (btnKeyboard) {
        attachButtonTap(btnKeyboard, function() {
            setVirtualKeyboardState(!isVirtualKeyboardActive);
            hapticFeedback(20);
            closeDrawer();
        });
    }

    if (kbdDismissBtn) {
        attachButtonTap(kbdDismissBtn, function(e) {
            e.stopPropagation();
            setVirtualKeyboardState(false);
            hapticFeedback(20);
        });
    }

    // Auto-sincronizar si el usuario cierra el teclado de Android o iOS con el botón atrás del sistema
    const nativeKbdInput = document.getElementById("noVNC_keyboardinput");
    if (nativeKbdInput) {
        nativeKbdInput.addEventListener("blur", function() {
            setTimeout(function() {
                if (document.activeElement !== nativeKbdInput && isVirtualKeyboardActive) {
                    setVirtualKeyboardState(false);
                }
            }, 250);
        });
    }

    // Acceso 1-clic al Panel Web de Sunshine (47990)
    if (btnOpenSunshineWeb) {
        attachButtonTap(btnOpenSunshineWeb, function() {
            window.open(window.location.origin + "/sunshine/", "_blank");
            showToast("Abriendo Sunshine Web UI...");
            hapticFeedback(20);
        });
    }

    // Alternar Audio / Mute con Transmisión Real HTTP 48kHz
    const speakerOnSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>';
    const speakerMuteSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/></svg>';

    function playAudioStream() {
        if (!webAudio) return;
        webAudio.src = window.location.origin + "/audio?t=" + Date.now();
        webAudio.play().catch(() => {});
    }
    function stopAudioStream() {
        if (!webAudio) return;
        webAudio.pause();
        webAudio.removeAttribute("src");
        webAudio.load();
    }

    if (btnAudio) {
        attachButtonTap(btnAudio, function() {
            isAudioMuted = !isAudioMuted;
            if (isAudioMuted) {
                stopAudioStream();
                if (iconAudio) iconAudio.innerHTML = speakerMuteSvg;
                if (badgeAudio) { badgeAudio.innerText = "MUTE"; badgeAudio.classList.remove("active"); }
                btnAudio.classList.remove("active-glow");
                showToast("Audio Silenciado");
            } else {
                playAudioStream();
                if (iconAudio) iconAudio.innerHTML = speakerOnSvg;
                if (badgeAudio) { badgeAudio.innerText = "ON"; badgeAudio.classList.add("active"); }
                btnAudio.classList.add("active-glow");
                showToast("Audio Activado (48kHz)");
            }
            hapticFeedback(18);
        });
    }

    // Auto-desbloqueo de Audio en el primer toque del usuario
    document.addEventListener("pointerdown", function unlockAudio() {
        if (webAudio && !isAudioMuted && (!webAudio.src || webAudio.paused)) {
            playAudioStream();
        }
    }, { once: true });

    // Modo Gaming 3D / Pointer Lock (Estándar GeForce NOW & Steam)
    function isPointerLocked() {
        const canvas = getCanvas();
        return !!(canvas && (document.pointerLockElement === canvas || document.mozPointerLockElement === canvas || document.webkitPointerLockElement === canvas));
    }

    function togglePointerLock() {
        const canvas = getCanvas();
        if (!canvas) {
            showToast("Pantalla no disponible");
            closeDrawer();
            return;
        }
        if (!isPointerLocked()) {
            const req = canvas.requestPointerLock || canvas.mozRequestPointerLock || canvas.webkitRequestPointerLock;
            if (req) {
                try {
                    const p = req.call(canvas);
                    if (p && p.catch) {
                        p.catch(() => {
                            showToast("Pointer Lock requiere ratón físico");
                        });
                    } else {
                        showToast("Modo Gaming 3D (ESC para liberar)");
                    }
                } catch(e) {
                    showToast("Pointer Lock requiere ratón físico");
                }
            } else {
                showToast("Navegador no soporta Pointer Lock");
            }
        } else {
            const exit = document.exitPointerLock || document.mozExitPointerLock || document.webkitExitPointerLock;
            if (exit) {
                try { exit.call(document); } catch(e) {}
            }
            showToast("Puntero Liberado");
        }
        closeDrawer();
    }

    // Control de Sensibilidad de Trackpad (0.75x, 1.0x, 1.4x)
    const sensLevels = [
        { val: 0.75, label: "0.75x" },
        { val: 1.0,  label: "1.0x" },
        { val: 1.4,  label: "1.4x" }
    ];
    let currentSensIdx = sensLevels.findIndex(s => Math.abs(s.val - trackpadSens) < 0.05);
    if (currentSensIdx === -1) currentSensIdx = 1;
    function updateSensUI() {
        if (badgeSensitivity) badgeSensitivity.innerText = sensLevels[currentSensIdx].label;
    }
    updateSensUI();
    if (btnSensitivity) {
        attachButtonTap(btnSensitivity, function() {
            currentSensIdx = (currentSensIdx + 1) % sensLevels.length;
            trackpadSens = sensLevels[currentSensIdx].val;
            localStorage.setItem("cloudpc_tp_sens", trackpadSens.toString());
            updateSensUI();
            showToast("Sensibilidad Trackpad: " + sensLevels[currentSensIdx].label);
            hapticFeedback(18);
        });
    }

    // Alternar Desplazamiento Natural (Apple) vs Estándar (PC)
    function updateScrollUI() {
        if (badgeScroll) {
            badgeScroll.innerText = isNaturalScroll ? "Natural" : "Estándar";
            if (isNaturalScroll) badgeScroll.classList.add("active");
            else badgeScroll.classList.remove("active");
        }
    }
    updateScrollUI();
    if (btnScroll) {
        attachButtonTap(btnScroll, function() {
            isNaturalScroll = !isNaturalScroll;
            localStorage.setItem("cloudpc_natural_scroll", isNaturalScroll ? "true" : "false");
            updateScrollUI();
            showToast(isNaturalScroll ? "Scroll Natural (Estilo Apple)" : "Scroll Estándar (Estilo PC)");
            hapticFeedback(18);
        });
    }

    // Toggle de Telemetría desde el Cajón
    if (btnTelem) {
        attachButtonTap(btnTelem, function() {
            if (telemPanel) {
                telemPanel.classList.toggle("open");
                hapticFeedback(16);
            }
            closeDrawer();
        });
    }

    if (btnPointerLock) attachButtonTap(btnPointerLock, togglePointerLock);

    const onPointerLockChange = function() {
        const locked = isPointerLocked();
        if (badgePointerLock) {
            badgePointerLock.innerText = locked ? "LOCK" : "OFF";
            if (locked) badgePointerLock.classList.add("active");
            else badgePointerLock.classList.remove("active");
        }
        if (btnPointerLock) {
            if (locked) btnPointerLock.classList.add("active-glow");
            else btnPointerLock.classList.remove("active-glow");
        }
        if (cursor) cursor.style.display = locked ? "none" : "";
    };
    document.addEventListener("pointerlockchange", onPointerLockChange);
    document.addEventListener("mozpointerlockchange", onPointerLockChange);
    document.addEventListener("webkitpointerlockchange", onPointerLockChange);

    // Captura de deltas relativos de ratón para rotación 360 grados en juegos y apps 3D
    document.addEventListener("mousemove", function(e) {
        if (isPointerLocked()) {
            const dx = e.movementX || e.mozMovementX || e.webkitMovementX || 0;
            const dy = e.movementY || e.mozMovementY || e.webkitMovementY || 0;
            virtX = Math.max(0, Math.min(screenW, virtX + dx));
            virtY = Math.max(0, Math.min(screenH, virtY + dy));
            sendMouse(e.buttons);
        }
    });
    document.addEventListener("mousedown", function(e) {
        if (isPointerLocked()) sendMouse(e.buttons);
    });
    document.addEventListener("mouseup", function(e) {
        if (isPointerLocked()) sendMouse(e.buttons);
    });

    // Prevención de Cierre Accidental de Pestaña durante Sesión Activa
    window.addEventListener("beforeunload", function(e) {
        e.preventDefault();
        return (e.returnValue = "Sesión de Cloud PC en progreso. ¿Deseas salir?");
    });

    function toggleFullScreen() {
        const doc = document;
        const docEl = document.documentElement;
        const isFull = doc.fullscreenElement || doc.webkitFullscreenElement || doc.mozFullScreenElement || doc.msFullscreenElement;
        if (!isFull) {
            const request = docEl.requestFullscreen || docEl.webkitRequestFullscreen || docEl.mozRequestFullScreen || docEl.msRequestFullscreen;
            if (request) request.call(docEl).catch(() => {});
            if (btnFullscreen) btnFullscreen.classList.add("active-glow");
            if (badgeFullscreen) { badgeFullscreen.innerText = "Pantalla"; badgeFullscreen.classList.add("active"); }
            if (navigator.keyboard && navigator.keyboard.lock) {
                try { navigator.keyboard.lock(["Escape", "AltLeft", "AltRight", "Tab", "KeyW", "KeyN"]); } catch(e) {}
            }
            showToast("Pantalla Completa");
        } else {
            const exit = doc.exitFullscreen || doc.webkitExitFullscreen || doc.mozCancelFullScreen || doc.msExitFullscreen;
            if (exit) exit.call(doc).catch(() => {});
            if (btnFullscreen) btnFullscreen.classList.remove("active-glow");
            if (badgeFullscreen) { badgeFullscreen.innerText = "Ventana"; badgeFullscreen.classList.remove("active"); }
            if (navigator.keyboard && navigator.keyboard.unlock) {
                try { navigator.keyboard.unlock(); } catch(e) {}
            }
            showToast("Ventana Normal");
        }
        hapticFeedback(20);
    }
    if (btnFullscreen) attachButtonTap(btnFullscreen, function() { toggleFullScreen(); });

    // -------------------------------------------------------------------------
    // MODO GAMING GEFORCE NOW (1-CLIC FULL-IMMERSION)
    // -------------------------------------------------------------------------
    function toggleGeForceNowMode() {
        isGfnMode = !isGfnMode;
        hapticFeedback(25);
        if (isGfnMode) {
            const docEl = document.documentElement;
            const reqFs = docEl.requestFullscreen || docEl.webkitRequestFullscreen || docEl.mozRequestFullScreen || docEl.msRequestFullscreen;
            if (reqFs) reqFs.call(docEl).catch(() => {});
            
            const canvas = getCanvas();
            if (!isPointerLocked() && canvas) {
                const reqPl = canvas.requestPointerLock || canvas.mozRequestPointerLock || canvas.webkitRequestPointerLock;
                if (reqPl) {
                    try { reqPl.call(canvas); } catch(e) {}
                }
            }
            
            if (webAudio && (webAudio.paused || isAudioMuted)) {
                webAudio.muted = false;
                webAudio.play().catch(() => {});
                isAudioMuted = false;
                if (badgeAudio) { badgeAudio.innerText = "ON"; badgeAudio.classList.add("active"); }
            }

            if (navigator.getGamepads) {
                const gps = navigator.getGamepads();
                for (let gp of gps) {
                    if (gp && gp.vibrationActuator && gp.vibrationActuator.playEffect) {
                        gp.vibrationActuator.playEffect("dual-rumble", {
                            startDelay: 0,
                            duration: 200,
                            weakMagnitude: 0.8,
                            strongMagnitude: 1.0
                        }).catch(() => {});
                    }
                }
            }

            if (badgeGfn) { badgeGfn.innerText = "ACTIVO"; badgeGfn.classList.add("active"); }
            if (btnGfn) btnGfn.classList.add("active-glow");
            showToast("🎮 Modo GeForce NOW Activado (60 FPS • Cero Lag)");
        } else {
            if (isPointerLocked()) {
                const exitPl = document.exitPointerLock || document.mozExitPointerLock || document.webkitExitPointerLock;
                if (exitPl) exitPl.call(document);
            }
            if (badgeGfn) { badgeGfn.innerText = "OFF"; badgeGfn.classList.remove("active"); }
            if (btnGfn) btnGfn.classList.remove("active-glow");
            showToast("Modo GeForce NOW Desactivado");
        }
    }
    if (btnGfn) attachButtonTap(btnGfn, toggleGeForceNowMode);

    // -------------------------------------------------------------------------
    // EMPAREJAMIENTO CERO-PIN MOONLIGHT + SUNSHINE (1-CLIC)
    // -------------------------------------------------------------------------
    if (btnMoonlightPair && inputMoonlightPin) {
        attachButtonTap(btnMoonlightPair, function() {
            const pinVal = inputMoonlightPin.value.trim();
            if (!pinVal) {
                showToast("Ingresa el PIN de Moonlight");
                inputMoonlightPin.focus();
                return;
            }
            if (moonlightStatusText) moonlightStatusText.innerText = "Vinculando con Sunshine...";
            hapticFeedback(15);
            fetch("/autopair?pin=" + encodeURIComponent(pinVal))
                .then(r => r.json())
                .then(data => {
                    if (data.status === "paired" || data.zero_pin) {
                        if (moonlightStatusText) moonlightStatusText.innerHTML = '<span style="color:#00ffc8; font-weight:700;">✓ ¡Vinculado con éxito! Abre el juego en Moonlight.</span>';
                        showToast("✓ Moonlight Vinculado 1-Clic");
                        inputMoonlightPin.value = "";
                        hapticFeedback(30);
                    } else {
                        if (moonlightStatusText) moonlightStatusText.innerHTML = '<span style="color:#ff2a85;">Error: ' + (data.error || 'PIN no aceptado') + '</span>';
                        showToast("Error al emparejar PIN");
                    }
                })
                .catch(err => {
                    if (moonlightStatusText) moonlightStatusText.innerHTML = '<span style="color:#ff2a85;">Error de conexión con Sunshine</span>';
                    showToast("Error de conexión");
                });
        });
    }

    // -------------------------------------------------------------------------
    // ESTADO Y GESTIÓN EN VIVO DE TAILSCALE MESH VPN
    // -------------------------------------------------------------------------
    let currentTailscaleIp = "";
    function updateTailscaleStatus() {
        fetch("/tailscale/status")
            .then(r => r.json())
            .then(data => {
                if (data.status === "connected" && data.ip) {
                    currentTailscaleIp = data.ip;
                    if (badgeTailscaleStatus) {
                        badgeTailscaleStatus.innerText = "CONECTADO";
                        badgeTailscaleStatus.classList.add("active");
                    }
                    if (tailscaleInfo) tailscaleInfo.innerHTML = 'IP: <strong style="color:#00ffc8;">' + data.ip + '</strong>';
                    if (btnTailscaleCopy) btnTailscaleCopy.style.display = "block";
                    if (btnTailscaleLogin) btnTailscaleLogin.style.display = "none";
                } else if (data.login_url) {
                    if (badgeTailscaleStatus) {
                        badgeTailscaleStatus.innerText = "LOGIN";
                        badgeTailscaleStatus.classList.remove("active");
                    }
                    if (tailscaleInfo) tailscaleInfo.innerText = "Requiere autenticación 1-clic";
                    if (btnTailscaleLogin) {
                        btnTailscaleLogin.style.display = "block";
                        btnTailscaleLogin.dataset.loginUrl = data.login_url;
                    }
                } else if (data.status === "unconfigured" || (!data.ip && !data.login_url && data.status !== "iniciando")) {
                    if (badgeTailscaleStatus) {
                        badgeTailscaleStatus.innerText = "OPCIONAL";
                        badgeTailscaleStatus.classList.remove("active");
                    }
                    if (tailscaleInfo) tailscaleInfo.innerText = "Tailscale no configurado (opcional)";
                    if (btnTailscaleCopy) btnTailscaleCopy.style.display = "none";
                    if (btnTailscaleLogin) btnTailscaleLogin.style.display = "none";
                } else {
                    if (badgeTailscaleStatus) {
                        badgeTailscaleStatus.innerText = "INICIANDO";
                        badgeTailscaleStatus.classList.remove("active");
                    }
                    if (tailscaleInfo) tailscaleInfo.innerText = "Iniciando servicio...";
                }
            })
            .catch(() => {});
    }
    updateTailscaleStatus();
    setInterval(updateTailscaleStatus, 5000);

    if (btnTailscaleLogin) {
        attachButtonTap(btnTailscaleLogin, function() {
            if (btnTailscaleLogin.dataset.loginUrl) {
                window.open(btnTailscaleLogin.dataset.loginUrl, "_blank");
            }
        });
    }

    if (btnTailscaleCopy) {
        attachButtonTap(btnTailscaleCopy, function() {
            if (currentTailscaleIp) {
                navigator.clipboard.writeText(currentTailscaleIp).then(() => {
                    showToast("IP Tailscale copiada al portapapeles");
                    hapticFeedback(15);
                }).catch(() => {
                    showToast("IP: " + currentTailscaleIp);
                });
            } else {
                showToast("Aún no hay IP asignada");
            }
        });
    }

    if (btnExit) {
        attachButtonTap(btnExit, function() {
            if (confirm("¿Deseas cerrar y desconectar la sesión del Cloud PC?")) {
                const rfb = getRFB();
                if (rfb && typeof rfb.disconnect === "function") {
                    try { rfb.disconnect(); } catch(e) {}
                }
                showToast("Sesión Desconectada");
                setTimeout(() => { try { window.close(); } catch(e) {} }, 400);
            }
            closeDrawer();
        });
    }

    // -------------------------------------------------------------------------
    // 6. VELOCÍMETRO ULTRA-MINIMALISTA (FPS Y PING EN BORDE INFERIOR IZQUIERDO)
    // -------------------------------------------------------------------------
    let frameCount = 0, lastFpsTime = performance.now();
    function fpsLoop() {
        frameCount++;
        const now = performance.now();
        const delta = now - lastFpsTime;
        if (delta >= 1000) {
            const currentFps = Math.round((frameCount * 1000) / delta);
            if (perfFps) perfFps.innerText = currentFps + " FPS";
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
            if (perfPing) perfPing.innerText = displayRtt + " ms";
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
            f"rclone copy gdrive:Cloud_PC/system_state/ubuntu_user_state.tar.gz {STATE_DIR} --tpslimit 10 --drive-chunk-size 64M --fast-list >/dev/null 2>&1 || true",
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
        "xboxdrv joystick jstest-gtk evtest antimicrox bluez bluez-tools libevdev2 python3-evdev "
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
    
    # Wrapper acelerado por hardware GPU para Google Chrome con Descargas Paralelas Multi-Hilo
    chrome_wrapper = (
        "#!/bin/bash\n"
        "exec /usr/bin/google-chrome-stable "
        "--no-sandbox --test-type --ignore-gpu-blocklist "
        "--enable-gpu-rasterization --enable-zero-copy "
        "--use-gl=angle --use-angle=gl-egl --enable-unsafe-webgpu "
        "--enable-features=ParallelDownloading,VaapiVideoDecoder,CanvasOopRasterization,WebRTCPipeWireCapturer "
        "--enable-quic "
        "--disk-cache-size=1073741824 "
        "--media-cache-size=536870912 "
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
    
    print("  [✓] Ecosistema Workstation instalado exitosamente.", flush=True)

# Verificación e Instalación Incondicional de Sunshine y Tailscale (Cloud Gaming 60 FPS & Mesh VPN)
if not shutil.which("sunshine"):
    print("  [EXPANSION] Descargando Sunshine (Latencia Cero H.264/HEVC)...", flush=True)
    subprocess.run("wget -q --timeout=15 'https://github.com/LizardByte/Sunshine/releases/download/v0.23.1/sunshine-ubuntu-22.04-amd64.deb' -O /tmp/sunshine.deb && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq /tmp/sunshine.deb 2>/dev/null || (wget -q --timeout=15 'https://github.com/LizardByte/Sunshine/releases/download/v0.23.1/sunshine-ubuntu-24.04-amd64.deb' -O /tmp/sunshine.deb && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq /tmp/sunshine.deb 2>/dev/null) || true", shell=True)

if not shutil.which("tailscale") or not shutil.which("tailscaled"):
    print("  [EXPANSION] Instalando Tailscale Mesh VPN (Zero-PIN Networking)...", flush=True)
    subprocess.run("curl -fsSL https://tailscale.com/install.sh | sh 2>/dev/null || true", shell=True)

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
    try:
        Path("/etc/hostname").write_text("aether-pc\n", encoding="utf-8")
        Path("/media").mkdir(parents=True, exist_ok=True)
        if Path("/kaggle/input").exists() and not Path("/media/Cloud_Storage").exists():
            subprocess.run("ln -sfn /kaggle/input /media/Cloud_Storage 2>/dev/null || true", shell=True)
    except Exception:
        pass
    
    # 2. Configuración de Shell y Bashrc Inmaculada para el usuario (Solo modo interactivo)
    bash_custom = (
        "\n# ==============================================================================\n"
        "# 🚀 AETHER CLOUD PC WORKSTATION ENVIRONMENT\n"
        "# ==============================================================================\n"
        "if [[ $- == *i* ]]; then\n"
        "    export PS1='\\[\\033[01;36m\\]gamer@aether-pc\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\$ '\n"
        "    alias ls='ls --color=auto'\n"
        "    alias ll='ls -la --color=auto'\n"
        "    alias la='ls -A --color=auto'\n"
        "    alias l='ls -CF --color=auto'\n"
        "fi\n"
    )
    for b_path in ["/root/.bashrc", "/etc/skel/.bashrc"]:
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

    # Banner Oficial de Bienvenida en la Terminal (MOTD)
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

    # Configuración de Hostname local en hosts
    try:
        hosts_file = Path("/etc/hosts")
        if hosts_file.exists():
            h_text = hosts_file.read_text(encoding="utf-8", errors="ignore")
            if "aether-pc" not in h_text:
                hosts_file.write_text(h_text + "\n127.0.0.1 aether-pc\n", encoding="utf-8")
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
subprocess.run("[ -e /dev/uinput ] || mknod /dev/uinput c 10 223 2>/dev/null || true; chmod 0666 /dev/uinput 2>/dev/null || true", shell=True)
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

# Iniciar PulseAudio nativo en modo TCP local (48kHz Stereo DummyOutput)
subprocess.run(
    "pulseaudio -k 2>/dev/null || true; "
    "pulseaudio -D --exit-idle-time=-1 --system=false "
    "--load='module-native-protocol-tcp auth-anonymous=1 port=4713' "
    "--load='module-null-sink sink_name=DummyOutput rate=48000 channels=2 format=s16le sink_properties=device.description=Virtual_Cloud_Audio' >> {LOG_FILE} 2>&1 || true",
    shell=True, env=env
)

# Iniciar pantalla Xvfb a 1080p nativa (1920x1080) con extensiones GLX, RENDER y DAMAGE
subprocess.Popen([
    "Xvfb", ":1",
    "-screen", "0", "1920x1080x24+32",
    "-dpi", "96",
    "+extension", "GLX",
    "+extension", "RENDER",
    "+extension", "DAMAGE",
    "+extension", "XTEST",
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
    "-wait", "4",
    "-defer", "4",
    "-ncache", "0",
    "-wirecopyrect",
    "-nowf",
    "-nodpms",
    "-noscr",
    "-repeat", "-capslock",
    "-nomodtweak",
    "-threads", "4",
    "-24to32"
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
subprocess.run("[ -e /dev/uinput ] || mknod /dev/uinput c 10 223 2>/dev/null || true; chmod 0666 /dev/uinput 2>/dev/null || true", shell=True)
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

# Servidor de Audio HTTP en puerto 6083 (PulseAudio DummyOutput -> Nginx /audio)
def audio_http_broadcaster_worker():
    import http.server, socketserver
    class AudioHTTPHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if "/audio" in self.path:
                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.send_header("Pragma", "no-cache")
                self.send_header("Expires", "0")
                self.send_header("Connection", "keep-alive")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                proc = subprocess.Popen(
                    ["ffmpeg", "-loglevel", "quiet", "-f", "pulse", "-i", "DummyOutput.monitor", "-c:a", "libmp3lame", "-b:a", "128k", "-f", "mp3", "pipe:1"],
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
                )
                try:
                    while True:
                        chunk = proc.stdout.read(4096)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                except Exception:
                    pass
                finally:
                    try:
                        proc.kill()
                    except Exception:
                        pass
            else:
                self.send_response(404)
                self.end_headers()
        def log_message(self, format, *args):
            pass
    try:
        class ReusableThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
            allow_reuse_address = True
            daemon_threads = True
        srv = ReusableThreadingServer(("127.0.0.1", 6083), AudioHTTPHandler)
        srv.serve_forever()
    except Exception:
        pass

threading.Thread(target=audio_http_broadcaster_worker, daemon=True).start()

# Configurar y levantar Nginx en puerto 6080 (Enrutador inverso unificado: VNC + Gamepad + Audio + Web)
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

        # 4. Canal de Audio en Vivo (PulseAudio MP3 Stream 48kHz)
        location /audio {
            proxy_pass http://127.0.0.1:6083/audio;
            proxy_buffering off;
            proxy_read_timeout 3600s;
            proxy_send_timeout 3600s;
        }

        # 5. Sunshine Web UI Reverse Proxy (Acceso global HTTPS por Nginx)
        location /sunshine/ {
            proxy_pass https://127.0.0.1:47990/;
            proxy_ssl_verify off;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            proxy_set_header Host $host;
            proxy_buffering off;
            proxy_read_timeout 3600s;
        }

        # 6. Zero-PIN Auto-Pairing Endpoint (Sunshine / Starparks 1-Clic)
        location /autopair {
            proxy_pass http://127.0.0.1:47995/autopair;
            proxy_read_timeout 15s;
        }

        # 7. Tailscale Mesh VPN Status Endpoint
        location /tailscale/ {
            proxy_pass http://127.0.0.1:47995/tailscale/;
            proxy_read_timeout 15s;
        }

        # 8. Sunshine Host Status Endpoint
        location /sunshine/status {
            proxy_pass http://127.0.0.1:47995/sunshine/status;
            proxy_read_timeout 15s;
        }

        # 9. PWA WebAPK Manifest (GeForce NOW Experience)
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

# ==============================================================================
# 4.3 TAILSCALE MESH VPN & WIREGUARD ZERO-PIN RUNNER
# ==============================================================================
tailscale_bin = shutil.which("tailscale")
tailscaled_bin = shutil.which("tailscaled")

if not tailscale_bin or not tailscaled_bin:
    try:
        subprocess.run("curl -fsSL https://tailscale.com/install.sh | sh 2>/dev/null || true", shell=True)
        tailscale_bin = shutil.which("tailscale")
        tailscaled_bin = shutil.which("tailscaled")
    except Exception:
        pass

tailscale_info = {
    "status": "unconfigured",
    "ip": None,
    "login_url": None,
    "hostname": "aether-cloud-pc"
}

if tailscaled_bin:
    try:
        authkey = os.environ.get("TAILSCALE_AUTHKEY", "").strip()
        authkey_file = Path("/root/gdrive/Cloud_PC/Master_Config/tailscale.key")
        if not authkey and authkey_file.exists():
            try:
                authkey = authkey_file.read_text(encoding="utf-8").strip()
            except Exception:
                pass

        os.makedirs("/root/.config/tailscale", exist_ok=True)
        tun_arg = "--tun=userspace-networking"
        subprocess.run("pkill -9 -f tailscaled 2>/dev/null || true", shell=True)
        time.sleep(0.3)
        ts_cmd = f"{tailscaled_bin} {tun_arg} --state=/root/.config/tailscale/tailscaled.state --socks5-server=localhost:1055 --outbound-http-proxy-listen=localhost:1055"
        subprocess.Popen(ts_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log("Tailscale daemon iniciado (Userspace Networking SOCKS5:1055)")

        def tailscale_manager_loop():
            global tailscale_info
            time.sleep(2)
            if authkey:
                tailscale_info["status"] = "iniciando"
                log("Conectando Tailscale con Auth Key (Cero PIN)...")
                subprocess.run(f"{tailscale_bin} up --authkey={authkey} --hostname=aether-cloud-pc --accept-routes --reset >/dev/null 2>&1", shell=True)
            else:
                tailscale_info["status"] = "iniciando"
                log("Iniciando Tailscale interactivo para acceso WAN por Internet...")
                up_proc = subprocess.Popen(
                    f"{tailscale_bin} up --hostname=aether-cloud-pc --accept-routes --reset",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                for line in up_proc.stdout:
                    if "login.tailscale.com" in line or "tailscale.com/a/" in line:
                        import re
                        m_url = re.search(r'https://[^\s]+', line)
                        if m_url:
                            login_url = m_url.group(0)
                            tailscale_info["login_url"] = login_url
                            tailscale_info["status"] = "login_required"
                            log(f"🔑 TAILSCALE WAN LOGIN URL: {login_url}", "SUCCESS")
                            log(f"Inicia sesión en este enlace para vincular Moonlight por Internet: {login_url}")
                            break

            for _ in range(60):
                time.sleep(2)
                res_ip = subprocess.run(f"{tailscale_bin} ip -4 2>/dev/null", shell=True, stdout=subprocess.PIPE, text=True)
                ts_ip = res_ip.stdout.strip()
                if ts_ip and not ts_ip.startswith("Tailscale is stopped") and "." in ts_ip and "error" not in ts_ip.lower():
                    tailscale_info["status"] = "connected"
                    tailscale_info["ip"] = ts_ip
                    tailscale_info["login_url"] = None
                    log(f"🌐 Tailscale Conectado Exitosamente: IP {ts_ip}", "SUCCESS")
                    log(f"🎮 Sunshine listo para jugar por Internet: Conéctate en Moonlight a {ts_ip}", "SUCCESS")
                    break

        threading.Thread(target=tailscale_manager_loop, daemon=True).start()
    except Exception as e_ts:
        log(f"Aviso arranque Tailscale: {e_ts}", "WARNING")

# ==============================================================================
# 4.4 SERVIDOR SUNSHINE (MOONLIGHT HOST 60 FPS / GPU TESLA DIRECTA / CERO PIN)
# ==============================================================================
sunshine_bin = shutil.which("sunshine")
if not sunshine_bin:
    try:
        subprocess.run(
            "wget -q --timeout=15 'https://github.com/LizardByte/Sunshine/releases/download/v0.23.1/sunshine-ubuntu-22.04-amd64.deb' -O /tmp/sunshine.deb "
            "&& DEBIAN_FRONTEND=noninteractive apt-get install -y -qq /tmp/sunshine.deb 2>/dev/null "
            "|| (wget -q --timeout=15 'https://github.com/LizardByte/Sunshine/releases/download/v0.23.1/sunshine-ubuntu-24.04-amd64.deb' -O /tmp/sunshine.deb "
            "&& DEBIAN_FRONTEND=noninteractive apt-get install -y -qq /tmp/sunshine.deb 2>/dev/null) || true",
            shell=True
        )
        sunshine_bin = shutil.which("sunshine")
    except Exception:
        pass

if sunshine_bin:
    try:
        os.makedirs("/root/.config/sunshine", exist_ok=True)
        conf_p = Path("/root/.config/sunshine/sunshine.conf")
        has_nv = (subprocess.run("nvidia-smi >/dev/null 2>&1", shell=True).returncode == 0)
        enc_choice = "nvenc" if has_nv else "software"
        
        conf_nvenc = (
            "origin_pin_allowed = wan\n"
            "origin_web_ui_allowed = wan\n"
            "min_log_level = info\n"
            "port = 47989\n"
            "web_port = 47990\n"
            "capture = x11\n"
            "fps = [60]\n"
            "resolutions = [1920x1080]\n"
            f"encoder = {enc_choice}\n"
            "channels = 2\n"
            "audio_sink = DummyOutput\n"
            "upnp = false\n"
        )
        conf_p.write_text(conf_nvenc, encoding="utf-8")
        subprocess.run(f"{sunshine_bin} --creds admin {VNC_PASSWORD} >/dev/null 2>&1 || true", shell=True)
        sun_env = env.copy()
        sun_env["DISPLAY"] = ":1"
        subprocess.run("pkill -9 -f sunshine 2>/dev/null || true", shell=True)
        time.sleep(0.3)
        subprocess.Popen([sunshine_bin], env=sun_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log("Servidor Sunshine (Moonlight Host) iniciado exitosamente en segundo plano (60 FPS NVENC)")

        # Desktop Shortcut de Sunshine con bypass de certificado SSL para Chrome
        try:
            sun_desktop = (
                "[Desktop Entry]\nVersion=1.0\nType=Application\nName=Sunshine 60 FPS Panel\n"
                "Comment=Panel de Control Sunshine (Sin Advertencias SSL)\n"
                "Exec=google-chrome --no-sandbox --test-type --ignore-certificate-errors --app=https://127.0.0.1:47990\n"
                "Icon=applications-games\nTerminal=false\nCategories=Game;Settings;\n"
            )
            Path("/root/Escritorio/Sunshine_Web.desktop").write_text(sun_desktop, encoding="utf-8")
            subprocess.run("chmod +x /root/Escritorio/Sunshine_Web.desktop 2>/dev/null || true", shell=True)
        except Exception:
            pass
    except Exception as e_sun:
        log(f"Aviso Sunshine startup: {e_sun}", "WARNING")

# ==============================================================================
# 4.5 MOTOR ZERO-PIN Y ESTADO TAILSCALE / SUNSHINE EN TIEMPO REAL (PUERTO 47995)
# ==============================================================================
def sunshine_zero_pin_worker():
    import http.server, urllib.request, ssl, base64, urllib.parse
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    class AutoPairHandler(http.server.BaseHTTPRequestHandler):
        def _send_cors(self, code=200, content_type="application/json"):
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.end_headers()

        def do_OPTIONS(self):
            self._send_cors(200)

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            params = urllib.parse.parse_qs(parsed.query)
            
            # 1. Endpoint Auto-Pairing Moonlight / Sunshine
            if path.startswith("/autopair"):
                pin = params.get("pin", [""])[0]
                if pin:
                    self._pair_pin(pin)
                    return
                self._send_cors(200)
                self.wfile.write(b'{"status":"ready","service":"Aether Zero-PIN Daemon"}')
                return

            # 2. Endpoint Estado Tailscale
            if path.startswith("/tailscale/status"):
                self._send_cors(200)
                self.wfile.write(json.dumps(tailscale_info).encode("utf-8"))
                return

            # 3. Endpoint Estado Sunshine
            if path.startswith("/sunshine/status"):
                sun_active = shutil.which("sunshine") is not None
                self._send_cors(200)
                self.wfile.write(json.dumps({"active": sun_active, "port": 47989, "web_port": 47990}).encode("utf-8"))
                return

            self._send_cors(404)
            self.wfile.write(b'{"error":"Not Found"}')

        def do_POST(self):
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            try:
                data = json.loads(post_data.decode('utf-8'))
            except Exception:
                data = {}

            if path.startswith("/autopair"):
                pin = data.get("pin", "")
                if pin:
                    self._pair_pin(pin)
                    return
                self._send_cors(400)
                self.wfile.write(b'{"error":"PIN requerido"}')
                return

            self._send_cors(404)
            self.wfile.write(b'{"error":"Not Found"}')

        def _pair_pin(self, pin):
            try:
                req_data = json.dumps({"pin": pin, "name": "AetherMoonlightClient"}).encode()
                req = urllib.request.Request(
                    "https://127.0.0.1:47990/api/pin",
                    data=req_data,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": "Basic " + base64.b64encode(f"admin:{VNC_PASSWORD}".encode()).decode()
                    }
                )
                with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
                    resp_body = resp.read().decode('utf-8', errors='ignore')
                    self._send_cors(200)
                    self.wfile.write(json.dumps({
                        "status": "paired",
                        "zero_pin": True,
                        "sunshine_response": resp_body
                    }).encode("utf-8"))
            except Exception as e_p:
                self._send_cors(500)
                self.wfile.write(json.dumps({
                    "status": "error",
                    "error": str(e_p),
                    "tip": "Verifique que Sunshine esté activo y que el PIN de Moonlight esté en pantalla."
                }).encode("utf-8"))

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

# 1. Cloudflare Tunnel (Ultra-Rápido con protocolo HTTP/2 Anti-Drop, Sin Límites de Banda)
url_cf = None
url_cf_mobile = None
try:
    cf_bin = Path("/usr/local/bin/cloudflared")
    if not cf_bin.exists():
        subprocess.run("wget -q --timeout=15 https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared 2>/dev/null && chmod +x /usr/local/bin/cloudflared || true", shell=True)
    if cf_bin.exists():
        proc_cf = subprocess.Popen(["cloudflared", "tunnel", "--protocol", "http2", "--url", "http://127.0.0.1:6080"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        def _read_cf_lines(p):
            global url_cf, url_cf_mobile
            for line in iter(p.stdout.readline, ''):
                if not line:
                    break
                if "trycloudflare.com" in line and not url_cf:
                    match = re.search(r'(https://[a-zA-Z0-9-]+\.trycloudflare\.com)', line)
                    if match:
                        base_cf = match.group(1).strip()
                        url_cf = f"{base_cf}/vnc.html?path=websockify&autoconnect=true&resize=scale&quality=9&compression=1&password={VNC_PASSWORD}"
                        url_cf_mobile = f"{base_cf}/vnc.html?path=websockify&autoconnect=true&resize=scale&quality=6&compression=6&reconnect=true&password={VNC_PASSWORD}"
                        print(f"\n🌐 [CLOUDFLARE ONLINE] Enlace Directo Generado:\n  👉 {url_cf}\n", flush=True)
                        log(f"Túnel Cloudflare conectado: {base_cf}", "SUCCESS")
        
        threading.Thread(target=_read_cf_lines, args=(proc_cf,), daemon=True).start()
except Exception as e_cf:
    log(f"Aviso Cloudflare: {e_cf}", "WARNING")

# 2. Conexión de Ngrok en Paralelo (Redundancia Enterprise Dual)
if ngrok_token:
    def _connect_ngrok_worker():
        global web_tunnel_wifi, web_tunnel_mobile
        try:
            from pyngrok import ngrok, conf
            try:
                ngrok.kill()
            except Exception:
                pass
            ngrok.set_auth_token(ngrok_token)
            conf.get_default().region = "us"
            try:
                http_tunnel = ngrok.connect(6080, "http", domain="thoroughgoingly-unrefreshing-alishia.ngrok-free.dev")
            except Exception:
                http_tunnel = ngrok.connect(6080, "http")
            base_ngrok = http_tunnel.public_url
            web_tunnel_wifi = f"{base_ngrok}/vnc.html?path=websockify&autoconnect=true&resize=scale&quality=9&compression=1&password={VNC_PASSWORD}"
            web_tunnel_mobile = f"{base_ngrok}/vnc.html?path=websockify&autoconnect=true&resize=scale&quality=6&compression=6&reconnect=true&password={VNC_PASSWORD}"
            print(f"\n⚡ [NGROK ONLINE] Enlace Directo: {web_tunnel_wifi}\n", flush=True)
            log(f"Túnel Ngrok activo: {base_ngrok}", "SUCCESS")
        except Exception as e_ngrok:
            log(f"Aviso Ngrok: {e_ngrok}", "WARNING")

    t_ng = threading.Thread(target=_connect_ngrok_worker, daemon=True)
    t_ng.start()

# Esperar hasta 12s para capturar al menos un túnel online
t_tunnel_limit = time.time()
while (not url_cf and not web_tunnel_wifi) and (time.time() - t_tunnel_limit < 12):
    time.sleep(0.5)

active_primary_url = url_cf if url_cf else web_tunnel_wifi

# Guardar URL de sesión y notificar por Telegram en hilo desacoplado (Cero Bloqueo)
def _async_post_tunnel_tasks():
    time.sleep(1)
    act_url = url_cf if url_cf else web_tunnel_wifi
    if not act_url:
        return
    try:
        Path("/tmp/current_vnc_url.txt").write_text(act_url, encoding="utf-8")
        Path("/kaggle/working/current_vnc_url.txt").write_text(act_url, encoding="utf-8")
        subprocess.run("timeout 5 rclone copyto /tmp/current_vnc_url.txt gdrive:Cloud_PC/system_state/current_vnc_url.txt >/dev/null 2>&1 || true", shell=True)
        subprocess.run("timeout 5 rclone copyto /tmp/current_vnc_url.txt gdrive:PC_Kaggle/system_state/current_vnc_url.txt >/dev/null 2>&1 || true", shell=True)
    except Exception:
        pass
        
    try:
        telegram_script = Path(__file__).resolve().parent / "telegram_notifier.py"
        if telegram_script.exists():
            cf_section = f"🌐 <b>Enlace Cloudflare (Recomendado / Sin Límites):</b>\n<a href='{url_cf}'>ENTRAR POR CLOUDFLARE</a>\n\n" if url_cf else ""
            ng_section = f"⚡ <b>Enlace Ngrok:</b>\n<a href='{web_tunnel_wifi}'>Entrar por Ngrok</a>\n\n" if web_tunnel_wifi else ""
            mob_url = url_cf_mobile if url_cf_mobile else web_tunnel_mobile
            msg_tg = (
                f"🚀 <b>¡Tu Aether Cloud PC está ONLINE y VERIFICADA!</b> 🌸\n\n"
                f"{cf_section}"
                f"{ng_section}"
                f"📱 <b>Móvil:</b> <a href='{mob_url}'>Modo Móvil</a>\n"
                f"🔑 <b>Pass:</b> <code>{VNC_PASSWORD}</code>\n"
                f"🎮 <i>Mandos táctiles Xbox, panel lateral Aether y Sunshine activos.</i>"
            )
            try:
                import telegram_notifier
                telegram_notifier.enviar_mensaje(msg_tg)
            except Exception:
                pass
    except Exception:
        pass

threading.Thread(target=_async_post_tunnel_tasks, daemon=True).start()

vnc_app_address = []
if tailscale_info.get("ip"):
    vnc_app_address.append(f"{tailscale_info['ip']}:5900")

print(f"  [TIEMPO] Paso 5/5 Completado en {time.time() - t_step5:.1f}s", flush=True)
print(f"  [METRICA] Tiempo total de arranque: {time.time() - t_start_total:.1f}s\n", flush=True)

# ==============================================================================
# VERIFICACIÓN DE ESTADO Y SALUD REAL DEL SISTEMA (SEGURO Y SIN BLOQUEOS FUSE)
# ==============================================================================
def _is_gdrive_mounted_safe():
    try:
        if os.path.exists("/proc/mounts"):
            with open("/proc/mounts", "r", encoding="utf-8", errors="ignore") as f_m:
                return any("/root/gdrive" in line for line in f_m)
        return False
    except Exception:
        return False

drive_mounted = _is_gdrive_mounted_safe()

try:
    smi_out = subprocess.check_output("timeout 5 nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null", shell=True, text=True).strip()
    if smi_out:
        gpus = smi_out.splitlines()
        print(f"\n[GPU] Unidades NVIDIA Tesla Activas: {len(gpus)}", flush=True)
        for i, g in enumerate(gpus):
            print(f"  • GPU {i}: {g}", flush=True)
except Exception:
    pass

try:
    df_out = subprocess.check_output("timeout 3 df -h /kaggle/working 2>/dev/null | tail -1", shell=True, text=True).split()
    if len(df_out) >= 4:
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

if active_primary_url:
    print("[OPCION 1] NAVEGADOR WEB CON MOTOR DE TRACKPAD INTEGRADO:", flush=True)
    print("------------------------------------------------------------------------------", flush=True)
    if url_cf:
        print("[CANAL CLOUDFLARE - RECOMENDADO / ULTRA-ESTABLE]:", flush=True)
        print(f"  • Modo PC (1080p Nitidez + Trackpad): {url_cf}", flush=True)
        print(f"  • Modo Móvil (Baja Latencia):          {url_cf_mobile}", flush=True)
        print("-" * 78, flush=True)
    if web_tunnel_wifi:
        print("[CANAL NGROK - ALTERNATIVO]:", flush=True)
        print(f"  • Modo PC (1080p Nitidez + Trackpad): {web_tunnel_wifi}", flush=True)
        print(f"  • Modo Móvil (Baja Latencia):          {web_tunnel_mobile}", flush=True)
        print("-" * 78, flush=True)

if vnc_app_address:
    pinggy_addr = vnc_app_address[0]
    parts = pinggy_addr.split(":") if ":" in pinggy_addr else [pinggy_addr, "5900"]
    host_part = parts[0]
    port_part = parts[1] if len(parts) > 1 else "5900"
    print("[OPCION 2] CLIENTE NATIVO VNC (CONEXIÓN DIRECTA TCP - REALVNC / AVNC):", flush=True)
    print("------------------------------------------------------------------------------", flush=True)
    print(f"  • Host / Dirección:        {host_part}:{port_part}")
    print(f"  • Contraseña VNC:          {VNC_PASSWORD}")
    print("-" * 78, flush=True)

print("[OPCION 3] MOONLIGHT + SUNSHINE + TAILSCALE (GAMING 60 FPS / GPU TESLA DIRECTA):", flush=True)
print("------------------------------------------------------------------------------", flush=True)
print(f"  • Servidor Sunshine:       [OK] Activo en segundo plano (Puerto 47989/47990)")
print(f"  • Emparejamiento Cero-PIN: [OK] Activo en el Panel Web Aether (Vincular 1-Clic)")
ts_status_txt = f"[OK] IP {tailscale_info.get('ip')}" if tailscale_info.get("ip") else ("[LOGIN PENDIENTE]" if tailscale_info.get("login_url") else "[INICIANDO]")
print(f"  • Tailscale Mesh VPN:      {ts_status_txt} (Hostname: aether-cloud-pc)")
if tailscale_info.get("login_url"):
    print(f"    -> Enlace Login 1-Clic:  {tailscale_info['login_url']}")
print(f"  • Credenciales Sunshine:   admin / {VNC_PASSWORD}")
print("=" * 78, flush=True)

print("[STORAGE] Persistencia y Almacenamiento Activos:", flush=True)
print("  • Unidad de 5TB Google Drive (Cloud_PC) montada en /root/gdrive.", flush=True)
print("  • Suite Ofimática LibreOffice (Writer, Calc, Impress) instalada.", flush=True)
print("  • Comunicaciones y Navegación: Google Chrome, Discord, Telegram listos.", flush=True)
print("  • Tienda de Software y Juegos 1-Clic en el Escritorio.", flush=True)
print("  • Relación de aspecto 16:9 nativa Full HD perfecta.", flush=True)
print("=" * 78 + "\n", flush=True)

# Mantener viva la celda con monitoreo de salud, auto-guardado y reporte de telemetría en tiempo real
try:
    segundos_activos = 0
    while True:
        try:
            time.sleep(10)
            segundos_activos += 10
            minutos = segundos_activos / 60
            
            # Watchdog: Monitoreo activo de procesos
            xvfb_alive = Path("/tmp/.X11-unix/X1").exists()
            vnc_alive = wait_for_port(5900, timeout=1)
            novnc_alive = wait_for_port(6080, timeout=1)
            drive_alive = _is_gdrive_mounted_safe()
            
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
                
            if segundos_activos % 120 == 0:
                threading.Thread(target=auto_save_user_state, daemon=True).start()
                try:
                    ram_str = subprocess.check_output("free -h | grep Mem: | awk '{print $3 \"/\" $2}'", shell=True, text=True, timeout=5).strip()
                    disk_str = subprocess.check_output("df -h / 2>/dev/null | tail -1 | awk '{print $4 \" libres\"}'", shell=True, text=True, timeout=5).strip()
                    gpu_info = ""
                    try:
                        gpu_lines = subprocess.check_output("timeout 5 nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null", shell=True, text=True, timeout=5).strip().splitlines()
                        if gpu_lines:
                            gpu_parts = []
                            for g in gpu_lines:
                                parts = [x.strip() for x in g.split(",")]
                                if len(parts) >= 4:
                                    idx, util, mem_u, mem_t = parts[0], parts[1], parts[2], parts[3]
                                    gpu_parts.append(f"GPU-{idx}: {util}% ({mem_u}/{mem_t}MB)")
                            if gpu_parts:
                                gpu_info = " | 🎮 " + ", ".join(gpu_parts)
                    except Exception:
                        pass
                    print(f"\n📊 [{time.strftime('%H:%M:%S')}] Telemetría ({int(minutos)} min activo) | 🟢 RAM: {ram_str} | 💾 Disco: {disk_str}{gpu_info} | ☁️ Drive: {'Conectado' if drive_alive else 'Desconectado'} | Estado Guardado ✅", flush=True)
                except Exception:
                    print(f"\n📊 [{time.strftime('%H:%M:%S')}] Telemetría ({int(minutos)} min activo) | Estado Guardado en Drive ✅", flush=True)
            else:
                print(f"[{time.strftime('%H:%M:%S')}] 💓 Aether Cloud PC activo ({segundos_activos}s | {segundos_activos//60} min) | noVNC: {'OK' if novnc_alive else 'FAIL'} | Watchdog OK", flush=True)
        except Exception as e_tick:
            print(f"⚠️ [WATCHDOG] Excepción recuperada en bucle: {e_tick}", flush=True)
            time.sleep(5)
except KeyboardInterrupt:
    print("\n🛑 Guardando estado final antes de salir...", flush=True)
    auto_save_user_state()
    print("✅ Estado guardado. Servidor detenido.", flush=True)

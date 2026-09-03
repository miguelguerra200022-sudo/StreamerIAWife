#!/usr/bin/env python3
"""
================================================================================
🐧 COMPILADOR MAESTRO DEFINITIVO: DATABASE 1 - UBUNTU CORE & SUITE GAMER (100GB)
================================================================================
Empaqueta de forma 100% autónoma y profesional el sistema operativo Ubuntu Core:

1. Gráficos & 32-bit Multi-Arch: Mesa Vulkan, VA-API, DRI i386 para Steam & Proton.
2. Audio Virtual Headless: PulseAudio Dummy Sink a 48kHz para streaming nítido.
3. Acelerador GPU Google Chrome: Wrapper con rasterización por hardware y zero-copy.
4. Periféricos SOTA: Gamepad UInput Bridge (Xbox 360 virtual en /dev/uinput).
5. noVNC Dual-Engine: Trackpad Balístico Chrome Remote Desktop + Auto-Detector Gamepad.
6. Suite Gamer: Steam, Lutris, MangoHud, Gamemode, Sunshine 60 FPS, Discord, Telegram.
7. Tienda de Software 1-Clic: Aplicación de escritorio para activar los 20 packs.
8. Test de Velocidad Real Gigabit: Medidor de 10GB/20GB con Aria2 16x.
9. Activador ultra-rápido (setup.py) y Desconectador modular (desconectar_database1.py).
10. Empaquetado Multi-Núcleo con Pigz en RAM (/dev/shm) para 0% uso de los 20GB locales.
================================================================================
"""

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path("/kaggle/working/StreamerIAWife") if Path("/kaggle/working/StreamerIAWife").exists() else Path(__file__).resolve().parent

# Selección de directorio de trabajo ultra-rápido en RAM (/dev/shm) o /tmp (Protege los 20GB locales)
try:
    if Path("/dev/shm").exists() and shutil.disk_usage("/dev/shm").free > 6 * 1024 * 1024 * 1024:
        WORK_DIR = Path("/dev/shm/ubuntu_core_build")
    else:
        WORK_DIR = Path("/tmp/ubuntu_core_build")
except Exception:
    WORK_DIR = Path("/tmp/ubuntu_core_build")

WORK_DIR.mkdir(parents=True, exist_ok=True)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "09032000Mi.").strip()

print("=" * 78, flush=True)
print("🐧 INICIANDO COMPILACIÓN PROFESIONAL SOTA DE DATABASE 1 (UBUNTU CORE & GAMING)...", flush=True)
print("=" * 78, flush=True)

t_start = time.time()

# 1. Configurar credenciales de Kaggle
kaggle_dir = Path.home() / ".kaggle"
kaggle_dir.mkdir(parents=True, exist_ok=True)
kaggle_file = kaggle_dir / "kaggle.json"
legacy_json = BASE_DIR / "kaggle legacy.json"

if not kaggle_file.exists() and legacy_json.exists():
    shutil.copy2(legacy_json, kaggle_file)
    subprocess.run(f"chmod 600 '{kaggle_file}'", shell=True)

# Cargar automáticamente credenciales maestras desde cuentas_kaggle.json si falta kaggle.json
if not kaggle_file.exists():
    cuentas_path = BASE_DIR / "cuentas_kaggle.json"
    if cuentas_path.exists():
        try:
            c_data = json.loads(cuentas_path.read_text(encoding="utf-8"))
            act = c_data.get("cuenta_activa") or "djkevinzito@gmail.com"
            c_info = c_data.get("cuentas", {}).get(act) or list(c_data.get("cuentas", {}).values())[0]
            k_payload = {"username": c_info["username"], "key": c_info["key"]}
            kaggle_file.write_text(json.dumps(k_payload), encoding="utf-8")
            kaggle_file.chmod(0o600)
            os.environ["KAGGLE_USERNAME"] = c_info["username"]
            os.environ["KAGGLE_KEY"] = c_info["key"]
        except Exception:
            pass

os.environ["MASTER_ADMIN_MODE"] = "1"

# 2. Configurar entorno no interactivo y aceleración I/O Multi-Núcleo al 100%
os.environ["DEBIAN_FRONTEND"] = "noninteractive"
os.environ["NEEDRESTART_MODE"] = "a"
os.environ["NEEDRESTART_SUSPEND"] = "1"
os.environ["TMPDIR"] = "/tmp"
os.environ["PIP_CACHE_DIR"] = "/tmp/pip_cache"
os.environ["XDG_CACHE_HOME"] = "/tmp/.cache"

print("⚡ [1/8] Activando DPKG Turbo (force-unsafe-io), Multi-Arch i386 y APT Pipelines...", flush=True)
subprocess.run("dpkg --add-architecture i386", shell=True)
subprocess.run("add-apt-repository -y universe >/dev/null 2>&1 || true", shell=True)
subprocess.run("add-apt-repository -y multiverse >/dev/null 2>&1 || true", shell=True)
subprocess.run("mkdir -p /etc/dpkg/dpkg.cfg.d && echo 'force-unsafe-io' > /etc/dpkg/dpkg.cfg.d/02apt-speedup 2>/dev/null || true", shell=True)

apt_turbo = (
    'Acquire::Languages "none";\n'
    'Acquire::Queue-Mode "host";\n'
    'Acquire::http::Pipeline-Depth "10";\n'
    'APT::Install-Recommends "0";\n'
    'APT::Install-Suggests "0";\n'
    'DPkg::Options { "--force-confdef"; "--force-confold"; "--force-unsafe-io"; };\n'
    'Dir::Cache::pkgcache "";\n'
    'Dir::Cache::srcpkgcache "";\n'
    'APT::Keep-Downloaded-Packages "0";\n'
)
Path("/etc/apt/apt.conf.d/99turbo").write_text(apt_turbo, encoding="utf-8")
subprocess.run("echo 'man-db man-db/auto-update boolean false' | debconf-set-selections 2>/dev/null || true", shell=True)

# Instalar aceleradores de compresión y red
subprocess.run("apt-get update -qq && apt-get install -y -qq pigz pv wget curl git python3-pip aria2 >/dev/null 2>&1", shell=True)
if Path("/usr/bin/pigz").exists():
    subprocess.run("ln -sf /usr/bin/pigz /usr/local/bin/gzip 2>/dev/null || true", shell=True)

# 3. Instalación de Suite de Escritorio XFCE 4.18 y VNC
print("📦 [2/8] Instalando Suite de Escritorio XFCE 4.18, Servidores Gráficos y Utilidades...", flush=True)
subprocess.run("apt-get install -y -qq xfce4 xfce4-terminal xfce4-goodies dbus-x11 x11-xserver-utils x11-utils xterm tigervnc-standalone-server tigervnc-common websockify nginx", shell=True)

# 4. Instalación de Google Chrome Oficial x64 con Wrapper GPU
print("🌐 [3/8] Instalando Google Chrome Oficial con aceleración por hardware GPU (Vulkan/VA-API)...", flush=True)
subprocess.run(
    "wget -q 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb' -O /tmp/chrome.deb && "
    "(apt-get install -y -qq /tmp/chrome.deb || dpkg -i /tmp/chrome.deb || apt-get install -f -y -qq) && rm -f /tmp/chrome.deb",
    shell=True
)

chrome_wrapper = (
    "#!/bin/bash\n"
    "exec /usr/bin/google-chrome-stable "
    "--no-sandbox --test-type --ignore-gpu-blocklist "
    "--enable-gpu-rasterization --enable-zero-copy "
    "--enable-features=VaapiVideoDecoder,CanvasOopRasterization "
    "--disable-dev-shm-usage \"$@\"\n"
)
Path("/usr/local/bin/google-chrome").write_text(chrome_wrapper, encoding="utf-8")
subprocess.run("chmod +x /usr/local/bin/google-chrome", shell=True)

# Wrapper Optimizado para Steam en Entornos Cloud/VNC (Evita cuelgues headless)
steam_wrapper = (
    "#!/bin/bash\n"
    "export STEAM_RUNTIME_PREFER_HOST_LIBRARIES=0\n"
    "export SDL_VIDEO_X11_DGAMOUSE=0\n"
    "export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json:/etc/vulkan/icd.d/nvidia_icd.json\n"
    "REAL_STEAM=\"/usr/games/steam\"\n"
    "[ -x \"$REAL_STEAM\" ] || REAL_STEAM=\"/usr/bin/steam\"\n"
    "exec \"$REAL_STEAM\" \"$@\"\n"
)
Path("/usr/local/bin/steam").write_text(steam_wrapper, encoding="utf-8")
subprocess.run("chmod +x /usr/local/bin/steam 2>/dev/null || true", shell=True)

# 5. Suite Gamer & Multi-Arch 32-bit (Steam, Proton, Lutris, Mandos)
print("🎮 [4/8] Instalando Suite Gamer (Steam, Lutris, MangoHud, Gamemode, Runtimes 32-bit i386)...", flush=True)
subprocess.run(
    "apt-get install -y -qq steam lutris mangohud gamemode xboxdrv joystick jstest-gtk evtest "
    "antimicrox bluez bluez-tools blueman xserver-xorg-input-all xserver-xorg-input-evdev "
    "xdotool xautomation libevdev2 python3-evdev python3-tk "
    "libgl1-mesa-dri:i386 libgl1:i386 libvulkan1:i386 mesa-vulkan-drivers:i386 libasound2-plugins:i386 || "
    "(apt-get --fix-broken install -y -qq && apt-get install -y -qq steam mangohud gamemode antimicrox libgl1:i386 libvulkan1:i386)",
    shell=True
)

# Instalar módulos de Python para Gamepad y Redes
subprocess.run("pip3 install --no-cache-dir websockets evdev pyudev >/dev/null 2>&1 || true", shell=True)

# Configurar permisos de uinput y udev para mandos físicos y virtuales (Xbox, PlayStation, Switch)
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

# Configuración de Aceleración Gráfica Vulkan por Hardware (Nvidia Tesla T4 / DXVK / Proton)
try:
    Path("/etc/vulkan/icd.d").mkdir(parents=True, exist_ok=True)
    nvidia_icd = {
        "file_format_version": "1.0.0",
        "ICD": {
            "library_path": "libGLX_nvidia.so.0",
            "api_version": "1.3.0"
        }
    }
    Path("/etc/vulkan/icd.d/nvidia_icd.json").write_text(json.dumps(nvidia_icd, indent=2), encoding="utf-8")
except Exception:
    pass

# 6. Audio Virtual Headless a 48kHz (PulseAudio Dummy Sink + Latencia Cero)
print("🔊 [5/8] Configurando dispositivo de Audio Virtual Headless (PulseAudio 48kHz)...", flush=True)
try:
    # Optimización de buffer de audio a 48kHz (Elimina chasquidos en Discord y Sunshine)
    pulse_daemon = Path("/etc/pulse/daemon.conf")
    if pulse_daemon.exists():
        p_d_txt = pulse_daemon.read_text(encoding="utf-8")
        if "default-sample-rate = 48000" not in p_d_txt:
            p_d_txt += "\ndefault-sample-rate = 48000\ndefault-sample-channels = 2\ndefault-fragments = 2\ndefault-fragment-size-msec = 10\nresample-method = speex-float-1\n"
            pulse_daemon.write_text(p_d_txt, encoding="utf-8")

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
                "load-module module-native-protocol-tcp auth-anonymous=1\n"
            )
            pulse_cfg.write_text(pulse_text + pulse_extra, encoding="utf-8")
except Exception:
    pass

# 7. Multimedia, Productividad, Herramientas y Comunicaciones
print("⭐ [6/8] Instalando Herramientas, Productividad, Discord, Sunshine y Tailscale...", flush=True)
subprocess.run(
    "apt-get install -y -qq libreoffice-writer libreoffice-calc libreoffice-impress vlc "
    "telegram-desktop plank papirus-icon-theme yaru-theme-gtk yaru-theme-icon flameshot copyq "
    "evince p7zip-full unrar-free pavucontrol onboard redshift redshift-gtk qbittorrent "
    "v4l2loopback-dkms v4l2loopback-utils pulseaudio pulseaudio-utils ffmpeg sox libportaudio2 "
    "wireguard-tools iptables bridge-utils iproute2 kdeconnect qrencode avahi-daemon iputils-ping "
    "traceroute nethogs iftop iperf3 mesa-vulkan-drivers mesa-utils libvulkan1 vulkan-tools",
    shell=True
)

subprocess.run(
    "wget -q 'https://discord.com/api/download?platform=linux&format=deb' -O /tmp/discord.deb && "
    "(apt-get install -y -qq /tmp/discord.deb || dpkg -i /tmp/discord.deb || apt-get install -f -y -qq) && rm -f /tmp/discord.deb",
    shell=True
)

subprocess.run(
    "wget -q 'https://github.com/LizardByte/Sunshine/releases/download/v0.23.1/sunshine-ubuntu-22.04-amd64.deb' -O /tmp/sunshine.deb && "
    "(apt-get install -y -qq /tmp/sunshine.deb || dpkg -i /tmp/sunshine.deb || apt-get install -f -y -qq) && rm -f /tmp/sunshine.deb || true",
    shell=True
)

# Pre-configuración de Sunshine para NVENC 60 FPS sin configuración manual
try:
    sunshine_dir = Path("/etc/sunshine")
    sunshine_dir.mkdir(parents=True, exist_ok=True)
    sunshine_cfg = (
        "origin_pin_allowed = pc\n"
        "encoder = nvenc\n"
        "channels = 2\n"
        "audio_sink = DummyOutput\n"
        "min_log_level = info\n"
        "fec_percentage = 20\n"
    )
    (sunshine_dir / "sunshine.conf").write_text(sunshine_cfg, encoding="utf-8")
except Exception:
    pass

subprocess.run("curl -fsSL https://tailscale.com/install.sh | sh 2>/dev/null || true", shell=True)

# Generación de PWAs oficiales
web_apps = {
    "whatsapp-web": ("WhatsApp Web", "https://web.whatsapp.com", "chat", "Internet;Network;Chat;"),
    "spotify-web": ("Spotify Music", "https://open.spotify.com", "audio-x-generic", "AudioVideo;Audio;Player;"),
    "twitter-x": ("Twitter / X", "https://twitter.com", "internet-web-browser", "Network;WebBrowser;"),
    "instagram-web": ("Instagram", "https://www.instagram.com", "camera-photo", "Network;WebBrowser;"),
    "youtube-music": ("YouTube Music", "https://music.youtube.com", "multimedia-player", "AudioVideo;Audio;Player;"),
    "google-meet": ("Google Meet", "https://meet.google.com", "camera-web", "Network;VideoConference;")
}

os.makedirs("/usr/share/applications", exist_ok=True)
for app_id, (name, url, icon, cats) in web_apps.items():
    pwa_content = (
        f"[Desktop Entry]\nVersion=1.0\nType=Application\nName={name}\n"
        f"Comment=Aplicación oficial de {name}\n"
        f"Exec=google-chrome --no-sandbox --no-first-run --app={url}\n"
        f"Icon={icon}\nTerminal=false\nCategories={cats}\n"
    )
    Path(f"/usr/share/applications/{app_id}.desktop").write_text(pwa_content, encoding="utf-8")

# Configurar XFCE: Eliminar Panel 2 y activar Plank Dock
xfconf_dir = Path.home() / ".config" / "xfce4" / "xfconf" / "xfce-perchannel-xml"
xfconf_dir.mkdir(parents=True, exist_ok=True)
panel_xml = """<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfce4-panel" version="1.0">
  <property name="panels" type="uint" value="1"/>
  <property name="panels">
    <property name="panel-1" type="empty">
      <property name="position" type="string" value="p=6;x=0;y=0"/>
      <property name="length" type="uint" value="100"/>
      <property name="position-locked" type="bool" value="true"/>
      <property name="size" type="uint" value="28"/>
    </property>
  </property>
</channel>
"""
(xfconf_dir / "xfce4-panel.xml").write_text(panel_xml, encoding="utf-8")
os.makedirs("/etc/xdg/xfce4/xfconf/xfce-perchannel-xml", exist_ok=True)
Path("/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml").write_text(panel_xml, encoding="utf-8")

# Autostarts: Plank Dock y Gamepad Uinput Daemon
autostart_dir = Path.home() / ".config" / "autostart"
autostart_dir.mkdir(parents=True, exist_ok=True)
(autostart_dir / "plank.desktop").write_text(
    "[Desktop Entry]\nType=Application\nExec=plank\nHidden=false\nNoDisplay=false\nX-GNOME-Autostart-enabled=true\nName=Plank\n"
)
(autostart_dir / "gamepad-uinput-bridge.desktop").write_text(
    "[Desktop Entry]\nType=Application\nExec=python3 /usr/local/bin/gamepad_uinput_bridge.py\nHidden=false\nNoDisplay=true\nX-GNOME-Autostart-enabled=true\nName=GamepadBridge\n"
)

# Copiar scripts maestros a /usr/local/bin
for sc in ["gamepad_uinput_bridge.py", "tienda_software_1clic.py", "test_velocidad_real.py", "telegram_notifier.py", "escaner_redes_y_conexiones.py"]:
    src = BASE_DIR / sc
    if src.exists():
        shutil.copy2(src, f"/usr/local/bin/{sc}")
        subprocess.run(f"chmod +x '/usr/local/bin/{sc}'", shell=True)

# 8. noVNC Dual-Engine (Trackpad Balístico + Auto-Detector Gamepad)
novnc_dest = WORK_DIR / "noVNC"
if novnc_dest.exists():
    shutil.rmtree(novnc_dest)

print("🚀 [7/8] Clonando y horneando noVNC Dual-Engine (Trackpad Balístico + HTML5 Gamepad)...", flush=True)
subprocess.run(f"git clone --depth 1 https://github.com/novnc/noVNC.git '{novnc_dest}' >/dev/null 2>&1", shell=True)
subprocess.run(f"git clone --depth 1 https://github.com/novnc/websockify.git '{novnc_dest}/utils/websockify' >/dev/null 2>&1", shell=True)

vnc_html_file = novnc_dest / "vnc.html"
if vnc_html_file.exists():
    vnc_html_content = vnc_html_file.read_text(encoding="utf-8", errors="ignore")
    dual_engine_snippet = """
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
/* 1. CLOUD PC PERFORMANCE BADGE (DISCRETO, ADAPTATIVO Y ULTRA-CRISTALINO)    */
/* ========================================================================== */
#cloud-perf-badge {
    position: fixed;
    bottom: calc(8px + var(--safe-bottom));
    left: calc(10px + var(--safe-left));
    background: rgba(10, 15, 26, 0.45);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 3px 8px;
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
    font-size: 10px;
    font-weight: 700;
    color: #f8fafc;
    z-index: 999980;
    pointer-events: none;
    user-select: none;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
    line-height: 1;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
#cloud-perf-badge .perf-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--aether-cyan);
    box-shadow: 0 0 6px var(--aether-cyan);
    transition: background-color 0.3s;
}
#cloud-perf-badge .fps-val { color: var(--aether-cyan); }
#cloud-perf-badge .ping-val { color: var(--aether-blue); }

/* Auto-reubicación inteligente: si los mandos están activos, sube para no estorbar el joystick */
body.tp-gamepad-active #cloud-perf-badge {
    bottom: auto;
    top: calc(8px + var(--safe-top));
    left: calc(125px + var(--safe-left));
}

/* ========================================================================== */
/* 2. PESTAÑA LATERAL AETHER (ERGONOMÍA NATURAL DEL PULGAR A 42% DE ALTURA)   */
/* ========================================================================== */
#aether-edge-tab {
    position: fixed;
    right: 0;
    top: 42%;
    width: 28px;
    height: 56px;
    background: rgba(13, 18, 30, 0.50);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1.5px solid rgba(0, 255, 200, 0.35);
    border-right: none;
    border-radius: 16px 0 0 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--aether-cyan);
    font-size: 18px;
    font-weight: 700;
    z-index: 999990;
    cursor: pointer;
    touch-action: none;
    user-select: none;
    opacity: 0.32; /* Discreto en reposo estilo Apple HIG / Xbox TAK */
    transition: opacity 0.25s ease, background 0.2s ease, width 0.2s ease, box-shadow 0.25s ease;
    box-shadow: -3px 0 14px rgba(0, 255, 200, 0.2);
}
/* Hitbox expandido invisible de 60px para el pulgar */
#aether-edge-tab::before {
    content: "";
    position: absolute;
    right: 0;
    top: -15px;
    width: 60px;
    height: 86px;
}
#aether-edge-tab:hover, #aether-edge-tab:active, #aether-edge-tab.active {
    opacity: 0.95 !important;
    background: rgba(13, 18, 30, 0.92);
    width: 36px;
    box-shadow: -4px 0 22px rgba(0, 255, 200, 0.5);
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

/* Cajón Lateral Desplegable (Side Drawer - Cristal Líquido / Glassmorphism) */
#aether-drawer {
    position: fixed;
    right: 0;
    top: 0;
    width: min(270px, 82vw);
    height: 100vh;
    background: rgba(10, 15, 26, 0.86);
    backdrop-filter: blur(30px) saturate(180%);
    -webkit-backdrop-filter: blur(30px) saturate(180%);
    border-left: 1px solid rgba(0, 255, 200, 0.25);
    box-shadow: -10px 0 45px rgba(0, 0, 0, 0.85);
    z-index: 999998;
    transform: translate3d(100%, 0, 0);
    transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
    display: flex;
    flex-direction: column;
    padding: calc(14px + var(--safe-top)) calc(14px + var(--safe-right)) calc(14px + var(--safe-bottom)) 14px;
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
    padding: 10px 12px;
    display: flex;
    align-items: center;
    gap: 12px;
    color: #f8fafc;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    touch-action: manipulation;
    transition: all 0.2s ease;
}
.drawer-btn:hover, .drawer-btn:active {
    background: rgba(0, 255, 200, 0.18);
    border-color: var(--aether-cyan);
    color: var(--aether-cyan);
}
.drawer-btn.active-glow {
    background: rgba(0, 255, 200, 0.20);
    border-color: var(--aether-cyan);
    color: var(--aether-cyan);
    box-shadow: 0 0 14px rgba(0, 255, 200, 0.35);
}
.drawer-btn .d-icon {
    font-size: 16px;
    width: 22px;
    text-align: center;
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
        width: min(240px, 75vw);
        padding: calc(8px + var(--safe-top)) calc(10px + var(--safe-right)) calc(8px + var(--safe-bottom)) 10px;
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

<!-- 1. BADGE DE RENDIMIENTO INFERIOR IZQUIERDA (DISCRETO Y CRISTALINO) -->
<div id="cloud-perf-badge" title="Rendimiento del Stream en tiempo real">
    <div class="perf-dot" id="perf-status-dot"></div>
    <span class="fps-val" id="perf-fps-text">60 FPS</span>
    <span style="color: rgba(255,255,255,0.25)">•</span>
    <span class="ping-val" id="perf-ping-text">-- ms</span>
</div>

<!-- 2. PESTAÑA LATERAL TRANSPARENTE AETHER -->
<div id="aether-edge-tab" title="Deslizar o tocar para abrir controles">
    ‹
</div>
<div id="aether-scrim"></div>

<!-- 3. CAJÓN LATERAL DE HERRAMIENTAS (AETHER SIDE DRAWER) -->
<div id="aether-drawer">
    <div class="drawer-header">
        <div class="drawer-title">⚡ Aether Control Panel</div>
        <button class="drawer-close" id="btn-drawer-close">›</button>
    </div>
    <div class="drawer-items">
        <button class="drawer-btn" id="btn-aether-gamepad">
            <span class="d-icon">🎮</span>
            <span id="label-aether-gamepad">Mandos en Pantalla: OFF</span>
        </button>
        <button class="drawer-btn active-glow" id="btn-aether-mode">
            <span class="d-icon" id="icon-aether-mode">🖱️</span>
            <span id="label-aether-mode">Modo Trackpad</span>
        </button>
        <button class="drawer-btn" id="btn-aether-keyboard">
            <span class="d-icon">⌨️</span>
            <span>Teclado en Pantalla</span>
        </button>
        <button class="drawer-btn" id="btn-aether-aspect">
            <span class="d-icon">📺</span>
            <span id="label-aether-aspect">Pantalla: Ajuste 16:9</span>
        </button>
        <button class="drawer-btn" id="btn-aether-zoom">
            <span class="d-icon">🔍</span>
            <span id="label-aether-zoom">Restablecer Zoom (100%)</span>
        </button>
        <button class="drawer-btn" id="btn-aether-audio">
            <span class="d-icon" id="icon-aether-audio">🔊</span>
            <span id="label-aether-audio">Audio: Activado</span>
        </button>
        <button class="drawer-btn" id="btn-aether-fullscreen">
            <span class="d-icon">⛶</span>
            <span>Pantalla Completa</span>
        </button>
    </div>
    <div class="drawer-footer">
        <button class="drawer-exit-btn" id="btn-aether-exit">🚪 Desconectar Sesión</button>
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
    const labelGamepad = document.getElementById("label-aether-gamepad");
    const btnMode = document.getElementById("btn-aether-mode");
    const iconMode = document.getElementById("icon-aether-mode");
    const labelMode = document.getElementById("label-aether-mode");
    const btnKeyboard = document.getElementById("btn-aether-keyboard");
    const btnAspect = document.getElementById("btn-aether-aspect");
    const labelAspect = document.getElementById("label-aether-aspect");
    const btnZoom = document.getElementById("btn-aether-zoom");
    const btnAudio = document.getElementById("btn-aether-audio");
    const iconAudio = document.getElementById("icon-aether-audio");
    const labelAudio = document.getElementById("label-aether-audio");
    const btnFullscreen = document.getElementById("btn-aether-fullscreen");
    const btnExit = document.getElementById("btn-aether-exit");

    const gpOverlay = document.getElementById("virtual-gamepad-overlay");
    const leftStickZone = document.getElementById("left-stick-zone");
    const leftStickThumb = document.getElementById("left-stick-thumb");
    const rightStickZone = document.getElementById("right-stick-zone");
    const rightStickThumb = document.getElementById("right-stick-thumb");

    const perfFps = document.getElementById("perf-fps-text");
    const perfPing = document.getElementById("perf-ping-text");
    const perfDot = document.getElementById("perf-status-dot");

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
                console.log("🎮 Gamepad UInput bridge conectado con éxito:", wsPath);
                showToast("🎮 Mando Conectado al Kernel");
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
        console.log("🎮 Mando físico conectado:", e.gamepad.id);
        const name = e.gamepad.id.length > 20 ? e.gamepad.id.substring(0, 20) + "..." : e.gamepad.id;
        showToast("🎮 Mando: " + name);
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
            labelGamepad.innerText = "Mandos en Pantalla: ON";
            btnGamepad.classList.add("active-glow");
            document.body.classList.add("tp-gamepad-active");
            initGamepadWebSocket();
            showToast("🎮 Mandos Táctiles Xbox Activados");
        } else {
            gpOverlay.classList.remove("visible");
            labelGamepad.innerText = "Mandos en Pantalla: OFF";
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

    function setInputMode(mode) {
        currentMode = mode;
        localStorage.setItem("cloudpc_input_mode", mode);
        if (mode === "TRACKPAD") {
            document.body.classList.add("tp-trackpad-mode");
            document.body.classList.remove("tp-touch-mode");
            iconMode.innerText = "🖱️";
            labelMode.innerText = "Modo Trackpad";
            showToast("Modo Trackpad Activo (Estilo Laptop)");
        } else {
            document.body.classList.add("tp-touch-mode");
            document.body.classList.remove("tp-trackpad-mode");
            iconMode.innerText = "👆";
            labelMode.innerText = "Modo Táctil Directo";
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
                if (labelAspect) labelAspect.innerText = "Pantalla: Estirada (20:9)";
                if (btnAspect) btnAspect.classList.add("active-glow");
            } else {
                canvas.style.objectFit = "contain";
                canvas.style.width = "100%";
                canvas.style.height = "100%";
                if (labelAspect) labelAspect.innerText = "Pantalla: Ajuste 16:9";
                if (btnAspect) btnAspect.classList.remove("active-glow");
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
    if (btnAudio) {
        attachButtonTap(btnAudio, function() {
            isAudioMuted = !isAudioMuted;
            const rfb = getRFB();
            if (isAudioMuted) {
                iconAudio.innerText = "🔇";
                labelAudio.innerText = "Audio: Silenciado";
                btnAudio.classList.remove("active-glow");
                showToast("Audio Silenciado");
            } else {
                iconAudio.innerText = "🔊";
                labelAudio.innerText = "Audio: Activado";
                btnAudio.classList.add("active-glow");
                showToast("Audio Activado");
            }
            hapticFeedback(18);
        });
    }

    function toggleFullScreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(() => {});
            if (btnFullscreen) btnFullscreen.classList.add("active-glow");
            showToast("Pantalla Completa");
        } else {
            document.exitFullscreen().catch(() => {});
            if (btnFullscreen) btnFullscreen.classList.remove("active-glow");
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
    // 6. MEDICIÓN DE FPS Y LATENCIA (BADGE INFERIOR IZQUIERDA)
    // -------------------------------------------------------------------------
    let frameCount = 0, lastFpsTime = performance.now();
    function fpsLoop() {
        frameCount++;
        const now = performance.now();
        const delta = now - lastFpsTime;
        if (delta >= 1000) {
            const currentFps = Math.round((frameCount * 1000) / delta);
            if (perfFps) perfFps.innerText = currentFps + " FPS";
            if (perfDot) {
                perfDot.style.backgroundColor = currentFps >= 45 ? "#00ffc8" : (currentFps >= 25 ? "#facc15" : "#f43f5e");
                perfDot.style.boxShadow = "0 0 6px " + perfDot.style.backgroundColor;
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
            if (perfPing) perfPing.innerText = (rtt > 0 ? rtt : "< 40") + " ms";
        };
    }
    setInterval(measureNetworkPing, 2500);
    measureNetworkPing();

    // Inicializar estados guardados
    setInputMode(currentMode);
    if (isGamepadVisible) setGamepadVisibility(true);
    const savedAspect = localStorage.getItem("cloudpc_aspect") === "stretched";
    if (savedAspect) applyAspect(true);
})();
</script>"""
    vnc_html_file.write_text(vnc_html_content.replace("</body>", f"{dual_engine_snippet}\n</body>"), encoding="utf-8")

# 9. Empaquetado Maestro RootFS en /dev/shm
print("💾 [8/8] Empaquetando RootFS Maestro con Pigz (ubuntu_master_rootfs.tar.data)...", flush=True)
rootfs_tar = WORK_DIR / "ubuntu_master_rootfs.tar.data"

excludes = (
    "--exclude='/root/gdrive' --exclude='/kaggle' --exclude='/proc' --exclude='/sys' "
    "--exclude='/dev' --exclude='/tmp' --exclude='/run' --exclude='/usr/src' "
    "--exclude='/usr/share/doc' --exclude='/usr/share/man' --exclude='/opt/conda' "
    "--exclude='/usr/local/cuda*' --exclude='/usr/local/share' --exclude='/var/cache' "
    "--exclude='/var/log' --exclude='/var/tmp' --exclude='/root/.cache' --exclude='/root/.npm'"
)

cmd_tar = f"tar {excludes} -cf - /usr /opt /etc /var/lib/dpkg /var/lib/apt 2>/dev/null | pv -f -pterb | pigz -4 > '{rootfs_tar}'"
subprocess.run(cmd_tar, shell=True)

# 10. Generar Script de Activación en 1 Segundo (setup.py)
setup_script = WORK_DIR / "setup.py"
setup_code = """#!/usr/bin/env python3
import os, sys, shutil, subprocess
from pathlib import Path

print("⚡ [✓] Activando Database 1 (Ubuntu Core & Suite Gamer)...")
DATASET_DIR = Path(__file__).resolve().parent
DESKTOP_DIR = Path.home() / "Desktop"
DESKTOP_DIR.mkdir(parents=True, exist_ok=True)

# 1. Asegurar Permisos de Periféricos y Audio Virtual
os.system("chmod 666 /dev/uinput 2>/dev/null || true")
os.system("pactl set-default-sink DummyOutput 2>/dev/null || true")
os.system("pgrep -f gamepad_uinput_bridge.py >/dev/null || (python3 /usr/local/bin/gamepad_uinput_bridge.py >/dev/null 2>&1 &)")

# 2. Accesos Directos Principales en el Escritorio
main_shortcuts = {
    "Tienda_Software_1Clic.desktop": (
        "[Desktop Entry]\\nVersion=1.0\\nType=Application\\n"
        "Name=🛍️ Tienda de Software & Juegos 1-Clic\\n"
        "Comment=Explora e instala juegos, emuladores y herramientas en 1 clic\\n"
        "Exec=python3 /usr/local/bin/tienda_software_1clic.py\\n"
        "Icon=system-software-install\\nTerminal=false\\nCategories=System;\\n"
    ),
    "Test_Velocidad_Gigabit.desktop": (
        "[Desktop Entry]\\nVersion=1.0\\nType=Application\\n"
        "Name=🚀 Test de Velocidad Real Gigabit (10GB-20GB)\\n"
        "Comment=Prueba de ancho de banda Gigabit real con Aria2 16x y auto-borrado\\n"
        "Exec=python3 /usr/local/bin/test_velocidad_real.py\\n"
        "Icon=network-transmit-receive\\nTerminal=true\\nCategories=Network;\\n"
    ),
    "Escaner_Redes_Conexiones.desktop": (
        "[Desktop Entry]\\nVersion=1.0\\nType=Application\\n"
        "Name=🔍 Escáner de Redes, WiFi y Conexiones\\n"
        "Comment=Auditoría de adaptadores de red, puertos de servicio y conexiones de afuera\\n"
        "Exec=xfce4-terminal --title='Escáner de Redes y Conexiones' -e 'bash -c \"python3 /usr/local/bin/escaner_redes_y_conexiones.py; echo; read -p \\\"Presiona Enter para salir...\\\"\"'\\n"
        "Icon=network-wired\\nTerminal=false\\nCategories=Network;System;\\n"
    )
}

for name, cont in main_shortcuts.items():
    s = DESKTOP_DIR / name
    s.write_text(cont, encoding="utf-8")
    s.chmod(0o755)

# 3. Carpeta Organizada de Suite Core y Redes
folder = DESKTOP_DIR / "📁 [01] Ubuntu Core & Redes Sociales"
folder.mkdir(parents=True, exist_ok=True)

core_shortcuts = {
    "Google_Chrome.desktop": "[Desktop Entry]\\nVersion=1.0\\nType=Application\\nName=Google Chrome (GPU)\\nExec=google-chrome\\nIcon=google-chrome\\nTerminal=false\\nCategories=Network;WebBrowser;\\n",
    "Steam_Gamer.desktop": "[Desktop Entry]\\nVersion=1.0\\nType=Application\\nName=Steam (Juegos PC)\\nExec=steam\\nIcon=steam\\nTerminal=false\\nCategories=Game;\\n",
    "Discord.desktop": "[Desktop Entry]\\nVersion=1.0\\nType=Application\\nName=Discord\\nExec=discord\\nIcon=discord\\nTerminal=false\\nCategories=Network;InstantMessaging;\\n",
    "Telegram.desktop": "[Desktop Entry]\\nVersion=1.0\\nType=Application\\nName=Telegram Desktop\\nExec=telegram-desktop\\nIcon=telegram\\nTerminal=false\\nCategories=Network;InstantMessaging;\\n",
    "Sunshine_Streamer.desktop": "[Desktop Entry]\\nVersion=1.0\\nType=Application\\nName=Sunshine 60 FPS Panel\\nExec=google-chrome https://localhost:47990\\nIcon=input-gaming\\nTerminal=false\\nCategories=Settings;\\n",
    "Calibrador_Mandos.desktop": "[Desktop Entry]\\nVersion=1.0\\nType=Application\\nName=🎮 Calibrador de Mandos (JSTest GTK)\\nExec=jstest-gtk\\nIcon=input-gaming\\nTerminal=false\\nCategories=Game;Settings;\\n",
    "Mapeador_AntiMicroX.desktop": "[Desktop Entry]\\nVersion=1.0\\nType=Application\\nName=🎮 Mapeador AntiMicroX (Mandos a Teclado/Mouse)\\nExec=antimicrox\\nIcon=input-gaming\\nTerminal=false\\nCategories=Game;Utility;\\n",
    "Bluetooth_Manager.desktop": "[Desktop Entry]\\nVersion=1.0\\nType=Application\\nName=📶 Gestor Bluetooth (Emparejar Mandos y Teclados)\\nExec=blueman-manager\\nIcon=preferences-system-bluetooth\\nTerminal=false\\nCategories=Settings;\\n",
    "Teclado_Tactil.desktop": "[Desktop Entry]\\nVersion=1.0\\nType=Application\\nName=⌨️ Teclado en Pantalla (Onboard)\\nExec=onboard\\nIcon=input-keyboard\\nTerminal=false\\nCategories=Utility;\\n"
}

for name, cont in core_shortcuts.items():
    s = folder / name
    s.write_text(cont, encoding="utf-8")
    s.chmod(0o755)

# Marcar lanzadores como confiables en XFCE
os.system("chmod +x ~/Desktop/*.desktop ~/Desktop/*/*.desktop 2>/dev/null || true")
os.system("gio set ~/Desktop/*.desktop metadata::trusted true 2>/dev/null || true")
os.system("gio set ~/Desktop/*/*.desktop metadata::trusted true 2>/dev/null || true")

print("🎉 [✓] ¡Database 1 (Ubuntu Core & Suite Gamer) 100% activa en 1 segundo!")
"""
setup_script.write_text(setup_code, encoding="utf-8")
setup_script.chmod(0o755)

# Copiar desconectar_database1.py a WORK_DIR
if (BASE_DIR / "desconectar_database1.py").exists():
    shutil.copy2(BASE_DIR / "desconectar_database1.py", WORK_DIR / "desconectar_database1.py")
    subprocess.run(f"chmod +x '{WORK_DIR}/desconectar_database1.py'", shell=True)

# 11. Metadatos Oficiales para Kaggle Datasets
usuario_activo = "miguelguerra26"
if kaggle_file.exists():
    try:
        data = json.loads(kaggle_file.read_text())
        if data.get("username"):
            usuario_activo = data["username"]
    except Exception:
        pass

metadata = {
    "title": "Ubuntu - Core Desktop & Social Hub",
    "id": f"{usuario_activo}/ubuntu-core-os-social",
    "licenses": [{"name": "CC0-1.0"}],
    "isPrivate": True
}
(WORK_DIR / "dataset-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

# 12. Subida Segura a Kaggle (100% PRIVADA - Blindaje Anti-Robo)
ts_msg = time.strftime("%Y-%m-%d %H:%M:%S")
print(f"☁️ Subiendo versión privada a {usuario_activo}/ubuntu-core-os-social...", flush=True)
cmd_version = f"kaggle datasets version -p '{WORK_DIR}' -m 'Compilacion SOTA Core + Gaming + Audio + Dual-Engine ({ts_msg})' --dir-mode tar"
res = subprocess.run(cmd_version, shell=True)

if res.returncode != 0:
    print("Intentando crear dataset inicial 100% PRIVADO...", flush=True)
    res = subprocess.run(f"kaggle datasets create -p '{WORK_DIR}' -r tar", shell=True)

# 13. Auto-Registro Instantáneo en el Catálogo de la Tienda (Zero-Comandos)
try:
    cat_file = BASE_DIR / "catalogo_tienda.json"
    if cat_file.exists():
        cat_data = json.loads(cat_file.read_text(encoding="utf-8"))
        existing = next((x for x in cat_data if x.get("id") == 1 or x.get("slug") == "ubuntu-core-os-social"), None)
        entry = {
            "id": 1,
            "name": "Ubuntu Core & Social Hub",
            "slug": "ubuntu-core-os-social",
            "cat": "Sistema Base",
            "desc": "Escritorio XFCE Dark, Google Chrome GPU, Steam, Discord, Telegram, noVNC Trackpad.",
            "icon": "computer"
        }
        if existing: existing.update(entry)
        else: cat_data.insert(0, entry)
        cat_file.write_text(json.dumps(cat_data, indent=2, ensure_ascii=False), encoding="utf-8")
        subprocess.run(f"cd '{BASE_DIR}' && git add catalogo_tienda.json && git commit -m 'Auto-Catalog: Sincronizar Database 1 en la nube' && git push origin main >/dev/null 2>&1 || true", shell=True)
        print("📢 [✓] ¡Catálogo de la Tienda actualizado automáticamente en la nube!", flush=True)
except Exception:
    pass

t_total = time.time() - t_start
print("=" * 78, flush=True)
print(f"🎉 ¡DATABASE 1 COMPILADA CON ÉXITO TOTAL EN {t_total:.1f} SEGUNDOS!", flush=True)
print(f"📦 Tamaño empaquetado: {rootfs_tar.stat().st_size / (1024**3):.2f} GB")
print("=" * 78, flush=True)

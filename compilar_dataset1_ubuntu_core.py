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

# 2. Configurar entorno no interactivo y aceleración I/O Multi-Núcleo al 100%
os.environ["DEBIAN_FRONTEND"] = "noninteractive"
os.environ["NEEDRESTART_MODE"] = "a"
os.environ["NEEDRESTART_SUSPEND"] = "1"
os.environ["TMPDIR"] = "/tmp"
os.environ["PIP_CACHE_DIR"] = "/tmp/pip_cache"
os.environ["XDG_CACHE_HOME"] = "/tmp/.cache"

print("⚡ [1/8] Activando DPKG Turbo (force-unsafe-io), Multi-Arch i386 y APT Pipelines...", flush=True)
subprocess.run("dpkg --add-architecture i386", shell=True)
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
subprocess.run("apt-get install -y -qq xfce4 xfce4-terminal xfce4-goodies dbus-x11 x11-xserver-utils x11-utils xterm tigervnc-standalone-server tigervnc-common websockify", shell=True)

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

# 5. Suite Gamer & Multi-Arch 32-bit (Steam, Proton, Lutris, Mandos)
print("🎮 [4/8] Instalando Suite Gamer (Steam, Lutris, MangoHud, Gamemode, Runtimes 32-bit i386)...", flush=True)
subprocess.run(
    "apt-get install -y -qq steam lutris mangohud gamemode xboxdrv joystick jstest-gtk evtest "
    "antimicrox bluez bluez-tools blueman xserver-xorg-input-all xserver-xorg-input-evdev "
    "xdotool xautomation libevdev2 python3-evdev python3-tk "
    "libgl1-mesa-dri:i386 libgl1:i386 libvulkan1:i386 mesa-vulkan-drivers:i386 libasound2-plugins:i386",
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

# 6. Audio Virtual Headless a 48kHz (PulseAudio Dummy Sink)
print("🔊 [5/8] Configurando dispositivo de Audio Virtual Headless (PulseAudio 48kHz)...", flush=True)
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
for sc in ["gamepad_uinput_bridge.py", "tienda_software_1clic.py", "test_velocidad_real.py", "telegram_notifier.py"]:
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
#linu-virtual-cursor {
    position: fixed; width: 24px; height: 24px; pointer-events: none;
    z-index: 999999; transform: translate3d(0, 0, 0); display: none;
    filter: drop-shadow(0 2px 5px rgba(0,0,0,0.85)); will-change: transform;
}
body.tp-active #linu-virtual-cursor { display: block; }
</style>
<svg id="linu-virtual-cursor" viewBox="0 0 24 24" fill="#ffffff" stroke="#000000" stroke-width="1.6">
    <path d="M4 4l7 17 2.5-6.5L20 12 4 4z"/>
</svg>
<script>
(function() {
    // 1. Motor de Trackpad Balístico Chrome Remote Desktop
    const cursor = document.getElementById("linu-virtual-cursor");
    let isTrackpadEnabled = true;
    let virtX = 960, virtY = 540;
    const screenW = 1920, screenH = 1080;
    function getRFB() { return (window.UI && window.UI.rfb) ? window.UI.rfb : null; }
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
        if (navigator.vibrate) { try { navigator.vibrate(pattern); } catch(e) {} }
    }
    let startX = 0, startY = 0, lastX = 0, lastY = 0, touchStartTime = 0;
    let isTouching = false, totalMoved = 0, isDragging = false, dragHoldTimer = null, initialTouchCount = 0;

    window.addEventListener("touchstart", function(e) {
        if (!isTrackpadEnabled || e.target.closest("#noVNC_control_bar")) return;
        initialTouchCount = e.touches.length;
        touchStartTime = performance.now();
        totalMoved = 0;
        if (e.touches.length === 1) {
            isTouching = true; isDragging = false;
            startX = lastX = e.touches[0].clientX;
            startY = lastY = e.touches[0].clientY;
            clearTimeout(dragHoldTimer);
            dragHoldTimer = setTimeout(function() {
                if (isTouching && totalMoved < 15 && e.touches.length === 1) {
                    isDragging = true; hapticFeedback(25); sendMouse(1);
                }
            }, 250);
        } else if (e.touches.length === 2) {
            clearTimeout(dragHoldTimer); isDragging = false;
            lastY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
        } else { clearTimeout(dragHoldTimer); }
    }, { passive: false });

    window.addEventListener("touchmove", function(e) {
        if (!isTrackpadEnabled || e.target.closest("#noVNC_control_bar")) return;
        if (isTouching && e.touches.length === 1) {
            e.preventDefault();
            const curX = e.touches[0].clientX, curY = e.touches[0].clientY;
            const dx = curX - lastX, dy = curY - lastY;
            lastX = curX; lastY = curY;
            const dist = Math.hypot(dx, dy);
            totalMoved += dist;
            if (totalMoved > 10 && !isDragging) clearTimeout(dragHoldTimer);
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
            if (dy > 10) { sendMouse(16); setTimeout(() => sendMouse(0), 30); }
            else if (dy < -10) { sendMouse(8); setTimeout(() => sendMouse(0), 30); }
        }
    }, { passive: false });

    window.addEventListener("touchend", function(e) {
        if (!isTrackpadEnabled || e.target.closest("#noVNC_control_bar")) return;
        clearTimeout(dragHoldTimer);
        const duration = performance.now() - touchStartTime;
        if (isDragging) {
            isDragging = false; sendMouse(0); hapticFeedback(12); return;
        }
        if (e.touches.length === 0) {
            isTouching = false;
            if (initialTouchCount === 1 && duration < 220 && totalMoved < 10) {
                hapticFeedback(12); sendMouse(1); setTimeout(() => sendMouse(0), 40);
            } else if (initialTouchCount === 2 && duration < 260) {
                hapticFeedback([12, 35, 12]); sendMouse(4); setTimeout(() => sendMouse(0), 40);
            } else if (initialTouchCount === 3 && duration < 280) {
                hapticFeedback(20); sendMouse(2); setTimeout(() => sendMouse(0), 40);
            }
            initialTouchCount = 0;
        }
    }, { passive: false });
    document.body.classList.add("tp-active");
    updateCursorElement();

    // 2. Detector Plug & Play de Mandos (HTML5 Gamepad API -> WS:6081)
    let gpSocket = null, connectedGpIndex = -1;
    function initGpSocket() {
        if (gpSocket && gpSocket.readyState === WebSocket.OPEN) return;
        const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = proto + "//" + window.location.hostname + ":6081";
        try {
            gpSocket = new WebSocket(wsUrl);
            gpSocket.onopen = function() { console.log("🎮 Gamepad uinput bridge conectado."); };
        } catch(e) {}
    }
    function checkGamepads() {
        const gamepads = navigator.getGamepads ? navigator.getGamepads() : [];
        for (let i = 0; i < gamepads.length; i++) {
            const gp = gamepads[i];
            if (gp && gp.connected) {
                if (connectedGpIndex === -1) {
                    connectedGpIndex = gp.index;
                    initGpSocket();
                    if (gp.vibrationActuator && typeof gp.vibrationActuator.playEffect === "function") {
                        gp.vibrationActuator.playEffect("dual-rumble", { startDelay: 0, duration: 150, weakMagnitude: 0.5, strongMagnitude: 0.5 });
                    }
                }
                if (gpSocket && gpSocket.readyState === WebSocket.OPEN) {
                    const buttons = gp.buttons.map(b => b.pressed ? 1 : 0);
                    const axes = [
                        Math.abs(gp.axes[0]) > 0.08 ? gp.axes[0] : 0,
                        Math.abs(gp.axes[1]) > 0.08 ? gp.axes[1] : 0,
                        Math.abs(gp.axes[2]) > 0.08 ? gp.axes[2] : 0,
                        Math.abs(gp.axes[3]) > 0.08 ? gp.axes[3] : 0
                    ];
                    gpSocket.send(JSON.stringify({ axes: axes, buttons: buttons }));
                }
                return;
            }
        }
        connectedGpIndex = -1;
    }
    function gpLoop() {
        checkGamepads();
        requestAnimationFrame(gpLoop);
    }
    requestAnimationFrame(gpLoop);
})();
</script>
"""
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

# 1. Accesos Directos Principales en el Escritorio
main_shortcuts = {
    "Tienda_Software_1Clic.desktop": (
        "[Desktop Entry]\\nVersion=1.0\\nType=Application\\n"
        "Name=🛍️ Tienda de Software & Juegos 1-Clic\\n"
        "Comment=Explora e instala cualquiera de los 20 packs de 100GB en 1 clic\\n"
        "Exec=python3 /usr/local/bin/tienda_software_1clic.py\\n"
        "Icon=system-software-install\\nTerminal=false\\nCategories=System;\\n"
    ),
    "Test_Velocidad_Gigabit.desktop": (
        "[Desktop Entry]\\nVersion=1.0\\nType=Application\\n"
        "Name=🚀 Test de Velocidad Real Gigabit (10GB-20GB)\\n"
        "Comment=Prueba de ancho de banda Gigabit real con Aria2 16x y auto-borrado\\n"
        "Exec=python3 /usr/local/bin/test_velocidad_real.py\\n"
        "Icon=network-transmit-receive\\nTerminal=true\\nCategories=Network;\\n"
    )
}

for name, cont in main_shortcuts.items():
    s = DESKTOP_DIR / name
    s.write_text(cont, encoding="utf-8")
    s.chmod(0o755)

# 2. Carpeta Organizada de Suite Core y Redes
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
    "licenses": [{"name": "CC0-1.0"}]
}
(WORK_DIR / "dataset-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

# 12. Subida a Kaggle (Solo cuando se ejecute explícitamente en la nube)
ts_msg = time.strftime("%Y-%m-%d %H:%M:%S")
print(f"☁️ Subiendo versión a {usuario_activo}/ubuntu-core-os-social...", flush=True)
cmd_version = f"kaggle datasets version -p '{WORK_DIR}' -m 'Compilacion SOTA Core + Gaming + Audio + Dual-Engine ({ts_msg})' --dir-mode tar"
res = subprocess.run(cmd_version, shell=True)

if res.returncode != 0:
    print("Intentando crear dataset inicial...", flush=True)
    res = subprocess.run(f"kaggle datasets create -p '{WORK_DIR}' -u -r tar", shell=True)

t_total = time.time() - t_start
print("=" * 78, flush=True)
print(f"🎉 ¡DATABASE 1 COMPILADA CON ÉXITO TOTAL EN {t_total:.1f} SEGUNDOS!", flush=True)
print(f"📦 Tamaño empaquetado: {rootfs_tar.stat().st_size / (1024**3):.2f} GB")
print("=" * 78, flush=True)

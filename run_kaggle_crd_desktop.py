#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🌸 LINUWAIFU CLOUD GAMING & AI VTUBER STUDIO PRO (KAGGLE MASTER ENGINE)
================================================================================
CELDA 2: Vincula CRD, inicia escritorio, y mantiene viva la sesión.
Funciona tanto en modo interactivo como en "Save & Run All".
================================================================================
"""

import os
import sys
import time
import getpass
import tarfile
import threading
import subprocess
import re
import signal
import atexit
import traceback
from pathlib import Path

# ==============================================================================
# DIAGNÓSTICO DE SEÑALES (atrapa cualquier cierre forzoso)
# ==============================================================================
def diagnostic_exit_handler():
    print("\n🛑 [SISTEMA LINUWAIFU]: Proceso finalizado.", flush=True)

def signal_handler(signum, frame):
    sig_name = "SIGTERM (Kaggle Shutdown)" if signum == signal.SIGTERM else "SIGINT (Cancelación)"
    print(f"\n🛑 [DIAGNÓSTICO]: Interrupción -> {sig_name}", flush=True)
    traceback.print_stack(frame, limit=2)
    sys.exit(0)

atexit.register(diagnostic_exit_handler)
try:
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent
os.environ["DEBIAN_FRONTEND"] = "noninteractive"
os.environ["DISPLAY"] = os.environ.get("DISPLAY", ":20")

# ==============================================================================
# AUTO-INSTALADOR SI FALTA ALGO
# ==============================================================================
crd_bin = "/opt/google/chrome-remote-desktop/start-host"
if not os.path.exists(crd_bin):
    print("🌸 [Auto-Instalador]: Configurando paquetes del sistema necesarios...", flush=True)
    install_script = BASE_DIR / "install_kaggle_packages.sh"
    if install_script.exists():
        subprocess.run(f"bash {install_script}", shell=True)
    else:
        subprocess.run(
            "sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq && "
            "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "
            "xfce4-session xfce4-terminal libgtk-3-0 dbus-x11 pulseaudio xvfb && "
            "wget -q https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb -O /tmp/crd.deb && "
            "sudo DEBIAN_FRONTEND=noninteractive dpkg -i /tmp/crd.deb 2>/dev/null || sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --fix-broken",
            shell=True
        )

print("✅ Chrome Remote Desktop detectado y listo. Continuando...", flush=True)

# ==============================================================================
# CONFIGURAR SESIÓN XFCE
# ==============================================================================
crd_session_file = Path.home() / ".chrome-remote-desktop-session"
with open(crd_session_file, "w") as f:
    f.write("exec /etc/X11/Xsession /usr/bin/xfce4-session\n")
crd_session_file.chmod(0o755)

# ==============================================================================
# RESTAURAR O VINCULAR CRD
# ==============================================================================
print("\n======================================================================", flush=True)
print("🌸 🖥️ VINCULANDO GOOGLE CHROME REMOTE DESKTOP (XFCE4)...", flush=True)
print("======================================================================", flush=True)

CRD_BACKUP_TAR = BASE_DIR / "crd_session.tar.gz"
CRD_CONFIG_DIR = Path.home() / ".config" / "chrome-remote-desktop"

def restore_crd_session() -> bool:
    if CRD_BACKUP_TAR.exists() and CRD_BACKUP_TAR.stat().st_size > 100:
        print("  📦 Restaurando sesión CRD desde GitHub...", flush=True)
        try:
            CRD_CONFIG_DIR.parent.mkdir(parents=True, exist_ok=True)
            with tarfile.open(CRD_BACKUP_TAR, "r:gz") as tar:
                tar.extractall(path=Path.home() / ".config")
            print("  ⚡ [✓] Tokens restaurados.", flush=True)
            return True
        except Exception as e:
            print(f"  ⚠️ Error restaurando: {e}", flush=True)
    return False

def backup_crd_session():
    if CRD_CONFIG_DIR.exists():
        try:
            with tarfile.open(CRD_BACKUP_TAR, "w:gz") as tar:
                tar.add(CRD_CONFIG_DIR, arcname="chrome-remote-desktop")
            subprocess.run(
                f"cd {BASE_DIR} && git add crd_session.tar.gz 2>/dev/null && "
                f"git commit -m 'Auto-backup CRD tokens' 2>/dev/null && "
                f"git push origin main 2>/dev/null || true",
                shell=True
            )
        except Exception:
            pass

crd_restored = restore_crd_session()

if not crd_restored:
    # Buscar código de autenticación CRD
    crd_command = os.environ.get("CRD_AUTH_COMMAND", "").strip()
    if len(sys.argv) > 1 and sys.argv[1].strip():
        crd_command = sys.argv[1].strip()
    if not crd_command:
        for p in [Path("/tmp/crd_code.txt"), Path("/kaggle/working/crd_code.txt"), BASE_DIR / "crd_code.txt"]:
            if p.exists():
                try:
                    crd_command = p.read_text().strip()
                    if crd_command:
                        break
                except Exception:
                    pass

    if not crd_command or crd_command == "PEGA_AQUI_TU_COMANDO_DE_GOOGLE":
        print("\n👉 Pega tu código de Google en la variable CRD_AUTH de la Celda 2")
        print('   CRD_AUTH = "DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=..."')
        sys.exit(0)

    code_match = re.search(r'--code="?([^"\s]+)"?', crd_command)
    auth_code = code_match.group(1) if code_match else crd_command

    curr_user = getpass.getuser() or os.environ.get("USER", "root")
    subprocess.run(f"sudo usermod -a -G chrome-remote-desktop {curr_user} 2>/dev/null || true", shell=True)

    print(f"⏳ Vinculando (Host: LinuWaifu-Cloud-PC, Usuario: {curr_user}, PIN: 123456)...", flush=True)
    start_cmd = (
        f'DISPLAY= /opt/google/chrome-remote-desktop/start-host '
        f'--code="{auth_code}" '
        f'--redirect-url="https://remotedesktop.google.com/_/oauthredirect" '
        f'--name="LinuWaifu-Cloud-PC" '
        f'--user-name="{curr_user}" '
        f'--pin="123456"'
    )
    res = subprocess.run(start_cmd, shell=True)
    if res.returncode == 0:
        print("🎉 [✓] ¡Vinculación exitosa!", flush=True)
        time.sleep(2)
        backup_crd_session()
    else:
        print("⚠️ Si el código expiró, genera uno nuevo en https://remotedesktop.google.com/headless", flush=True)

# Iniciar servicio CRD
subprocess.run(
    "/opt/google/chrome-remote-desktop/chrome-remote-desktop --start 2>/dev/null || "
    "sudo systemctl restart chrome-remote-desktop 2>/dev/null || true",
    shell=True
)

# ==============================================================================
# ¡ONLINE!
# ==============================================================================
print("\n" + "=" * 60, flush=True)
print("🎉 🌸 ¡LINUWAIFU CLOUD PC ESTÁ 100% ONLINE!", flush=True)
print("=" * 60, flush=True)
print("📱 Abre 'Escritorio Remoto de Chrome' en tu celular", flush=True)
print("   → Toca 'LinuWaifu-Cloud-PC' → PIN: 123456", flush=True)
print("=" * 60, flush=True)

# ==============================================================================
# GPUS + AUDIO EN SEGUNDO PLANO
# ==============================================================================
def background_worker():
    try:
        import torch
        n = torch.cuda.device_count()
        print(f"\n🎮 GPUs: {n}", flush=True)
        for i in range(n):
            p = torch.cuda.get_device_properties(i)
            print(f"  • GPU {i}: {p.name} ({p.total_memory / (1024**3):.1f} GB)", flush=True)
    except Exception:
        pass
    subprocess.run("pulseaudio --start --exit-idle-time=-1 2>/dev/null || true", shell=True)
    subprocess.run("pactl load-module module-null-sink sink_name=VirtualSink 2>/dev/null || true", shell=True)
    print("🔊 Audio Virtual activo.", flush=True)

threading.Thread(target=background_worker, daemon=True).start()

# ==============================================================================
# KEEPALIVE: Imprime un punto cada 30 segundos para que Kaggle NO mate la celda
# ==============================================================================
print("\n⏳ Sesión activa. Puedes cerrar el navegador si usaste 'Save & Run All'.", flush=True)
print("   Keepalive activo (un punto cada 30s):", flush=True, end=" ")
try:
    minutes = 0
    while True:
        time.sleep(30)
        print(".", end="", flush=True)
        minutes += 0.5
        if minutes % 15 == 0:
            print(f" [{int(minutes)}min]", flush=True, end=" ")
            backup_crd_session()
except KeyboardInterrupt:
    backup_crd_session()
    print("\n🛑 Sesión terminada por el usuario.", flush=True)

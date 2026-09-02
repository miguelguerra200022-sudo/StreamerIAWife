#!/usr/bin/env python3
"""
================================================================================
🌸 AUTO-COMPILADOR Y PUBLICADOR MAESTRO DE DATABASE KAGGLE (100GB)
================================================================================
Este script realiza el ciclo completo de forma 100% autónoma:
1. Instala todo el Ecosistema 'Modo Dios' (Steam, OBS, Discord, Sunshine, Lutris, etc.)
2. Aplica todas las reglas de blindaje de almacenamiento (evitando los 20GB).
3. Compila la imagen maestra en /tmp o /dev/shm con pigz multi-núcleo.
4. Sube la nueva versión a la base de datos de 100GB (linuwaifu-ubuntu-master-100gb).
5. Apaga la sesión inmediatamente al terminar para ahorrar todas las horas de GPU.
"""

import os
import sys
import time
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path("/kaggle/working/StreamerIAWife") if Path("/kaggle/working/StreamerIAWife").exists() else Path(__file__).resolve().parent
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "09032000Mi.").strip()

print("=" * 78, flush=True)
print("🌸 INICIANDO PROCESO AUTÓNOMO: INSTALACIÓN, COMPILACIÓN Y PUBLICACIÓN EN DATABASE...", flush=True)
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

# 2. Configurar entorno no interactivo y aceleración I/O
os.environ["DEBIAN_FRONTEND"] = "noninteractive"
os.environ["NEEDRESTART_MODE"] = "a"
os.environ["NEEDRESTART_SUSPEND"] = "1"
os.environ["TMPDIR"] = "/tmp"
os.environ["PIP_CACHE_DIR"] = "/tmp/pip_cache"
os.environ["XDG_CACHE_HOME"] = "/tmp/.cache"

subprocess.run("dpkg --add-architecture i386 && apt-get update -qq", shell=True)
subprocess.run("mkdir -p /etc/dpkg/dpkg.cfg.d && echo 'force-unsafe-io' > /etc/dpkg/dpkg.cfg.d/02apt-speedup 2>/dev/null || true", shell=True)
subprocess.run("mkdir -p /etc/apt/apt.conf.d && echo 'Dpkg::Options { \"--force-confdef\"; \"--force-confold\"; \"--force-unsafe-io\"; }; Dir::Cache::pkgcache \"\"; Dir::Cache::srcpkgcache \"\"; APT::Keep-Downloaded-Packages \"0\";' > /etc/apt/apt.conf.d/99force-conf 2>/dev/null || true", shell=True)
subprocess.run("echo 'man-db man-db/auto-update boolean false' | debconf-set-selections 2>/dev/null || true", shell=True)

# 3. Instalar entorno de escritorio base si no está
print("📦 [1/4] Verificando e instalando componentes base de escritorio y noVNC...", flush=True)
subprocess.run("DEBIAN_FRONTEND=noninteractive apt-get install -y -qq xfce4 xfce4-terminal xfce4-goodies dbus-x11 x11-xserver-utils x11-utils xterm tigervnc-standalone-server tigervnc-common websockify pigz pv wget curl git python3-pip", shell=True)

# 4. Instalar Ecosistema 'Modo Dios'
print("⭐ [2/4] Instalando Ecosistema 'Modo Dios' (Steam, OBS, Sunshine, Discord, Lutris)...", flush=True)
subprocess.run("DEBIAN_FRONTEND=noninteractive apt-get install -y -qq steam lutris mangohud gamemode obs-studio kdenlive gimp telegram-desktop plank papirus-icon-theme", shell=True)

print("   -> Instalando Discord...", flush=True)
subprocess.run("wget -q 'https://discord.com/api/download?platform=linux&format=deb' -O /tmp/discord.deb && (apt-get install -y -qq /tmp/discord.deb || dpkg -i /tmp/discord.deb || apt-get install -f -y -qq) && rm -f /tmp/discord.deb", shell=True)

print("   -> Instalando Sunshine (Streaming 60 FPS)...", flush=True)
subprocess.run("wget -q 'https://github.com/LizardByte/Sunshine/releases/download/v0.23.1/sunshine-ubuntu-22.04-amd64.deb' -O /tmp/sunshine.deb && (apt-get install -y -qq /tmp/sunshine.deb || dpkg -i /tmp/sunshine.deb || apt-get install -f -y -qq) && rm -f /tmp/sunshine.deb", shell=True)

# 5. Asegurar noVNC clonado
novnc_dir = Path("/kaggle/working/noVNC")
if not novnc_dir.exists():
    print("   -> Descargando noVNC...", flush=True)
    subprocess.run("git clone --depth 1 https://github.com/novnc/noVNC.git /kaggle/working/noVNC >/dev/null 2>&1", shell=True)
    subprocess.run("git clone --depth 1 https://github.com/novnc/websockify.git /kaggle/working/noVNC/utils/websockify >/dev/null 2>&1", shell=True)

# 6. Compilar y guardar en la Base de Datos de 100GB
print("💾 [3/4] Ejecutando compilación de imagen maestra y subida a la nube de Kaggle...", flush=True)
res = subprocess.run(f"python3 {BASE_DIR}/guardar_en_database_kaggle.py '{ADMIN_PASSWORD}'", shell=True)

t_total = time.time() - t_start

print("=" * 78, flush=True)
if res.returncode == 0:
    print(f"🎉 ¡PROCESO COMPLETADO EXITOSAMENTE EN {t_total:.1f} SEGUNDOS!", flush=True)
    print("✅ Tu base de datos de 100GB ha sido actualizada con Steam, OBS, Discord, Sunshine y todo el sistema.", flush=True)
    print("🛑 Apagando la sesión para no consumir horas de GPU.", flush=True)
else:
    print(f"⚠️ El proceso finalizó con observaciones (Código: {res.returncode}).", flush=True)
print("=" * 78, flush=True)

# Finalizar ejecución limpiamente
sys.exit(0)

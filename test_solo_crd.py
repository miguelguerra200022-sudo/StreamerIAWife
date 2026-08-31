#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🧪 PRUEBA PURA Y AISLADA: SOLO GOOGLE CHROME REMOTE DESKTOP (CRD) EN KAGGLE
================================================================================
Este script instala ÚNICAMENTE lo mínimo necesario para probar Chrome Remote Desktop:
1. Instala el paquete oficial de Google Chrome Remote Desktop (.deb) y XFCE mínimo.
2. Crea el usuario 'linuwaifu' y configura la sesión.
3. Te pide el comando de autorización de Google y lo vincula con PIN: 123456.
4. Te muestra en pantalla cada segundo cualquier log o error de Google.
================================================================================
"""

import os
import sys
import time
import re
import subprocess
import glob
from pathlib import Path

os.environ["DEBIAN_FRONTEND"] = "noninteractive"
os.environ["LC_ALL"] = "C.UTF-8"
os.environ["LANG"] = "C.UTF-8"

print("\n" + "=" * 78, flush=True)
print("🧪 INICIANDO PRUEBA PURA: SOLO CHROME REMOTE DESKTOP...", flush=True)
print("=" * 78, flush=True)

# 1. Limpieza de procesos y repositorios
subprocess.run("pkill -9 -f 'chrome-remote-desktop|Xvfb|xfce4' 2>/dev/null || true", shell=True)
subprocess.run("rm -rf /etc/apt/sources.list.d/* 2>/dev/null || true", shell=True)

# 2. Crear usuario no-root estándar
print("👤 [1/3] Creando usuario de sistema 'linuwaifu'...", flush=True)
subprocess.run("id -u linuwaifu >/dev/null 2>&1 || (useradd -m -s /bin/bash -G sudo,audio,video linuwaifu && echo 'linuwaifu:123456' | chpasswd)", shell=True)
subprocess.run("echo 'linuwaifu ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers 2>/dev/null || true", shell=True)
subprocess.run("mkdir -p /var/run/dbus && dbus-daemon --system --fork 2>/dev/null || true", shell=True)

USER_HOME = Path("/home/linuwaifu")

# 3. Instalar exclusivamente paquetes requeridos para CRD
print("📦 [2/3] Instalando Chrome Remote Desktop oficial (.deb) y XFCE mínimo...", flush=True)
cmd_install = (
    "apt-get update -qq && "
    "apt-get install -y --no-install-recommends xfce4 xfce4-terminal xvfb dbus-x11 wget curl psmisc x11-xserver-utils python3-psutil >/dev/null 2>&1 && "
    "wget -q https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb -O /tmp/crd.deb && "
    "dpkg -i /tmp/crd.deb >/dev/null 2>&1 || apt-get install -y --fix-broken >/dev/null 2>&1"
)
subprocess.run(cmd_install, shell=True)

# Configurar archivo de sesión
session_file = USER_HOME / ".chrome-remote-desktop-session"
session_file.write_text("exec /etc/X11/Xsession /usr/bin/startxfce4\n")
session_file.chmod(0o755)
subprocess.run(f"chown -R linuwaifu:linuwaifu {USER_HOME}", shell=True)
print("  ✅ [✓] Paquetes de Google y sesión listos.", flush=True)

# 4. Vinculación
print("\n" + "=" * 78, flush=True)
print("🔑 [3/3] VINCULACIÓN CON GOOGLE", flush=True)
print("=" * 78, flush=True)
print("👉 1. Abre este enlace en tu navegador o celular:", flush=True)
print("   🔗 https://remotedesktop.google.com/headless", flush=True)
print("👉 2. Toca 'Configurar otra computadora' ➔ 'Comenzar' ➔ 'Autorizar'.", flush=True)
print("👉 3. Copia el comando que te da Google para Debian Linux.", flush=True)
print("-" * 78, flush=True)

try:
    crd_auth_cmd = input("📋 Pega aquí el comando de Google: ").strip()
except EOFError:
    crd_auth_cmd = ""

if not crd_auth_cmd:
    print("❌ No se proporcionó el comando de Google. Cancelando.", flush=True)
    sys.exit(1)

# Extraer parámetros
code_match = re.search(r'--code="?([^"\s]+)"?', crd_auth_cmd)
redirect_match = re.search(r'--redirect-url="?([^"\s]+)"?', crd_auth_cmd)

code = code_match.group(1) if code_match else crd_auth_cmd.strip()
redirect_url = redirect_match.group(1) if redirect_match else "https://remotedesktop.google.com/_/oauthredirect"
host_name = "Kaggle-PureCRD"
pin = "123456"

print(f"\n⚡ Ejecutando start-host para vincular [{host_name}] con PIN: {pin}...", flush=True)

cmd_crd = (
    f"su - linuwaifu -c '"
    f"/opt/google/chrome-remote-desktop/start-host "
    f"--code=\"{code}\" "
    f"--redirect-url=\"{redirect_url}\" "
    f"--name=\"{host_name}\" "
    f"--pin=\"{pin}\"'"
)

res = subprocess.run(cmd_crd, shell=True, capture_output=True, text=True)
if res.stdout:
    print(f"  [Google Output]: {res.stdout.strip()}", flush=True)
if res.stderr:
    print(f"  [Google Errors]: {res.stderr.strip()}", flush=True)

# Iniciar servicio CRD
subprocess.run(
    f"su - linuwaifu -c '/opt/google/chrome-remote-desktop/chrome-remote-desktop --start >/dev/null 2>&1 || true'",
    shell=True
)

# Verificar si el proceso de Google está corriendo
time.sleep(2)
ps_crd = subprocess.run("pgrep -f 'chrome-remote-desktop' >/dev/null 2>&1", shell=True)

print("\n" + "=" * 78, flush=True)
if ps_crd.returncode == 0:
    print("🎉 🌸 ¡CHROME REMOTE DESKTOP ESTÁ CORRIENDO EN KAGGLE!", flush=True)
    print("=" * 78, flush=True)
    print("📱 CÓMO ENTRAR DESDE TU CELULAR O PC:", flush=True)
    print("   • Entra a: https://remotedesktop.google.com/access")
    print(f"   • Toca en tu PC: 💻 [{host_name}] (Color Verde)")
    print(f"   • Ingresa tu PIN: 🔑 {pin}")
else:
    print("⚠️ El proceso de CRD no quedó en ejecución. Revisa los logs abajo:", flush=True)

print("=" * 78 + "\n", flush=True)

# Bucle de diagnóstico continuo
try:
    minutos = 0
    while True:
        time.sleep(10)
        minutos += (10 / 60)
        crd_logs = glob.glob("/tmp/chrome_remote_desktop*.log") + glob.glob("/home/linuwaifu/.config/chrome-remote-desktop/*.log")
        for cl in crd_logs:
            try:
                p = Path(cl)
                if p.exists() and p.stat().st_size > 0:
                    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()[-3:]
                    for line in lines:
                        print(f"📋 [CRD Log]: {line.strip()}", flush=True)
            except Exception:
                pass
except KeyboardInterrupt:
    print("\n🛑 Prueba detenida.", flush=True)

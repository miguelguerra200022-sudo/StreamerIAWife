#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🧪 PRUEBA PURA Y AISLADA: SOLO GOOGLE CHROME REMOTE DESKTOP (CRD) EN KAGGLE
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
print("🧪 INICIANDO PRUEBA PURA: SOLO CHROME REMOTE DESKTOP (REGISTROS COMPLETOS)...", flush=True)
print("=" * 78, flush=True)

# 1. Limpieza de procesos y repositorios
print("🧹 [1/4] Limpiando procesos previos...", flush=True)
subprocess.run("pkill -9 -f 'chrome-remote-desktop|Xvfb|xfce4' 2>/dev/null || true", shell=True)
subprocess.run("rm -rf /etc/apt/sources.list.d/* 2>/dev/null || true", shell=True)

# 2. Crear usuario no-root estándar
print("👤 [2/4] Creando usuario de sistema 'linuwaifu'...", flush=True)
subprocess.run("id -u linuwaifu >/dev/null 2>&1 || (useradd -m -s /bin/bash -G sudo,audio,video linuwaifu && echo 'linuwaifu:123456' | chpasswd)", shell=True)
subprocess.run("echo 'linuwaifu ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers 2>/dev/null || true", shell=True)
subprocess.run("mkdir -p /var/run/dbus && dbus-daemon --system --fork 2>/dev/null || true", shell=True)

USER_HOME = Path("/home/linuwaifu")

# 3. Instalar exclusivamente paquetes requeridos para CRD con salida en vivo
print("📦 [3/4] Instalando Chrome Remote Desktop oficial (.deb) y XFCE mínimo...", flush=True)

pkgs = [
    "xfce4", "xfce4-terminal", "xvfb", "dbus-x11", "wget", "curl",
    "psmisc", "x11-xserver-utils", "python3-psutil"
]

print(f"  • Actualizando repositorios e instalando paquetes base...", flush=True)
res_apt = subprocess.run(
    f"apt-get update -qq && apt-get install -y --no-install-recommends {' '.join(pkgs)}",
    shell=True, capture_output=True, text=True
)
if res_apt.returncode != 0:
    print(f"🔴 Error APT: {res_apt.stderr}", flush=True)
else:
    print("  ✅ [✓] Paquetes base instalados.", flush=True)

print("  • Descargando paquete oficial Chrome Remote Desktop (.deb)...", flush=True)
subprocess.run("wget -q https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb -O /tmp/crd.deb", shell=True)

print("  • Instalando paquete de Google...", flush=True)
res_dpkg = subprocess.run("dpkg -i /tmp/crd.deb || apt-get install -y --fix-broken", shell=True, capture_output=True, text=True)
if res_dpkg.stderr:
    for line in res_dpkg.stderr.splitlines():
        if "error" in line.lower():
            print(f"⚠️ {line.strip()}", flush=True)

# Configurar archivo de sesión
session_file = USER_HOME / ".chrome-remote-desktop-session"
session_file.write_text("exec /etc/X11/Xsession /usr/bin/startxfce4\n")
session_file.chmod(0o755)
subprocess.run(f"chown -R linuwaifu:linuwaifu {USER_HOME}", shell=True)
print("  ✅ [✓] Entorno y sesión de Google configurados.", flush=True)

# 4. Vinculación
print("\n" + "=" * 78, flush=True)
print("🔑 [4/4] VINCULACIÓN CON GOOGLE", flush=True)
print("=" * 78, flush=True)

crd_auth_cmd = ""
if len(sys.argv) > 1 and sys.argv[1].strip() and not sys.argv[1].startswith("--"):
    crd_auth_cmd = " ".join(sys.argv[1:]).strip()

if not crd_auth_cmd:
    print("⚠️ NO SE ENCONTRÓ EL COMANDO DE GOOGLE EN LA LÍNEA DE EJECUCIÓN.", flush=True)
    print("-" * 78, flush=True)
    print("👉 Pasos para obtener tu comando:", flush=True)
    print("   1. Abre: https://remotedesktop.google.com/headless", flush=True)
    print("   2. Toca 'Configurar otra computadora' ➔ 'Comenzar' ➔ 'Autorizar'.", flush=True)
    print("   3. Copia el comando para Debian Linux.", flush=True)
    print("   4. Ejecuta la celda pegando tu comando entre comillas al final, así:", flush=True)
    print('\n   !rm -rf /kaggle/working/StreamerIAWife && git clone https://github.com/miguelguerra200022-sudo/StreamerIAWife.git /kaggle/working/StreamerIAWife && cd /kaggle/working/StreamerIAWife && python3 -u test_solo_crd.py "DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=4/0A..."', flush=True)
    print("=" * 78 + "\n", flush=True)
    sys.exit(0)

# Extraer parámetros
code_match = re.search(r'--code="?([^"\s]+)"?', crd_auth_cmd)
redirect_match = re.search(r'--redirect-url="?([^"\s]+)"?', crd_auth_cmd)

code = code_match.group(1) if code_match else crd_auth_cmd.strip()
redirect_url = redirect_match.group(1) if redirect_match else "https://remotedesktop.google.com/_/oauthredirect"
host_name = "Kaggle-PureCRD"
pin = "123456"

print(f"⚡ Ejecutando start-host para vincular [{host_name}] con PIN: {pin}...", flush=True)

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
    print(f"  [Google Output]:\n{res.stdout.strip()}", flush=True)
if res.stderr:
    print(f"  [Google Errors/Warnings]:\n{res.stderr.strip()}", flush=True)

# Iniciar servicio CRD
print("🚀 Levantando servicio de Chrome Remote Desktop...", flush=True)
res_start = subprocess.run(
    f"su - linuwaifu -c '/opt/google/chrome-remote-desktop/chrome-remote-desktop --start'",
    shell=True, capture_output=True, text=True
)
if res_start.stdout:
    print(f"  {res_start.stdout.strip()}", flush=True)
if res_start.stderr:
    print(f"  {res_start.stderr.strip()}", flush=True)

time.sleep(3)
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
    print("⚠️ El proceso de CRD no quedó en ejecución. Mostrando registros de diagnóstico:", flush=True)

print("=" * 78 + "\n", flush=True)

# Diagnóstico continuo
try:
    while True:
        time.sleep(10)
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

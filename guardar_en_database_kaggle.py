#!/usr/bin/env python3
"""
================================================================================
💾 GUARDADOR DE SISTEMA Y JUEGOS EN KAGGLE DATASET (100 GB)
================================================================================
Este script sincroniza todos los programas instalados mediante 'apt install' y
juegos nuevos directamente a tu base de datos (Kaggle Dataset de 100GB).
"""

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path("/kaggle/working/StreamerIAWife") if Path("/kaggle/working/StreamerIAWife").exists() else Path(__file__).resolve().parent
PAYLOAD_DIR = Path("/kaggle/working/linuwaifu_dataset_update_payload")
LOG_FILE = Path("/kaggle/working/linuwaifu_system.log")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "09032000Mi.").strip()

def notify(msg, title="💾 Base de Datos Kaggle"):
    print(f"[{title}] {msg}", flush=True)
    if os.environ.get("DISPLAY"):
        subprocess.run(f"notify-send '{title}' '{msg}' 2>/dev/null || true", shell=True)

def verify_admin():
    # 1. Si se pasa por argumento: python3 guardar_en_database_kaggle.py "09032000Mi."
    if len(sys.argv) > 1 and sys.argv[1].strip() == ADMIN_PASSWORD:
        return True
    if "--password" in sys.argv:
        try:
            idx = sys.argv.index("--password")
            if sys.argv[idx + 1].strip() == ADMIN_PASSWORD:
                return True
        except Exception:
            pass
    # 2. Si está en entorno gráfico (Escritorio XFCE), pedir contraseña con Zenity
    if os.environ.get("DISPLAY") and shutil.which("zenity"):
        try:
            p_res = subprocess.run(
                ["zenity", "--password", "--title=🔐 Seguridad LinuWaifu Master", "--text=Introduce la Contraseña de Administrador para modificar la Base de Datos de 100GB:"],
                capture_output=True, text=True
            )
            if p_res.returncode == 0 and p_res.stdout.strip() == ADMIN_PASSWORD:
                return True
            else:
                notify("❌ Acceso Denegado: Contraseña de Administrador incorrecta.", "🚫 Bloqueo de Seguridad")
                return False
        except Exception:
            pass
    # 3. Si se corre en Terminal interactiva
    if sys.stdin.isatty():
        import getpass
        entered = getpass.getpass("🔐 Introduce la Contraseña de Administrador (LinuWaifu): ")
        if entered.strip() == ADMIN_PASSWORD:
            return True
        else:
            print("❌ Acceso Denegado: Contraseña incorrecta.", flush=True)
            return False
    # 4. Sin contraseña
    notify("❌ Acceso Denegado: Se requiere la Contraseña de Administrador para modificar el Dataset Maestro.", "🚫 Bloqueo de Seguridad")
    print(f"Uso: python3 {sys.argv[0]} '09032000Mi.'", flush=True)
    return False

def update_dataset():
    if not verify_admin():
        sys.exit(1)
    notify("Iniciando guardado de programas y cambios en el Dataset de 100GB...")
    PAYLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Asegurar credenciales de Kaggle
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(parents=True, exist_ok=True)
    kaggle_file = kaggle_dir / "kaggle.json"
    legacy_json = BASE_DIR / "kaggle legacy.json"
    
    if not kaggle_file.exists() and legacy_json.exists():
        shutil.copy2(legacy_json, kaggle_file)
        subprocess.run(f"chmod 600 '{kaggle_file}'", shell=True)
    
    # 2. Limpiar caché de apt para liberar espacio crítico (Ya no necesitamos respaldar los .deb gracias a que el .data tiene todo instalado)
    archives_dir = Path("/var/cache/apt/archives")
    if archives_dir.exists():
        for deb in archives_dir.glob("*.deb"):
            try:
                deb.unlink() # Destruir basura temporal para liberar gigabytes
            except Exception:
                pass
    
    # 2.5 Generar imagen pre-compilada de Ubuntu para arranque en 3 segundos
    notify("Preparando acelerador multi-núcleo y medidor de progreso...")
    rootfs_tar = PAYLOAD_DIR / "ubuntu_master_rootfs.tar.data"
    
    # Instalar pigz (compresión paralela) y pv (barra de progreso en tiempo real con % y ETA)
    subprocess.run("DEBIAN_FRONTEND=noninteractive apt-get install -y -qq pigz pv >/dev/null 2>&1", shell=True)
    
    # Calcular tamaño total exacto en bytes para alimentar la barra de progreso (toma 2 segundos)
    notify("Calculando tamaño total de archivos...")
    excludes = "--exclude='/root/gdrive' --exclude='/kaggle' --exclude='/proc' --exclude='/sys' --exclude='/dev' --exclude='/tmp' --exclude='/run' --exclude='/usr/src' --exclude='/usr/share/doc' --exclude='/usr/share/man'"
    calc_cmd = f"du -sb {excludes} /usr /opt /etc /var/lib/dpkg /var/lib/apt 2>/dev/null | awk '{{s+=$1}} END {{print s}}'"
    try:
        total_bytes_str = subprocess.check_output(calc_cmd, shell=True, text=True).strip()
        total_bytes = int(total_bytes_str) if total_bytes_str.isdigit() and int(total_bytes_str) > 0 else 0
    except Exception:
        total_bytes = 0

    notify("⏳ Compilando sistema operativo (Progreso en tiempo real con % y tiempo estimado):")
    if total_bytes > 0 and shutil.which("pv"):
        # Tubo de alto rendimiento: tar crudo | pv (progreso/ETA) | pigz (multi-núcleo) -> archivo final
        cmd_tar = f"tar {excludes} -cf - /usr /opt /etc /var/lib/dpkg /var/lib/apt 2>/dev/null | pv -pterb -s {total_bytes} | pigz -3 > '{rootfs_tar}'"
    else:
        cmd_tar = f"tar {excludes} --checkpoint=5000 --checkpoint-action=echo='⏳ Compilando... %u bloques' -I 'pigz -3' -cf '{rootfs_tar}' /usr /opt /etc /var/lib/dpkg /var/lib/apt"
    
    subprocess.run(cmd_tar, shell=True)

    # 2.6 Incluir suite noVNC pre-configurada
    if Path("/kaggle/working/noVNC").exists():
        try:
            shutil.copytree("/kaggle/working/noVNC", PAYLOAD_DIR / "noVNC", dirs_exist_ok=True)
        except Exception:
            pass

    # 3. Metadatos del Dataset con detección dinámica de usuario (Multi-Cuenta)
    usuario_activo = "miguelguerra26"
    if kaggle_file.exists():
        try:
            data = json.loads(kaggle_file.read_text())
            if data.get("username"):
                usuario_activo = data["username"]
        except Exception:
            pass
    elif os.environ.get("KAGGLE_USERNAME"):
        usuario_activo = os.environ["KAGGLE_USERNAME"]

    metadata = {
        "title": "LinuWaifu Ubuntu Master Suite 100GB",
        "id": f"{usuario_activo}/linuwaifu-ubuntu-master-100gb",
        "licenses": [{"name": "CC0-1.0"}]
    }
    (PAYLOAD_DIR / "dataset-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    
    # 4. Enviar versión a la API de Kaggle
    ts_msg = time.strftime("%Y-%m-%d %H:%M:%S")
    cmd_version = f"kaggle datasets version -p '{PAYLOAD_DIR}' -m 'Auto-backup con imagen de 3s ({ts_msg})' --dir-mode tar"
    
    notify("☁️ Subiendo a la nube de Kaggle (mostrando progreso en vivo)...")
    # Quitamos capture_output=True para que se vea la barra de progreso de Kaggle en la terminal
    res = subprocess.run(cmd_version, shell=True)
    if res.returncode == 0:
        notify(f"🎉 ¡Guardado exitoso en {usuario_activo}/linuwaifu-ubuntu-master-100gb!", "✅ Guardado Exitoso")
    else:
        # Si el dataset no existía, intentar crear
        notify("Intentando crear dataset por primera vez...")
        cmd_create = f"kaggle datasets create -p '{PAYLOAD_DIR}' -u -r tar"
        res2 = subprocess.run(cmd_create, shell=True)
        if res2.returncode == 0:
            notify(f"🎉 ¡Dataset creado en {usuario_activo}/linuwaifu-ubuntu-master-100gb!", "✅ Guardado Exitoso")
        else:
            notify(f"❌ Error al guardar en Dataset (Revisa la consola para más detalles).", "❌ Error de Guardado")

if __name__ == "__main__":
    update_dataset()

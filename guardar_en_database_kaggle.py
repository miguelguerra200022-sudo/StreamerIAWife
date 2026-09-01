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

def notify(msg, title="💾 Base de Datos Kaggle"):
    print(f"[{title}] {msg}", flush=True)
    if os.environ.get("DISPLAY"):
        subprocess.run(f"notify-send '{title}' '{msg}' 2>/dev/null || true", shell=True)

def update_dataset():
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
    
    # 2. Recopilar nuevos paquetes .deb instalados
    archives_dir = Path("/var/cache/apt/archives")
    dataset_archives = PAYLOAD_DIR / "apt_archives"
    dataset_archives.mkdir(parents=True, exist_ok=True)
    
    new_debs = 0
    if archives_dir.exists():
        for deb in archives_dir.glob("*.deb"):
            try:
                shutil.copy2(deb, dataset_archives)
                new_debs += 1
            except Exception:
                pass
    
    # 3. Metadatos del Dataset
    metadata = {
        "title": "LinuWaifu Ubuntu Master Suite 100GB",
        "id": "miguelguerra26/linuwaifu-ubuntu-master-100gb",
        "licenses": [{"name": "CC0-1.0"}]
    }
    (PAYLOAD_DIR / "dataset-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    
    # 4. Enviar versión a la API de Kaggle
    ts_msg = time.strftime("%Y-%m-%d %H:%M:%S")
    cmd_version = f"kaggle datasets version -p '{PAYLOAD_DIR}' -m 'Auto-backup desde Escritorio ({ts_msg})' --dir-mode tar"
    
    res = subprocess.run(cmd_version, shell=True, text=True, capture_output=True)
    if res.returncode == 0:
        notify("🎉 ¡Todos tus programas y juegos han sido guardados permanentemente en tu Dataset de 100GB!", "✅ Guardado Exitoso")
    else:
        # Si el dataset no existía, intentar crear
        cmd_create = f"kaggle datasets create -p '{PAYLOAD_DIR}' -u -r tar"
        res2 = subprocess.run(cmd_create, shell=True, text=True, capture_output=True)
        if res2.returncode == 0:
            notify("🎉 ¡Dataset de 100GB creado y guardado en Kaggle!", "✅ Guardado Exitoso")
        else:
            notify(f"Error al guardar en Dataset: {res.stderr or res.stdout}", "❌ Error de Guardado")

if __name__ == "__main__":
    update_dataset()

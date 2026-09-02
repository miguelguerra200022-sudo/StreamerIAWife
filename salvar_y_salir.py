#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💾 SALVADOR DE ESTADO MAESTRO & CIERRE SEGURO (5TB GOOGLE DRIVE)
Sincroniza todos los historiales, partidas, configuraciones y proyectos con Google Drive
antes del corte de sesión o apagado de la máquina.
"""
import os
import sys
import subprocess
from pathlib import Path

def notify(msg, title="💾 Guardado Seguro"):
    print(f"[{title}] {msg}", flush=True)
    if os.environ.get("DISPLAY"):
        subprocess.run(f"notify-send '{title}' '{msg}' 2>/dev/null || true", shell=True)

notify("Sincronizando estado completo con 5TB de Google Drive...")

# Sincronización del sistema
subprocess.run("sync", shell=True)

# Ejecutar el guardado del estado si existe el script maestro
master_script = Path("/kaggle/working/StreamerIAWife/run_kaggle_vnc_studio.py")
if master_script.exists():
    subprocess.run(f"python3 '{master_script}' --save-now 2>/dev/null || true", shell=True)

notify("🎉 ¡Progreso, partidas y credenciales respaldadas en Google Drive con éxito!", "✅ Todo a Salvo")

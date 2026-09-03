#!/usr/bin/env python3
"""
================================================================================
🧹 DESCONECTADOR DE DATABASE 1: UBUNTU CORE & SUITE GAMER
================================================================================
Limpia de forma segura los accesos directos y configuraciones temporales de la
Database 1 del Escritorio sin tocar datos de usuario ni Google Drive.
================================================================================
"""

import os
import sys
import shutil
from pathlib import Path

DESKTOP_DIR = Path.home() / "Desktop"
folder = DESKTOP_DIR / "📁 [01] Ubuntu Core & Redes Sociales"

print("🧹 Desconectando Database 1 (Ubuntu Core & Suite Gamer)...", flush=True)

# 1. Eliminar accesos directos
if folder.exists():
    shutil.rmtree(folder, ignore_errors=True)
    print("  [✓] Accesos directos de Database 1 eliminados del Escritorio.", flush=True)

# 2. Detener procesos en segundo plano de Database 1
os.system("pkill -f gamepad_uinput_bridge.py 2>/dev/null || true")

# 3. Refrescar escritorio XFCE
os.system("xfdesktop --reload 2>/dev/null || true")

print("🎉 [✓] Database 1 desconectada limpiamente.")

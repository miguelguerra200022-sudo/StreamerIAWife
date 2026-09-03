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

if folder.exists():
    shutil.rmtree(folder)
    print("  [✓] Accesos directos de Database 1 eliminados del Escritorio.", flush=True)

print("🎉 [✓] Database 1 desconectada limpiamente.")

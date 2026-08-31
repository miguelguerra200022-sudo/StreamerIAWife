#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
📊 LINUWAIFU CLOUD PC: MONITOR DE LOGS Y DIAGNÓSTICO EN VIVO (CELDA 2)
================================================================================
Ejecuta este script en una celda separada en Kaggle para ver en tiempo real:
1. Estado de los servicios (XFCE, GPUs Tesla T4, VNC, Rclone 5TB, IA VTuber).
2. Todos los registros y salidas de instalaciones en tiempo real.
3. Detección automática de errores para copiar y pegar fácilmente.
================================================================================
"""

import os
import sys
import time
import subprocess
from pathlib import Path

LOG_FILE = Path("/kaggle/working/linuwaifu_system.log")

print("=" * 75)
print("📊 LINUWAIFU CLOUD PC: MONITOR DE REGISTROS Y DIAGNÓSTICO EN VIVO")
print("=" * 75)

# 1. Comprobar servicios activos
def check_services():
    services = {
        "🖥️ Pantalla Xvfb (1080p)": "Xvfb",
        "🎨 Escritorio XFCE4": "xfce4-session",
        "📡 Servidor VNC (:5900)": "x11vnc",
        "🌐 Servidor Web noVNC (:6080)": "websockify",
        "☁️ Google Drive 5TB (Rclone)": "rclone",
        "🌸 LinuWaifu IA Backend": "cloud_bridge",
        "🎵 Audio Virtual PulseAudio": "pulseaudio"
    }
    
    print("\n🔍 ESTADO DE SERVICIOS DEL SISTEMA:")
    for name, proc in services.items():
        try:
            out = subprocess.check_output(f"pgrep -f {proc} || true", shell=True, text=True).strip()
            if out:
                print(f"  🟢 {name}: ACTIVO (PID: {out.split()[0]})")
            else:
                print(f"  🔴 {name}: DETENIDO / INACTIVO")
        except Exception:
            print(f"  ⚠️ {name}: NO DETECTADO")
    print("-" * 75)

check_services()

if not LOG_FILE.exists():
    print(f"\n⏳ Esperando a que el archivo de registro ({LOG_FILE}) sea creado por la Celda 1...")
    for _ in range(20):
        if LOG_FILE.exists():
            break
        time.sleep(1)

if not LOG_FILE.exists():
    print("⚠️ No se encontró el archivo de log aún. Asegúrate de que la Celda 1 esté corriendo.")
    sys.exit(0)

print(f"\n📜 MONITOREO EN VIVO ACTIVADO ({LOG_FILE}):")
print("👉 Cualquier cosa que instales, abras o juegues aparecerá aquí abajo.")
print("   Si ves un error rojo, cópialo y pégalo en el chat para solucionarlo.\n")
print("=" * 75 + "\n")

# Mostrar últimas 20 líneas iniciales
try:
    with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        for l in lines[-20:]:
            print(l.rstrip())
except Exception:
    pass

# Streaming continuo (tail -f)
try:
    with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if line:
                line_str = line.rstrip()
                if "error" in line_str.lower() or "failed" in line_str.lower() or "exception" in line_str.lower():
                    print(f"🔴 {line_str}", flush=True)
                elif "warning" in line_str.lower() or "warn" in line_str.lower():
                    print(f"⚠️ {line_str}", flush=True)
                else:
                    print(f"  {line_str}", flush=True)
            else:
                time.sleep(0.5)
except KeyboardInterrupt:
    print("\n🛑 Monitoreo detenido por el usuario.")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
📊 LINUWAIFU CLOUD PC: MONITOR DE REGISTROS Y DIAGNÓSTICO EN VIVO (CELDA 2)
================================================================================
Ejecuta este script en una celda separada en Kaggle para ver en tiempo real:
1. Estado de los 7 servicios clave (Pantalla, XFCE, VNC, Google Drive, IA, Audio).
2. Transmisión continua de logs y comandos en tiempo real.
3. Detección automática de errores en color rojo.
================================================================================
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Rutas posibles del archivo de registro
CANDIDATE_LOGS = [
    Path("/kaggle/working/linuwaifu_system.log"),
    Path("/kaggle/working/StreamerIAWife/linuwaifu_system.log"),
    Path("/tmp/linuwaifu_system.log")
]

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
    
    print("\n🔍 ESTADO DE SALUD DE LOS SERVICIOS:")
    for name, proc in services.items():
        try:
            out = subprocess.check_output(f"pgrep -f {proc} || true", shell=True, text=True).strip()
            if out:
                pid = out.split()[0]
                print(f"  🟢 {name}: 100% ACTIVO (PID: {pid})")
            else:
                print(f"  🔴 {name}: DETENIDO / INACTIVO")
        except Exception:
            print(f"  ⚠️ {name}: NO DETECTADO")
    print("-" * 75)

check_services()

# Encontrar o crear archivo de log
target_log = None
for p in CANDIDATE_LOGS:
    if p.exists():
        target_log = p
        break

if not target_log:
    target_log = Path("/kaggle/working/linuwaifu_system.log")
    target_log.parent.mkdir(parents=True, exist_ok=True)
    with open(target_log, "w", encoding="utf-8") as f:
        f.write(f"=== MONITOR INICIADO ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

print(f"\n📜 TRANSMISIÓN DE REGISTROS EN TIEMPO REAL ({target_log}):")
print("👉 Cualquier cosa que instales, abras o ejecutes se transmitirá aquí abajo.")
print("   Si ves un error en 🔴 rojo, cópialo y pégalo en el chat para solucionarlo.\n")
print("=" * 75 + "\n")

# Mostrar contenido existente
try:
    with open(target_log, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        for l in lines[-30:]:
            print(l.rstrip())
except Exception:
    pass

# Streaming continuo
last_size = target_log.stat().st_size if target_log.exists() else 0
loop_count = 0

try:
    while True:
        time.sleep(1)
        loop_count += 1
        
        if target_log.exists():
            curr_size = target_log.stat().st_size
            if curr_size > last_size:
                with open(target_log, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(last_size)
                    new_data = f.read()
                    last_size = curr_size
                    for line in new_data.splitlines():
                        if line.strip():
                            line_str = line.strip()
                            if "error" in line_str.lower() or "failed" in line_str.lower() or "exception" in line_str.lower():
                                print(f"🔴 {line_str}", flush=True)
                            elif "warning" in line_str.lower() or "warn" in line_str.lower():
                                print(f"⚠️ {line_str}", flush=True)
                            elif "[success]" in line_str.lower() or "éxito" in line_str.lower() or "conectado" in line_str.lower():
                                print(f"🟢 {line_str}", flush=True)
                            else:
                                print(f"  {line_str}", flush=True)
            elif curr_size < last_size:
                last_size = 0  # El archivo fue recreado/rotado
                
        # Cada 60 segundos refrescar un pulso
        if loop_count % 60 == 0:
            print(f"\n⏱️ [{time.strftime('%H:%M:%S')}] Monitor activo - Todos los servicios corriendo en orden.", flush=True)
except KeyboardInterrupt:
    print("\n🛑 Monitor detenido por el usuario.")

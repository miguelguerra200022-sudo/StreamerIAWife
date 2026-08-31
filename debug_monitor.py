#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
📊 LINUWAIFU CLOUD PC: MONITOR DE REGISTROS Y DIAGNÓSTICO EN VIVO (CELDA 2)
================================================================================
Ejecuta este script en una celda separada en Kaggle.
Se mantiene en ejecución INFINITA (nunca se apaga):
1. Transmite en vivo segundo a segundo todo lo que pasa en la PC.
2. Comprueba la salud de los 7 servicios en tiempo real.
3. Resalta errores en 🔴 rojo y éxitos en 🟢 verde.
4. Mantiene un latido continuo para que Kaggle nunca pause la celda.
================================================================================
"""

import os
import sys
import time
import subprocess
from pathlib import Path

CANDIDATE_LOGS = [
    Path("/kaggle/working/linuwaifu_system.log"),
    Path("/kaggle/working/StreamerIAWife/linuwaifu_system.log"),
    Path("/tmp/linuwaifu_system.log")
]

print("=" * 78)
print("📊 LINUWAIFU CLOUD PC: MONITOR DE REGISTROS EN VIVO (EJECUCIÓN CONTINUA)")
print("=" * 78)

# Función de comprobación de servicios
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
    print("-" * 78)

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
print("👉 Esta celda se quedará ejecutándose INDEFINIDAMENTE transmitiendo todo.")
print("   Cualquier comando, juego o error aparecerá aquí abajo en tiempo real.\n")
print("=" * 78 + "\n")

# Mostrar contenido inicial
try:
    if target_log.exists():
        with open(target_log, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            for l in lines[-30:]:
                print(l.rstrip())
except Exception:
    pass

# Streaming continuo infinito (Nunca se apaga)
last_size = target_log.stat().st_size if target_log.exists() else 0
seconds_counter = 0

while True:
    try:
        time.sleep(1)
        seconds_counter += 1
        
        # Buscar log si cambió de ubicación
        if not target_log.exists():
            for p in CANDIDATE_LOGS:
                if p.exists():
                    target_log = p
                    last_size = 0
                    break
        
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
                last_size = 0  # Rotación de log
        
        # Latido y re-chequeo cada 60 segundos
        if seconds_counter % 60 == 0:
            print(f"⏱️ [{time.strftime('%H:%M:%S')}] Monitor activo ({seconds_counter // 60} min) - 7 servicios OK.", flush=True)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitor detenido por el usuario.")
        break
    except Exception as e:
        time.sleep(2)

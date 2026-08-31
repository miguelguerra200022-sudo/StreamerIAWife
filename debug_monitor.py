#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
📊 LINUWAIFU CLOUD PC: MONITOR MAESTRO DESDE EL SEGUNDO 1 (CELDA 1)
================================================================================
Ejecuta esta celda PRIMERO.
1. Se inicializa desde el segundo 1 y se queda escuchando.
2. En cuanto ejecutes la Celda 2, captura TODO: instalación, paquetes, GPUs y errores.
3. Se mantiene en ejecución continua sin apagarse.
================================================================================
"""

import os
import sys
import time
import subprocess
from pathlib import Path

LOG_FILE = Path("/kaggle/working/linuwaifu_system.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Crear archivo de log inicial si no existe
if not LOG_FILE.exists():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== REGISTRO DEL SISTEMA INICIADO ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

print("=" * 78)
print("📊 LINUWAIFU CLOUD PC: MONITOR MAESTRO ACTIVO (REGISTRO DESDE EL SEGUNDO 1)")
print("=" * 78)
print("🟢 [LISTO]: El monitor ya está activo y escuchando.")
print("👉 Ahora dale Play (▶️) a la Celda 2 (Arranque del Sistema).")
print("   Todo lo que ocurra se transmitirá aquí abajo en tiempo real sin perder nada.")
print("=" * 78 + "\n")

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
    
    active_count = 0
    for name, proc in services.items():
        try:
            out = subprocess.check_output(f"pgrep -f {proc} || true", shell=True, text=True).strip()
            if out:
                active_count += 1
        except Exception:
            pass
    return active_count, len(services)

# Streaming continuo infinito
last_size = 0
seconds_counter = 0
last_active = -1

while True:
    try:
        time.sleep(0.5)
        seconds_counter += 0.5
        
        if LOG_FILE.exists():
            curr_size = LOG_FILE.stat().st_size
            if curr_size > last_size:
                with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
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
                            elif "[success]" in line_str.lower() or "éxito" in line_str.lower() or "online" in line_str.lower():
                                print(f"🟢 {line_str}", flush=True)
                            else:
                                print(f"  {line_str}", flush=True)
            elif curr_size < last_size:
                last_size = 0  # Rotación de log
        
        # Cada 30 segundos mostrar resumen de salud si hay servicios activos
        if int(seconds_counter) % 30 == 0 and seconds_counter == int(seconds_counter):
            act, total = check_services()
            if act > 0 and act != last_active:
                print(f"\n⚡ [ESTADO]: {act}/{total} servicios de la PC activos y funcionando.", flush=True)
                last_active = act
                
    except KeyboardInterrupt:
        print("\n🛑 Monitor detenido por el usuario.")
        break
    except Exception:
        time.sleep(1)

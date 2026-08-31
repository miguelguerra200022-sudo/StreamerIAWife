#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
📊 LINUWAIFU CLOUD PC: MONITOR MAESTRO EN TIEMPO REAL (CELDA 2)
================================================================================
Usa detección real por puertos y sockets (0 falsos positivos).
"""

import os
import sys
import time
import json
import socket
import urllib.request
import subprocess
from pathlib import Path

LOG_FILE = Path("/kaggle/working/linuwaifu_system.log")

print("=" * 78, flush=True)
print("📊 LINUWAIFU CLOUD PC: MONITOR MAESTRO ACTIVO (ESCUCHANDO EN VIVO)", flush=True)
print("=" * 78, flush=True)
print("🟢 [LISTO]: Monitor esperando el arranque de la Celda 3...", flush=True)
print("👉 Ahora dale Play (▶️) a la Celda 3 (Arranque del Sistema).", flush=True)
print("=" * 78 + "\n", flush=True)

# Función de comprobación real por sockets (0 falsos positivos)
def check_port(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.1):
            return True
    except Exception:
        return False

def get_services_status():
    services = {
        "🖥️ Pantalla Xvfb (1080p)": os.path.exists("/tmp/.X11-unix/X1"),
        "☁️ Google Drive 5TB (Puerto 8088)": check_port(8088),
        "🌸 LinuWaifu IA (Puerto 8000)": check_port(8000),
        "📡 Servidor VNC (Puerto 5900)": check_port(5900),
        "🌐 Servidor Web noVNC (Puerto 6080)": check_port(6080)
    }
    active = [k for k, v in services.items() if v]
    return active, len(services)

# Extraer URL de Ngrok en vivo
def get_ngrok_url():
    try:
        req = urllib.request.Request("http://127.0.0.1:4040/api/tunnels")
        with urllib.request.urlopen(req, timeout=0.5) as response:
            data = json.loads(response.read().decode())
            for t in data.get("tunnels", []):
                p_url = t.get("public_url", "")
                if "ngrok" in p_url and "http" in p_url:
                    return f"{p_url}/vnc.html?autoconnect=true&resize=scale"
    except Exception:
        pass
    return None

last_size = 0
seconds_counter = 0
system_online = False
last_active_count = -1

while True:
    try:
        time.sleep(0.5)
        seconds_counter += 0.5
        
        # 1. Leer nuevas líneas del archivo de log en tiempo real
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
                last_size = 0
        
        # 2. Comprobar servicios cada 3 segundos
        if int(seconds_counter) % 3 == 0 and seconds_counter == int(seconds_counter):
            active_list, total_services = get_services_status()
            curr_count = len(active_list)
            
            if curr_count > 0 and curr_count != last_active_count and not system_online:
                print(f"⚡ [PROGRESO]: {curr_count}/{total_services} servicios encendidos...", flush=True)
                last_active_count = curr_count
            
            # Si todos los puertos están abiertos y el sistema está listo
            if curr_count == total_services and not system_online:
                ngrok_url = get_ngrok_url()
                print("\n" + "=" * 78, flush=True)
                print("🎉 🌸 ¡TU PC EN LA NUBE ESTÁ 100% ONLINE Y FUNCIONANDO!", flush=True)
                print("=" * 78, flush=True)
                if ngrok_url:
                    print("🌐 ENLACE WEB DIRECTO (Ábrelo en Chrome/Brave en tu celular):", flush=True)
                    print(f"👉 {ngrok_url}", flush=True)
                    print("-" * 78, flush=True)
                print("📱 APP MÓVIL (RealVNC Viewer / AVNC con Touchpad y Zoom):", flush=True)
                print("   • Abre la app en tu celular -> Toca '+'", flush=True)
                print("   • Pega la dirección tcp://... de Pinggy que aparece en el log.", flush=True)
                print("=" * 78 + "\n", flush=True)
                system_online = True
                
    except KeyboardInterrupt:
        print("\n🛑 Monitor detenido por el usuario.", flush=True)
        break
    except Exception:
        time.sleep(1)

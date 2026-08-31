#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
📊 LINUWAIFU CLOUD PC: MONITOR MAESTRO DESDE EL SEGUNDO 1 (CELDA 1)
================================================================================
"""

import os
import sys
import time
import json
import urllib.request
import subprocess
from pathlib import Path

LOG_FILE = Path("/kaggle/working/linuwaifu_system.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

if not LOG_FILE.exists():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== REGISTRO DEL SISTEMA INICIADO ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

print("=" * 78, flush=True)
print("📊 LINUWAIFU CLOUD PC: MONITOR MAESTRO ACTIVO (REGISTRO DESDE EL SEGUNDO 1)", flush=True)
print("=" * 78, flush=True)
print("🟢 [LISTO]: El monitor ya está activo y escuchando.", flush=True)
print("👉 Ahora dale Play (▶️) a la Celda 2 (Arranque del Sistema).", flush=True)
print("=" * 78 + "\n", flush=True)

# Comprobar servicios activos
def get_services_status():
    services = {
        "🖥️ Pantalla Xvfb (1080p)": "Xvfb",
        "🎨 Escritorio XFCE4": "xfce4-session",
        "📡 Servidor VNC (:5900)": "x11vnc",
        "🌐 Servidor Web noVNC (:6080)": "websockify",
        "☁️ Google Drive 5TB (Rclone)": "rclone",
        "🌸 LinuWaifu IA Backend": "cloud_bridge",
        "🎵 Audio Virtual PulseAudio": "pulseaudio"
    }
    
    active = []
    for name, proc in services.items():
        try:
            out = subprocess.check_output(f"pgrep -f {proc} || true", shell=True, text=True).strip()
            if out:
                active.append((name, out.split()[0]))
        except Exception:
            pass
    return active, len(services)

# Extraer URL de Ngrok en vivo
def get_ngrok_url():
    try:
        req = urllib.request.Request("http://127.0.0.1:4040/api/tunnels")
        with urllib.request.urlopen(req, timeout=1) as response:
            data = json.loads(response.read().decode())
            for t in data.get("tunnels", []):
                p_url = t.get("public_url", "")
                if "ngrok" in p_url:
                    return f"{p_url}/vnc.html?autoconnect=true&resize=scale"
    except Exception:
        pass
    return None

# Streaming continuo infinito
last_size = 0
seconds_counter = 0
links_shown = False

while True:
    try:
        time.sleep(0.5)
        seconds_counter += 0.5
        
        # Leer nuevas líneas del archivo de log
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
                            elif "[success]" in line_str.lower() or "éxito" in line_str.lower() or "conectado" in line_str.lower():
                                print(f"🟢 {line_str}", flush=True)
                            else:
                                print(f"  {line_str}", flush=True)
            elif curr_size < last_size:
                last_size = 0
        
        # Comprobar si los 7 servicios están activos y mostrar los enlaces
        if int(seconds_counter) % 5 == 0 and seconds_counter == int(seconds_counter):
            active_list, total_services = get_services_status()
            
            if len(active_list) == total_services and not links_shown:
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
                print("   • Busca la dirección tcp://... de Pinggy que aparece arriba en el log.", flush=True)
                print("=" * 78 + "\n", flush=True)
                links_shown = True
            elif len(active_list) > 0 and not links_shown:
                print(f"⚡ [INICIANDO]: {len(active_list)}/{total_services} servicios activos...", flush=True)
                
    except KeyboardInterrupt:
        print("\n🛑 Monitor detenido por el usuario.", flush=True)
        break
    except Exception:
        time.sleep(1)

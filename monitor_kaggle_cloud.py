#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 MONITOR EN TIEMPO REAL CONTINUO PARA KAGGLE CLOUD PC (GPU TESLA T4)
Monitorea la máquina, extrae enlaces de conexión desde Kaggle API y Google Drive FUSE,
notifica a Telegram y sigue vigilando en segundo plano ante cualquier error.
"""

import requests
import json
import time
import re
import sys
import subprocess
from pathlib import Path
import telegram_notifier

auth = ('miguelguerra22', 'b4031084ad25f34042347dfd7b6af451')
status_url = "https://www.kaggle.com/api/v1/kernels/status?userName=miguelguerra22&kernelSlug=aether-cloud-pc"
output_url = "https://www.kaggle.com/api/v1/kernels/output?userName=miguelguerra22&kernelSlug=aether-cloud-pc"

t_start = time.time()
print("=" * 78, flush=True)
print("⏳ MONITOR ACTIVO: AETHER CLOUD PC (GPU TESLA T4 + DATABASE 1)", flush=True)
print("   Cuenta: miguelguerra200022@gmail.com (miguelguerra22)", flush=True)
print("   Notebook: aether-cloudpc (StarParks Gaming Edition)", flush=True)
print("=" * 78, flush=True)

found_url = None
telegram_notified = False
last_log_len = 0
last_url_check = 0

def check_gdrive_url():
    """Verifica si la máquina ya sincronizó su URL en Google Drive."""
    for remote_path in ["gdrive:Cloud_PC/system_state/current_vnc_url.txt", "gdrive:PC_Kaggle/system_state/current_vnc_url.txt"]:
        try:
            res = subprocess.run(["rclone", "cat", remote_path], capture_output=True, text=True, timeout=8)
            if res.returncode == 0 and res.stdout.strip():
                content = res.stdout.strip()
                if "trycloudflare.com" in content or "ngrok-free.app" in content:
                    return content
        except Exception:
            pass
    return None

def test_url_alive(url):
    """Prueba si el enlace de noVNC responde 200 OK."""
    try:
        clean_url = url.split("?")[0]
        r = requests.get(clean_url, timeout=6)
        return r.status_code == 200
    except Exception:
        return False

# Monitorear hasta por 12 horas continuas (43200 segundos)
for iteration in range(7200):
    try:
        r_status = requests.get(status_url, auth=auth, timeout=10)
        if r_status.status_code == 200:
            status_data = r_status.json()
            current_status = status_data.get("status", "unknown")
        else:
            current_status = "network_wait"

        # Reportar logs de salida si Kaggle los emite
        try:
            r_out = requests.get(output_url, auth=auth, timeout=10)
            if r_out.status_code == 200:
                out_data = r_out.json()
                log_text = out_data.get("log", "") or out_data.get("logNullable", "") or ""
                if len(log_text) > last_log_len:
                    new_lines = log_text[last_log_len:]
                    last_log_len = len(log_text)
                    for line in new_lines.splitlines():
                        if line.strip():
                            print(f"[{time.strftime('%H:%M:%S')}] {line.strip()}", flush=True)
        except Exception:
            pass

        # Chequear URL en Google Drive cada 15 segundos
        now = time.time()
        if not found_url and (now - last_url_check > 15):
            last_url_check = now
            candidate_url = check_gdrive_url()
            if candidate_url:
                is_alive = test_url_alive(candidate_url)
                if is_alive:
                    found_url = candidate_url
                    t_elapsed = time.time() - t_start
                    print("\n" + "=" * 78, flush=True)
                    print(f"🎉 ¡UBUNTU CLOUD PC CON GPU ONLINE EN {t_elapsed:.1f} SEGUNDOS!", flush=True)
                    print(f"🌐 ENLACE DE ACCESO DIRECTO: {found_url}", flush=True)
                    print("=" * 78 + "\n", flush=True)
                    
                    if not telegram_notified:
                        try:
                            telegram_notifier.enviar_mensaje(
                                f"🚀 <b>¡UBUNTU CLOUD PC ONLINE CON GPU TESLA T4!</b> 🌸\n\n"
                                f"⚡ <b>Hardware:</b> NVIDIA Tesla T4\n"
                                f"⏱️ <b>Tiempo de arranque:</b> {t_elapsed:.1f}s\n\n"
                                f"👉 <a href='{found_url}'>Entrar a tu Ubuntu en Navegador</a>\n\n"
                                f"🔑 <b>Contraseña:</b> <code>09032000Mi.</code>\n"
                                f"📱 <i>Menú lateral Starparks y mandos táctiles activos.</i>"
                            )
                            telegram_notified = True
                        except Exception as e_tg:
                            print(f"Aviso Telegram: {e_tg}", flush=True)

        if iteration % 10 == 0:
            print(f"[{time.strftime('%H:%M:%S')}] [Vigilante Kaggle]: Estado: {current_status.upper()} | Enlace Activo: {'SÍ' if found_url else 'Iniciando servicios...'}", flush=True)

        if current_status in ["error", "cancelAcknowledged"]:
            print(f"\n🔴 [{time.strftime('%H:%M:%S')}] El kernel se detuvo con estado: {current_status}", flush=True)
            if status_data.get("failureMessage"):
                print(f"Detalle del error de Kaggle: {status_data.get('failureMessage')}", flush=True)
            break

    except Exception as e:
        pass
            
    time.sleep(5)

print(f"\n🏁 [{time.strftime('%H:%M:%S')}] Monitor de sesión finalizado.", flush=True)

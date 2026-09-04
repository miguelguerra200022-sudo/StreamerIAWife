#!/usr/bin/env python3
import time, json, requests
from pathlib import Path

print("📡 Monitoreando arranque en vivo de Ubuntu Cloud PC...", flush=True)

t0 = time.time()
while time.time() - t0 < 600: # 10 minutos max
    try:
        # 1. Consultar ntfy para recepción de telemetría de encendido
        r = requests.get("https://ntfy.sh/miguelguerra_cloudpc_status/json?poll=1&since=all", timeout=5)
        if r.status_code == 200:
            lines = [l.strip() for l in r.text.strip().split("\n") if l.strip()]
            for line in reversed(lines):
                try:
                    data = json.loads(line)
                    msg_txt = data.get("message", "")
                    if msg_txt:
                        try:
                            payload = json.loads(msg_txt)
                            if payload.get("status") == "online":
                                elapsed = round(time.time() - t0, 1)
                                print(f"\n🎉 ¡SISTEMA ONLINE Y OPERATIVO!", flush=True)
                                print(f"⏱️ Tiempo total de arranque: {payload.get('boot_time_seconds', elapsed)}s", flush=True)
                                print(f"🔗 URL WiFi: {payload.get('wifi_url')}", flush=True)
                                print(f"📱 URL Móvil: {payload.get('mobile_url')}", flush=True)
                                print(f"🔑 Password VNC: {payload.get('vnc_password')}", flush=True)
                                exit(0)
                        except Exception:
                            pass
                except Exception:
                    pass
    except Exception:
        pass
    time.sleep(3)

print("⏱️ Timeout esperando señal de encendido.", flush=True)

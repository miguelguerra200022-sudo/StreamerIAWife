#!/usr/bin/env python3
import time, json, requests, subprocess
from pathlib import Path

creds = json.loads(Path("~/.kaggle/kaggle.json").expanduser().read_text())
auth = (creds['username'], creds['key'])
user = creds['username']
kernel_slug = "ubuntu-cloud-pc-live"

print(f"📡 Monitoreando arranque continuo de {user}/{kernel_slug}...", flush=True)

t0 = time.time()
while time.time() - t0 < 1800: # 30 min
    elapsed = int(time.time() - t0)
    
    # 1. Chequear canal ntfy
    try:
        r_n = requests.get("https://ntfy.sh/miguelguerra_cloudpc_status/json?poll=1&since=all", timeout=4)
        if r_n.status_code == 200 and r_n.text.strip():
            for line in reversed(r_n.text.strip().split("\n")):
                try:
                    d = json.loads(line)
                    msg_txt = d.get("message", "")
                    if msg_txt:
                        payload = json.loads(msg_txt)
                        if payload.get("status") == "online":
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

    # 2. Chequear estado en Kaggle
    try:
        r_k = requests.get(f"https://www.kaggle.com/api/v1/kernels/status?userName={user}&kernelSlug={kernel_slug}", auth=auth, timeout=6)
        if r_k.status_code == 200:
            k_data = r_k.json()
            st = k_data.get("status")
            if st != "running":
                print(f"\n🏁 Kernel cambió de estado a: {st}", flush=True)
                if k_data.get("failureMessage"):
                    print(f"⚠️ Error: {k_data.get('failureMessage')}", flush=True)
                subprocess.run(f"kaggle kernels output {user}/{kernel_slug} -p ~/kernel_test", shell=True)
                exit(0)
    except Exception:
        pass

    time.sleep(5)

print("⏱️ Monitor finalizado por tiempo.", flush=True)

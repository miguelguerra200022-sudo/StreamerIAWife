#!/usr/bin/env python3
import time, json, requests, os, subprocess
from pathlib import Path

creds_file = Path("~/.kaggle/kaggle.json").expanduser()
if not creds_file.exists():
    print("❌ No se encontró ~/.kaggle/kaggle.json")
    exit(1)

creds = json.loads(creds_file.read_text())
auth = (creds['username'], creds['key'])
kernel_slug = "compilar-database-1-ubuntu-core"
user = creds['username']
url_status = f"https://www.kaggle.com/api/v1/kernels/status?userName={user}&kernelSlug={kernel_slug}"

log_dir = Path.home() / "kernel_log"
log_dir.mkdir(parents=True, exist_ok=True)

print(f"📡 Monitoreando compilación de {user}/{kernel_slug}...")

last_status = None
t_start = time.time()

while True:
    try:
        r = requests.get(url_status, auth=auth, timeout=10)
        if r.status_code == 200:
            data = r.json()
            status = data.get("status")
            fail_msg = data.get("failureMessage", "")
            has_fail = data.get("hasFailureMessage", False)
            elapsed = int(time.time() - t_start)
            
            if status != last_status:
                print(f"[{time.strftime('%X')}] Estado: {status} (Transcurrido: {elapsed}s)")
                last_status = status
            
            if status in ["complete", "error"] or has_fail:
                print(f"\n🏁 Kernel finalizado con estado: {status}")
                if fail_msg:
                    print(f"⚠️ Mensaje de fallo: {fail_msg}")
                
                # Descargar salida
                subprocess.run(f"kaggle kernels output {user}/{kernel_slug} -p '{log_dir}'", shell=True)
                print("📄 Archivos de salida descargados en ~/kernel_log/")
                break
        else:
            print(f"⚠️ Error consultando API de Kaggle: {r.status_code}")
    except Exception as e:
        print(f"⚠️ Excepción en monitor: {e}")
    
    time.sleep(20)


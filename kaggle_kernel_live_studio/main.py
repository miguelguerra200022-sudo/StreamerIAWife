import os, sys, subprocess, shutil, time

print("=" * 78, flush=True)
print("🚀 [BOOT] INICIANDO UBUNTU CLOUD PC CON GPU (CUENTA: miguelguerra22)", flush=True)
print("=" * 78, flush=True)

t_boot_begin = time.time()

# 1. Clonar o actualizar el repositorio con las últimas mejoras de GitHub
repo_dir = "/kaggle/working/StreamerIAWife"
if os.path.exists(repo_dir):
    shutil.rmtree(repo_dir, ignore_errors=True)

print("📥 Obteniendo última versión de GitHub...", flush=True)
res_clone = subprocess.run(f"git clone https://github.com/miguelguerra200022-sudo/StreamerIAWife.git {repo_dir}", shell=True)
if res_clone.returncode != 0:
    print("❌ Error clonando repositorio desde GitHub", flush=True)
    sys.exit(1)

# 2. Configurar credenciales maestras de Kaggle para miguelguerra22
kaggle_dir = os.path.expanduser("~/.kaggle")
os.makedirs(kaggle_dir, exist_ok=True)
with open(os.path.join(kaggle_dir, "kaggle.json"), "w") as f:
    f.write('{"username": "miguelguerra22", "key": "b4031084ad25f34042347dfd7b6af451"}\n')
os.chmod(os.path.join(kaggle_dir, "kaggle.json"), 0o600)

os.environ["KAGGLE_USERNAME"] = "miguelguerra22"
os.environ["KAGGLE_KEY"] = "b4031084ad25f34042347dfd7b6af451"
os.environ["NGROK_TOKEN"] = "DISABLED"
os.environ["MASTER_BOOT_START"] = str(t_boot_begin)
os.environ["PYTHONUNBUFFERED"] = "1"

# 3. Lanzar el servidor en vivo con bucle infinito anti-caídas (Cloudflare Tunnel Puro)
os.chdir(repo_dir)
while True:
    print("🐧 Ejecutando run_kaggle_vnc_studio.py con GPU activa y Cloudflare...", flush=True)
    res_run = subprocess.run([sys.executable, "-u", "run_kaggle_vnc_studio.py", "SIN_TOKEN"])
    print(f"⚠️ run_kaggle_vnc_studio.py finalizó con código {res_run.returncode}. Reiniciando en 10s...", flush=True)
    time.sleep(10)

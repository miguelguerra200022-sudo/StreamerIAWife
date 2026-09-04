import os, sys, subprocess, shutil, time

print("=" * 78, flush=True)
print("🚀 [BOOT] INICIANDO UBUNTU CLOUD PC CON GPU (INSTALACIÓN LIMPIA 100% DESDE CERO)", flush=True)
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

# 2. Configurar credenciales maestras de Kaggle
kaggle_dir = os.path.expanduser("~/.kaggle")
os.makedirs(kaggle_dir, exist_ok=True)
with open(os.path.join(kaggle_dir, "kaggle.json"), "w") as f:
    f.write('{"username": "miguel55755", "key": "54bfca5f24e2347b9dcc55073abe8952"}\n')
os.chmod(os.path.join(kaggle_dir, "kaggle.json"), 0o600)

os.environ["KAGGLE_USERNAME"] = "miguel55755"
os.environ["KAGGLE_KEY"] = "54bfca5f24e2347b9dcc55073abe8952"
os.environ["MASTER_BOOT_START"] = str(t_boot_begin)

# 3. Lanzar el servidor en vivo con bucle infinito anti-caídas
os.chdir(repo_dir)
while True:
    print("🐧 Ejecutando run_kaggle_vnc_studio.py (Instalación limpia sin Database)...", flush=True)
    res_run = subprocess.run([sys.executable, "run_kaggle_vnc_studio.py"])
    print(f"⚠️ run_kaggle_vnc_studio.py finalizó con código {res_run.returncode}. Reiniciando en 10s...", flush=True)
    time.sleep(10)

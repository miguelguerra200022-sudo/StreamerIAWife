import os, sys, subprocess, shutil, time

print("=" * 78, flush=True)
print("🚀 [BOOT] INICIANDO UBUNTU CLOUD PC CON ACELERACIÓN GPU & DATABASE 1", flush=True)
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
    f.write('{"username": "miguelguerra22", "key": "b4031084ad25f34042347dfd7b6af451"}\n')
os.chmod(os.path.join(kaggle_dir, "kaggle.json"), 0o600)

os.environ["KAGGLE_USERNAME"] = "miguelguerra22"
os.environ["KAGGLE_KEY"] = "b4031084ad25f34042347dfd7b6af451"
os.environ["MASTER_BOOT_START"] = str(t_boot_begin)

# 3. Lanzar el servidor en vivo
os.chdir(repo_dir)
print("🐧 Ejecutando run_kaggle_vnc_studio.py...", flush=True)
res_run = subprocess.run([sys.executable, "run_kaggle_vnc_studio.py"])
sys.exit(res_run.returncode)

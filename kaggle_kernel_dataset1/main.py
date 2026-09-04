import os, sys, subprocess, shutil, time

print("=" * 78)
print("🚀 INICIANDO EJECUCIÓN MAESTRA: COMPILACIÓN DATABASE 1 EN KAGGLE")
print("=" * 78)

# 1. Clonar repositorio StreamerIAWife
repo_dir = "/kaggle/working/StreamerIAWife"
if os.path.exists(repo_dir):
    shutil.rmtree(repo_dir, ignore_errors=True)

res_clone = subprocess.run(f"git clone https://github.com/miguelguerra200022-sudo/StreamerIAWife.git {repo_dir}", shell=True)
if res_clone.returncode != 0:
    print("❌ Error clonando repositorio desde GitHub")
    sys.exit(1)

# 2. Configurar credenciales Kaggle para permitir la subida del dataset final
kaggle_dir = os.path.expanduser("~/.kaggle")
os.makedirs(kaggle_dir, exist_ok=True)
with open(os.path.join(kaggle_dir, "kaggle.json"), "w") as f:
    f.write('{"username": "miguelguerra22", "key": "b4031084ad25f34042347dfd7b6af451"}\n')
os.chmod(os.path.join(kaggle_dir, "kaggle.json"), 0o600)

os.environ["KAGGLE_USERNAME"] = "miguelguerra22"
os.environ["KAGGLE_KEY"] = "b4031084ad25f34042347dfd7b6af451"

# 3. Lanzar el compilador maestro de Database 1
os.chdir(repo_dir)
print("📦 Ejecutando compilar_dataset1_ubuntu_core.py...", flush=True)
res_build = subprocess.run([sys.executable, "compilar_dataset1_ubuntu_core.py"])
sys.exit(res_build.returncode)

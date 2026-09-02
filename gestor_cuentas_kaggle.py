#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔑 GESTOR MULTI-CUENTAS DE KAGGLE POR CORREO ELECTRÓNICO
Permite administrar múltiples cuentas de Kaggle para rotar cuotas de GPU
sin confundir los tokens ni los usuarios.
"""
import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CUENTAS_FILE = BASE_DIR / "cuentas_kaggle.json"
KAGGLE_DIR = Path.home() / ".kaggle"
KAGGLE_JSON = KAGGLE_DIR / "kaggle.json"

def cargar_cuentas():
    if not CUENTAS_FILE.exists():
        return {"cuentas": {}, "cuenta_activa": None}
    try:
        return json.loads(CUENTAS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"cuentas": {}, "cuenta_activa": None}

def guardar_cuentas(data):
    CUENTAS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    # Copia de seguridad en SD Card
    sd_file = Path("/sdcard/Antigravity/IdeasMillonarias/StreamerIAWife/cuentas_kaggle.json")
    try:
        sd_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

def activar_cuenta(email):
    data = cargar_cuentas()
    cuentas = data.get("cuentas", {})
    if email not in cuentas:
        print(f"❌ La cuenta con correo '{email}' no está registrada.")
        return False
        
    for k in cuentas:
        cuentas[k]["activa"] = (k == email)
    data["cuenta_activa"] = email
    guardar_cuentas(data)
    
    # Escribir en ~/.kaggle/kaggle.json
    KAGGLE_DIR.mkdir(parents=True, exist_ok=True)
    c_info = cuentas[email]
    k_data = {"username": c_info["username"], "key": c_info["key"]}
    KAGGLE_JSON.write_text(json.dumps(k_data), encoding="utf-8")
    KAGGLE_JSON.chmod(0o600)
    print(f"✅ [✓] Cuenta activa cambiada a: {email} (Usuario: {c_info['username']})")
    return True

def listar_cuentas():
    data = cargar_cuentas()
    cuentas = data.get("cuentas", {})
    activa = data.get("cuenta_activa")
    print("\n" + "=" * 78)
    print("🔑 CATÁLOGO DE CUENTAS KAGGLE REGISTRADAS:")
    print("=" * 78)
    if not cuentas:
        print("  (No hay cuentas registradas)")
    for mail, info in cuentas.items():
        marcador = "🟢 [ACTIVA]" if mail == activa else "⚪ [DISPONIBLE]"
        print(f"{marcador} {mail}")
        print(f"   • Usuario Kaggle: {info.get('username')}")
        print(f"   • Título:         {info.get('titulo')}")
        print(f"   • Notas:          {info.get('notas', 'Sin notas')}")
        print("-" * 78)

def agregar_cuenta(email, username, key, titulo=None, notas=None):
    data = cargar_cuentas()
    cuentas = data.setdefault("cuentas", {})
    cuentas[email] = {
        "email": email,
        "username": username,
        "key": key,
        "titulo": titulo or f"Cuenta {email}",
        "activa": False,
        "notas": notas or ""
    }
    if not data.get("cuenta_activa"):
        data["cuenta_activa"] = email
        cuentas[email]["activa"] = True
        activar_cuenta(email)
    else:
        guardar_cuentas(data)
    print(f"✅ Cuenta '{email}' ({username}) registrada con éxito.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "listar":
            listar_cuentas()
        elif cmd == "activar" and len(sys.argv) > 2:
            activar_cuenta(sys.argv[2])
        elif cmd == "agregar" and len(sys.argv) > 4:
            email = sys.argv[2]
            user = sys.argv[3]
            k = sys.argv[4]
            t = sys.argv[5] if len(sys.argv) > 5 else None
            agregar_cuenta(email, user, k, t)
        else:
            print("Uso:")
            print("  python3 gestor_cuentas_kaggle.py listar")
            print("  python3 gestor_cuentas_kaggle.py activar <correo>")
            print("  python3 gestor_cuentas_kaggle.py agregar <correo> <usuario> <api_key> [titulo]")
    else:
        listar_cuentas()

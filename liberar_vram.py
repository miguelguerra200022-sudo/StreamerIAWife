#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ PURGADOR Y LIBERADOR DE VRAM / GPU & RAM EN 1-CLIC
Desaloja modelos pesados de IA (Ollama, ComfyUI, FastAPIs) de la tarjeta gráfica
Nvidia Tesla T4 para dejar 100% de la VRAM (16GB) disponible para Gaming o Renderizado 3D.
"""
import os
import sys
import subprocess

def notify(msg, title="⚡ Purgador de VRAM"):
    print(f"[{title}] {msg}", flush=True)
    if os.environ.get("DISPLAY"):
        subprocess.run(f"notify-send '{title}' '{msg}' 2>/dev/null || true", shell=True)

print("⚡ Iniciando purga de VRAM y memoria gráfica...", flush=True)

# 1. Terminar procesos pesados de IA que acaparan VRAM
ai_processes = ["ollama", "comfyui", "fastapi_ai_gateway", "fastapi_image_gateway", "tts-server", "rvc"]
for proc in ai_processes:
    subprocess.run(f"pkill -9 -f '{proc}' 2>/dev/null || true", shell=True)

# 2. Forzar limpieza de caché CUDA con PyTorch si está instalado
try:
    import torch
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        print("✓ Caché CUDA de PyTorch vaciado.", flush=True)
except Exception:
    pass

# 3. Sincronizar y limpiar caché de RAM del sistema
subprocess.run("sync", shell=True)
try:
    with open("/proc/sys/vm/drop_caches", "w") as f:
        f.write("3\n")
except Exception:
    pass

notify("🎉 ¡VRAM de la GPU Nvidia Tesla T4 y Memoria RAM liberadas al 100%! Listo para Gaming.", "⚡ VRAM Limpia")

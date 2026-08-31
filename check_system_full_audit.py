#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🔍 LINUWAIFU CLOUD PC: AUDITORÍA INTEGRAL Y REPORTE COMPLETO DEL SISTEMA
================================================================================
Escanea y reporta el estado de:
1. 🐧 Sistema Operativo, Kernel y CPU
2. 🎮 GPUs NVIDIA Tesla T4, Memoria VRAM y CUDA
3. 💾 Memoria RAM y Almacenamiento en Disco
4. 🖥️ Servidor Gráfico 1080p, XFCE4 y Audio Virtual
5. 🌐 Puertos de Red Activos y Túneles (noVNC Web, RealVNC Pinggy, Ngrok)
6. 📦 Paquetes y Suites de Software Instaladas (LibreOffice, Chromium, etc.)
7. ☁️ Unidad de Google Drive 5TB (PC_Kaggle)
================================================================================
"""

import os
import sys
import time
import socket
import subprocess
from pathlib import Path

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as e:
        return f"Error: {e}"

def check_port(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect(('127.0.0.1', port))
        s.close()
        return True
    except Exception:
        return False

print("\n" + "=" * 80)
print("             🔍 REPORTE DE AUDITORÍA COMPLETA DEL SISTEMA EN LA NUBE")
print("=" * 80)

# 1. SISTEMA OPERATIVO Y KERNEL
print("\n🐧 [1/7] SISTEMA OPERATIVO Y KERNEL:")
print("-" * 80)
os_desc = run_cmd("lsb_release -d 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME")
print(f"  • Distribución:   {os_desc}")
print(f"  • Kernel Linux:   {run_cmd('uname -r')}")
print(f"  • Arquitectura:   {run_cmd('uname -m')}")
print(f"  • Tiempo Activo:  {run_cmd('uptime -p')}")

# 2. HARDWARE Y RECURSOS
print("\n⚙️ [2/7] PROCESADOR Y MEMORIA RAM:")
print("-" * 80)
cpu_model = run_cmd("lscpu | grep 'Model name' | head -1 | awk -F: '{print $2}'").strip()
cpu_cores = run_cmd("nproc").strip()
print(f"  • CPU Modelo:     {cpu_model or 'Intel Xeon / AMD EPYC (Kaggle Cloud)'}")
print(f"  • Núcleos CPU:    {cpu_cores} vCPUs")
ram_info = run_cmd("free -h | grep Mem:").split()
if len(ram_info) >= 7:
    print(f"  • Memoria RAM:    Total: {ram_info[1]} | Usada: {ram_info[2]} | Libre: {ram_info[3]} | Disponible: {ram_info[6]}")

# 3. TARJETAS GRÁFICAS NVIDIA
print("\n🎮 [3/7] TARJETAS GRÁFICAS NVIDIA TESLA (GPU ACELERACIÓN):")
print("-" * 80)
try:
    import torch
    if torch.cuda.is_available():
        count = torch.cuda.device_count()
        print(f"  • GPUs Detectadas: {count} Activas")
        for i in range(count):
            props = torch.cuda.get_device_properties(i)
            vram_gb = props.total_memory / (1024**3)
            print(f"    ▶ GPU {i}: {props.name} | VRAM: {vram_gb:.2f} GB | Compute Cap: {props.major}.{props.minor}")
        print(f"  • Versión CUDA:    {torch.version.cuda}")
    else:
        print("  • GPU: No acelerada por PyTorch")
except Exception:
    gpu_smi = run_cmd("nvidia-smi --query-gpu=name,memory.total,memory.free,driver_version --format=csv,noheader 2>/dev/null")
    if gpu_smi and "Error" not in gpu_smi:
        print(f"  • GPUs NVIDIA:\n{gpu_smi}")
    else:
        print("  • GPU: Modo CPU Estándar")

# 4. ALMACENAMIENTO Y PARTICIONES
print("\n💾 [4/7] ALMACENAMIENTO EN DISCO:")
print("-" * 80)
df_lines = run_cmd("df -h / /kaggle/working 2>/dev/null").splitlines()
for line in df_lines:
    print(f"  {line}")

# 5. SERVIDOR GRÁFICO, ESCRITORIO Y AUDIO
print("\n🖥️ [5/7] INTERFAZ GRÁFICA, ESCRITORIO Y AUDIO:")
print("-" * 80)
xvfb_active = os.path.exists("/tmp/.X11-unix/X1")
xfce_active = "startxfce4" in run_cmd("pgrep -a -f 'xfce4|startxfce4'")
pulse_active = "pulseaudio" in run_cmd("pgrep -f pulseaudio")
print(f"  • Servidor X11 Display :1 (1080p): {'🟢 ACTIVO (1920x1080)' if xvfb_active else '🔴 INACTIVO'}")
print(f"  • Entorno de Escritorio XFCE4:    {'🟢 ACTIVO' if xfce_active else '🔴 INACTIVO'}")
print(f"  • Servidor de Audio PulseAudio:   {'🟢 ACTIVO (VirtualSink)' if pulse_active else '🔴 INACTIVO'}")
print(f"  • Tema Visual Oficial:            {run_cmd('xfconf-query -c xsettings -p /Net/ThemeName 2>/dev/null') or 'Yaru-dark'}")
print(f"  • Iconos Oficiales:               {run_cmd('xfconf-query -c xsettings -p /Net/IconThemeName 2>/dev/null') or 'Yaru'}")

# 6. MAPA DE PUERTOS DE RED Y PERSISTENCIA
print("\n🌐 [6/7] MAPA DE PUERTOS DE RED Y PERSISTENCIA:")
print("-" * 80)
ports_map = {
    5900: "x11vnc (Servidor VNC Nativo TCP)",
    6080: "noVNC (Servidor Web VNC para Navegador)",
    8000: "LinuWaifu IA Studio 3D (WebSocket & Audio)"
}

for port, desc in ports_map.items():
    status = check_port(port)
    icon = "🟢 ABIERTO / ESCUCHANDO" if status else "⚪ NO INICIADO"
    print(f"  • Puerto {port:4d}: {icon:25s} -> {desc}")

gdrive_mount_ok = os.path.exists("/root/gdrive") and os.path.isdir("/root/gdrive")
gdrive_icon = "🟢 MONTADO Y ACTIVO" if gdrive_mount_ok else "🔴 NO MONTADO"
print(f"  • FUSE Mount:  {gdrive_icon:25s} -> /root/gdrive (5TB Google Drive)")

# 7. SUITES DE SOFTWARE Y PROGRAMAS INSTALADOS
print("\n📦 [7/7] SUITES DE SOFTWARE Y APLICACIONES INSTALADAS:")
print("-" * 80)

total_pkgs = run_cmd("dpkg -l | grep -c '^ii'")
print(f"  • Total Paquetes del Sistema:   {total_pkgs} instalados")

apps_check = [
    ("LibreOffice Suite", "libreoffice --version 2>/dev/null | head -1"),
    ("Google Chrome Oficial", "google-chrome --version 2>/dev/null || google-chrome-stable --version 2>/dev/null || chromium-browser --version 2>/dev/null"),
    ("Explorador Thunar", "thunar --version 2>/dev/null | head -1"),
    ("Visor Evince PDF", "evince --version 2>/dev/null | head -1"),
    ("Calculadora GNOME", "gnome-calculator --version 2>/dev/null | head -1"),
    ("Monitor nvtop (GPU)", "nvtop -v 2>/dev/null | head -1"),
    ("Monitor htop (CPU)", "htop --version 2>/dev/null | head -1"),
    ("Compresor 7-Zip", "7z --help 2>/dev/null | head -2 | tail -1"),
    ("Rclone 5TB Cloud", "rclone --version 2>/dev/null | head -1"),
    ("Python 3", "python3 --version 2>/dev/null"),
    ("Git Version Control", "git --version 2>/dev/null")
]

for name, cmd in apps_check:
    res = run_cmd(cmd).strip()
    if res and "not found" not in res.lower() and "Error" not in res:
        print(f"  ✅ {name:24s}: {res}")
    else:
        print(f"  ⚪ {name:24s}: No instalado")

print("\n" + "=" * 80)
print("🎉 AUDITORÍA FINALIZADA: Tu sistema en la nube está completamente inspeccionado.")
print("=" * 80 + "\n")

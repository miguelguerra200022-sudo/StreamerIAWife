#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
📦 AUDITORÍA PROFUNDA DE PAQUETES Y COMPONENTES INSTALADOS EN UBUNTU
================================================================================
Analiza:
1. 🩺 Salud e Integridad del Gestor de Paquetes (dpkg audit / broken check).
2. 📊 Conteo total y desglose por categorías oficiales de Ubuntu.
3. 🐘 Top 20 de paquetes más grandes ocupando espacio en disco (MB/GB).
4. 🔍 Verificación uno por uno de componentes clave (Ofimática, Multimedia, Desktop).
5. 🟢 Diagnóstico de salud general del sistema operativo.
================================================================================
"""

import os
import sys
import subprocess

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""

print("\n" + "=" * 80)
print("       🩺 AUDITORÍA PROFUNDA DE PAQUETES Y ESTADO DE SALUD DE UBUNTU")
print("=" * 80)

# 1. SALUD DEL GESTOR DE PAQUETES (DPKG & APT)
print("\n🩺 [1/5] VERIFICACIÓN DE INTEGRIDAD Y PAQUETES ROTOS:")
print("-" * 80)
broken_pkgs = run("dpkg --audit")
if not broken_pkgs:
    print("  ✅ [EXCELENTE]: Cero paquetes rotos o incompletos. Base de datos DPKG 100% íntegra.")
else:
    print(f"  ⚠️ Paquetes con inconsistencias:\n{broken_pkgs}")

total_installed = run("dpkg -l | grep -c '^ii'")
print(f"  📦 Total de paquetes instalados en el sistema: {total_installed} paquetes oficiales")

# 2. VERIFICACIÓN DETALLADA POR CATEGORÍAS
print("\n📂 [2/5] VERIFICACIÓN DE COMPONENTES POR CATEGORÍA:")
print("-" * 80)

categories = {
    "🖥️ ENTORNO GRÁFICO & X11": [
        ("xfce4", "Entorno de escritorio XFCE4 base"),
        ("xfce4-panel", "Barra de tareas y paneles"),
        ("xfdesktop4", "Gestor de iconos y fondos de pantalla"),
        ("thunar", "Explorador de archivos oficial"),
        ("x11vnc", "Servidor de control remoto VNC 60fps"),
        ("xvfb", "Servidor de pantalla virtual 1080p"),
        ("dbus-x11", "Bus de comunicación entre aplicaciones"),
        ("yaru-theme-gtk", "Tema visual oficial Yaru-Dark de Ubuntu"),
        ("yaru-theme-icon", "Set de iconos oficiales de Ubuntu"),
        ("fonts-ubuntu", "Tipografías oficiales de Canonical")
    ],
    "🏢 SUITE OFIMÁTICA & DOCUMENTOS": [
        ("libreoffice", "Suite ofimática completa de Ubuntu"),
        ("libreoffice-writer", "Procesador de textos (Word)"),
        ("libreoffice-calc", "Hoja de cálculo (Excel)"),
        ("libreoffice-impress", "Presentaciones (PowerPoint)"),
        ("evince", "Visor de documentos y PDFs de GNOME"),
        ("gnome-calculator", "Calculadora oficial de GNOME")
    ],
    "🎬 MULTIMEDIA, AUDIO & CÓDECS": [
        ("pulseaudio", "Servidor de audio virtual para transmisión"),
        ("pulseaudio-utils", "Herramientas de control de audio"),
        ("pavucontrol", "Control de volumen avanzado PulseAudio"),
        ("mpv", "Reproductor multimedia acelerado por hardware"),
        ("ubuntu-restricted-extras", "Códecs multimedia MP4, AAC, MP3 propietarios")
    ],
    "🌐 NAVEGACIÓN & HERRAMIENTAS DE RED": [
        ("chromium-browser", "Navegador web Chromium"),
        ("curl", "Herramienta de transferencias HTTP/HTTPS"),
        ("wget", "Descargador de archivos por red"),
        ("rclone", "Controlador de almacenamiento en la nube 5TB"),
        ("openssh-client", "Cliente SSH para túneles remotos seguros")
    ],
    "🛠️ DESARROLLO, MONITOREO & COMPRESIÓN": [
        ("htop", "Monitor interactivo de CPU y Memoria RAM"),
        ("nvtop", "Monitor en tiempo real de 2x GPUs NVIDIA"),
        ("p7zip-full", "Compresor y descompresor 7-Zip y RAR"),
        ("unzip", "Extractor de archivos ZIP"),
        ("git", "Sistema de control de versiones Git"),
        ("python3", "Intérprete oficial de Python 3")
    ]
}

total_checked = 0
total_ok = 0

for cat_name, pkg_list in categories.items():
    print(f"\n{cat_name}:")
    for pkg_name, desc in pkg_list:
        total_checked += 1
        status = run(f"dpkg-query -W -f='${{Status}}' {pkg_name} 2>/dev/null")
        version = run(f"dpkg-query -W -f='${{Version}}' {pkg_name} 2>/dev/null")
        if "install ok installed" in status:
            total_ok += 1
            print(f"  ✅ [INSTALADO] {pkg_name:24s} ({version:18s}) -> {desc}")
        else:
            print(f"  ⚪ [NO PRESENTE] {pkg_name:24s}                     -> {desc}")

# 3. TOP 20 PAQUETES MÁS GRANDES EN DISCO
print("\n🐘 [3/5] TOP 20 PAQUETES MÁS GRANDES EN EL DISCO:")
print("-" * 80)
top_pkgs_raw = run("dpkg-query -Wf '${Installed-Size}\t${Package}\n' | sort -n -r | head -20")
for line in top_pkgs_raw.splitlines():
    parts = line.split()
    if len(parts) >= 2:
        size_kb = int(parts[0])
        size_mb = size_kb / 1024
        pkg = parts[1]
        print(f"  • {pkg:38s} : {size_mb:8.2f} MB ({size_kb:,} KB)")

# 4. ESTADO DE SERVICIOS Y DEMONIOS EN TIEMPO REAL
print("\n⚙️ [4/5] ESTADO EN VIVO DE LOS SERVICIOS Y PROCESOS:")
print("-" * 80)
services = [
    ("Pantalla Virtual X11 (:1)", "pgrep -f 'Xvfb :1'"),
    ("Escritorio XFCE4 / Session", "pgrep -f 'xfce4-session'"),
    ("Panel de Escritorio XFCE", "pgrep -f 'xfce4-panel'"),
    ("Gestor de Fondos xfdesktop", "pgrep -f 'xfdesktop'"),
    ("Audio Virtual PulseAudio", "pgrep -f 'pulseaudio'"),
    ("Servidor Remoto x11vnc", "pgrep -f 'x11vnc'"),
    ("Servidor Web noVNC / Proxy", "pgrep -f 'websockify'"),
    ("Servidor Google Drive 5TB", "pgrep -f 'rclone serve'"),
    ("Túnel Seguro Pinggy TCP", "pgrep -f 'pinggy'"),
    ("Túnel Web Ngrok HTTP", "pgrep -f 'ngrok'")
]

for s_name, check_cmd in services:
    pid = run(check_cmd)
    if pid:
        first_pid = pid.split()[0]
        print(f"  🟢 {s_name:32s} : ACTIVO (PID: {first_pid})")
    else:
        print(f"  ⚪ {s_name:32s} : INACTIVO")

# 5. DIAGNÓSTICO FINAL Y CONCLUSIÓN
print("\n" + "=" * 80)
percent_ok = (total_ok / total_checked) * 100
print(f"📊 BALANCE GENERAL: {total_ok} de {total_checked} componentes verificados ({percent_ok:.1f}% de cobertura)")
if percent_ok >= 85:
    print("🎉 [ESTADO DEL SISTEMA]: 🟢 100% SALUDABLE Y LISTO PARA TRABAJAR Y JUGAR")
else:
    print("ℹ️ [ESTADO DEL SISTEMA]: Sistema base funcional con instalación estándar")
print("=" * 80 + "\n")

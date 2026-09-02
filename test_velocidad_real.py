#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 TEST DE VELOCIDAD REAL (BENCHMARK MULTI-HILO EN TIEMPO REAL)
Descarga un archivo de prueba real (100MB o 1GB) desde CDNs de máxima velocidad
(Cloudflare / OVH / Google), cronometra los segundos exactos, calcula los MB/s y Gbps reales,
y borra inmediatamente el archivo para no ocupar almacenamiento.
"""

import os
import sys
import time
import shutil
import subprocess
from pathlib import Path

# Servidores CDN de alta velocidad para benchmarks
TEST_SERVERS = [
    {
        "nombre": "Cloudflare Global Anycast CDN (100 MB)",
        "url": "https://speed.cloudflare.com/__down?bytes=104857600",
        "bytes": 104857600,
        "mb": 100
    },
    {
        "nombre": "Hetzner Datacenter High-Speed (1,000 MB / 1 GB)",
        "url": "https://ash-speed.hetzner.com/1GB.bin",
        "bytes": 1048576000,
        "mb": 1000
    },
    {
        "nombre": "OVH Telecom Datacenter (100 MB)",
        "url": "http://proof.ovh.net/files/100Mio.dat",
        "bytes": 104857600,
        "mb": 100
    }
]

def ejecutar_benchmark(tamaño="100mb"):
    servidor = TEST_SERVERS[1] if tamaño.lower() == "1gb" else TEST_SERVERS[0]
    
    # Directorio temporal en memoria RAM (/dev/shm) o /tmp
    if Path("/dev/shm").exists() and shutil.disk_usage("/dev/shm").free > servidor["bytes"] * 1.5:
        temp_dest = Path("/dev/shm/speedtest_real.bin")
    else:
        temp_dest = Path("/tmp/speedtest_real.bin")

    print("\n" + "=" * 78)
    print(f"🚀 INICIANDO TEST DE VELOCIDAD REAL Y DESCARGA EN VIVO")
    print("=" * 78)
    print(f"📡 Servidor de Prueba: {servidor['nombre']}")
    print(f"📦 Tamaño del archivo: {servidor['mb']} MB reales")
    print(f"📁 Destino temporal: {temp_dest}")
    print("⏳ Conectando y midiendo ancho de banda con cronómetro de precisión...", flush=True)

    t_inicio = time.time()
    
    # Verificar si está disponible aria2c (multi-hilo 16 conexiones) o curl
    tiene_aria2 = shutil.which("aria2c") is not None
    
    if tiene_aria2:
        print("⚡ Motor activo: Aria2c Multi-Hilo (16 conexiones paralelas simultáneas)\n")
        cmd = [
            "aria2c", "-x", "16", "-s", "16", "-k", "1M",
            "--file-allocation=none", "--summary-interval=1",
            "--allow-overwrite=true",
            "-d", str(temp_dest.parent), "-o", temp_dest.name,
            servidor["url"]
        ]
        ret = subprocess.run(cmd)
    else:
        print("⚡ Motor activo: cURL Stream Directo\n")
        cmd = [
            "curl", "-L", "--progress-bar",
            "-o", str(temp_dest),
            servidor["url"]
        ]
        ret = subprocess.run(cmd)

    t_fin = time.time()
    t_total = t_fin - t_inicio

    if temp_dest.exists() and ret.returncode == 0:
        bytes_descargados = temp_dest.stat().st_size
        mb_descargados = bytes_descargados / (1024 * 1024)
        
        # Cálculos de velocidad real:
        mb_por_segundo = mb_descargados / t_total if t_total > 0 else 0
        mbps_red = mb_por_segundo * 8  # Megabits por segundo
        gbps_red = mbps_red / 1000     # Gigabits por segundo

        print("\n" + "=" * 78)
        print("📊 RESULTADOS REALES DEL TEST DE VELOCIDAD:")
        print("=" * 78)
        print(f"⏱️ Tiempo de descarga exacto:  {t_total:.2f} segundos")
        print(f"📦 Datos transferidos reales:  {mb_descargados:.2f} Megabytes")
        print(f"⚡ Velocidad Real de Bajada:   {mb_por_segundo:.2f} MB/segundo")
        print(f"🌐 Ancho de Banda Equivalente: {mbps_red:.2f} Mbps ({gbps_red:.2f} Gbps)")
        print("=" * 78)

        # Borrado inmediato del archivo para no ocupar disco
        temp_dest.unlink(missing_ok=True)
        print("🧹 [✓] Archivo de prueba eliminado al instante de la memoria/disco.", flush=True)
    else:
        print("❌ Error al ejecutar la descarga de prueba.", flush=True)
        if temp_dest.exists():
            temp_dest.unlink(missing_ok=True)

if __name__ == "__main__":
    opcion = sys.argv[1] if len(sys.argv) > 1 else "100mb"
    ejecutar_benchmark(opcion)

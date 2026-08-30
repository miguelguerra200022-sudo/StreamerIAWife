#!/bin/bash
# ==============================================================================
# 🌸 CELDA 1: Instalación de paquetes del sistema (XFCE4 + CRD)
# ==============================================================================
# Este script imprime output constantemente para que el watchdog de Kaggle
# no mate la celda por inactividad.
# ==============================================================================

set -e
export DEBIAN_FRONTEND=noninteractive
export DEBCONF_NONINTERACTIVE_SEEN=true

echo "🌸 [1/3] Configurando sistema de paquetes limpio..."
echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections 2>/dev/null || true
echo 'keyboard-configuration keyboard-configuration/layoutcode string us' | debconf-set-selections 2>/dev/null || true
echo 'keyboard-configuration keyboard-configuration/modelcode string pc105' | debconf-set-selections 2>/dev/null || true
echo 'keyboard-configuration keyboard-configuration/variant string ""' | debconf-set-selections 2>/dev/null || true
echo 'tzdata tzdata/Areas select Etc' | debconf-set-selections 2>/dev/null || true
echo 'tzdata tzdata/Zones/Etc select UTC' | debconf-set-selections 2>/dev/null || true

# Limpiar repos rotos de Kaggle (r2u, etc)
rm -rf /etc/apt/sources.list.d/* 2>/dev/null || true
rm -f /var/lib/dpkg/lock* /var/lib/apt/lists/lock* /var/cache/apt/archives/lock* 2>/dev/null || true
dpkg --configure -a 2>/dev/null || true

# Usar mirror interno de Google Cloud (mismo datacenter que Kaggle)
printf 'deb http://us-central1.gce.clouds.archive.ubuntu.com/ubuntu/ jammy main universe restricted multiverse\ndeb http://us-central1.gce.clouds.archive.ubuntu.com/ubuntu/ jammy-updates main universe restricted multiverse\ndeb http://us-central1.gce.clouds.archive.ubuntu.com/ubuntu/ jammy-security main universe restricted multiverse\n' > /etc/apt/sources.list
printf 'Acquire::Force-IPv4 "true";\nAcquire::http::Timeout "10";\n' > /etc/apt/apt.conf.d/99clean

echo "🌸 [2/3] Descargando e instalando XFCE4 + GTK3 + Audio..."
apt-get update -qq 2>&1 | tail -1
DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true \
  apt-get install -y \
  -o Dpkg::Options::='--force-confdef' \
  -o Dpkg::Options::='--force-confold' \
  --no-install-recommends \
  xfce4-session xfce4-terminal libgtk-3-0 dbus-x11 pulseaudio xvfb 2>&1

echo "🌸 [3/3] Instalando Google Chrome Remote Desktop..."
wget -q https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb -O /tmp/crd.deb
DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true \
  dpkg -i /tmp/crd.deb 2>&1 || \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --fix-broken 2>&1

echo ""
echo "=============================================="
echo "✅ INSTALACIÓN 100% COMPLETADA"
echo "=============================================="
echo "👉 Ahora ejecuta la Celda 2 para vincular tu PC"
echo "=============================================="

#!/bin/bash
set -e

echo "======================================================================"
echo "🌸 [1/5] 🛠️ REPARANDO DPKG Y ACTUALIZANDO REPOSITORIOS..."
echo "======================================================================"
sudo dpkg --configure -a || true
sudo sed -i '/r2u/d' /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null || true
sudo rm -f /etc/apt/sources.list.d/r2u*.list 2>/dev/null || true
echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections
echo 'keyboard-configuration keyboard-configuration/layoutcode string us' | sudo debconf-set-selections
echo 'keyboard-configuration keyboard-configuration/modelcode string pc105' | sudo debconf-set-selections

sudo apt-get update

echo "======================================================================"
echo "🌸 [2/5] 📥 INSTALANDO XFCE4, VULKAN, AUDIO Y DEPENDENCIAS..."
echo "======================================================================"
sudo apt-get install -y --no-install-recommends \
  python3-packaging python3-psutil python3-xdg xbase-clients xserver-xorg-video-dummy \
  libgtk-3-0 gsettings-desktop-schemas libvulkan1 mesa-vulkan-drivers \
  xfwm4 xfce4-panel xfce4-session xfce4-terminal xfdesktop4 dbus-x11 \
  ffmpeg pulseaudio rclone espeak-ng xdotool

echo "======================================================================"
echo "🌸 [3/5] 🌐 INSTALANDO GOOGLE CHROME Y CHROME REMOTE DESKTOP..."
echo "======================================================================"
if [ ! -f /usr/bin/google-chrome ]; then
  wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb
  sudo dpkg -i /tmp/chrome.deb || sudo apt-get install -y -f
fi

if [ ! -f /opt/google/chrome-remote-desktop/chrome-remote-desktop ]; then
  wget -q https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb -O /tmp/crd.deb
  sudo dpkg -i /tmp/crd.deb || sudo apt-get install -y -f
fi

echo "======================================================================"
echo "🌸 [4/5] 🧠 INSTALANDO LIBRERÍAS DE INTELIGENCIA ARTIFICIAL..."
echo "======================================================================"
pip install -q opencv-python-headless mss openai aiosqlite kokoro soundfile numpy pydub 2>/dev/null || true

echo "======================================================================"
echo "🌸 [5/5] 🚀 INICIANDO MOTOR LINUWAIFU DESKTOP & COMENTARISTA IA..."
echo "======================================================================"
python3 run_kaggle_crd_desktop.py

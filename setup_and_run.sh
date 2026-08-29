#!/bin/bash

# Prevenir fallos de servicios en contenedores Docker de Kaggle
printf '#!/bin/sh\nexit 101\n' | sudo tee /usr/sbin/policy-rc.d >/dev/null 2>&1
sudo chmod +x /usr/sbin/policy-rc.d

echo "======================================================================"
echo "🌸 [1/5] 🛠️ PREPARANDO SISTEMA Y ACTUALIZANDO REPOSITORIOS..."
echo "======================================================================"
sudo dpkg --configure -a 2>/dev/null || true
sudo sed -i '/r2u/d' /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null || true
sudo rm -f /etc/apt/sources.list.d/r2u*.list 2>/dev/null || true
echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections 2>/dev/null || true
echo 'keyboard-configuration keyboard-configuration/layoutcode string us' | sudo debconf-set-selections 2>/dev/null || true
echo 'keyboard-configuration keyboard-configuration/modelcode string pc105' | sudo debconf-set-selections 2>/dev/null || true

sudo DEBIAN_FRONTEND=noninteractive apt-get update

echo "======================================================================"
echo "🌸 [2/5] 📥 INSTALANDO XFCE4, VULKAN, AUDIO Y DEPENDENCIAS..."
echo "======================================================================"
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  python3-packaging python3-psutil python3-xdg xbase-clients xserver-xorg-video-dummy \
  libgtk-3-0 gsettings-desktop-schemas libvulkan1 mesa-vulkan-drivers \
  xfwm4 xfce4-panel xfce4-session xfce4-terminal xfdesktop4 dbus-x11 \
  ffmpeg pulseaudio rclone espeak-ng xdotool

echo "======================================================================"
echo "🌸 [3/5] 🌐 INSTALANDO GOOGLE CHROME Y CHROME REMOTE DESKTOP..."
echo "======================================================================"
if [ ! -f /usr/bin/google-chrome ]; then
  wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb
  sudo DEBIAN_FRONTEND=noninteractive dpkg -i /tmp/chrome.deb 2>/dev/null || sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -f
fi

if [ ! -f /opt/google/chrome-remote-desktop/chrome-remote-desktop ]; then
  wget -q https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb -O /tmp/crd.deb
  sudo DEBIAN_FRONTEND=noninteractive dpkg -i /tmp/crd.deb 2>/dev/null || sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -f
fi

sudo DEBIAN_FRONTEND=noninteractive apt-get install -f -y 2>/dev/null || true

# Configurar sesión XFCE para CRD
echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > ~/.chrome-remote-desktop-session
chmod +x ~/.chrome-remote-desktop-session

echo "======================================================================"
echo "🌸 [4/5] 🧠 INSTALANDO LIBRERÍAS DE INTELIGENCIA ARTIFICIAL..."
echo "======================================================================"
pip install --no-cache-dir opencv-python-headless mss openai aiosqlite kokoro soundfile numpy pydub

echo "======================================================================"
echo "🌸 [5/5] 🚀 INICIANDO MOTOR LINUWAIFU DESKTOP & COMENTARISTA IA..."
echo "======================================================================"
python3 run_kaggle_crd_desktop.py

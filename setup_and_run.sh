#!/bin/bash

# Guardar código de autenticación si se pasa como argumento
if [ -n "$1" ]; then
  echo "$1" > /tmp/crd_code.txt
fi

echo "======================================================================"
echo "🌸 [1/4] 📥 INSTALANDO ENTORNO GRÁFICO XFCE4 & AUDIO..."
echo "======================================================================"
sudo sed -i 's|http://archive.ubuntu.com/ubuntu/|http://mirrors.edge.kernel.org/ubuntu/|g' /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null || true
sudo sed -i 's|http://security.ubuntu.com/ubuntu/|http://mirrors.edge.kernel.org/ubuntu/|g' /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null || true
sudo sed -i '/r2u/d' /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null || true
sudo rm -f /etc/apt/sources.list.d/r2u*.list 2>/dev/null || true

printf 'Acquire::Force-IPv4 "true";\nAcquire::http::Timeout "10";\nAcquire::https::Timeout "10";\nAcquire::Retries "5";\nAcquire::http::Pipeline-Depth "0";\n' | sudo tee /etc/apt/apt.conf.d/99anti-freeze >/dev/null

sudo apt-get update -qq

sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-upgrade --no-install-recommends \
  xfwm4 xfce4-session xfce4-terminal xfdesktop4 dbus-x11 \
  pulseaudio rclone espeak-ng xdotool xserver-xorg-video-dummy

echo "======================================================================"
echo "🌸 [2/4] 🌐 INSTALANDO GOOGLE CHROME & CHROME REMOTE DESKTOP..."
echo "======================================================================"
if [ ! -f /usr/bin/google-chrome ]; then
  wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb
  sudo dpkg -i /tmp/chrome.deb 2>/dev/null || sudo apt-get install -y -f -qq
fi

if [ ! -f /opt/google/chrome-remote-desktop/chrome-remote-desktop ]; then
  wget -q https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb -O /tmp/crd.deb
  sudo dpkg -i /tmp/crd.deb 2>/dev/null || sudo apt-get install -y -f -qq
fi

echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > ~/.chrome-remote-desktop-session
chmod +x ~/.chrome-remote-desktop-session

echo "======================================================================"
echo "🌸 [3/4] 🧠 INSTALANDO LIBRERÍAS DE INTELIGENCIA ARTIFICIAL (SIN CONFLICTOS)..."
echo "======================================================================"
pip install --prefer-binary opencv-python-headless mss openai aiosqlite soundfile numpy pydub loguru misaki espeakng_loader
pip install --no-deps kokoro

echo "======================================================================"
echo "🌸 [4/4] 🚀 INICIANDO MOTOR LINUWAIFU CLOUD DESKTOP..."
echo "======================================================================"
python3 run_kaggle_crd_desktop.py

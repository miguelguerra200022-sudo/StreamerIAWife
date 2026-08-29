#!/bin/bash

# Guardar código de autenticación si se pasa como argumento
if [ -n "$1" ]; then
  echo "$1" > /tmp/crd_code.txt
fi

echo "======================================================================"
echo "🌸 [1/4] 📥 INSTALANDO ENTORNO GRÁFICO XFCE4 & AUDIO..."
echo "======================================================================"
sudo apt-get update -qq

sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  xfwm4 xfce4-session xfce4-terminal xfdesktop4 dbus-x11 \
  pulseaudio rclone espeak-ng xdotool xserver-xorg-video-dummy xvfb python3-psutil python3-xdg

echo "======================================================================"
echo "🌸 [2/4] 🌐 INSTALANDO GOOGLE CHROME & CHROME REMOTE DESKTOP..."
echo "======================================================================"
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb
wget -q https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb -O /tmp/crd.deb

sudo DEBIAN_FRONTEND=noninteractive apt-get install -y /tmp/chrome.deb /tmp/crd.deb 2>/dev/null || (sudo dpkg -i /tmp/chrome.deb /tmp/crd.deb 2>/dev/null; sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --fix-broken)

echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > ~/.chrome-remote-desktop-session
chmod +x ~/.chrome-remote-desktop-session

echo "======================================================================"
echo "🌸 [3/4] 🧠 INSTALANDO LIBRERÍAS DE INTELIGENCIA ARTIFICIAL..."
echo "======================================================================"
pip install --prefer-binary opencv-python-headless mss openai aiosqlite soundfile numpy pydub loguru misaki espeakng_loader kokoro-onnx kokoro

echo "======================================================================"
echo "🌸 [4/4] 🚀 INICIANDO MOTOR LINUWAIFU CLOUD DESKTOP..."
echo "======================================================================"
python3 run_kaggle_crd_desktop.py "$@"

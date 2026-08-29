#!/bin/bash
# ==============================================================================
# 🌸 LINUWAIFU CLOUD GAMING & AI VTUBER STUDIO PRO - KAGGLE LAUNCHER
# ==============================================================================

# Si se pasó el código como argumento, guardarlo en /tmp/crd_code.txt
if [ -n "$1" ]; then
  echo "$1" > /tmp/crd_code.txt
fi

echo "======================================================================"
echo "🌸 [1/4] 📥 INSTALANDO XFCE4, AUDIO Y SERVIDOR DE PANTALLA..."
echo "======================================================================"
apt-get update -y
apt-get install -y --no-install-recommends \
  xfwm4 xfce4-panel xfce4-session xfce4-terminal xfdesktop4 dbus-x11 \
  pulseaudio rclone espeak-ng xdotool xserver-xorg-video-dummy

echo "======================================================================"
echo "🌸 [2/4] 🌐 INSTALANDO GOOGLE CHROME & CHROME REMOTE DESKTOP..."
echo "======================================================================"
if [ ! -f /usr/bin/google-chrome ]; then
  wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb
  dpkg -i /tmp/chrome.deb 2>/dev/null || apt-get install -y -f
fi

if [ ! -f /opt/google/chrome-remote-desktop/chrome-remote-desktop ]; then
  wget -q https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb -O /tmp/crd.deb
  dpkg -i /tmp/crd.deb 2>/dev/null || apt-get install -y -f
fi

# Configurar sesión XFCE para Chrome Remote Desktop
echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > ~/.chrome-remote-desktop-session
chmod +x ~/.chrome-remote-desktop-session

echo "======================================================================"
echo "🌸 [3/4] 🧠 INSTALANDO LIBRERÍAS DE INTELIGENCIA ARTIFICIAL..."
echo "======================================================================"
pip install --no-cache-dir opencv-python-headless mss openai aiosqlite kokoro soundfile numpy pydub 2>/dev/null || true

echo "======================================================================"
echo "🌸 [4/4] 🚀 INICIANDO MOTOR DUAL-GPU, AUDIO Y ESCRITORIO REMOTO..."
echo "======================================================================"
python3 run_kaggle_crd_desktop.py

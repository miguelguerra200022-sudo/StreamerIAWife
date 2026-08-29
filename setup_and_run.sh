#!/bin/bash
# Prevenir bloqueos de servicios en contenedores Docker de Kaggle
printf '#!/bin/sh\nexit 101\n' | sudo tee /usr/sbin/policy-rc.d >/dev/null 2>&1
sudo chmod +x /usr/sbin/policy-rc.d

python3 run_kaggle_crd_desktop.py

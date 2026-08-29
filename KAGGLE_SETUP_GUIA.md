# 🎬 GUÍA MAESTRA: LINUWAIFU CLOUD GAMING & AI VTUBER (KAGGLE DUAL-GPU T4 + CRD)
### ⚡ Motor Maestro 1-Click: Escritorio Remoto 1080p 60 FPS + Comentarista IA Gamer (Neuro-sama Mode) + Auto-Persistencia GitHub

---

## 📌 PASO 1: Opciones del Notebook en Kaggle (Barra Lateral Derecha)
En la barra lateral derecha de tu Notebook en Kaggle:
* **Accelerator**: Selecciona `GPU T4 x2`
* **Internet**: Actívalo en `Internet on` *(Obligatorio)*

---

## 🚀 CELDA MAESTRA (1-CLICK CLOUD GAMING & AI VTUBER DESKTOP):

> [!TIP]
> **¡Solo necesitas esta única celda en todo tu Notebook de Kaggle!**
> Al darle Play, descarga tus cambios de GitHub, inicia tu escritorio Ubuntu XFCE4 a 1080p 60 FPS, monta tu Google Drive (5TB), levanta a LinuWaifu en la GPU 1 con visión en tiempo real y conecta tu celular a través de Google Chrome Remote Desktop.

```python
# ==============================================================================
# 🎮 LINUWAIFU CLOUD GAMING & AI VTUBER DESKTOP (CHROME REMOTE DESKTOP 60 FPS)
# ==============================================================================
!git clone https://github.com/miguelguerra200022-sudo/StreamerIAWife.git /kaggle/working/StreamerIAWife 2>/dev/null || (cd /kaggle/working/StreamerIAWife && git reset --hard origin/main && git pull origin main)
%cd /kaggle/working/StreamerIAWife
!python3 run_kaggle_crd_desktop.py
```

---

## 🔑 VINCULACIÓN INICIAL CON GOOGLE REMOTE DESKTOP (SOLO 1 VEZ EN LA VIDA):

1. Abre en tu navegador: [**remotedesktop.google.com/headless**](https://remotedesktop.google.com/headless)
2. Toca en **"Comenzar"** $\rightarrow$ **"Siguiente"** $\rightarrow$ **"Autorizar"**.
3. Copia el comando que dice **Debian Linux** y pégalo en la consola de Kaggle cuando te lo solicite.
4. **¡Listo para siempre!** El script guardará tus tokens en GitHub (`crd_session.tar.gz`). En cualquier sesión futura o cuenta nueva de Kaggle, se conectará solo en 5 segundos sin pedirte códigos jamás.

---

## 📱 CÓMO ENTRAR DESDE TU CELULAR:
1. Abre la app oficial **"Escritorio Remoto de Chrome"** en tu celular (o entra en [remotedesktop.google.com/access](https://remotedesktop.google.com/access)).
2. Toca tu equipo **`LinuWaifu-Cloud-PC`**.
3. Ingresa tu PIN: **`123456`**.

---

## 💾 CELDA DE RESPALDO (CUANDO TERMINES TU STREAM):

```python
# ==============================================================================
# 💾 GUARDAR MEMORIA Y SESIÓN CRD A GITHUB (1-CLICK BACKUP)
# ==============================================================================
!cd /kaggle/working/StreamerIAWife && git add streamer_memory.db crd_session.tar.gz 2>/dev/null && git commit -m "Auto-backup memoria stream & CRD" 2>/dev/null && git push origin main 2>/dev/null || echo "Memoria al día."
```

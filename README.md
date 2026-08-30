# 🌸 LinuWaifu Cloud Gaming & AI VTuber Studio Pro

> **Ubuntu Nativo Pro Edition en Kaggle** con 2x GPUs NVIDIA Tesla T4 (32GB VRAM), Google Drive (5TB vía Rclone), Modo Touchpad y Zoom con 2 dedos en RealVNC Viewer.

---

## 🚀 Comando Rápido para Kaggle (1 Sola Celda)

Copia y pega este comando en tu Notebook de Kaggle y dale **Play (▶️)**:

```python
!rm -rf /kaggle/working/StreamerIAWife && git clone https://github.com/miguelguerra200022-sudo/StreamerIAWife.git /kaggle/working/StreamerIAWife && cd /kaggle/working/StreamerIAWife && python3 run_kaggle_vnc_studio.py "34P4Gndh4EFxHQUFbbtO6lxsWBH_3HK2oZoxLj1D3qkSJn17b"
```

---

## 📱 Cómo Conectarte desde tu Celular

1. Descarga la app gratuita **RealVNC Viewer** en tu teléfono (Google Play Store).
2. Al ejecutar el comando en Kaggle, copia la dirección generada:
   ```text
   🌟 OPCIÓN 1: APP MÓVIL RECOMENDADA:
      👉 Servidor VNC: xxxxxx.free.pinggy.link:12345
   ```
3. En la app **RealVNC Viewer**:
   - Toca el botón **`+`**.
   - En **Address**, pega la dirección (ej: `xxxxxx.free.pinggy.link:12345`).
   - En **Name**, escribe: `Ubuntu Kaggle PC`.
   - Toca **Connect**.
4. ¡Listo! Tendrás:
   - 🖱️ **Modo Touchpad**: Deslizas el dedo como el ratón de una laptop.
   - 🔍 **Pinch-to-Zoom**: Agrandas y achicas la pantalla con 2 dedos en **Full HD 1080p**.
   - 🎨 **Tema Oficial Ubuntu Yaru-Dark**, explorador Thunar, editor Mousepad y monitor de GPUs `nvtop`.

---

## 💾 Usar tus 5TB de Google Drive

En la terminal de tu Ubuntu o en Kaggle escribe:
```bash
rclone config
```
Sigue los pasos interactivos para vincular tu cuenta de Google Drive y acceder a tus archivos a más de 500 MB/s.

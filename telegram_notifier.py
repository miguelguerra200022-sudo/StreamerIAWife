#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 MÓDULO MAESTRO DE NOTIFICACIONES Y CONTROL POR TELEGRAM
Bot Oficial: @MiguelGameStudio_Bot
Token: 8557490216:AAGAI2hTogiVswcdcoPlJ91DODaD_6BqZ2U
"""
import os
import sys
import json
import time
import requests
from pathlib import Path

BOT_TOKEN = "8557490216:AAGAI2hTogiVswcdcoPlJ91DODaD_6BqZ2U"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
DEFAULT_CHAT_ID = "1514766577"
CHAT_ID_FILE = Path(__file__).resolve().parent / "telegram_chat_id.txt"

def obtener_chat_id():
    """Recupera el chat_id guardado o usa el default oficial."""
    if CHAT_ID_FILE.exists():
        c_id = CHAT_ID_FILE.read_text().strip()
        if c_id:
            return c_id
    if DEFAULT_CHAT_ID:
        return DEFAULT_CHAT_ID
            
    # Intentar obtener de getUpdates
    try:
        r = requests.get(f"{BASE_URL}/getUpdates", timeout=10)
        data = r.json()
        if data.get("ok") and data.get("result"):
            for update in reversed(data["result"]):
                if "message" in update and "chat" in update["message"]:
                    chat_id = str(update["message"]["chat"]["id"])
                    CHAT_ID_FILE.write_text(chat_id)
                    return chat_id
    except Exception as e:
        print(f"Aviso getUpdates: {e}", flush=True)
    return None

def enviar_mensaje(texto, parse_mode="HTML"):
    """Envía un mensaje a través del bot al usuario."""
    chat_id = obtener_chat_id()
    if not chat_id:
        print("⚠️ No se ha detectado el chat_id. Envía un mensaje o /start a @MiguelGameStudio_Bot en Telegram.", flush=True)
        return False

    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        res = r.json()
        if res.get("ok"):
            print("✓ Mensaje de Telegram enviado con éxito.", flush=True)
            return True
        else:
            print(f"❌ Error Telegram: {res.get('description')}", flush=True)
    except Exception as e:
        print(f"❌ Error al enviar mensaje: {e}", flush=True)
    return False

def notificar_arranque_cloud_pc(wifi_url, mobile_url, vnc_password="09032000Mi."):
    """Envía una alerta elegante con los enlaces de acceso de la Cloud PC."""
    msg = (
        "🚀 <b>¡TU UBUNTU CLOUD PC ESTÁ ONLINE!</b> 🌸\n\n"
        "🖥️ <b>Modo WiFi / Fibra (1080p Máxima Calidad):</b>\n"
        f"👉 <a href='{wifi_url}'>Abrir Ubuntu en Navegador</a>\n\n"
        "📱 <b>Modo Móvil 4G (Ping Ultrabajo):</b>\n"
        f"👉 <a href='{mobile_url}'>Abrir Modo Rápido</a>\n\n"
        f"🔑 <b>Contraseña VNC:</b> <code>{vnc_password}</code>\n\n"
        "🎮 <i>Sunshine y Google Drive 5TB sincronizados.</i>"
    )
    return enviar_mensaje(msg)

def notificar_alerta_cuota(minutos_restantes):
    """Envía un aviso de expiración de sesión de 12 horas."""
    msg = (
        f"⚠️ <b>ALERTA DE SESIÓN: Faltan {minutos_restantes} minutos</b>\n\n"
        "Tu máquina de Kaggle se reiniciará automáticamente al cumplir las 12 horas.\n"
        "💾 Presiona 'Guardar Estado' o tu progreso se guardará automáticamente a tus 5TB de Google Drive."
    )
    return enviar_mensaje(msg)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        texto = " ".join(sys.argv[1:])
        enviar_mensaje(texto)
    else:
        c_id = obtener_chat_id()
        if c_id:
            print(f"✓ Bot listo y vinculado con chat_id: {c_id}")
            enviar_mensaje("🤖 <b>¡Bot de MiguelGameStudio activado y vinculado a tu Cloud PC con éxito!</b>")
        else:
            print("⚠️ Envía un mensaje o dale a /start en Telegram a: https://t.me/MiguelGameStudio_Bot")

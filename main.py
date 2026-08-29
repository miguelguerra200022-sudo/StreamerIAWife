import asyncio
import sys
import re
import os
import uvicorn
from database import init_db, get_user_context, update_user_interaction, record_donation_event
from brain_orchestrator import BrainOrchestrator
from cloud_bridge import app as fastapi_app, cloud_manager
from twitch_bot import TwitchChatBot
from config import HOST, PORT

class StreamerServiceCoordinator:
    def __init__(self):
        self.brain = BrainOrchestrator()
        self.is_processing = False
        self.message_queue = asyncio.Queue()

    async def handle_incoming_message(self, username: str, message: str, is_donation: bool = False):
        """Manejador central de cualquier mensaje (Chat, Donación, Móvil o Terminal)."""
        print(f"\n[💬 Chat] {username}: {message} {'(VIP 🎁)' if is_donation else ''}")
        
        # 1. Recuperar contexto de la memoria SQLite
        user_context = await get_user_context(username)
        
        print(f"[🧠 LinuWaifu pensando con NVIDIA NIM...]")
        full_reply = ""
        final_mood = "ALEGRE"
        
        # 2. Generar con Streaming y emitir a la nube con gestos 3D en tiempo real
        async for item in self.brain.generate_response(username, message, user_context, is_donation=is_donation):
            chunk = item.get("chunk", "")
            mood = item.get("mood", "ALEGRE")
            gesture = item.get("gesture", "explain")
            
            full_reply += chunk
            final_mood = mood
            
            # Emitir a Kaggle para síntesis de audio y animación 3D
            await cloud_manager.broadcast_speech_event(
                chunk=chunk,
                mood=mood,
                gesture=gesture,
                is_donation=is_donation
            )
        
        # 3. Guardar interacción en SQLite
        await update_user_interaction(
            username=username,
            role="user",
            user_message=message,
            assistant_reply=full_reply,
            mood=final_mood,
            affection_delta=5 if is_donation else 1
        )
        
        if is_donation:
            await record_donation_event(username, 5.0, message)
            
        print(f"[✓ Respuesta completada]: {full_reply}")

    async def handle_vision_reaction(self, image_b64: str):
        """Maneja la reacción visual autónoma a lo que se ve en la pantalla de Google Chrome."""
        print("[👀 Cerebro]: Analizando fotograma de pantalla con Llama 3.2 Vision...")
        reaction_text = await self.brain.react_to_screen(image_b64, "El streamer está navegando en Google Chrome.")
        if reaction_text:
            print(f"[👀 Reacción Visual]: {reaction_text}")
            await cloud_manager.broadcast_speech_event(
                chunk=reaction_text,
                mood="ALEGRE",
                gesture="wave",
                is_donation=False
            )

async def run_terminal_interactive_mode(coordinator: StreamerServiceCoordinator):
    """Permite enviar mensajes desde la consola de la Canaima para pruebas interactivas."""
    if not sys.stdin.isatty():
        while True:
            await asyncio.sleep(3600)
            
    print("\n" + "=" * 60)
    print("💬 MODO CONSOLA ACTIVO (Escribe cualquier mensaje y presiona Enter)")
    print("   Tip: Escribe 'VIP: mensaje' para simular donación o 'salir' para terminar")
    print("=" * 60 + "\n")
    
    loop = asyncio.get_event_loop()
    while True:
        try:
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            if line.lower() == "salir":
                break
            
            is_vip = False
            if line.lower().startswith("vip:"):
                is_vip = True
                line = line[4:].strip()
            
            if ":" in line:
                user, msg = line.split(":", 1)
                user = user.strip()
                msg = msg.strip()
            else:
                user = "Miguel"
                msg = line
            
            await coordinator.handle_incoming_message(user, msg, is_donation=is_vip)
        except Exception as e:
            print(f"Error en entrada de consola: {e}")

async def start_cloudflare_tunnel():
    """Inicia Cloudflare Tunnel optimizado con QUIC e IPv4 Anycast para mínima latencia."""
    try:
        cmd = [
            "cloudflared", "tunnel",
            "--url", f"http://localhost:{PORT}",
            "--protocol", "quic",
            "--edge-ip-version", "4"
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        
        async def read_tunnel_output():
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                line_str = line.decode("utf-8", errors="ignore")
                match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line_str)
                if match:
                    http_url = match.group(0)
                    ws_url = http_url.replace("https://", "wss://") + "/ws/cloud"
                    try:
                        with open("active_tunnel.txt", "w") as f:
                            f.write(ws_url)
                    except Exception:
                        pass
                    print("\n" + "★" * 65)
                    print(f"🌐 TÚNEL QUIC ULTRA-RÁPIDO ACTIVO PARA KAGGLE Y CELULAR:")
                    print(f"👉 Enlace del Estudio Móvil:")
                    print(f"   {http_url}/static/studio.html")
                    print(f"👉 URL de WebSocket para Kaggle:")
                    print(f"   CANAIMA_WS_URL = \"{ws_url}\"")
                    print("★" * 65 + "\n")
        
        asyncio.create_task(read_tunnel_output())
        return proc
    except Exception as e:
        print(f"[ℹ️] Cloudflare tunnel no disponible ({e}), usando modo LAN directa.")
        return None

async def main():
    print("=" * 65)
    print("🚀 INICIANDO CEREBRO 24/7 DE LINUWAIFU - CANAIMA antiX (LATENCIA ULTRA-BAJA)")
    print("=" * 65)
    
    # 1. Inicializar Base de Datos
    await init_db()
    
    # 2. Coordinador
    coordinator = StreamerServiceCoordinator()
    
    # Conectar el Estudio Móvil al Coordinador para responder al instante
    cloud_manager.set_message_callback(coordinator.handle_incoming_message)
    cloud_manager.set_vision_callback(coordinator.handle_vision_reaction)
    
    # 3. Levantar Servidor FastAPI para puente con la nube (Uvicorn con websockets nativo)
    config = uvicorn.Config(
        fastapi_app,
        host=HOST,
        port=PORT,
        log_level="warning",
        ws="websockets",
        ws_ping_interval=None,
        ws_ping_timeout=None
    )
    server = uvicorn.Server(config)
    
    # 4. Twitch / Kick Bot
    twitch_bot = TwitchChatBot(message_handler_callback=coordinator.handle_incoming_message)
    
    # 5. Iniciar Servidor, Túnel y Consola
    await start_cloudflare_tunnel()
    
    tasks = [
        asyncio.create_task(server.serve()),
        asyncio.create_task(run_terminal_interactive_mode(coordinator))
    ]
    
    if twitch_bot.active:
        tasks.append(asyncio.create_task(twitch_bot.start()))
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

import os
import json
import asyncio
from pathlib import Path
from typing import List, Set, Optional, Callable
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Streamer IA Waifu - Canaima Brain Bridge")

BASE_DIR = Path(__file__).resolve().parent
AVATARS_DIR = BASE_DIR / "avatars"
os.makedirs(AVATARS_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(AVATARS_DIR)), name="static")

class CloudConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.message_callback: Optional[Callable] = None
        self.vision_callback: Optional[Callable] = None
        self.ai_enabled: bool = True
        self.latest_screen_frame_bytes: bytes = b""
        self.latest_screen_frame_b64: str = ""
        self.latest_telemetry: dict = {
            "ping_ms": 0,
            "fps": 0,
            "voice_rtt_ms": 0,
            "status": "online"
        }

    def set_message_callback(self, cb: Callable):
        self.message_callback = cb

    def set_vision_callback(self, cb: Callable):
        self.vision_callback = cb

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"[☁️ Bridge] Cliente conectado. Total activos: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        print(f"[☁️ Bridge] Cliente desconectado. Total activos: {len(self.active_connections)}")

    async def broadcast_speech_event(self, chunk: str, mood: str, gesture: str = "explain", is_donation: bool = False):
        """Envía el paquete de voz y gesto 3D en menos de 20ms a Kaggle."""
        payload = {
            "type": "speech_chunk",
            "text": chunk,
            "mood": mood,
            "gesture": gesture,
            "is_donation": is_donation
        }
        await self.broadcast_raw(payload)

    async def broadcast_raw(self, payload: dict, sender: Optional[WebSocket] = None):
        """Reenvía cualquier paquete JSON a todos los clientes conectados excepto el remitente."""
        if not self.active_connections:
            return
        
        to_remove = set()
        for conn in list(self.active_connections):
            if conn == sender:
                continue
            try:
                await conn.send_json(payload)
            except Exception:
                to_remove.add(conn)
        
        for dead_conn in to_remove:
            self.disconnect(dead_conn)

    async def broadcast_bytes(self, raw_bytes: bytes, sender: Optional[WebSocket] = None):
        """Reenvía fotogramas binarios sin tocar memoria a < 0.5ms de latencia."""
        if not self.active_connections:
            return
        
        to_remove = set()
        for conn in list(self.active_connections):
            if conn == sender:
                continue
            try:
                await conn.send_bytes(raw_bytes)
            except Exception:
                to_remove.add(conn)
        
        for dead_conn in to_remove:
            self.disconnect(dead_conn)

cloud_manager = CloudConnectionManager()

@app.websocket("/ws/cloud")
async def websocket_cloud_endpoint(websocket: WebSocket):
    await cloud_manager.connect(websocket)
    try:
        while True:
            # Recibir tanto texto como bytes crudos de forma polimórfica ultra-rápida
            message = await websocket.receive()
            
            # 1. FLUJO BINARIO (FOTOGRAMAS JPEG - 0% SOBRECARGA BASE64/JSON)
            if "bytes" in message and message["bytes"]:
                raw_bytes = message["bytes"]
                if len(raw_bytes) > 0 and raw_bytes[0] == 0x01:
                    cloud_manager.latest_screen_frame_bytes = raw_bytes[1:]
                    # Reenviar bytes directamente a todos los demás clientes (celular)
                    await cloud_manager.broadcast_bytes(raw_bytes, sender=websocket)
                continue
            
            # 2. FLUJO DE TEXTO / JSON (COMANDOS, TELEMETRÍA, AUDIO)
            if "text" in message and message["text"]:
                raw_text = message["text"]
                try:
                    data = json.loads(raw_text)
                    
                    # A. Reporte de Telemetría (Ping, FPS, Voice RTT)
                    if data.get("type") == "telemetry_report":
                        cloud_manager.latest_telemetry = {
                            "ping_ms": data.get("ping_ms", 0),
                            "fps": data.get("fps", 0),
                            "voice_rtt_ms": data.get("voice_rtt_ms", 0),
                            "status": "online"
                        }
                        try:
                            with open(BASE_DIR / "telemetry_live.json", "w") as f:
                                json.dump(cloud_manager.latest_telemetry, f)
                        except Exception:
                            pass
                        continue
                    
                    # B. Soporte de compatibilidad para frames base64 legados
                    if data.get("type") == "screen_frame":
                        cloud_manager.latest_screen_frame_b64 = data.get("data", "")
                        await cloud_manager.broadcast_raw(data, sender=websocket)
                        continue
                    
                    # C. Control de flujo ACK (reenviar a Kaggle)
                    if data.get("type") == "frame_ack" or data.get("type") == "ping" or data.get("type") == "pong":
                        await cloud_manager.broadcast_raw(data, sender=websocket)
                        continue
                    
                    # D. Comandos de control del estudio
                    if data.get("type") == "studio_command":
                        action = data.get("action")
                        
                        # Reenviar comando físico a Kaggle (mouse, teclas, navegación, sonido)
                        await cloud_manager.broadcast_raw(data, sender=websocket)
                        
                        if action == "ai_toggle":
                            cloud_manager.ai_enabled = bool(data.get("value", True))
                            print(f"[🤖 Modo IA]: {'ACTIVADO (24/7)' if cloud_manager.ai_enabled else 'DESACTIVADO (Manual)'}")
                        
                        elif action == "ask_ai" or action == "chat_message":
                            user_text = data.get("text", "").strip()
                            if user_text and cloud_manager.message_callback and cloud_manager.ai_enabled:
                                asyncio.create_task(cloud_manager.message_callback("Miguel", user_text))
                        
                        elif action == "vision_react":
                            print("[👀 Visión]: Solicitud de reacción visual a la pantalla...")
                            # Usar bytes o base64 según disponibilidad
                            if cloud_manager.vision_callback:
                                if cloud_manager.latest_screen_frame_bytes:
                                    import base64
                                    b64_data = base64.b64encode(cloud_manager.latest_screen_frame_bytes).decode('utf-8')
                                    asyncio.create_task(cloud_manager.vision_callback(b64_data))
                                elif cloud_manager.latest_screen_frame_b64:
                                    asyncio.create_task(cloud_manager.vision_callback(cloud_manager.latest_screen_frame_b64))
                                else:
                                    print("[⚠️ Visión]: No hay fotograma de pantalla disponible aún.")
                    
                    else:
                        # Reenviar cualquier otro mensaje a los demás clientes
                        await cloud_manager.broadcast_raw(data, sender=websocket)
                
                except Exception as e:
                    print(f"[!] Error procesando JSON WebSocket: {e}")

    except WebSocketDisconnect:
        cloud_manager.disconnect(websocket)
    except Exception as e:
        cloud_manager.disconnect(websocket)

@app.get("/api/telemetry")
def get_live_telemetry():
    """Devuelve la telemetría en tiempo real para diagnóstico de Antigravity."""
    return {
        **cloud_manager.latest_telemetry,
        "cloud_clients": len(cloud_manager.active_connections)
    }

@app.get("/health")
def health_check():
    return {
        "status": "online",
        "device": "Canaima antiX Linux",
        "cloud_clients": len(cloud_manager.active_connections)
    }

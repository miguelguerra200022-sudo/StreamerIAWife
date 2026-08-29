import asyncio
from config import TWITCH_CHANNEL, TWITCH_OAUTH_TOKEN

try:
    from twitchio.ext import commands
    BaseBot = commands.Bot
    TWITCHIO_AVAILABLE = True
except ImportError:
    BaseBot = object
    TWITCHIO_AVAILABLE = False

class TwitchChatBot(BaseBot):
    def __init__(self, message_handler_callback):
        self.message_handler_callback = message_handler_callback
        if TWITCHIO_AVAILABLE and TWITCH_CHANNEL and TWITCH_OAUTH_TOKEN:
            super().__init__(
                token=TWITCH_OAUTH_TOKEN,
                prefix="!",
                initial_channels=[TWITCH_CHANNEL]
            )
            self.active = True
        else:
            self.active = False
            print("[ℹ️] Twitch Bot: No se detectaron credenciales OAuth en .env. Modo pasivo/manual activo.")

    async def event_ready(self):
        print(f"[🎮 Twitch Bot] Conectado exitosamente como {self.nick} en #{TWITCH_CHANNEL}")

    async def event_message(self, message):
        # Ignorar mensajes del propio bot
        if hasattr(message, "echo") and message.echo:
            return
        
        username = message.author.name if hasattr(message, "author") and message.author else "Anónimo"
        content = message.content if hasattr(message, "content") else str(message)
        
        # Enviar al manejador central
        if self.message_handler_callback:
            await self.message_handler_callback(username, content, is_donation=False)

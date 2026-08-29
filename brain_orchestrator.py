import itertools
import asyncio
from openai import AsyncOpenAI
from config import NVIDIA_API_KEYS, NVIDIA_BASE_URL, DEFAULT_MODEL
from personality import PersonalityManager

class BrainOrchestrator:
    def __init__(self):
        if not NVIDIA_API_KEYS:
            raise ValueError("No se encontraron claves de API de NVIDIA en la configuración.")
        
        self.keys = NVIDIA_API_KEYS
        self.key_cycle = itertools.cycle(self.keys)
        self.personality = PersonalityManager()
        print(f"[🧠] Orquestador inicializado con {len(self.keys)} claves de NVIDIA Build.")

    def _get_next_client(self):
        key = next(self.key_cycle)
        return AsyncOpenAI(
            base_url=NVIDIA_BASE_URL,
            api_key=key
        ), key

    async def generate_response(self, username: str, message: str, user_context: str, is_donation: bool = False):
        mood = self.personality.analyze_and_update_mood(message, is_donation=is_donation)
        system_prompt = self.personality.build_system_prompt(user_context, mood)
        
        user_prompt = f"{username} te dice: {message}"
        if is_donation:
            user_prompt = f"¡ALERTA VIP! {username} acaba de donar y dice: {message}"

        max_attempts = len(self.keys)
        for attempt in range(max_attempts):
            client, key_used = self._get_next_client()
            key_preview = f"{key_used[:12]}...{key_used[-4:]}"
            
            try:
                stream = await client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=60,
                    temperature=0.75,
                    stream=True
                )

                full_text = ""
                sentence_buffer = ""
                
                try:
                    async for chunk in stream:
                        delta = chunk.choices[0].delta.content if chunk.choices and chunk.choices[0].delta else ""
                        if not delta:
                            continue
                        
                        full_text += delta
                        sentence_buffer += delta
                        
                        # División ultrarrápida por comas o frases de 3+ palabras para latencia <400ms
                        palabras = sentence_buffer.strip().split()
                        if any(punct in delta for punct in [".", "!", "?", ",", "\n"]) and len(palabras) >= 3:
                            chunk_text = sentence_buffer.strip()
                            gesture = self.personality.detect_gesture(chunk_text, mood, is_donation=is_donation)
                            yield {
                                "type": "chunk",
                                "chunk": chunk_text,
                                "mood": mood,
                                "gesture": gesture,
                                "is_donation": is_donation
                            }
                            sentence_buffer = ""
                        elif len(palabras) >= 6 and " " in delta:
                            chunk_text = sentence_buffer.strip()
                            gesture = self.personality.detect_gesture(chunk_text, mood, is_donation=is_donation)
                            yield {
                                "type": "chunk",
                                "chunk": chunk_text,
                                "mood": mood,
                                "gesture": gesture,
                                "is_donation": is_donation
                            }
                            sentence_buffer = ""
                finally:
                    if hasattr(stream, "response") and hasattr(stream.response, "aclose"):
                        await stream.response.aclose()

                if sentence_buffer.strip():
                    chunk_text = sentence_buffer.strip()
                    gesture = self.personality.detect_gesture(chunk_text, mood, is_donation=is_donation)
                    yield {
                        "type": "chunk",
                        "chunk": chunk_text,
                        "mood": mood,
                        "gesture": gesture,
                        "is_donation": is_donation
                    }

                gesture_final = self.personality.detect_gesture(full_text.strip(), mood, is_donation=is_donation)
                yield {
                    "type": "final",
                    "full_text": full_text.strip(),
                    "mood": mood,
                    "gesture": gesture_final,
                    "is_donation": is_donation
                }
                return

            except Exception as e:
                print(f"[!] Error con clave NVIDIA {key_preview}: {e}. Probando siguiente clave...")
                await asyncio.sleep(0.05)
        
        # Fallback de emergencia
        fb_text = "¡E-espera un momento! Me distraje un segundo con el chat, ¡pero ya estoy de vuelta!"
        yield {
            "type": "final",
            "full_text": fb_text,
            "mood": "nervous",
            "gesture": "think",
            "is_donation": is_donation
        }

    async def react_to_screen(self, image_b64: str, context: str = ""):
        """Usa Llama 3.2 Vision para observar la pantalla de Chrome y comentar en vivo."""
        mood = self.personality.current_mood
        system_prompt = (
            f"{self.personality.build_system_prompt('', mood)}\n"
            "INSTRUCCIÓN ESPECIAL DE VISIÓN: Estás viendo la pantalla compartida en el directo. "
            "Haz un comentario muy corto (1 sola frase, máximo 15 palabras), espontáneo, gracioso o tsundere "
            "reaccionando a lo que ves en la imagen (video de YouTube, meme, página web, búsqueda, etc.)."
        )
        
        max_attempts = len(self.keys)
        for attempt in range(max_attempts):
            client, key_used = self._get_next_client()
            key_preview = f"{key_used[:12]}...{key_used[-4:]}"
            
            try:
                response = await client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "¡Mira la pantalla de nuestro stream y reacciona ahora mismo!"},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
                            ]
                        }
                    ],
                    max_tokens=45,
                    temperature=0.8
                )
                
                comment = response.choices[0].message.content.strip()
                gesture = self.personality.detect_gesture(comment, mood)
                
                return {
                    "type": "final",
                    "full_text": comment,
                    "mood": mood,
                    "gesture": gesture,
                    "is_donation": False
                }
            except Exception as e:
                print(f"[!] Error de visión con clave NVIDIA {key_preview}: {e}. Probando siguiente clave...")
                await asyncio.sleep(0.05)
        
        return {
            "type": "final",
            "full_text": "¡Oye, qué interesante se ve eso que tienes en pantalla!",
            "mood": "happy",
            "gesture": "explain",
            "is_donation": False
        }

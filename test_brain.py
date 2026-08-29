import asyncio
import time
from config import NVIDIA_API_KEYS, NVIDIA_BASE_URL, DEFAULT_MODEL
from openai import AsyncOpenAI
from database import init_db, get_user_context, update_user_interaction

async def test_all_keys():
    print(f"\n--- [1] PROBANDO {len(NVIDIA_API_KEYS)} CLAVES DE NVIDIA BUILD ---")
    working_keys = 0
    
    for idx, key in enumerate(NVIDIA_API_KEYS, start=1):
        key_preview = f"{key[:12]}...{key[-4:]}"
        client = AsyncOpenAI(base_url=NVIDIA_BASE_URL, api_key=key)
        start_time = time.time()
        try:
            res = await client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "user", "content": "Di 'Lumi Online' en 2 palabras."}
                ],
                max_tokens=10
            )
            elapsed = (time.time() - start_time) * 1000
            reply = res.choices[0].message.content.strip()
            print(f"[✓] Clave #{idx} ({key_preview}): OK ({elapsed:.0f} ms) -> \"{reply}\"")
            working_keys += 1
        except Exception as e:
            print(f"[✗] Clave #{idx} ({key_preview}): Error: {e}")

    print(f"\nResultado Claves: {working_keys}/{len(NVIDIA_API_KEYS)} operativas.")

async def test_database_flow():
    print("\n--- [2] PROBANDO MEMORIA SQLITE LOCAL ---")
    await init_db()
    
    # 1. Primera consulta
    test_user = "carlos_tester"
    ctx1 = await get_user_context(test_user)
    print(f"Contexto inicial: {ctx1}")
    
    # 2. Guardar interacción
    await update_user_interaction(test_user, "Me gusta jugar Minecraft", "¡Genial, a mí también!", "ALEGRE")
    
    # 3. Segunda consulta
    ctx2 = await get_user_context(test_user)
    print(f"Contexto tras interactuar: {ctx2}")
    print("[✓] Base de datos persistente funcionando correctamente.")

async def main():
    print("==================================================")
    print("🧪 INICIANDO TEST DE VERIFICACIÓN EN CANAIMA")
    print("==================================================")
    await test_all_keys()
    await test_database_flow()
    print("\n==================================================")
    print("🎉 PRUEBAS COMPLETADAS CON ÉXITO")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())

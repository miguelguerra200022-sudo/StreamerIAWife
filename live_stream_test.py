import asyncio
import time
from database import init_db
from main import StreamerServiceCoordinator
import aiosqlite
from config import DATABASE_PATH

async def run_live_stream_simulation():
    print("=" * 65)
    print("🎬 INICIANDO SIMULACIÓN EN VIVO DE STREAM EN CANAIMA")
    print("=" * 65)
    
    await init_db()
    coord = StreamerServiceCoordinator()
    
    chat_events = [
        ("AlexGamer", "¡Hola Lumi! ¿Qué juego vamos a jugar hoy en el directo?", False),
        ("Sofii_21", "Lumi eres demasiado hermosa y tierna te amooo <3", False),
        ("TrollMaster", "Eres una manquita y mala jugando, seguro pierdes", False),
        ("AlexGamer", "Oye Lumi, ¿recuerdas lo que te pregunté antes?", False),
        ("DonadorPro", "¡Toma $20 para la pizza de la mejor streamer del mundo!", True),
        ("GamerPro99", "Perdiste la partida, qué noob jajaja f", False),
        ("DonadorPro", "¿Te gustó la donación Lumi?", False)
    ]
    
    for i, (user, msg, is_vip) in enumerate(chat_events, 1):
        print(f"\n--- [Evento #{i}] ---")
        t0 = time.time()
        await coord.handle_incoming_message(user, msg, is_donation=is_vip)
        elapsed = (time.time() - t0) * 1000
        print(f"⏱️ Tiempo total de procesamiento: {elapsed:.0f} ms")
        await asyncio.sleep(0.3)
    
    # Esperar que las tareas en segundo plano terminen de escribir en la BD
    await asyncio.sleep(0.5)
    
    print("\n" + "=" * 65)
    print("📊 INSPECCIONANDO BASE DE DATOS SQLITE EN CANAIMA")
    print("=" * 65)
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        print("\n[👥 TABLA: ESPECTADORES REGISTRADOS]")
        async with db.execute("SELECT username, mensajes_totales, donaciones_total, primera_visita FROM espectadores") as cur:
            rows = await cur.fetchall()
            for r in rows:
                u = r["username"]
                m = r["mensajes_totales"]
                d = r["donaciones_total"]
                print(f"  • Usuario: {u:<15} | Mensajes: {m} | Donado: ${d:.2f}")
        
        print("\n[💬 TABLA: HISTORIAL DE CHAT Y EMOCIONES RECIENTES]")
        async with db.execute("SELECT username, estado_animo, mensaje, respuesta_ia FROM historial_chat ORDER BY id DESC LIMIT 5") as cur:
            rows = await cur.fetchall()
            for r in rows:
                mood = r["estado_animo"]
                user = r["username"]
                msg = r["mensaje"]
                resp = r["respuesta_ia"]
                print(f"  [{mood:<14}] {user}: {msg}")
                print(f"                 -> Lumi: \"{resp}\"")

    print("\n" + "=" * 65)
    print("🎉 TODAS LAS PRUEBAS EN VIVO COMPLETADAS EXITOSAMENTE")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(run_live_stream_simulation())

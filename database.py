import aiosqlite
import datetime
from config import DATABASE_PATH

async def init_db():
    """Inicializa las tablas de SQLite en la Canaima."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS espectadores (
                username TEXT PRIMARY KEY,
                primera_visita TEXT,
                ultima_visita TEXT,
                mensajes_totales INTEGER DEFAULT 1,
                donaciones_total REAL DEFAULT 0.0,
                resumen_memoria TEXT DEFAULT '',
                tags TEXT DEFAULT ''
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS historial_chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                mensaje TEXT,
                respuesta_ia TEXT,
                estado_animo TEXT,
                timestamp TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS donaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                monto REAL,
                mensaje TEXT,
                timestamp TEXT,
                procesado INTEGER DEFAULT 1
            )
        """)
        await db.commit()
    print("[✓] Base de datos SQLite inicializada correctamente.")

async def get_user_context(username: str) -> str:
    """Recupera la ficha de contexto del espectador para inyectarla en el prompt."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM espectadores WHERE username = ?", (username.lower(),)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return "Es la primera vez que este usuario escribe en el chat."
            
            mensajes = row["mensajes_totales"]
            donado = row["donaciones_total"]
            memoria = row["resumen_memoria"]
            
            contexto = f"Espectador conocido. Ha enviado {mensajes} mensajes."
            if donado > 0:
                contexto += f" Ha donado un total de ${donado:.2f} (es un donador VIP)."
            if memoria:
                contexto += f" Recuerdos previos: {memoria}."
            return contexto

async def update_user_interaction(username: str, message: str, reply: str, mood: str):
    """Actualiza estadísticas del usuario y guarda el turno de conversación."""
    now_str = datetime.datetime.now().isoformat()
    uname = username.lower()
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Actualizar o insertar espectador
        await db.execute("""
            INSERT INTO espectadores (username, primera_visita, ultima_visita, mensajes_totales)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(username) DO UPDATE SET
                ultima_visita = ?,
                mensajes_totales = mensajes_totales + 1
        """, (uname, now_str, now_str, now_str))
        
        # Guardar en historial
        await db.execute("""
            INSERT INTO historial_chat (username, mensaje, respuesta_ia, estado_animo, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (uname, message, reply, mood, now_str))
        
        await db.commit()

async def record_donation_event(username: str, amount: float, message: str):
    """Registra una donación VIP e incrementa el acumulado del usuario."""
    now_str = datetime.datetime.now().isoformat()
    uname = username.lower()
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO espectadores (username, primera_visita, ultima_visita, donaciones_total)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                ultima_visita = ?,
                donaciones_total = donaciones_total + ?
        """, (uname, now_str, now_str, amount, now_str, amount))
        
        await db.execute("""
            INSERT INTO donaciones (username, monto, mensaje, timestamp)
            VALUES (?, ?, ?, ?)
        """, (uname, amount, message, now_str))
        
        await db.commit()

import os
import traceback
import aiosqlite
from models.context import PatientContext
from pydantic_ai.messages import ModelMessagesTypeAdapter

# Paths for the local DB and the schema file
DB_PATH = "healthcare_state.db"
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

async def init_db():
    """Initialize database from the schema.sql file."""
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")
        
    with open(SCHEMA_PATH, "r") as f:
        schema_script = f.read()
        
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(schema_script)
        await db.commit()
    print("[SYSTEM] Database Initialized from schema.sql")

async def load_session(session_id: str) -> tuple[PatientContext, list]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT context, history FROM sessions WHERE session_id = ?", (session_id,))
        row = await cursor.fetchone()
        
        if row:
            # Use Pydantic's native JSON validators to instantly reconstruct states
            context = PatientContext.model_validate_json(row["context"])
            history = ModelMessagesTypeAdapter.validate_json(row["history"])
            return context, history
            
        return PatientContext(), []

async def save_session(session_id: str, context: PatientContext, history: list):
    try:
        # Pydantic natively handles datetime serialization to JSON strings
        context_json = context.model_dump_json()
        
        # FIX: Using dump_json() handles the message timestamps safely.
        # It returns bytes, so we decode it into a standard utf-8 string.
        history_json = ModelMessagesTypeAdapter.dump_json(history).decode('utf-8')
        
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO sessions (session_id, context, history, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id) DO UPDATE SET
                    context=excluded.context,
                    history=excluded.history,
                    updated_at=CURRENT_TIMESTAMP
            """, (session_id, context_json, history_json))
            await db.commit()
            
    except Exception as e:
        # AS REQUESTED: Hardcore debugging trace if serialization fails
        print("\n[CRITICAL SERIALIZATION ERROR]")
        print(f"Error Message: {e}")
        print("\n--- Raw Context Dump ---")
        print(repr(context))
        print("\n--- Raw History Dump ---")
        for msg in history:
            print(repr(msg))
        print("-" * 25)
        traceback.print_exc()
        raise
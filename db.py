import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent / "studybuddy.db"

def get_connection():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL COLLATE NOCASE,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

def save_note(topic: str, text: str) -> int:
    topic, text = topic.strip(), text.strip()
    if not topic:
        raise ValueError("Topic cannot be empty.")
    if not text:
        raise ValueError("Note text cannot be empty.")
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO notes (topic, text, created_at) VALUES (?, ?, ?)",
            (topic, text, created_at),
        )
        return cursor.lastrowid

def get_notes(topic: str) -> list[dict]:
    topic = topic.strip()
    if not topic:
        return []
    with get_connection() as connection:
        rows = connection.execute(
            """SELECT id, topic, text, created_at FROM notes
               WHERE topic = ? COLLATE NOCASE ORDER BY id DESC""",
            (topic,),
        ).fetchall()
    return [dict(row) for row in rows]

def list_topics() -> list[str]:
    with get_connection() as connection:
        rows = connection.execute(
            """SELECT topic FROM notes GROUP BY topic COLLATE NOCASE
               ORDER BY topic COLLATE NOCASE"""
        ).fetchall()
    return [row["topic"] for row in rows]

init_db()

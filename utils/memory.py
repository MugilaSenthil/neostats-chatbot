# utils/memory.py
import sqlite3
import json
import os
import uuid
from typing import List, Dict
from datetime import datetime
from config.config import CHAT_MEMORY_DB, CHAT_MEMORY_JSON_DIR

DB_PATH = CHAT_MEMORY_DB
JSON_BACKUP_DIR = CHAT_MEMORY_JSON_DIR
os.makedirs(JSON_BACKUP_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            role TEXT,
            content TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    return conn

_conn = init_db()

def new_session_id() -> str:
    return str(uuid.uuid4())

def save_message(session_id: str, role: str, content: str):
    mid = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    cur = _conn.cursor()
    cur.execute(
        "INSERT INTO messages (id, session_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
        (mid, session_id, role, content, now),
    )
    _conn.commit()

def load_session_messages(session_id: str) -> List[Dict]:
    cur = _conn.cursor()
    cur.execute("SELECT id, role, content, created_at FROM messages WHERE session_id = ? ORDER BY created_at ASC", (session_id,))
    rows = cur.fetchall()
    msgs = [{"id": r[0], "role": r[1], "content": r[2], "created_at": r[3]} for r in rows]
    return msgs

def dump_session_json(session_id: str) -> str:
    msgs = load_session_messages(session_id)
    path = os.path.join(JSON_BACKUP_DIR, f"session_{session_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"session_id": session_id, "messages": msgs}, f, ensure_ascii=False, indent=2)
    return path

def list_sessions(limit: int = 100) -> List[str]:
    cur = _conn.cursor()
    cur.execute("SELECT DISTINCT session_id FROM messages ORDER BY rowid DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    return [r[0] for r in rows]

def delete_session(session_id: str):
    cur = _conn.cursor()
    cur.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    _conn.commit()
    json_path = os.path.join(JSON_BACKUP_DIR, f"session_{session_id}.json")
    if os.path.exists(json_path):
        os.remove(json_path)

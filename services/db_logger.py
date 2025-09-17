# services/db_logger.py
import sqlite3
import json
from typing import Dict, Any
from config.settings import DB_PATH


def init_db():
    """
    Initialize SQLite database with the required logs table.
    """
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            input TEXT,
            intents TEXT,
            sentiment TEXT,
            urgency TEXT,
            actions TEXT,
            response TEXT,
            escalation INTEGER,
            meta TEXT,
            feedback TEXT
        )
        """)
        conn.commit()


def save_log(payload: Dict[str, Any]) -> int:
    """
    Save a log entry and return its row id.
    """
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
        INSERT INTO logs (input, intents, sentiment, urgency, actions, response, escalation, meta, feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            payload.get("input"),
            json.dumps(payload.get("intents", []), ensure_ascii=False),
            payload.get("sentiment"),
            payload.get("urgency"),
            json.dumps(payload.get("actions", []), ensure_ascii=False),
            payload.get("response"),
            1 if payload.get("escalation") else 0,
            json.dumps(payload.get("meta", {}), ensure_ascii=False),
            payload.get("feedback"),
        ))
        conn.commit()
        return c.lastrowid


def save_feedback(log_id: int, feedback: str):
    """
    Update feedback for a given log entry.
    """
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("UPDATE logs SET feedback=? WHERE id=?", (feedback, log_id))
        conn.commit()

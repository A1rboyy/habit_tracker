import sqlite3
from contextlib import closing

DB_NAME = "habits.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they do not yet exist."""
    with closing(get_connection()) as conn:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS habits (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    name         TEXT NOT NULL,
                    description  TEXT,
                    periodicity  TEXT CHECK(periodicity IN ('daily', 'weekly')) NOT NULL,
                    created_at   TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS completions (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id     INTEGER NOT NULL,
                    completed_at TEXT     NOT NULL,
                    FOREIGN KEY (habit_id)
                        REFERENCES habits (id) ON DELETE CASCADE
                )
                """
            )
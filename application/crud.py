from datetime import datetime
from typing import List, Tuple
import sqlite3
from .database import get_connection


# --------------------------- HABIT OPERATIONS ------------------------------

def create_habit(name: str, description: str, periodicity: str) -> int:
    """Insert a habit and return its new id."""
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO habits (name, description, periodicity, created_at) VALUES (?, ?, ?, ?)",
            (name, description, periodicity, datetime.utcnow().isoformat()),
        )
        return cursor.lastrowid


def delete_habit(habit_id: int) -> None:
    """Remove a habit (and its completions via cascade)."""
    with get_connection() as conn:
        conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))


# --------------------------- READ OPERATIONS ------------------------------

def get_all_habits() -> List[sqlite3.Row]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM habits ORDER BY id")
        return cursor.fetchall()


def get_habits_by_periodicity(periodicity: str) -> List[sqlite3.Row]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM habits WHERE periodicity = ? ORDER BY id", (periodicity,))
        return cursor.fetchall()


def get_habit_by_id(habit_id: int):
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
        return cursor.fetchone()


# --------------------------- COMPLETIONS -----------------------------------

def complete_habit(habit_id: int) -> None:
    """Insert a completion timestamp for a habit."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)",
            (habit_id, datetime.utcnow().isoformat()),
        )


def get_completions(habit_id: int) -> List[str]:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT completed_at FROM completions WHERE habit_id = ? ORDER BY completed_at", (habit_id,)
        )
        return [row[0] for row in cursor.fetchall()]
    
# --------------------------- ADMIN -----------------------------------

def insert_completion_at(habit_id: int, dt: datetime) -> None:
    """Insert a completion with an explicit timestamp (used for predefined habits)."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)",
            (habit_id, dt.isoformat()),
        )

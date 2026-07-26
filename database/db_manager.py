"""
HealthGuard AI — Database Manager
Handles SQLite operations for users, medications, health metrics, and reminders.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional

DB_PATH = os.getenv("DB_PATH", "health_data.db")


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # ── Users ────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            age         INTEGER,
            gender      TEXT,
            weight_kg   REAL,
            height_cm   REAL,
            blood_group TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Medications ───────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medications (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL REFERENCES users(id),
            name         TEXT    NOT NULL,
            dosage       TEXT    NOT NULL,
            frequency    TEXT    NOT NULL,     -- e.g. "Once daily", "Twice daily"
            time_slots   TEXT    NOT NULL,     -- JSON list of HH:MM strings
            start_date   TEXT    NOT NULL,
            end_date     TEXT,
            notes        TEXT,
            is_active    INTEGER DEFAULT 1,
            created_at   TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Medication Logs (adherence tracking) ──────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medication_logs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            medication_id INTEGER NOT NULL REFERENCES medications(id),
            user_id       INTEGER NOT NULL REFERENCES users(id),
            scheduled_at  TEXT    NOT NULL,
            taken_at      TEXT,
            status        TEXT    DEFAULT 'pending',  -- pending / taken / missed
            notes         TEXT,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Health Metrics ────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_metrics (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL REFERENCES users(id),
            metric_type    TEXT    NOT NULL,   -- steps, heart_rate, blood_pressure, weight, etc.
            value          REAL    NOT NULL,
            value2         REAL,               -- for blood pressure (diastolic)
            unit           TEXT    NOT NULL,
            recorded_at    TEXT    NOT NULL,
            notes          TEXT,
            created_at     TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Health Goals ──────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_goals (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL REFERENCES users(id),
            goal_type    TEXT    NOT NULL,     -- steps, weight_loss, medication_adherence, etc.
            target_value REAL    NOT NULL,
            current_value REAL   DEFAULT 0,
            unit         TEXT    NOT NULL,
            deadline     TEXT,
            status       TEXT    DEFAULT 'active',   -- active / achieved / abandoned
            created_at   TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Chat History ──────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER REFERENCES users(id),
            role       TEXT NOT NULL,    -- user / assistant
            content    TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Nutrition Logs ────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nutrition_logs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL REFERENCES users(id),
            meal_type     TEXT    NOT NULL,   -- breakfast, lunch, dinner, snack
            calories      REAL    NOT NULL,
            protein_g     REAL,
            carbs_g       REAL,
            fat_g         REAL,
            food_items    TEXT,
            recorded_at   TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()



# ────────────────────────────────────────────────────────────────────────────
# USER OPERATIONS
# ────────────────────────────────────────────────────────────────────────────

def create_user(name: str, age: int = None, gender: str = None,
                weight_kg: float = None, height_cm: float = None,
                blood_group: str = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (name, age, gender, weight_kg, height_cm, blood_group)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, age, gender, weight_kg, height_cm, blood_group))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


def get_all_users() -> list:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user(user_id: int) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_user(user_id: int, **kwargs) -> bool:
    if not kwargs:
        return False
    fields = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [user_id]
    conn = get_connection()
    conn.execute(f"UPDATE users SET {fields} WHERE id = ?", values)
    conn.commit()
    conn.close()
    return True


# ────────────────────────────────────────────────────────────────────────────
# MEDICATION OPERATIONS
# ────────────────────────────────────────────────────────────────────────────

def add_medication(user_id: int, name: str, dosage: str, frequency: str,
                   time_slots: str, start_date: str, end_date: str = None,
                   notes: str = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO medications (user_id, name, dosage, frequency, time_slots, start_date, end_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, name, dosage, frequency, time_slots, start_date, end_date, notes))
    med_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return med_id


def get_medications(user_id: int, active_only: bool = True) -> list:
    conn = get_connection()
    query = "SELECT * FROM medications WHERE user_id = ?"
    params = [user_id]
    if active_only:
        query += " AND is_active = 1"
    query += " ORDER BY name"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def deactivate_medication(med_id: int) -> bool:
    conn = get_connection()
    conn.execute("UPDATE medications SET is_active = 0 WHERE id = ?", (med_id,))
    conn.commit()
    conn.close()
    return True


def log_medication(medication_id: int, user_id: int, scheduled_at: str,
                   status: str = "taken", taken_at: str = None,
                   notes: str = None) -> int:
    taken_at = taken_at or datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO medication_logs (medication_id, user_id, scheduled_at, taken_at, status, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (medication_id, user_id, scheduled_at, taken_at, status, notes))
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id


def get_medication_logs(user_id: int, days: int = 7) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT ml.*, m.name as med_name, m.dosage
        FROM medication_logs ml
        JOIN medications m ON ml.medication_id = m.id
        WHERE ml.user_id = ?
          AND ml.created_at >= datetime('now', ? || ' days')
        ORDER BY ml.scheduled_at DESC
    """, (user_id, f"-{days}")).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_adherence_rate(user_id: int, days: int = 7) -> float:
    conn = get_connection()
    row = conn.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'taken' THEN 1 ELSE 0 END) as taken
        FROM medication_logs
        WHERE user_id = ?
          AND created_at >= datetime('now', ? || ' days')
    """, (user_id, f"-{days}")).fetchone()
    conn.close()
    if row and row["total"] > 0:
        return round((row["taken"] / row["total"]) * 100, 1)
    return 0.0


# ────────────────────────────────────────────────────────────────────────────
# HEALTH METRICS OPERATIONS
# ────────────────────────────────────────────────────────────────────────────

def log_health_metric(user_id: int, metric_type: str, value: float,
                      unit: str, recorded_at: str = None,
                      value2: float = None, notes: str = None) -> int:
    recorded_at = recorded_at or datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO health_metrics (user_id, metric_type, value, value2, unit, recorded_at, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, metric_type, value, value2, unit, recorded_at, notes))
    metric_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return metric_id


def get_health_metrics(user_id: int, metric_type: str = None,
                       days: int = 30) -> list:
    conn = get_connection()
    query = """
        SELECT * FROM health_metrics
        WHERE user_id = ?
          AND recorded_at >= datetime('now', ? || ' days')
    """
    params = [user_id, f"-{days}"]
    if metric_type:
        query += " AND metric_type = ?"
        params.append(metric_type)
    query += " ORDER BY recorded_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_latest_metric(user_id: int, metric_type: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("""
        SELECT * FROM health_metrics
        WHERE user_id = ? AND metric_type = ?
        ORDER BY recorded_at DESC LIMIT 1
    """, (user_id, metric_type)).fetchone()
    conn.close()
    return dict(row) if row else None


# ────────────────────────────────────────────────────────────────────────────
# HEALTH GOALS OPERATIONS
# ────────────────────────────────────────────────────────────────────────────

def add_health_goal(user_id: int, goal_type: str, target_value: float,
                    unit: str, deadline: str = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO health_goals (user_id, goal_type, target_value, unit, deadline)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, goal_type, target_value, unit, deadline))
    goal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return goal_id


def get_health_goals(user_id: int, active_only: bool = True) -> list:
    conn = get_connection()
    query = "SELECT * FROM health_goals WHERE user_id = ?"
    params = [user_id]
    if active_only:
        query += " AND status = 'active'"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_goal_progress(goal_id: int, current_value: float) -> bool:
    conn = get_connection()
    conn.execute("""
        UPDATE health_goals SET current_value = ? WHERE id = ?
    """, (current_value, goal_id))
    conn.commit()
    conn.close()
    return True


# ────────────────────────────────────────────────────────────────────────────
# CHAT HISTORY OPERATIONS
# ────────────────────────────────────────────────────────────────────────────

def save_chat_message(user_id: int, role: str, content: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)
    """, (user_id, role, content))
    msg_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return msg_id


def get_chat_history(user_id: int, limit: int = 20) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT role, content, created_at FROM chat_history
        WHERE user_id = ?
        ORDER BY created_at DESC LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


# ────────────────────────────────────────────────────────────────────────────
# NUTRITION OPERATIONS
# ────────────────────────────────────────────────────────────────────────────

def log_nutrition(user_id: int, meal_type: str, calories: float,
                  protein_g: float = None, carbs_g: float = None,
                  fat_g: float = None, food_items: str = None,
                  recorded_at: str = None) -> int:
    recorded_at = recorded_at or datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO nutrition_logs (user_id, meal_type, calories, protein_g, carbs_g, fat_g, food_items, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, meal_type, calories, protein_g, carbs_g, fat_g, food_items, recorded_at))
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id


def get_nutrition_logs(user_id: int, days: int = 7) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM nutrition_logs
        WHERE user_id = ?
          AND recorded_at >= datetime('now', ? || ' days')
        ORDER BY recorded_at DESC
    """, (user_id, f"-{days}")).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_daily_macro_summary(user_id: int, days: int = 7) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT date(recorded_at) as date,
               SUM(calories) as total_calories,
               SUM(protein_g) as total_protein,
               SUM(carbs_g) as total_carbs,
               SUM(fat_g) as total_fat
        FROM nutrition_logs
        WHERE user_id = ?
          AND recorded_at >= datetime('now', ? || ' days')
        GROUP BY date(recorded_at)
        ORDER BY date DESC
    """, (user_id, f"-{days}")).fetchall()
    conn.close()
    return [dict(r) for r in rows]


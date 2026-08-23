"""
HealthGuard AI — Database Manager
Handles SQLite operations for users, medications, health metrics, and reminders.
"""

import sqlite3
import os
import sys
from datetime import datetime
from typing import Optional

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "health_data.db"))



def get_active_db_provider() -> str:
    """Return active database engine name (lazy import to avoid circular issues)."""
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from database.supabase_manager import is_supabase_active
        if is_supabase_active():
            return "Supabase PostgreSQL (Cloud Active)"
    except Exception:
        pass
    return "SQLite Engine (Local Active)"


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
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    UNIQUE,
            password_hash TEXT,
            firebase_uid  TEXT,
            age           INTEGER,
            gender        TEXT,
            weight_kg     REAL,
            height_cm     REAL,
            blood_group   TEXT,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)

    # Check and add columns if upgrading existing db
    cursor.execute("PRAGMA table_info(users)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    if "email" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if "password_hash" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    if "firebase_uid" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN firebase_uid TEXT")
    if "allergies" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN allergies TEXT DEFAULT 'None'")


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

    # ── Family Members ───────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS family_members (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL REFERENCES users(id),
            name         TEXT    NOT NULL,
            relationship TEXT    NOT NULL,  -- Parent, Spouse, Child, Sibling, Self
            age          INTEGER,
            gender       TEXT,
            blood_group  TEXT,
            medical_notes TEXT,
            created_at   TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Caregiver Contacts ────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caregiver_contacts (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL REFERENCES users(id),
            name          TEXT    NOT NULL,
            relationship  TEXT    NOT NULL,
            phone         TEXT    NOT NULL,
            email         TEXT,
            notify_critical INTEGER DEFAULT 1,
            notify_missed INTEGER DEFAULT 1,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Indian Medications DB (1mg style) ──────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS indian_medications (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_name    TEXT    NOT NULL,
            generic_name  TEXT    NOT NULL,
            manufacturer  TEXT,
            price_inr     REAL    NOT NULL,
            form          TEXT,   -- Tablet, Syrup, Injection, Capsule
            strength      TEXT,   -- e.g. 650mg, 500mg
            usage_purpose TEXT,
            side_effects  TEXT,
            substitutes   TEXT,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Ayurvedic Herbs & Remedies DB ─────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ayurvedic_herbs (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            name             TEXT    NOT NULL,
            sanskrit_name    TEXT,
            primary_benefit  TEXT    NOT NULL,
            dosha_balancing  TEXT,   -- Vata, Pitta, Kapha, Tridoshic
            recommended_dosage TEXT,
            precautions      TEXT,
            formulation      TEXT,   -- Churna, Vati, Kwath, Oil
            created_at       TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Doctor Appointments (Practo style) ────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor_appointments (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL REFERENCES users(id),
            doctor_name      TEXT    NOT NULL,
            specialty        TEXT    NOT NULL,
            clinic_hospital  TEXT,
            city             TEXT    DEFAULT 'Mumbai',
            appointment_date TEXT    NOT NULL,
            appointment_time TEXT    NOT NULL,
            status           TEXT    DEFAULT 'Scheduled', -- Scheduled / Completed / Cancelled
            fee_inr          REAL    DEFAULT 500.0,
            notes            TEXT,
            created_at       TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Insurance & ABHA Health Locker ────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS insurance_policies (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL REFERENCES users(id),
            provider_name    TEXT    NOT NULL,  -- Ayushman Bharat, Star Health, ICICI Lombard, HDFC ERGO
            policy_number    TEXT    NOT NULL,
            abha_id          TEXT,              -- Ayushman Bharat Health Account ID
            coverage_amount  REAL    NOT NULL,
            expiry_date      TEXT,
            network_hospitals TEXT,
            status           TEXT    DEFAULT 'Active',
            created_at       TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Real-Time Health Alerts Log ────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_alerts_log (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL REFERENCES users(id),
            alert_type    TEXT    NOT NULL,  -- Critical Vitals, Missed Medication, Interaction Warning
            metric_name   TEXT,
            value         REAL,
            threshold     TEXT,
            severity      TEXT    NOT NULL,  -- Emergency / High / Moderate
            message       TEXT    NOT NULL,
            status        TEXT    DEFAULT 'Active',
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Nutrition Logs ────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nutrition_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            meal_type   TEXT NOT NULL,
            food_items  TEXT NOT NULL,
            calories    REAL DEFAULT 0,
            protein_g   REAL DEFAULT 0,
            carbs_g     REAL DEFAULT 0,
            fats_g      REAL DEFAULT 0,
            water_ml    REAL DEFAULT 0,
            date_str    TEXT DEFAULT (date('now')),
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()

    # Seed data if empty
    seed_db(cursor)
    conn.commit()
    conn.close()


def seed_db(cursor):
    """Seed database with pre-populated Indian medications, Ayurvedic herbs, sample doctor listings, etc."""
    # Check if indian_medications has data
    cursor.execute("SELECT COUNT(*) FROM indian_medications")
    if cursor.fetchone()[0] == 0:
        meds = [
            ("Dolo 650", "Paracetamol 650mg", "Micro Labs Ltd", 32.50, "Tablet", "650mg", "Fever, Mild to Moderate Pain", "Nausea, mild liver stress at high doses", "Calpol 650, Crocin 650, Pacimol 650"),
            ("Crocin 650", "Paracetamol 650mg", "GlaxoSmithKline", 34.00, "Tablet", "650mg", "Fever, Body Ache", "Mild skin rash if allergic", "Dolo 650, Calpol 650"),
            ("Pan 40", "Pantoprazole 40mg", "Alkem Laboratories", 155.00, "Tablet", "40mg", "Acidity, GERD, Stomach Ulcers", "Headache, diarrhea", "Pantocid 40, Pantodac 40"),
            ("Metformin 500", "Metformin Hydrochloride", "Sun Pharma", 42.00, "Tablet", "500mg", "Type 2 Diabetes Control", "Stomach upset, metallic taste", "Glycomet 500, Obimet 500"),
            ("Telmikind 40", "Telmisartan 40mg", "Mankind Pharma", 68.00, "Tablet", "40mg", "High Blood Pressure / Hypertension", "Dizziness, hyperkalemia", "Telma 40, Tazloc 40"),
            ("Augmentin 625 Duo", "Amoxicillin + Clavulanate", "GSK", 204.00, "Tablet", "625mg", "Bacterial Infections (Respiratory, ENT, Urinary)", "Diarrhea, loose motions", "Moxikind-CV 625, Advent 625"),
            ("Cilacar 10", "Cilnidipine 10mg", "JB Chemicals", 92.00, "Tablet", "10mg", "Hypertension & Kidney protection", "Ankle swelling, dizziness", "Cilny 10, Nimodip 10"),
            ("Azithral 500", "Azithromycin 500mg", "Alembic Pharma", 118.00, "Tablet", "500mg", "Throat Infection, Chest Infection", "Nausea, abdominal pain", "Azee 500, Zady 500")
        ]
        cursor.executemany("""
            INSERT INTO indian_medications (brand_name, generic_name, manufacturer, price_inr, form, strength, usage_purpose, side_effects, substitutes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, meds)

    # Check ayurvedic_herbs
    cursor.execute("SELECT COUNT(*) FROM ayurvedic_herbs")
    if cursor.fetchone()[0] == 0:
        herbs = [
            ("Ashwagandha", "Withania somnifera", "Stress relief, vitality, immune booster & stamina", "Vata & Kapha Pacifying", "1-2 tablets (300-600mg) with warm milk at bedtime", "Avoid in severe hyperthyroidism or acute fever", "Churna / Capsule / Arishta"),
            ("Tulsi", "Ocimum sanctum", "Respiratory immunity, cold relief & antioxidant protection", "Kapha & Vata Pacifying", "3-5 drops of Tulsi extract or 1 cup Tulsi tea twice daily", "Monitor blood glucose if taking diabetes medication", "Extract / Tea / Tablet"),
            ("Triphala", "Three Fruits Compound", "Digestive regularity, colon detox & eye health", "Tridoshic (Balances all 3 Doshas)", "1 teaspoon churna in warm water before bedtime", "Do not consume during pregnancy or acute diarrhea", "Churna / Tablet"),
            ("Turmeric / Curcumin", "Curcuma longa", "Anti-inflammatory, joint comfort & skin radiance", "Pitta & Kapha Pacifying", "500mg Curcumin with black pepper (Piperine) daily", "Caution with gallstones or blood thinners", "Powder / Extract"),
            ("Brahmi", "Bacopa monnieri", "Memory enhancer, focus & mental calm", "Pitta & Vata Pacifying", "250-500mg extract twice daily after meals", "May cause slight dry mouth if taken on empty stomach", "Tablet / Ghrita / Syrup"),
            ("Giloy / Guduchi", "Tinospora cordifolia", "Immune modulation, chronic fever recovery & liver detox", "Tridoshic (Vata, Pitta, Kapha Balance)", "500mg extract or 15ml juice in warm water morning", "Monitor if on autoimmune immunosuppressants", "Juice / Vati / Kwath"),
            ("Shatavari", "Asparagus racemosus", "Hormonal balance, vitality & reproductive wellness", "Pitta & Vata Pacifying", "1 capsule / 1 tsp powder with warm milk twice daily", "Caution if estrogen-sensitive conditions exist", "Churna / Granules")
        ]
        cursor.executemany("""
            INSERT INTO ayurvedic_herbs (name, sanskrit_name, primary_benefit, dosha_balancing, recommended_dosage, precautions, formulation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, herbs)





# ────────────────────────────────────────────────────────────────────────────
# USER OPERATIONS
# ────────────────────────────────────────────────────────────────────────────

def create_user(name: str, age: int = None, gender: str = None,
                weight_kg: float = None, height_cm: float = None,
                blood_group: str = None, email: str = None,
                password_hash: str = None, firebase_uid: str = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (name, age, gender, weight_kg, height_cm, blood_group, email, password_hash, firebase_uid)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, age, gender, weight_kg, height_cm, blood_group, email, password_hash, firebase_uid))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


def get_user_by_email(email: str) -> Optional[dict]:
    if not email:
        return None
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),)).fetchone()
    conn.close()
    return dict(row) if row else None


def authenticate_user_db(email: str, password_hash: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("""
        SELECT * FROM users WHERE LOWER(email) = LOWER(?) AND password_hash = ?
    """, (email.strip(), password_hash)).fetchone()
    conn.close()
    return dict(row) if row else None


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


def get_user_allergies(user_id: int) -> str:
    user = get_user(user_id)
    if user and user.get("allergies"):
        return user["allergies"]
    return "None"


def update_user_allergies(user_id: int, allergies: str) -> bool:
    return update_user(user_id, allergies=allergies.strip())



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


def clear_chat_history(user_id: int) -> bool:
    conn = get_connection()
    conn.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True


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


# ────────────────────────────────────────────────────────────────────────────
# INDIAN MEDICATIONS OPERATIONS (1mg)
# ────────────────────────────────────────────────────────────────────────────

def search_indian_medications(query: str = "") -> list:
    conn = get_connection()
    if query:
        pattern = f"%{query.strip()}%"
        rows = conn.execute("""
            SELECT * FROM indian_medications
            WHERE brand_name LIKE ? OR generic_name LIKE ? OR usage_purpose LIKE ?
            ORDER BY brand_name
        """, (pattern, pattern, pattern)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM indian_medications ORDER BY brand_name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_indian_medication(brand_name: str, generic_name: str, manufacturer: str,
                           price_inr: float, form: str, strength: str,
                           usage_purpose: str, side_effects: str, substitutes: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO indian_medications (brand_name, generic_name, manufacturer, price_inr, form, strength, usage_purpose, side_effects, substitutes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (brand_name, generic_name, manufacturer, price_inr, form, strength, usage_purpose, side_effects, substitutes))
    med_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return med_id


# ────────────────────────────────────────────────────────────────────────────
# AYURVEDIC HERBS OPERATIONS
# ────────────────────────────────────────────────────────────────────────────

def search_ayurvedic_herbs(query: str = "") -> list:
    conn = get_connection()
    if query:
        pattern = f"%{query.strip()}%"
        rows = conn.execute("""
            SELECT * FROM ayurvedic_herbs
            WHERE name LIKE ? OR sanskrit_name LIKE ? OR primary_benefit LIKE ? OR dosha_balancing LIKE ?
            ORDER BY name
        """, (pattern, pattern, pattern, pattern)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM ayurvedic_herbs ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ────────────────────────────────────────────────────────────────────────────
# DOCTOR APPOINTMENTS (PRACTO STYLE)
# ────────────────────────────────────────────────────────────────────────────

def create_doctor_appointment(user_id: int, doctor_name: str, specialty: str,
                              clinic_hospital: str, city: str,
                              appointment_date: str, appointment_time: str,
                              fee_inr: float = 500.0, notes: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO doctor_appointments (user_id, doctor_name, specialty, clinic_hospital, city, appointment_date, appointment_time, fee_inr, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, doctor_name, specialty, clinic_hospital, city, appointment_date, appointment_time, fee_inr, notes))
    app_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return app_id


def get_doctor_appointments(user_id: int) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM doctor_appointments WHERE user_id = ? ORDER BY appointment_date DESC, appointment_time DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_appointment_status(appointment_id: int, status: str) -> bool:
    conn = get_connection()
    conn.execute("UPDATE doctor_appointments SET status = ? WHERE id = ?", (status, appointment_id))
    conn.commit()
    conn.close()
    return True


# ────────────────────────────────────────────────────────────────────────────
# INSURANCE & ABHA HEALTH LOCKER
# ────────────────────────────────────────────────────────────────────────────

def add_insurance_policy(user_id: int, provider_name: str, policy_number: str,
                         abha_id: str, coverage_amount: float, expiry_date: str,
                         network_hospitals: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO insurance_policies (user_id, provider_name, policy_number, abha_id, coverage_amount, expiry_date, network_hospitals)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, provider_name, policy_number, abha_id, coverage_amount, expiry_date, network_hospitals))
    pol_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return pol_id


def get_insurance_policies(user_id: int) -> list:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM insurance_policies WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ────────────────────────────────────────────────────────────────────────────
# FAMILY & CAREGIVER OPERATIONS
# ────────────────────────────────────────────────────────────────────────────

def add_family_member(user_id: int, name: str, relationship: str, age: int = None,
                       gender: str = None, blood_group: str = None, medical_notes: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO family_members (user_id, name, relationship, age, gender, blood_group, medical_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, name, relationship, age, gender, blood_group, medical_notes))
    member_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return member_id


def get_family_members(user_id: int) -> list:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM family_members WHERE user_id = ? ORDER BY name", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_caregiver_contact(user_id: int, name: str, relationship: str, phone: str,
                          email: str = "", notify_critical: int = 1, notify_missed: int = 1) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO caregiver_contacts (user_id, name, relationship, phone, email, notify_critical, notify_missed)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, name, relationship, phone, email, notify_critical, notify_missed))
    cg_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return cg_id


def get_caregiver_contacts(user_id: int) -> list:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM caregiver_contacts WHERE user_id = ? ORDER BY name", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ────────────────────────────────────────────────────────────────────────────
# REAL-TIME HEALTH ALERTS LOG
# ────────────────────────────────────────────────────────────────────────────

def log_health_alert(user_id: int, alert_type: str, severity: str, message: str,
                     metric_name: str = None, value: float = None, threshold: str = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO health_alerts_log (user_id, alert_type, metric_name, value, threshold, severity, message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, alert_type, metric_name, value, threshold, severity, message))
    alert_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return alert_id


def get_active_health_alerts(user_id: int, limit: int = 10) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM health_alerts_log WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]



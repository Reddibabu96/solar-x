import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solarguard_x.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Panels Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS panels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        panel_code TEXT UNIQUE NOT NULL,
        farm_id TEXT NOT NULL DEFAULT 'SOLAR-ALPHA-01',
        string_number INTEGER NOT NULL,
        row_number INTEGER NOT NULL,
        col_number INTEGER NOT NULL,
        current_health REAL NOT NULL DEFAULT 100.0,
        health_level TEXT NOT NULL DEFAULT 'Excellent',
        health_badge TEXT NOT NULL DEFAULT '🟢',
        current_risk REAL NOT NULL DEFAULT 5.0,
        current_severity REAL NOT NULL DEFAULT 0.0,
        current_priority TEXT NOT NULL DEFAULT 'P4 — LOW',
        current_defect TEXT NOT NULL DEFAULT 'healthy',
        affected_area_pct REAL NOT NULL DEFAULT 0.0,
        last_inspected TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Inspections Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        panel_code TEXT NOT NULL,
        defect_type TEXT NOT NULL,
        display_name TEXT,
        confidence REAL NOT NULL,
        affected_area_pct REAL NOT NULL,
        defect_count INTEGER NOT NULL,
        severity_score REAL NOT NULL,
        health_score REAL NOT NULL,
        risk_score REAL NOT NULL,
        priority_code TEXT NOT NULL,
        recommended_action TEXT NOT NULL,
        ai_summary TEXT NOT NULL,
        detection_b64 TEXT,
        segmentation_b64 TEXT,
        heatmap_b64 TEXT,
        inspected_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (panel_code) REFERENCES panels (panel_code)
    )
    """)

    # 3. Health History Table (60-day trend monitoring)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS health_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        panel_code TEXT NOT NULL,
        day_offset INTEGER NOT NULL,
        health_score REAL NOT NULL,
        recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (panel_code) REFERENCES panels (panel_code)
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database schema initialized successfully at:", DB_PATH)

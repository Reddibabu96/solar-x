import datetime
import random
from database.schema import get_db_connection, init_db

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing data to allow fresh seed
    cursor.execute("DELETE FROM health_history")
    cursor.execute("DELETE FROM inspections")
    cursor.execute("DELETE FROM panels")

    # Define specific landmark panels for demo consistency
    SPECIAL_PANELS = {
        17: {"code": "PNL-017", "defect": "hotspot", "health": 21.4, "risk": 86.5, "severity": 82.0, "priority": "P1 — URGENT", "badge": "🔴", "level": "Critical", "area": 14.8},
        42: {"code": "PNL-042", "defect": "inactive_region", "health": 18.2, "risk": 91.0, "severity": 88.5, "priority": "P1 — URGENT", "badge": "🔴", "level": "Critical", "area": 22.5},
        88: {"code": "PNL-088", "defect": "crack", "health": 24.0, "risk": 82.0, "severity": 78.0, "priority": "P1 — URGENT", "badge": "🔴", "level": "Critical", "area": 11.2},
        8:  {"code": "PNL-008", "defect": "micro-crack", "health": 48.0, "risk": 62.0, "severity": 45.0, "priority": "P2 — HIGH", "badge": "🟠", "level": "Warning", "area": 7.5},
        31: {"code": "PNL-031", "defect": "delamination", "health": 42.5, "risk": 68.0, "severity": 52.0, "priority": "P2 — HIGH", "badge": "🟠", "level": "Warning", "area": 9.2},
        55: {"code": "PNL-055", "defect": "micro-crack", "health": 38.0, "risk": 71.0, "severity": 58.0, "priority": "P2 — HIGH", "badge": "🟠", "level": "Warning", "area": 10.4},
        64: {"code": "PNL-064", "defect": "micro-crack", "health": 55.0, "risk": 50.0, "severity": 38.0, "priority": "P3 — MEDIUM", "badge": "🟡", "level": "Monitor", "area": 4.1},
        79: {"code": "PNL-079", "defect": "micro-crack", "health": 68.0, "risk": 38.0, "severity": 30.0, "priority": "P3 — MEDIUM", "badge": "🟡", "level": "Monitor", "area": 3.2},
    }

    now = datetime.datetime.utcnow()

    # Generate 100 panels (10x10 Grid)
    for i in range(1, 101):
        panel_code = f"PNL-{i:03d}"
        row = ((i - 1) // 10) + 1
        col = ((i - 1) % 10) + 1
        string_num = ((i - 1) // 25) + 1

        if i in SPECIAL_PANELS:
            sp = SPECIAL_PANELS[i]
            health = sp["health"]
            level = sp["level"]
            badge = sp["badge"]
            risk = sp["risk"]
            sev = sp["severity"]
            prio = sp["priority"]
            defect = sp["defect"]
            area = sp["area"]
        else:
            # Generate realistic standard health distributions
            rand_val = random.random()
            if rand_val > 0.85: # Monitor (🟡)
                health = round(random.uniform(65.0, 84.9), 1)
                level = "Monitor"
                badge = "🟡"
                risk = round(random.uniform(25.0, 45.0), 1)
                sev = round(random.uniform(15.0, 30.0), 1)
                prio = "P3 — MEDIUM"
                defect = random.choice(["micro-crack", "delamination"])
                area = round(random.uniform(1.5, 4.5), 1)
            else: # Healthy (🟢)
                health = round(random.uniform(90.0, 99.5), 1)
                level = "Excellent" if health > 95 else "Good"
                badge = "🟢"
                risk = round(random.uniform(2.0, 15.0), 1)
                sev = 0.0
                prio = "P4 — LOW"
                defect = "healthy"
                area = 0.0

        last_insp_date = (now - datetime.timedelta(days=random.randint(0, 5))).isoformat()

        cursor.execute("""
        INSERT INTO panels (
            panel_code, farm_id, string_number, row_number, col_number,
            current_health, health_level, health_badge, current_risk,
            current_severity, current_priority, current_defect, affected_area_pct,
            last_inspected
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            panel_code, "SOLAR-ALPHA-01", string_num, row, col,
            health, level, badge, risk, sev, prio, defect, area, last_insp_date
        ))

        # Generate 60-day historical health degradation log for each panel
        start_health = min(100.0, health + random.uniform(15.0, 35.0))
        daily_drop = (start_health - health) / 60.0

        for day in range(60, -1, -5): # Every 5 days back to day 0
            day_health = max(health, round(start_health - (daily_drop * (60 - day)) + random.uniform(-1.0, 1.0), 1))
            hist_date = (now - datetime.timedelta(days=day)).isoformat()
            cursor.execute("""
            INSERT INTO health_history (panel_code, day_offset, health_score, recorded_at)
            VALUES (?, ?, ?, ?)
            """, (panel_code, 60 - day, day_health, hist_date))

    conn.commit()
    conn.close()
    print("Solar Farm Digital Twin database successfully seeded with 100 panels and 60-day history logs.")

if __name__ == "__main__":
    seed_database()

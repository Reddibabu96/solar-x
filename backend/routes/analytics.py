from fastapi import APIRouter
from backend.database import fetch_all, fetch_one
from backend.config import MEASURED_MODEL_METRICS

router = APIRouter(prefix="/api", tags=["Analytics & Governance"])

@router.get("/dashboard")
async def get_dashboard_summary():
    total_panels = fetch_one("SELECT COUNT(*) as cnt FROM panels")["cnt"]
    healthy_cnt = fetch_one("SELECT COUNT(*) as cnt FROM panels WHERE health_badge = '🟢'")["cnt"]
    monitor_cnt = fetch_one("SELECT COUNT(*) as cnt FROM panels WHERE health_badge = '🟡'")["cnt"]
    warning_cnt = fetch_one("SELECT COUNT(*) as cnt FROM panels WHERE health_badge = '🟠'")["cnt"]
    critical_cnt = fetch_one("SELECT COUNT(*) as cnt FROM panels WHERE health_badge = '🔴'")["cnt"]

    avg_health_row = fetch_one("SELECT AVG(current_health) as avg_h FROM panels")
    avg_health = round(avg_health_row["avg_h"], 1) if avg_health_row["avg_h"] else 100.0

    high_risk_cnt = fetch_one("SELECT COUNT(*) as cnt FROM panels WHERE current_risk >= 60.0")["cnt"]
    urgent_p1_cnt = fetch_one("SELECT COUNT(*) as cnt FROM panels WHERE current_priority LIKE '%P1%'")["cnt"]

    recent_urgent_panels = fetch_all(
        "SELECT panel_code, current_defect, current_health, current_risk, current_priority, current_severity, affected_area_pct FROM panels WHERE current_priority LIKE '%P1%' OR current_priority LIKE '%P2%' ORDER BY current_health ASC LIMIT 5"
    )

    return {
        "total_panels": total_panels,
        "healthy_count": healthy_cnt,
        "monitor_count": monitor_cnt,
        "warning_count": warning_cnt,
        "critical_count": critical_cnt,
        "average_health": avg_health,
        "high_risk_count": high_risk_cnt,
        "urgent_p1_count": urgent_p1_cnt,
        "recent_urgent_panels": recent_urgent_panels
    }

@router.get("/analytics")
async def get_analytics_data():
    defect_counts = fetch_all(
        "SELECT current_defect as defect, COUNT(*) as count FROM panels GROUP BY current_defect"
    )
    
    priority_counts = fetch_all(
        "SELECT current_priority as priority, COUNT(*) as count FROM panels GROUP BY current_priority"
    )

    badge_counts = fetch_all(
        "SELECT health_badge as badge, COUNT(*) as count FROM panels GROUP BY health_badge"
    )

    health_ranges = fetch_all("""
        SELECT 
            CASE 
                WHEN current_health >= 90 THEN '90-100 (Excellent)'
                WHEN current_health >= 75 THEN '75-89 (Good)'
                WHEN current_health >= 50 THEN '50-74 (Monitor)'
                WHEN current_health >= 25 THEN '25-49 (Warning)'
                ELSE '0-24 (Critical)'
            END as range,
            COUNT(*) as count
        FROM panels
        GROUP BY range
    """)

    return {
        "defect_distribution": defect_counts,
        "priority_distribution": priority_counts,
        "badge_distribution": badge_counts,
        "health_distribution": health_ranges
    }

@router.get("/model-performance")
async def get_model_performance():
    """Returns measured ML vision model metrics and confusion matrix."""
    return MEASURED_MODEL_METRICS

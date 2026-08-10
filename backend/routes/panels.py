from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from backend.database import fetch_all, fetch_one

router = APIRouter(prefix="/api/panels", tags=["Solar Farm Digital Twin"])

@router.get("")
async def get_all_panels(
    search: Optional[str] = None,
    priority: Optional[str] = None,
    badge: Optional[str] = None,
    defect: Optional[str] = None
):
    query = "SELECT * FROM panels WHERE 1=1"
    params = []

    if search:
        query += " AND (panel_code LIKE ? OR current_defect LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if priority:
        query += " AND current_priority LIKE ?"
        params.append(f"%{priority}%")
    if badge:
        query += " AND health_badge = ?"
        params.append(badge)
    if defect:
        query += " AND current_defect = ?"
        params.append(defect)

    query += " ORDER BY current_health ASC, row_number ASC, col_number ASC"
    panels = fetch_all(query, tuple(params))
    return {"total": len(panels), "panels": panels}

@router.get("/compare")
async def compare_panels(panel_a: str = Query("PNL-017"), panel_b: str = Query("PNL-031")):
    data_a = fetch_one("SELECT * FROM panels WHERE panel_code = ?", (panel_a,))
    data_b = fetch_one("SELECT * FROM panels WHERE panel_code = ?", (panel_b,))

    if not data_a or not data_b:
        raise HTTPException(status_code=444, detail="One or both panels could not be found.")

    hist_a = fetch_all("SELECT day_offset, health_score FROM health_history WHERE panel_code = ? ORDER BY day_offset ASC", (panel_a,))
    hist_b = fetch_all("SELECT day_offset, health_score FROM health_history WHERE panel_code = ? ORDER BY day_offset ASC", (panel_b,))

    return {
        "panel_a": {**data_a, "history": hist_a},
        "panel_b": {**data_b, "history": hist_b}
    }

@router.get("/{panel_code}")
async def get_panel_profile(panel_code: str):
    panel = fetch_one("SELECT * FROM panels WHERE panel_code = ?", (panel_code,))
    if not panel:
        raise HTTPException(status_code=404, detail=f"Panel {panel_code} not found.")

    latest_inspection = fetch_one(
        "SELECT * FROM inspections WHERE panel_code = ? ORDER BY id DESC LIMIT 1",
        (panel_code,)
    )

    history = fetch_all(
        "SELECT day_offset, health_score, recorded_at FROM health_history WHERE panel_code = ? ORDER BY day_offset ASC",
        (panel_code,)
    )

    return {
        "panel": panel,
        "latest_inspection": latest_inspection,
        "history": history
    }

@router.get("/{panel_code}/history")
async def get_panel_history(panel_code: str):
    history = fetch_all(
        "SELECT day_offset, health_score, recorded_at FROM health_history WHERE panel_code = ? ORDER BY day_offset ASC",
        (panel_code,)
    )
    return {"panel_code": panel_code, "history": history}

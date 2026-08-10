from pydantic import BaseModel
from typing import Optional, List

class PanelSchema(BaseModel):
    id: int
    panel_code: str
    farm_id: str
    string_number: int
    row_number: int
    col_number: int
    current_health: float
    health_level: str
    health_badge: str
    current_risk: float
    current_severity: float
    current_priority: str
    current_defect: str
    affected_area_pct: float
    last_inspected: Optional[str] = None

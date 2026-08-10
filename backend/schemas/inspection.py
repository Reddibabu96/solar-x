from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class PriorityContributionSchema(BaseModel):
    severity_contribution: float
    risk_contribution: float
    health_degradation_contribution: float
    affected_area_contribution: float

class InspectionResponseSchema(BaseModel):
    panel_code: str
    defect_type: str
    display_name: str
    confidence: float
    affected_area_pct: float
    defect_count: int
    severity_score: float
    severity_level: str
    health_score: float
    health_level: str
    health_badge: str
    risk_score: float
    risk_level: str
    priority_score: float
    priority_code: str
    priority_color: str
    contribution_breakdown: PriorityContributionSchema
    recommended_action: str
    ai_summary: str
    quality_metrics: Dict[str, Any]
    detection_b64: str
    segmentation_b64: str
    heatmap_b64: str
    inference_latency_ms: float

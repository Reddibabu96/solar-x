from fastapi import APIRouter, File, UploadFile, Form, HTTPException
import time
import os
import cv2
import numpy as np
import base64
from typing import List, Optional

from ml.preprocessing.pipeline import ImagePreprocessingPipeline
from ml.models.detector import SolarVisionDetector
from ml.explainability.gradcam import GradCAMGenerator
from ml.inference.decision_engine import SolarDecisionEngine
from backend.database import execute_write, fetch_one
from backend.config import SAMPLE_DATA_DIR

router = APIRouter(prefix="/api", tags=["Inspection"])

pipeline = ImagePreprocessingPipeline()
detector = SolarVisionDetector()
gradcam = GradCAMGenerator()
decision_engine = SolarDecisionEngine()

def _process_image_bytes(image_bytes: bytes, panel_code: str = "PNL-017", filename: Optional[str] = None):
    start_time = time.time()
    
    # 1. ML Image Preprocessing & Quality Assessment
    prep_res = pipeline.process(image_bytes)
    original_bgr = prep_res["original_bgr"]
    preprocessed_gray = prep_res["preprocessed_gray"]
    quality_metrics = prep_res["quality"]

    # 2. Solar Vision Defect Detection, Bounding Box Localization & Pixel Segmentation
    detection_res = detector.detect_and_segment(preprocessed_gray, original_bgr)

    # 3. Explainable AI Grad-CAM Heatmap Generation
    heatmap_b64 = gradcam.generate_heatmap(
        preprocessed_gray,
        original_bgr,
        detection_res.get("segmentation_mask_array")
    )

    # 4. AI Decision Engine (Severity, Health, Risk, Priority, Recommendations)
    decision_res = decision_engine.evaluate(detection_res)

    # Calculate Latency
    inference_latency_ms = round((time.time() - start_time) * 1000.0, 1)
    target_panel = panel_code if panel_code else "PNL-017"

    # 5. Update SQLite Database for Solar Digital Twin Synchronization
    try:
        execute_write("""
        UPDATE panels SET
            current_health = ?,
            health_level = ?,
            health_badge = ?,
            current_risk = ?,
            current_severity = ?,
            current_priority = ?,
            current_defect = ?,
            affected_area_pct = ?,
            last_inspected = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE panel_code = ?
        """, (
            decision_res["health_score"],
            decision_res["health_level"],
            decision_res["health_badge"],
            decision_res["risk_score"],
            decision_res["severity_score"],
            decision_res["priority_code"],
            decision_res["defect_type"],
            decision_res["affected_area_pct"],
            target_panel
        ))

        # Log Inspection Record
        execute_write("""
        INSERT INTO inspections (
            panel_code, defect_type, display_name, confidence, affected_area_pct,
            defect_count, severity_score, health_score, risk_score, priority_code,
            recommended_action, ai_summary, detection_b64, segmentation_b64, heatmap_b64
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            target_panel, decision_res["defect_type"], decision_res["display_name"],
            decision_res["confidence"], decision_res["affected_area_pct"],
            decision_res["defect_count"], decision_res["severity_score"],
            decision_res["health_score"], decision_res["risk_score"],
            decision_res["priority_code"], decision_res["recommended_action"],
            decision_res["ai_summary"], detection_res["detection_image_b64"],
            detection_res["segmentation_image_b64"], heatmap_b64
        ))
    except Exception as db_err:
        print(f"Database write non-fatal warning: {db_err}")

    # Convert original image to base64 for frontend comparison
    _, orig_buffer = cv2.imencode(".jpg", original_bgr)
    original_b64 = base64.b64encode(orig_buffer).decode("utf-8")

    # Prep preprocessed b64
    _, prep_buffer = cv2.imencode(".jpg", preprocessed_gray)
    preprocessed_b64 = base64.b64encode(prep_buffer).decode("utf-8")

    return {
        "panel_code": target_panel,
        "filename": filename or f"{target_panel}.jpg",
        "defect_type": decision_res["defect_type"],
        "display_name": decision_res["display_name"],
        "confidence": decision_res["confidence"],
        "affected_area_pct": decision_res["affected_area_pct"],
        "defect_count": decision_res["defect_count"],
        "severity_score": decision_res["severity_score"],
        "severity_level": decision_res["severity_level"],
        "health_score": decision_res["health_score"],
        "health_level": decision_res["health_level"],
        "health_badge": decision_res["health_badge"],
        "risk_score": decision_res["risk_score"],
        "risk_level": decision_res["risk_level"],
        "priority_score": decision_res["priority_score"],
        "priority_code": decision_res["priority_code"],
        "priority_color": decision_res["priority_color"],
        "contribution_breakdown": decision_res["contribution_breakdown"],
        "recommended_action": decision_res["recommended_action"],
        "what_is_damaged": decision_res["what_is_damaged"],
        "remediation_method": decision_res["remediation_method"],
        "ai_summary": decision_res["ai_summary"],

        "quality_metrics": quality_metrics,
        "original_b64": original_b64,
        "preprocessed_b64": preprocessed_b64,
        "detection_b64": detection_res["detection_image_b64"],
        "segmentation_b64": detection_res["segmentation_image_b64"],
        "heatmap_b64": heatmap_b64,
        "inference_latency_ms": inference_latency_ms
    }

@router.post("/predict")
async def predict_single_image(
    file: Optional[UploadFile] = File(None),
    preset: Optional[str] = Form(None),
    panel_code: Optional[str] = Form("PNL-017")
):
    # 1. Read Image Bytes from upload file OR demo preset preset_key
    image_bytes = None
    filename = None
    if file is not None:
        image_bytes = await file.read()
        filename = file.filename
    elif preset is not None:
        preset_file_map = {
            "healthy": "preset_healthy.png",
            "microcrack": "preset_microcrack.png",
            "hotspot": "preset_hotspot.png",
            "critical": "preset_critical.png"
        }
        preset_filename = preset_file_map.get(preset.lower(), "preset_hotspot.png")
        preset_path = os.path.join(SAMPLE_DATA_DIR, preset_filename)
        if not os.path.exists(preset_path):
            from sample_data.generate_presets import generate_presets
            generate_presets()
        with open(preset_path, "rb") as f:
            image_bytes = f.read()
        filename = preset_filename
    else:
        raise HTTPException(status_code=400, detail="Must provide either an uploaded image file or a preset parameter.")

    try:
        target_panel = panel_code if panel_code else "PNL-017"
        return _process_image_bytes(image_bytes, target_panel, filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Processing Failure: {str(e)}")

@router.post("/batch-predict")
async def batch_predict(files: list[UploadFile] = File(...)):
    results = []
    start_time = time.time()
    
    for idx, file in enumerate(files):
        panel_code = f"PNL-{(idx + 1):03d}"
        image_bytes = await file.read()
        try:
            res_item = _process_image_bytes(image_bytes, panel_code, file.filename)
            results.append(res_item)
        except Exception as e:
            results.append({
                "panel_code": panel_code,
                "filename": file.filename,
                "error": str(e)
            })

    total_batch_time_ms = round((time.time() - start_time) * 1000.0, 1)
    return {
        "processed_count": len(results),
        "total_batch_time_ms": total_batch_time_ms,
        "results": results
    }

@router.get("/demo-presets")
async def get_demo_presets():
    """Returns sample preset options for instant UI testing."""
    return {
        "presets": [
            {"id": "healthy", "title": "Healthy Solar Panel", "description": "0% affected area, 98/100 Health, P4 Low", "badge": "🟢"},
            {"id": "microcrack", "title": "Micro-Crack Fracture", "description": "Micro-cracks, 8.5% affected area, P3 Medium", "badge": "🟡"},
            {"id": "hotspot", "title": "Thermal Hotspot Burnout", "description": "Cell burnout, 14.8% affected area, P1 Urgent", "badge": "🔴"},
            {"id": "critical", "title": "Critical Multi-Defect Cell", "description": "Inactive region & cracks, 22.5% affected area, P1 Urgent", "badge": "🔴"}
        ]
    }

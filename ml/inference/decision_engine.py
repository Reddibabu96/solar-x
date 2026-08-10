from typing import Dict, Any

class SolarDecisionEngine:
    """
    Industrial Solar Panel Decision Engine.
    Computes Severity, Panel Health Score (0-100), AI Maintenance Risk Score (0-100),
    Priority Ranking (P1-P4), Contribution Breakdown, and Recommended Field Actions.
    """
    BASE_SEVERITY_WEIGHTS = {
        "healthy": 0.0,
        "micro-crack": 35.0,
        "crack": 45.0,
        "delamination": 40.0,
        "hotspot": 60.0,
        "inactive_region": 70.0
    }

    ACTION_RECOMMENDATIONS = {
        "P1 — URGENT": "Dispatch O&M technician within 24–48 hours for immediate thermal bypass / string disconnection & replacement.",
        "P2 — HIGH": "Schedule targeted panel inspection & soldering repair within 7 business days.",
        "P3 — MEDIUM": "Log defect profile into supervisory log and re-inspect during next quarterly maintenance cycle.",
        "P4 — LOW": "Panel operates within normal degradation tolerances. No immediate intervention required."
    }

    WHAT_IS_DAMAGED = {
        "healthy": "Nominal PV Status: All monocrystalline silicon cells, busbar conductors, and EVA encapsulation layers operate within optimal parameters with zero micro-fractures.",
        "micro-crack": "Silicon Wafer Lattice Micro-Fractures: Microscopic cracks propagating across silicon cell boundaries disrupting local electron collection and reducing string efficiency.",
        "crack": "Major Structural Silicon Cell Fracture: Visible structural cell breakage severing cell interconnect ribbons, creating isolated dead zones and hot-spot risks.",
        "hotspot": "Thermal Overheating & Sub-String Cell Burnout: Severe localized temperature surge (> 85°C) caused by reverse-bias current dissipation, risk of backsheet melt or glass cracking.",
        "inactive_region": "Total Sub-String Electrical Disconnection: Complete loss of electrical current generation across multiple cells due to open-circuit busbar failure or severe delamination.",
        "delamination": "EVA Encapsulation Layer Moisture Ingress: Moisture penetration and chemical degradation of Ethylene Vinyl Acetate (EVA) film causing optical reflection loss and busbar corrosion."
    }

    REMEDIATION_METHODS = {
        "healthy": "Standard O&M Protocol: Perform routine automated dust/soiling cleaning and annual torque check on frame mounting clamps. No technical repair needed.",
        "micro-crack": "Micro-Solder Reflow & Sealant Injection: Perform Electroluminescence (EL) string mapping, apply conductive UV-polymer barrier coating, and perform infrared micro-solder joint reflow.",
        "crack": "Sub-String Isolation or Laser Solder Repair: Isolate damaged cell sub-string via junction box bypass diodes, perform laser interconnect ribbon resoldering, or replace module if area exceeds 10%.",
        "hotspot": "Bypass Diode Replacement & MPPT Tuning: Replace shorted Schottky bypass diodes in junction box, clean glass surface, rebalance inverter MPPT channel, or replace module if backsheet is charred.",
        "inactive_region": "Interconnect Ribbon Resoldering & Module Replacement: Resolder broken busbar interconnects; if unrepairable, disconnect module from string via MC4 quick connectors and swap with calibrated spare.",
        "delamination": "Vacuum Thermal Lamination Sealing: Apply edge sealant tape around aluminum frame perimeter, execute vacuum thermal lamination repair, or spray UV-resistant anti-reflective seal."
    }


    def evaluate(self, detection_result: Dict[str, Any], historical_degradation_rate: float = 0.0) -> Dict[str, Any]:
        defect_type = detection_result.get("defect_type", "healthy")
        display_name = detection_result.get("display_name", "Healthy Panel")
        confidence = float(detection_result.get("confidence", 0.95))
        affected_area_pct = float(detection_result.get("affected_area_pct", 0.0))
        defect_count = int(detection_result.get("defect_count", 0))

        # 1. Severity Calculation
        base_weight = self.BASE_SEVERITY_WEIGHTS.get(defect_type, 25.0)
        if defect_type == "healthy":
            severity_score = 0.0
            severity_level = "LOW"
        else:
            raw_severity = (base_weight * 0.45) + (affected_area_pct * 1.4) + (defect_count * 8.0)
            severity_score = float(round(min(100.0, max(10.0, raw_severity * confidence)), 1))
            
            if severity_score >= 76.0:
                severity_level = "CRITICAL"
            elif severity_score >= 51.0:
                severity_level = "HIGH"
            elif severity_score >= 26.0:
                severity_level = "MEDIUM"
            else:
                severity_level = "LOW"

        # 2. Panel Health Score (0 - 100)
        if defect_type == "healthy":
            health_score = float(round(min(100.0, 95.0 + (confidence * 5.0)), 1))
        else:
            raw_health = 100.0 - (severity_score * 0.65) - (affected_area_pct * 0.35) - (defect_count * 4.0)
            health_score = float(round(max(0.0, min(100.0, raw_health)), 1))

        if health_score >= 90.0:
            health_level = "Excellent"
            health_badge = "🟢"
        elif health_score >= 75.0:
            health_level = "Good"
            health_badge = "🟡"
        elif health_score >= 50.0:
            health_level = "Monitor"
            health_badge = "🟡"
        elif health_score >= 25.0:
            health_level = "Warning"
            health_badge = "🟠"
        else:
            health_level = "Critical"
            health_badge = "🔴"

        # 3. AI Maintenance Risk Score (0 - 100)
        health_degradation = 100.0 - health_score
        raw_risk = (health_degradation * 0.70) + (severity_score * 0.20) + min(30.0, affected_area_pct * 1.2) + (historical_degradation_rate * 10.0)
        risk_score = float(round(max(0.0, min(100.0, raw_risk)), 1))

        if risk_score >= 80.0:
            risk_level = "CRITICAL"
        elif risk_score >= 60.0:
            risk_level = "HIGH"
        elif risk_score >= 30.0:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"

        # 4. Maintenance Priority Engine
        sev_contrib = round(severity_score * 0.35, 1)
        risk_contrib = round(risk_score * 0.35, 1)
        health_contrib = round((100.0 - health_score) * 0.20, 1)
        area_contrib = round(affected_area_pct * 0.10, 1)

        priority_score = float(round(sev_contrib + risk_contrib + health_contrib + area_contrib, 1))

        if priority_score >= 75.0:
            priority_code = "P1 — URGENT"
            priority_color = "red"
        elif priority_score >= 55.0:
            priority_code = "P2 — HIGH"
            priority_color = "orange"
        elif priority_score >= 35.0:
            priority_code = "P3 — MEDIUM"
            priority_color = "yellow"
        else:
            priority_code = "P4 — LOW"
            priority_color = "green"

        recommended_action = self.ACTION_RECOMMENDATIONS[priority_code]

        # 5. Natural Language AI Inspection Summary
        if defect_type == "healthy":
            ai_summary = f"Panel analysis shows optimal operational status with zero detected defects. Health score is {health_score}/100 and maintenance risk is low."
        else:
            ai_summary = (
                f"Panel exhibits {display_name} affecting approximately {affected_area_pct}% of the inspection region. "
                f"With a severity score of {severity_score}/100 and health score of {health_score}/100, "
                f"the panel is assigned AI maintenance risk of {risk_score}/100 and prioritized as {priority_code}."
            )

        return {
            "defect_type": defect_type,
            "display_name": display_name,
            "confidence": confidence,
            "affected_area_pct": affected_area_pct,
            "defect_count": defect_count,
            "severity_score": severity_score,
            "severity_level": severity_level,
            "health_score": health_score,
            "health_level": health_level,
            "health_badge": health_badge,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "priority_score": priority_score,
            "priority_code": priority_code,
            "priority_color": priority_color,
            "contribution_breakdown": {
                "severity_contribution": sev_contrib,
                "risk_contribution": risk_contrib,
                "health_degradation_contribution": health_contrib,
                "affected_area_contribution": area_contrib
            },
            "recommended_action": recommended_action,
            "what_is_damaged": self.WHAT_IS_DAMAGED.get(defect_type, self.WHAT_IS_DAMAGED["healthy"]),
            "remediation_method": self.REMEDIATION_METHODS.get(defect_type, self.REMEDIATION_METHODS["healthy"]),
            "ai_summary": ai_summary
        }


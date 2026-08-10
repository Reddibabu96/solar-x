from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import HTMLResponse
import datetime
from backend.database import fetch_one, fetch_all

from ml.inference.decision_engine import SolarDecisionEngine

router = APIRouter(prefix="/api/reports", tags=["Inspection Reports"])
engine = SolarDecisionEngine()

@router.post("/generate", response_class=HTMLResponse)
async def generate_inspection_report(panel_code: str = Form("PNL-017")):
    panel = fetch_one("SELECT * FROM panels WHERE panel_code = ?", (panel_code,))
    if not panel:
        raise HTTPException(status_code=404, detail=f"Panel {panel_code} not found.")

    latest_insp = fetch_one(
        "SELECT * FROM inspections WHERE panel_code = ? ORDER BY id DESC LIMIT 1",
        (panel_code,)
    )

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    ai_summary = latest_insp["ai_summary"] if latest_insp else f"Panel {panel_code} currently operates at {panel['current_health']}/100 health level with maintenance priority {panel['current_priority']}."
    action = latest_insp["recommended_action"] if latest_insp else "Perform routine thermal and visual inspection during next O&M cycle."

    defect_key = panel["current_defect"]
    what_damaged = engine.WHAT_IS_DAMAGED.get(defect_key, engine.WHAT_IS_DAMAGED["healthy"])
    remediation = engine.REMEDIATION_METHODS.get(defect_key, engine.REMEDIATION_METHODS["healthy"])


    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>SOLARGUARD X — Inspection Report ({panel_code})</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 40px; }}
            .card {{ background: #1e293b; border-radius: 12px; border: 1px solid #334155; padding: 30px; max-width: 900px; margin: 0 auto; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #38bdf8; padding-bottom: 15px; margin-bottom: 25px; }}
            .logo {{ font-size: 24px; font-weight: 800; color: #38bdf8; letter-spacing: 1px; }}
            .badge {{ font-size: 14px; font-weight: 600; padding: 6px 14px; border-radius: 20px; text-transform: uppercase; background: #0284c7; color: white; }}
            .badge.P1 {{ background: #ef4444; }}
            .badge.P2 {{ background: #f97316; }}
            .badge.P3 {{ background: #eab308; color: black; }}
            .badge.P4 {{ background: #22c55e; }}
            .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 25px; }}
            .metric-box {{ background: #0f172a; padding: 18px; border-radius: 8px; border: 1px solid #334155; }}
            .metric-label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px; }}
            .metric-val {{ font-size: 22px; font-weight: 700; color: #f8fafc; }}
            .section-title {{ font-size: 16px; font-weight: 700; color: #38bdf8; margin-top: 25px; margin-bottom: 10px; border-left: 4px solid #38bdf8; padding-left: 10px; }}
            .action-box {{ background: rgba(56, 189, 248, 0.1); border: 1px solid #38bdf8; padding: 18px; border-radius: 8px; font-size: 15px; line-height: 1.6; }}
            .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #64748b; border-top: 1px solid #334155; padding-top: 15px; }}
            @media print {{ body {{ background: white; color: black; }} .card {{ background: white; border: none; box-shadow: none; color: black; }} .metric-box {{ background: #f8fafc; border-color: #cbd5e1; color: black; }} .metric-val {{ color: black; }} }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <div>
                    <div class="logo">⚡ SOLARGUARD X</div>
                    <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">Automated Industrial Inspection & Decision Support</div>
                </div>
                <div>
                    <span class="badge {panel['current_priority'][:2]}">{panel['current_priority']}</span>
                </div>
            </div>

            <div style="margin-bottom: 20px; font-size: 14px; color: #cbd5e1;">
                <strong>Panel ID:</strong> {panel['panel_code']} &nbsp;|&nbsp; 
                <strong>Solar Farm:</strong> {panel['farm_id']} &nbsp;|&nbsp; 
                <strong>String/Row/Col:</strong> S{panel['string_number']}-R{panel['row_number']}-C{panel['col_number']} &nbsp;|&nbsp; 
                <strong>Report Generated:</strong> {now_str}
            </div>

            <div class="grid">
                <div class="metric-box">
                    <div class="metric-label">Panel Health Score</div>
                    <div class="metric-val" style="color: {'#ef4444' if panel['current_health'] < 50 else '#22c55e'};">{panel['current_health']}/100 ({panel['health_level']})</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">AI Maintenance Risk</div>
                    <div class="metric-val" style="color: {'#ef4444' if panel['current_risk'] >= 60 else '#eab308'};">{panel['current_risk']}/100</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Detected Defect Type</div>
                    <div class="metric-val" style="text-transform: capitalize;">{panel['current_defect'].replace('_', ' ')}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Affected Inspection Area</div>
                    <div class="metric-val">{panel['affected_area_pct']}% of panel surface</div>
                </div>
            </div>

            <div class="section-title">Technical Damage Diagnosis (What is Damaged?)</div>
            <div style="background: #0f172a; padding: 15px; border-radius: 8px; line-height: 1.6; margin-bottom: 20px; border: 1px solid #334155; color: #facc15;">
                <strong>Damage Analysis:</strong> {what_damaged}
            </div>

            <div class="section-title">Engineering Remediation & Repair Method</div>
            <div style="background: #0f172a; padding: 15px; border-radius: 8px; line-height: 1.6; margin-bottom: 20px; border: 1px solid #334155; color: #38bdf8;">
                <strong>Repair Protocol:</strong> {remediation}
            </div>

            <div class="section-title">AI Decision Summary</div>
            <div style="background: #0f172a; padding: 15px; border-radius: 8px; line-height: 1.6; margin-bottom: 20px; border: 1px solid #334155;">
                {ai_summary}
            </div>

            <div class="section-title">Recommended Technician Action</div>
            <div class="action-box">
                {action}
            </div>


            <div class="footer">
                SOLARGUARD X Platform &bull; Certified AI Decision Engine &bull; Document Signature: SGX-{hash(panel_code + now_str) & 0xffffffff:08x}
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

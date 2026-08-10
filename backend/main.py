from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from database.schema import init_db
from database.seed import seed_database
from backend.routes.inspect import router as inspect_router
from backend.routes.panels import router as panels_router
from backend.routes.analytics import router as analytics_router
from backend.routes.reports import router as reports_router
from backend.config import FRONTEND_DIR

app = FastAPI(
    title="SOLARGUARD X API",
    description="Intelligent Solar Panel Defect Detection, Health Assessment, Risk Estimation & Predictive Maintenance Prioritization Platform API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(inspect_router)
app.include_router(panels_router)
app.include_router(analytics_router)
app.include_router(reports_router)

@app.on_event("startup")
def on_startup():
    init_db()
    # Check if panels table has data, if empty seed automatically
    from backend.database import fetch_one
    res = fetch_one("SELECT COUNT(*) as cnt FROM panels")
    if not res or res["cnt"] == 0:
        print("Database empty on startup. Running automatic seeding...")
        seed_database()

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "system": "SOLARGUARD X",
        "version": "1.0.0",
        "engine": "PyTorch + OpenCV CLAHE + XAI Decision Engine"
    }

# Mount Frontend static files
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", response_class=FileResponse)
    async def serve_index():
        return os.path.join(FRONTEND_DIR, "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

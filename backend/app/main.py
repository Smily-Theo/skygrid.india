import os
import random
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from .database import Base, DATABASE_CONFIGURED, engine, get_db
from .models import Incident
from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only initialize tables when a persistent database is explicitly configured.
    # This prevents startup failure on Vercel when DATABASE_URL has not been added yet.
    if DATABASE_CONFIGURED and engine is not None:
        Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="SKYGRID INDIA API",
    version="1.0.0",
    description="Simulation-only urban air mobility fleet and incident API.",
    lifespan=lifespan,
)

origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

def demo_fleet():
    rng = random.Random(42)
    vehicles = []
    for i in range(8):
        vehicles.append({
            "vehicle_id": f"FC-{0x9B030F + i * 17391:06X}"[-9:],
            "latitude": round(11.0180 + i * 0.0031, 4),
            "longitude": round(76.9433 + i * 0.0023, 4),
            "altitude_m": rng.choice([90, 120, 150, 180, 210]),
            "speed_mps": rng.randint(20, 35),
            "battery_pct": rng.randint(55, 95),
            "status": "SIMULATED",
        })
    return vehicles

@app.get("/", include_in_schema=False)
def root():
    page = FRONTEND / "index.html"
    if page.exists():
        return FileResponse(page)
    return JSONResponse({"name": "SKYGRID INDIA API", "docs": "/docs", "health": "/health"})

@app.get("/styles.css", include_in_schema=False)
def styles():
    return FileResponse(FRONTEND / "styles.css", media_type="text/css")

@app.get("/app.js", include_in_schema=False)
def javascript():
    return FileResponse(FRONTEND / "app.js", media_type="application/javascript")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return JSONResponse({}, status_code=204)

@app.get("/health")
def health():
    return {"status": "ok", "message": "FastAPI backend is reachable", "simulation_only": True}

@app.get("/api/fleet")
def fleet():
    return demo_fleet()

@app.get("/api/incidents")
def incidents(db: Session = Depends(get_db)):
    rows = db.query(Incident).order_by(Incident.id.desc()).limit(20).all()
    return [{
        "id": row.id,
        "kind": row.kind,
        "severity": row.severity,
        "message": row.message,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    } for row in rows]

@app.post("/api/simulate/tick")
def simulate_tick(db: Session = Depends(get_db)):
    row = Incident(
        kind="SIMULATION_TICK",
        severity="INFO",
        message="One demo simulation tick was requested.",
        created_at=datetime.now(timezone.utc),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"status": "ok", "message": "Simulation tick completed; demo event stored.", "incident_id": row.id}

"""
SetuX / VeriX — FastAPI Main Application Entry Point
Maharashtra AI-Powered Infrastructure Verification Platform
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database.database import init_db
from app.auth import routes as auth_routes
from app.api import (
    projects,
    evidence,
    verification,
    analytics,
    audit,
    departments,
    contractors,
    milestones,
    progress,
    issues,
    alerts,
    reports,
)

# ─── App Setup ──────────────────────────────────────────────────
app = FastAPI(
    title="VeriX / SetuX API",
    description="AI-Powered Government Infrastructure Verification Platform — SIH Prototype\n\n⚠ DEMO ENVIRONMENT — All data is simulated for prototyping purposes.",
    version="2.0.0-demo",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── Static Uploads Mounting ────────────────────────────────────
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "evidence"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "before"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "after"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "reports"), exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ─── CORS ───────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Startup ────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    init_db()


# ─── Routers ────────────────────────────────────────────────────
app.include_router(auth_routes.router)
app.include_router(departments.router)
app.include_router(contractors.router)
app.include_router(projects.router)
app.include_router(milestones.router)
app.include_router(progress.router)
app.include_router(issues.router)
app.include_router(evidence.router)
app.include_router(verification.router)
app.include_router(analytics.router)
app.include_router(audit.router)
app.include_router(alerts.router)
app.include_router(reports.router)


# ─── Root ───────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "product": "VeriX / SetuX",
        "tagline": "From Reported Progress to Verified Progress.",
        "version": "2.0.0-demo",
        "environment": "DEMO — Data is simulated for SIH prototype",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok", "demo": True, "uploads_mounted": True}

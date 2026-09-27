"""
SetuX / VeriX — Verification API Router
POST /api/verification/run               — Run AI verification for a project
POST /api/projects/{project_id}/verify   — Project specific verification endpoint
GET  /api/verification/:project_id       — Get latest verification result
"""
import os
import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Project, Verification, Evidence, AuditLog
from app.schemas.schemas import VerificationRequest, VerificationResponse
from app.services.verification_engine import run_verification

router = APIRouter(tags=["Verification"])


@router.post("/api/verification/run", response_model=VerificationResponse)
@router.post("/api/projects/{project_id}/verify", response_model=VerificationResponse)
def run_project_verification(
    req: Optional[VerificationRequest] = None,
    project_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Run the AI verification pipeline on actual uploaded evidence images.
    Returns structured verification result with explainability and anomaly scoring.
    """
    target_project_id = project_id or (req.project_id if req else None)
    if not target_project_id:
        raise HTTPException(status_code=400, detail="Project ID required.")

    project = db.query(Project).filter(Project.project_id == target_project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {target_project_id} not found")

    # Record Audit Log: verification started
    audit_start = AuditLog(
        project_id=target_project_id,
        user_name="AI Verification Engine",
        action="VERIFICATION_START",
        details=f"AI verification pipeline initiated for {target_project_id}",
        timestamp=datetime.utcnow()
    )
    db.add(audit_start)
    db.commit()

    # Find latest uploaded evidence images on disk
    latest_evidences = (
        db.query(Evidence)
        .filter(Evidence.project_id == target_project_id)
        .order_by(Evidence.submitted_at.desc())
        .limit(5)
        .all()
    )

    image_paths = [ev.file_path for ev in latest_evidences if ev.file_path and os.path.exists(ev.file_path)]

    reported_prog = req.reported_progress if req else project.reported_progress
    sub_lat = req.submitted_lat if (req and req.submitted_lat is not None) else (latest_evidences[0].latitude if latest_evidences else project.lat)
    sub_lng = req.submitted_lng if (req and req.submitted_lng is not None) else (latest_evidences[0].longitude if latest_evidences else project.lng)

    result = run_verification(
        project_id=target_project_id,
        project_type=project.project_type,
        registered_lat=project.lat,
        registered_lng=project.lng,
        submitted_lat=sub_lat,
        submitted_lng=sub_lng,
        reported_progress=reported_prog,
        image_paths=image_paths,
    )

    # Persist verification result
    db_verification = Verification(
        project_id=target_project_id,
        reported_progress=result["reported_progress"],
        estimated_progress=result["estimated_progress"],
        gps_verified=result["gps_verified"],
        gps_distance_m=result["gps_distance_m"],
        timestamp_verified=result["timestamp_verified"],
        duplicate_image=result["duplicate_image"],
        manipulation_risk=result["manipulation_risk"],
        anomaly_score=result["anomaly_score"],
        risk_level=result["risk_level"],
        recommendation=result["recommendation"],
        infrastructure_detected=json.dumps(result["infrastructure_detected"]),
        explanation=result["explanation"],
        is_demo=True,
    )
    db.add(db_verification)

    # Update project with latest AI results & status
    project.ai_estimated_progress = result["estimated_progress"]
    project.anomaly_score = result["anomaly_score"]
    project.risk_level = result["risk_level"]
    if result["recommendation"] == "MANUAL_INSPECTION":
        project.status = "Review Required"
    elif result["recommendation"] == "SUPERVISOR_REVIEW":
        project.status = "Review Required"
    else:
        project.status = "Verified"

    # Update evidence verification status
    for ev in latest_evidences:
        ev.verification_status = project.status
        ev.ai_result = json.dumps({
            "estimated_progress": result["estimated_progress"],
            "anomaly_score": result["anomaly_score"],
            "recommendation": result["recommendation"]
        })

    # Record Audit Log: verification completed & status changed
    audit_end = AuditLog(
        project_id=target_project_id,
        user_name="AI Verification Engine",
        action="VERIFICATION_COMPLETE",
        details=f"Verification completed. Estimated: {result['estimated_progress']}%, Anomaly: {result['anomaly_score']}/100, Status: {project.status}",
        timestamp=datetime.utcnow()
    )
    db.add(audit_end)

    db.commit()
    return result


@router.get("/api/verification/{project_id}")
def get_verification(project_id: str, db: Session = Depends(get_db)):
    """Get latest verification report for a project."""
    verification = (
        db.query(Verification)
        .filter(Verification.project_id == project_id)
        .order_by(Verification.created_at.desc())
        .first()
    )
    if not verification:
        raise HTTPException(status_code=404, detail="No verification found for this project")

    return {
        "project_id": verification.project_id,
        "reported_progress": verification.reported_progress,
        "estimated_progress": verification.estimated_progress,
        "gps_verified": verification.gps_verified,
        "gps_distance_m": verification.gps_distance_m,
        "timestamp_verified": verification.timestamp_verified,
        "duplicate_image": verification.duplicate_image,
        "manipulation_risk": verification.manipulation_risk,
        "anomaly_score": verification.anomaly_score,
        "risk_level": verification.risk_level,
        "recommendation": verification.recommendation,
        "infrastructure_detected": json.loads(verification.infrastructure_detected or "[]"),
        "explanation": verification.explanation,
        "is_demo": verification.is_demo,
        "ai_demo_mode": True,
        "disclaimer": "Prototype AI Output — Model validation pending",
    }

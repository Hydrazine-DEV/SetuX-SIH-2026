"""
SetuX / VeriX — Audit Log API Router
GET /api/audit/              — Get all audit logs
GET /api/audit/:project_id   — Get audit logs for specific project
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import AuditLog
from app.schemas.schemas import AuditLogResponse

router = APIRouter(prefix="/api/audit", tags=["Audit Logs"])


@router.get("/", response_model=List[AuditLogResponse])
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve recent government audit logs."""
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()


@router.get("/{project_id}", response_model=List[AuditLogResponse])
def get_project_audit_logs(project_id: str, db: Session = Depends(get_db)):
    """Retrieve audit trail for a specific infrastructure project."""
    return db.query(AuditLog).filter(AuditLog.project_id == project_id).order_by(AuditLog.timestamp.desc()).all()

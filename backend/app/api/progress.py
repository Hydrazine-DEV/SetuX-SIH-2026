"""
SetuX / VeriX — Historical Progress Tracking API Router
Endpoints:
POST /api/projects/{project_id}/progress        — Append new historical progress update & sync project (Officer)
GET  /api/projects/{project_id}/progress        — Get complete historical progress timeline
GET  /api/projects/{project_id}/progress/latest — Get latest verified progress update
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_officer
from app.models.progress import ProgressUpdate
from app.models.project import Project
from app.schemas.progress import (
    ProgressUpdateCreate,
    ProgressUpdateResponse,
)

router = APIRouter(tags=["Historical Progress"])


def _find_project(project_id_or_code: str, db: Session) -> Optional[Project]:
    p = db.query(Project).filter(Project.project_code == project_id_or_code).first()
    if not p and project_id_or_code.isdigit():
        p = db.query(Project).filter(Project.id == int(project_id_or_code)).first()
    return p


@router.post(
    "/api/projects/{project_id}/progress",
    response_model=ProgressUpdateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_progress_update(
    project_id: str,
    req: ProgressUpdateCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_officer),
):
    """
    Append an immutable progress update to project history (Officer authorized).
    Synchronizes the project's current progress metrics while keeping all historical records intact.
    """
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    reported_by = req.reported_by or current_user.full_name or current_user.email

    # 1. Create NEW immutable historical record
    update = ProgressUpdate(
        project_id=project.id,
        reported_by=reported_by,
        report_date=req.report_date,
        physical_progress=req.physical_progress,
        financial_progress=req.financial_progress,
        expenditure=req.expenditure,
        remarks=req.remarks.strip() if req.remarks else None,
        created_at=datetime.utcnow(),
    )
    db.add(update)

    # 2. Synchronize Project's current progress values (Part 3)
    # Check if this update is the latest chronologically
    project.physical_progress = req.physical_progress
    project.financial_progress = req.financial_progress
    if req.expenditure > 0:
        project.total_expenditure = req.expenditure
    project.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(update)
    return update


@router.get("/api/projects/{project_id}/progress", response_model=List[ProgressUpdateResponse])
def get_progress_history(
    project_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve full historical progress timeline for a project in chronological order.
    """
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    history = (
        db.query(ProgressUpdate)
        .filter(ProgressUpdate.project_id == project.id)
        .order_by(ProgressUpdate.report_date.asc(), ProgressUpdate.id.asc())
        .all()
    )
    return history


@router.get("/api/projects/{project_id}/progress/latest", response_model=ProgressUpdateResponse)
def get_latest_progress(
    project_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve the single most recent progress update for a project.
    """
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    latest = (
        db.query(ProgressUpdate)
        .filter(ProgressUpdate.project_id == project.id)
        .order_by(ProgressUpdate.report_date.desc(), ProgressUpdate.id.desc())
        .first()
    )
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No progress updates recorded yet for project '{project_id}'.",
        )
    return latest

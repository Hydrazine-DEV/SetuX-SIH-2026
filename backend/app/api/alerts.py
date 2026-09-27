"""
SetuX / VeriX — Early Warning Alerts API Router
SIH26103: Integrated Government Project Monitoring & Intelligence Platform
Phase 16: Early Warning & Alert System

Endpoints:
- GET   /api/alerts                          — Global alerts listing with multi-filtering and pagination
- GET   /api/alerts/{alert_id}               — Get single alert detail with metadata
- GET   /api/projects/{project_id}/alerts    — List active/historical alerts for a specific project
- POST  /api/projects/{project_id}/alerts/generate — Generate/refresh alerts for a project (Officer)
- POST  /api/alerts/generate-all             — Bulk trigger alert evaluation across all projects (Officer)
- PATCH /api/alerts/{alert_id}/read          — Mark alert as read (Authenticated User)
- PATCH /api/alerts/{alert_id}/resolve       — Mark alert as resolved (Officer)
- PATCH /api/alerts/{alert_id}/dismiss       — Mark alert as dismissed (Officer)
"""
from typing import List, Optional
import math
from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_officer, get_current_user
from app.models.user import User
from app.schemas.alert import (
    AlertResponse,
    AlertListResponse,
    AlertGenerateResponse,
    AlertStatusUpdate,
)
from app.services.alert_config import AlertStatus
from app.services.alert_service import (
    generate_alerts_for_project,
    get_alerts,
    get_alert_by_id,
    update_alert_status,
    bulk_generate_alerts,
    _find_project,
)

router = APIRouter(tags=["Alerts"])


# ─── Global Alerts Listing ──────────────────────────────────────
@router.get("/api/alerts", response_model=AlertListResponse)
def list_alerts(
    project_id: Optional[int] = Query(None, description="Filter by numeric Project ID"),
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    status: Optional[str] = Query(None, description="Filter by status: UNREAD, READ, RESOLVED, DISMISSED"),
    alert_type: Optional[str] = Query(None, description="Filter by AlertType code"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve paginated early warning alerts with filtering on severity, status, alert_type, or project_id.
    """
    items, total = get_alerts(
        db=db,
        project_id=project_id,
        severity=severity,
        status=status,
        alert_type=alert_type,
        page=page,
        limit=limit,
    )

    pages = math.ceil(total / limit) if total > 0 else 1
    resp_items = [AlertResponse.from_orm_custom(a) for a in items]

    return AlertListResponse(
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        items=resp_items,
    )


# ─── Project-Specific Alerts Listing ────────────────────────────
@router.get("/api/projects/{project_id}/alerts", response_model=List[AlertResponse])
def get_project_alerts(
    project_id: str,
    severity: Optional[str] = Query(None, description="Filter by severity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all early warning alerts for a specific project by numeric ID or project code.
    """
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    items, _ = get_alerts(
        db=db,
        project_id=project.id,
        severity=severity,
        status=status,
        page=1,
        limit=200,
    )
    return [AlertResponse.from_orm_custom(a) for a in items]


# ─── Single Alert Lookup ────────────────────────────────────────
@router.get("/api/alerts/{alert_id}", response_model=AlertResponse)
def get_single_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve single alert details by Alert ID.
    """
    alert = get_alert_by_id(alert_id, db)
    if not alert:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found.",
        )
    return AlertResponse.from_orm_custom(alert)


# ─── Generate Alerts for a Single Project ───────────────────────
@router.post("/api/projects/{project_id}/alerts/generate", response_model=AlertGenerateResponse)
def trigger_project_alert_generation(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    """
    Trigger risk engine and ML evaluations to generate/refresh early warning alerts for a project.
    (Officer/Admin access required)
    """
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    result = generate_alerts_for_project(
        project_id_or_code=project.id,
        db=db,
        current_user_name=current_user.email or current_user.full_name,
    )

    alert_responses = [AlertResponse.from_orm_custom(a) for a in result["alerts"]]

    return AlertGenerateResponse(
        project_id=project.id,
        project_code=project.project_code,
        generated_count=result["generated_count"],
        existing_active_count=result["existing_active_count"],
        alerts=alert_responses,
        summary=result["summary"],
    )


# ─── Bulk Trigger Alert Generation ──────────────────────────────
@router.post("/api/alerts/generate-all")
def trigger_bulk_alert_generation(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    """
    Run alert generation across all monitored projects.
    (Officer/Admin access required)
    """
    return bulk_generate_alerts(db)


# ─── Mark Alert as Read ─────────────────────────────────────────
@router.patch("/api/alerts/{alert_id}/read", response_model=AlertResponse)
def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark an early warning alert as READ.
    """
    try:
        alert = update_alert_status(
            alert_id=alert_id,
            new_status=AlertStatus.READ.value,
            db=db,
            user_identifier=current_user.email or current_user.full_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not alert:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found.",
        )
    return AlertResponse.from_orm_custom(alert)


# ─── Mark Alert as Resolved ─────────────────────────────────────
@router.patch("/api/alerts/{alert_id}/resolve", response_model=AlertResponse)
def mark_alert_resolved(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    """
    Mark an early warning alert as RESOLVED with officer audit signature.
    (Officer/Admin access required)
    """
    try:
        alert = update_alert_status(
            alert_id=alert_id,
            new_status=AlertStatus.RESOLVED.value,
            db=db,
            user_identifier=current_user.email or current_user.full_name or "OFFICER",
        )
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not alert:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found.",
        )
    return AlertResponse.from_orm_custom(alert)


# ─── Mark Alert as Dismissed ────────────────────────────────────
@router.patch("/api/alerts/{alert_id}/dismiss", response_model=AlertResponse)
def mark_alert_dismissed(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    """
    Mark an early warning alert as DISMISSED with officer audit signature.
    (Officer/Admin access required)
    """
    try:
        alert = update_alert_status(
            alert_id=alert_id,
            new_status=AlertStatus.DISMISSED.value,
            db=db,
            user_identifier=current_user.email or current_user.full_name or "OFFICER",
        )
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not alert:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found.",
        )
    return AlertResponse.from_orm_custom(alert)

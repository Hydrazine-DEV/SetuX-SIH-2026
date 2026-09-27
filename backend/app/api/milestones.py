"""
SetuX / VeriX — Milestones API Router
Endpoints:
POST   /api/projects/{project_id}/milestones  — Create milestone for project (Officer)
GET    /api/projects/{project_id}/milestones  — List milestones for project
GET    /api/milestones/{milestone_id}         — Get single milestone
PUT    /api/milestones/{milestone_id}         — Update milestone (Officer)
DELETE /api/milestones/{milestone_id}         — Delete milestone (Officer)
"""
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_officer
from app.models.milestone import Milestone
from app.models.project import Project
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate, MilestoneResponse
from app.services.schedule_analysis import calculate_milestone_delay

router = APIRouter(tags=["Milestones"])


def _find_project(project_id_or_code: str, db: Session) -> Optional[Project]:
    p = db.query(Project).filter(Project.project_code == project_id_or_code).first()
    if not p and project_id_or_code.isdigit():
        p = db.query(Project).filter(Project.id == int(project_id_or_code)).first()
    return p


def _enrich_milestone_response(m: Milestone) -> MilestoneResponse:
    delay_info = calculate_milestone_delay(
        planned_date_str=m.planned_date,
        actual_date_str=m.actual_date,
        status=m.status,
    )
    return MilestoneResponse(
        id=m.id,
        project_id=m.project_id,
        name=m.name,
        description=m.description,
        planned_date=m.planned_date,
        actual_date=m.actual_date,
        status=m.status,
        completion_percentage=m.completion_percentage,
        is_delayed=delay_info["is_delayed"],
        delay_days=delay_info["delay_days"],
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


@router.post(
    "/api/projects/{project_id}/milestones",
    response_model=MilestoneResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_milestone(
    project_id: str,
    req: MilestoneCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_officer),
):
    """Create a new project milestone (Officer authorized)."""
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    # Actual date assignment if marked COMPLETED
    actual_date_val = req.actual_date
    status_clean = req.status.upper().strip() if req.status else "PENDING"
    if status_clean == "COMPLETED" and not actual_date_val:
        actual_date_val = str(date.today())

    milestone = Milestone(
        project_id=project.id,
        name=req.name.strip(),
        description=req.description.strip() if req.description else None,
        planned_date=req.planned_date,
        actual_date=actual_date_val,
        status=status_clean,
        completion_percentage=req.completion_percentage if req.completion_percentage is not None else 0.0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(milestone)
    db.commit()
    db.refresh(milestone)

    return _enrich_milestone_response(milestone)


@router.get("/api/projects/{project_id}/milestones", response_model=List[MilestoneResponse])
def list_project_milestones(
    project_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve all milestones for a project in planned chronological order."""
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    milestones = (
        db.query(Milestone)
        .filter(Milestone.project_id == project.id)
        .order_by(Milestone.planned_date.asc(), Milestone.id.asc())
        .all()
    )
    return [_enrich_milestone_response(m) for m in milestones]


@router.get("/api/milestones/{milestone_id}", response_model=MilestoneResponse)
def get_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve a single milestone by its ID."""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Milestone with ID {milestone_id} not found.",
        )
    return _enrich_milestone_response(milestone)


@router.put("/api/milestones/{milestone_id}", response_model=MilestoneResponse)
def update_milestone(
    milestone_id: int,
    req: MilestoneUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_officer),
):
    """Update milestone details, status, or progress (Officer authorized)."""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Milestone with ID {milestone_id} not found.",
        )

    if req.name is not None:
        milestone.name = req.name.strip()
    if req.description is not None:
        milestone.description = req.description.strip() if req.description else None
    if req.planned_date is not None:
        milestone.planned_date = req.planned_date
    if req.actual_date is not None:
        milestone.actual_date = req.actual_date
    if req.completion_percentage is not None:
        milestone.completion_percentage = req.completion_percentage

    if req.status is not None:
        milestone.status = req.status.upper().strip()
        if milestone.status == "COMPLETED":
            if not milestone.actual_date:
                milestone.actual_date = str(date.today())
            if milestone.completion_percentage < 100.0:
                milestone.completion_percentage = 100.0

    milestone.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(milestone)

    return _enrich_milestone_response(milestone)


@router.delete("/api/milestones/{milestone_id}")
def delete_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_officer),
):
    """Delete a milestone (Officer authorized)."""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Milestone with ID {milestone_id} not found.",
        )

    name = milestone.name
    db.delete(milestone)
    db.commit()
    return {"success": True, "message": f"Milestone '{name}' deleted successfully."}

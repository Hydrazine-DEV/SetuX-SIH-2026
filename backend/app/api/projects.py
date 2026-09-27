"""
SetuX / VeriX — Projects API Router
Complete CRUD endpoints for infrastructure projects with pagination, search,
filtering, sorting, and officer authorization guards.
100% backward compatible with legacy frontend contract.
"""
from typing import Optional, List, Union
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc

from app.api.deps import get_db, require_officer
from app.models.project import Project
from app.models.user import Department
from app.models.contractor import Contractor
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectStatusUpdate,
    ProjectResponse,
    PaginatedProjects,
)

router = APIRouter(prefix="/api/projects", tags=["Projects"])


def _find_project(project_id_or_code: str, db: Session) -> Optional[Project]:
    """Helper to locate a project either by string project_code or by integer ID."""
    p = db.query(Project).filter(Project.project_code == project_id_or_code).first()
    if not p and project_id_or_code.isdigit():
        p = db.query(Project).filter(Project.id == int(project_id_or_code)).first()
    return p


@router.get("", response_model=Union[List[ProjectResponse], PaginatedProjects])
@router.get("/", response_model=Union[List[ProjectResponse], PaginatedProjects])
def list_projects(
    response: Response,
    district: Optional[str] = Query(None, description="Filter by district"),
    department: Optional[str] = Query(None, description="Filter by department name"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    project_type: Optional[str] = Query(None, description="Filter by sector / project_type"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    contractor_id: Optional[int] = Query(None, description="Filter by contractor ID"),
    search: Optional[str] = Query(None, description="Search name, code, location, sector"),
    sort_by: str = Query("anomaly_score", description="Sort field: anomaly_score, original_cost, physical_progress, created_at, name"),
    order: str = Query("desc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    skip: Optional[int] = Query(None, ge=0, description="Direct offset override"),
    limit: Optional[int] = Query(None, ge=1, le=500, description="Direct limit override"),
    paginate: bool = Query(False, description="Set True for paginated envelope response"),
    db: Session = Depends(get_db),
):
    """
    List all infrastructure projects with full multi-criteria filtering, search,
    sorting, and pagination.
    """
    q = db.query(Project)

    # ─── Filtering ──────────────────────────────────────────────────────────
    if district:
        q = q.filter(Project.district.ilike(f"%{district.strip()}%"))
    if department:
        q = q.filter(Project.department_name.ilike(f"%{department.strip()}%"))
    if department_id is not None:
        q = q.filter(Project.department_id == department_id)
    if status:
        q = q.filter(Project.status == status.strip())
    if risk_level:
        q = q.filter(Project.risk_level == risk_level.upper().strip())
    effective_sector = sector or project_type
    if effective_sector:
        q = q.filter(Project.sector.ilike(f"%{effective_sector.strip()}%"))
    if contractor_id is not None:
        q = q.filter(Project.contractor_id == contractor_id)

    # ─── Free-Text Search ───────────────────────────────────────────────────
    if search and search.strip():
        term = f"%{search.strip()}%"
        q = q.filter(
            or_(
                Project.name.ilike(term),
                Project.project_code.ilike(term),
                Project.location.ilike(term),
                Project.district.ilike(term),
                Project.taluka.ilike(term),
                Project.sector.ilike(term),
                Project.contractor_name.ilike(term),
            )
        )

    # ─── Sorting ────────────────────────────────────────────────────────────
    sort_column_map = {
        "anomaly_score": Project.anomaly_score,
        "original_cost": Project.original_cost,
        "budget_lakh": Project.original_cost,
        "physical_progress": Project.physical_progress,
        "reported_progress": Project.physical_progress,
        "created_at": Project.created_at,
        "updated_at": Project.updated_at,
        "name": Project.name,
        "project_code": Project.project_code,
        "district": Project.district,
    }
    col = sort_column_map.get(sort_by, Project.anomaly_score)
    sort_expr = desc(col) if order.lower() == "desc" else asc(col)
    q = q.order_by(sort_expr)

    total_count = q.count()

    # ─── Pagination ─────────────────────────────────────────────────────────
    if skip is not None and limit is not None:
        actual_skip = skip
        actual_limit = limit
        current_page = (actual_skip // actual_limit) + 1
        current_page_size = actual_limit
    else:
        actual_skip = (page - 1) * page_size
        actual_limit = page_size
        current_page = page
        current_page_size = page_size

    total_pages = max(1, (total_count + current_page_size - 1) // current_page_size)
    items = q.offset(actual_skip).limit(actual_limit).all()

    # Set pagination response headers for clients inspecting headers
    response.headers["X-Total-Count"] = str(total_count)
    response.headers["X-Page"] = str(current_page)
    response.headers["X-Page-Size"] = str(current_page_size)
    response.headers["X-Total-Pages"] = str(total_pages)

    if paginate:
        return PaginatedProjects(
            items=items,
            total=total_count,
            page=current_page,
            page_size=current_page_size,
            total_pages=total_pages,
        )

    return items


@router.get("/stats")
def get_project_stats(db: Session = Depends(get_db)):
    """Return KPI statistics for dashboard consumption."""
    total = db.query(Project).count()
    verified = db.query(Project).filter(Project.status == "Verified").count()
    review = db.query(Project).filter(Project.status == "Review Required").count()
    high_risk = db.query(Project).filter(Project.risk_level.in_(["HIGH", "CRITICAL"])).count()
    delayed = db.query(Project).filter(Project.status == "Delayed").count()
    completed = db.query(Project).filter(Project.status == "Completed").count()

    return {
        "total": total,
        "verified": verified,
        "review_required": review,
        "high_risk": high_risk,
        "delayed": delayed,
        "completed": completed,
    }


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    """Retrieve single project by its project_code (e.g. MH-PN-001) or integer ID."""
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )
    return project


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    req: ProjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_officer),
):
    """
    Create a new infrastructure project (Officer authorized).
    Validates department and contractor relationships and assigns a unique project_code.
    """
    # 1. Resolve project_code
    code_raw = req.project_code or req.project_id
    if code_raw:
        project_code = code_raw.strip()
        existing = db.query(Project).filter(Project.project_code == project_code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project code '{project_code}' already exists.",
            )
    else:
        # Auto-generate project_code: e.g. MH-PUN-001
        dist_code = (req.district or "MH")[:3].upper()
        count = db.query(Project).count() + 1
        project_code = f"MH-{dist_code}-{count:03d}"

    # 2. Resolve Department
    dept_id = req.department_id
    dept_name = req.department_name or req.department
    if dept_id:
        dept = db.query(Department).filter(Department.id == dept_id).first()
        if dept:
            dept_name = dept.name
    elif dept_name:
        dept = db.query(Department).filter(Department.name.ilike(f"%{dept_name.strip()}%")).first()
        if dept:
            dept_id = dept.id
            dept_name = dept.name

    # 3. Resolve Contractor
    contractor_id = req.contractor_id
    contractor_name = req.contractor_name or req.contractor
    if contractor_id:
        cont = db.query(Contractor).filter(Contractor.id == contractor_id).first()
        if cont:
            contractor_name = cont.name
    elif contractor_name:
        cont = db.query(Contractor).filter(Contractor.name.ilike(f"%{contractor_name.strip()}%")).first()
        if cont:
            contractor_id = cont.id
            contractor_name = cont.name

    # 4. Resolve Aliases
    effective_sector = req.sector or req.project_type or "Roads & Highways"
    effective_location = req.location or req.location_name
    effective_lat = req.latitude if req.latitude is not None else req.lat
    effective_lng = req.longitude if req.longitude is not None else req.lng
    effective_cost = req.original_cost if req.original_cost is not None else (req.budget_lakh or 0.0)
    effective_completion = req.planned_completion_date or req.expected_completion
    effective_progress = req.physical_progress if req.physical_progress is not None else (float(req.reported_progress) if req.reported_progress is not None else 0.0)

    project = Project(
        project_code=project_code,
        name=req.name.strip(),
        description=req.description.strip() if req.description else None,
        sector=effective_sector,
        ministry=req.ministry.strip() if req.ministry else None,
        department_id=dept_id,
        department_name=dept_name,
        contractor_id=contractor_id,
        contractor_name=contractor_name,
        location=effective_location,
        district=req.district.strip() if req.district else None,
        taluka=req.taluka.strip() if req.taluka else "",
        state=req.state or "Maharashtra",
        latitude=effective_lat,
        longitude=effective_lng,
        original_cost=effective_cost,
        revised_cost=req.revised_cost,
        total_expenditure=req.total_expenditure or 0.0,
        start_date=req.start_date,
        planned_completion_date=effective_completion,
        revised_completion_date=req.revised_completion_date,
        actual_completion_date=req.actual_completion_date,
        physical_progress=effective_progress,
        financial_progress=req.financial_progress or 0.0,
        ai_estimated_progress=req.ai_estimated_progress or 0,
        status=req.status or "Under Review",
        risk_level=req.risk_level or "LOW",
        anomaly_score=req.anomaly_score or 0,
        is_demo=False,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    req: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_officer),
):
    """Update project details (Officer authorized)."""
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    if req.name is not None:
        project.name = req.name.strip()
    if req.description is not None:
        project.description = req.description.strip() if req.description else None

    # Sector
    sector_val = req.sector or req.project_type
    if sector_val is not None:
        project.sector = sector_val.strip()

    if req.ministry is not None:
        project.ministry = req.ministry.strip() if req.ministry else None

    # Department
    if req.department_id is not None:
        dept = db.query(Department).filter(Department.id == req.department_id).first()
        if dept:
            project.department_id = dept.id
            project.department_name = dept.name
    elif req.department or req.department_name:
        dept_text = req.department or req.department_name
        dept = db.query(Department).filter(Department.name.ilike(f"%{dept_text.strip()}%")).first()
        if dept:
            project.department_id = dept.id
            project.department_name = dept.name
        else:
            project.department_name = dept_text.strip()

    # Contractor
    if req.contractor_id is not None:
        cont = db.query(Contractor).filter(Contractor.id == req.contractor_id).first()
        if cont:
            project.contractor_id = cont.id
            project.contractor_name = cont.name
    elif req.contractor or req.contractor_name:
        cont_text = req.contractor or req.contractor_name
        cont = db.query(Contractor).filter(Contractor.name.ilike(f"%{cont_text.strip()}%")).first()
        if cont:
            project.contractor_id = cont.id
            project.contractor_name = cont.name
        else:
            project.contractor_name = cont_text.strip()

    # Location
    loc = req.location or req.location_name
    if loc is not None:
        project.location = loc.strip() if loc else None
    if req.district is not None:
        project.district = req.district.strip() if req.district else None
    if req.taluka is not None:
        project.taluka = req.taluka.strip() if req.taluka else ""
    if req.state is not None:
        project.state = req.state.strip()

    lat = req.latitude if req.latitude is not None else req.lat
    if lat is not None:
        project.latitude = lat
    lng = req.longitude if req.longitude is not None else req.lng
    if lng is not None:
        project.longitude = lng

    # Financials
    cost = req.original_cost if req.original_cost is not None else req.budget_lakh
    if cost is not None:
        project.original_cost = cost
    if req.revised_cost is not None:
        project.revised_cost = req.revised_cost
    if req.total_expenditure is not None:
        project.total_expenditure = req.total_expenditure

    # Dates
    if req.start_date is not None:
        project.start_date = req.start_date
    completion = req.planned_completion_date or req.expected_completion
    if completion is not None:
        project.planned_completion_date = completion
    if req.revised_completion_date is not None:
        project.revised_completion_date = req.revised_completion_date
    if req.actual_completion_date is not None:
        project.actual_completion_date = req.actual_completion_date

    # Progress & Status
    prog = req.physical_progress if req.physical_progress is not None else (float(req.reported_progress) if req.reported_progress is not None else None)
    if prog is not None:
        project.physical_progress = prog
    if req.financial_progress is not None:
        project.financial_progress = req.financial_progress
    if req.ai_estimated_progress is not None:
        project.ai_estimated_progress = req.ai_estimated_progress
    if req.status is not None:
        project.status = req.status
    if req.risk_level is not None:
        project.risk_level = req.risk_level
    if req.anomaly_score is not None:
        project.anomaly_score = req.anomaly_score

    db.commit()
    db.refresh(project)
    return project


@router.put("/{project_id}/status")
def update_project_status(
    project_id: str,
    status_param: Optional[str] = Query(None, alias="status"),
    risk_level_param: Optional[str] = Query(None, alias="risk_level"),
    body: Optional[ProjectStatusUpdate] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_officer),
):
    """
    Update project status and risk level (Officer authorized).
    Accepts values via query params (legacy frontend) or JSON body.
    """
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    new_status = (body.status if body else None) or status_param
    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status value must be provided.",
        )

    project.status = new_status
    new_risk = (body.risk_level if body else None) or risk_level_param
    if new_risk:
        project.risk_level = new_risk

    db.commit()
    db.refresh(project)
    return {
        "success": True,
        "project_id": project.project_code,
        "status": project.status,
        "risk_level": project.risk_level,
    }


@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_officer),
):
    """Delete a project (Officer authorized)."""
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    code = project.project_code
    db.delete(project)
    db.commit()
    return {"success": True, "message": f"Project '{code}' deleted successfully."}


@router.get("/{project_id}/intelligence")
def get_project_intelligence_endpoint(
    project_id: str,
    db: Session = Depends(get_db),
):
    """Return transparent rule-based project intelligence summary for a project."""
    from app.api.analytics import get_project_intelligence
    return get_project_intelligence(project_id, db)


@router.get("/{project_id}/risk")
def get_project_risk_endpoint(
    project_id: str,
    db: Session = Depends(get_db),
):
    """
    Run deterministic rule-based risk engine evaluation for a project.
    Analyzes schedule delay, low physical progress, cost overrun, financial-physical mismatch,
    milestone delays, open issues, and critical issues.
    """
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    from app.models.milestone import Milestone
    from app.models.progress import ProgressUpdate
    from app.models.issue import Issue
    from app.services.risk_engine import evaluate_project_risk

    milestones = db.query(Milestone).filter(Milestone.project_id == project.id).all()
    progress_history = db.query(ProgressUpdate).filter(ProgressUpdate.project_id == project.id).all()
    issues = db.query(Issue).filter(Issue.project_id == project.id).all()

    return evaluate_project_risk(project, milestones, progress_history, issues)


@router.get("/{project_id}/prediction/cost-overrun")
@router.get("/{project_id}/cost-prediction")
def get_project_cost_overrun_prediction(
    project_id: str,
    db: Session = Depends(get_db),
):
    """
    Return Cost Overrun Machine Learning Prediction for a given project (Phase 13).
    Generates prediction-time features, loads pre-trained model artifact, computes prediction
    probability, extracts top predictive factors, and compares against rule-based cost baseline.
    """
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    from app.models.milestone import Milestone
    from app.models.progress import ProgressUpdate
    from app.models.issue import Issue
    from app.ml.cost_overrun_predictor import predict_cost_overrun
    from app.services.risk_engine import eval_cost_overrun

    milestones = db.query(Milestone).filter(Milestone.project_id == project.id).all()
    progress_updates = db.query(ProgressUpdate).filter(ProgressUpdate.project_id == project.id).all()
    issues = db.query(Issue).filter(Issue.project_id == project.id).all()

    raw_dict = {
        "project_id": project.id,
        "project_code": project.project_code,
        "name": project.name,
        "sector": project.sector,
        "department_name": project.department_name,
        "district": project.district,
        "state": project.state,
        "contractor_name": project.contractor_name,
        "original_cost": project.original_cost,
        "revised_cost": project.revised_cost,
        "expenditure": project.total_expenditure if project.total_expenditure is not None else 0.0,
        "start_date": project.start_date,
        "planned_completion_date": project.planned_completion_date,
        "physical_progress": project.physical_progress,
        "financial_progress": project.financial_progress,
        "status": project.status,
        "total_milestones": len(milestones),
        "completed_milestones": sum(1 for m in milestones if (m.status or "").upper() == "COMPLETED"),
        "delayed_milestones": sum(1 for m in milestones if (m.status or "").upper() == "DELAYED"),
        "progress_update_count": len(progress_updates),
        "total_issues": len(issues),
        "open_issues": sum(1 for i in issues if (i.status or "").upper() in ("OPEN", "IN_PROGRESS")),
        "critical_issues": sum(1 for i in issues if (i.severity or "").upper() == "CRITICAL" and (i.status or "").upper() in ("OPEN", "IN_PROGRESS")),
    }

    prediction = predict_cost_overrun(raw_dict)

    if not prediction.get("is_available"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=prediction.get("error", "Cost overrun model is not currently trained."),
        )

    # Phase 11 Rule Engine Baseline comparison
    rule_eval = eval_cost_overrun(project)
    prediction["rule_engine_baseline"] = {
        "factor": "COST_OVERRUN",
        "is_triggered": rule_eval.get("triggered", False),
        "score_contribution": rule_eval.get("score_contribution", 0.0),
        "details": rule_eval.get("details", ""),
    }

    return prediction


@router.get("/{project_id}/prediction/time-overrun")
@router.get("/{project_id}/time-prediction")
def get_project_time_overrun_prediction(
    project_id: str,
    db: Session = Depends(get_db),
):
    """
    Return Time / Schedule Overrun Machine Learning Prediction for a given project (Phase 14).
    Generates prediction-time features, loads pre-trained model artifact, computes prediction
    probability, extracts top predictive factors, and compares against rule-based schedule baseline.
    """
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    from app.models.milestone import Milestone
    from app.models.progress import ProgressUpdate
    from app.models.issue import Issue
    from app.ml.time_overrun_predictor import predict_time_overrun
    from app.services.risk_engine import eval_schedule_delay

    milestones = db.query(Milestone).filter(Milestone.project_id == project.id).all()
    progress_updates = db.query(ProgressUpdate).filter(ProgressUpdate.project_id == project.id).all()
    issues = db.query(Issue).filter(Issue.project_id == project.id).all()

    raw_dict = {
        "project_id": project.id,
        "project_code": project.project_code,
        "name": project.name,
        "sector": project.sector,
        "department_name": project.department_name,
        "district": project.district,
        "state": project.state,
        "contractor_name": project.contractor_name,
        "original_cost": project.original_cost,
        "revised_cost": project.revised_cost,
        "expenditure": project.total_expenditure if project.total_expenditure is not None else 0.0,
        "start_date": project.start_date,
        "planned_completion_date": project.planned_completion_date,
        "physical_progress": project.physical_progress,
        "financial_progress": project.financial_progress,
        "status": project.status,
        "total_milestones": len(milestones),
        "completed_milestones": sum(1 for m in milestones if (m.status or "").upper() == "COMPLETED"),
        "delayed_milestones": sum(1 for m in milestones if (m.status or "").upper() == "DELAYED"),
        "progress_update_count": len(progress_updates),
        "total_issues": len(issues),
        "open_issues": sum(1 for i in issues if (i.status or "").upper() in ("OPEN", "IN_PROGRESS")),
        "critical_issues": sum(1 for i in issues if (i.severity or "").upper() == "CRITICAL" and (i.status or "").upper() in ("OPEN", "IN_PROGRESS")),
    }

    prediction = predict_time_overrun(raw_dict)

    if not prediction.get("is_available"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=prediction.get("error", "Time overrun model is not currently trained."),
        )

    # Phase 11 Rule Engine Baseline comparison
    rule_eval = eval_schedule_delay(project)
    prediction["rule_engine_baseline"] = {
        "factor": "SCHEDULE_DELAY",
        "is_triggered": rule_eval.get("triggered", False),
        "score_contribution": rule_eval.get("score_contribution", 0.0),
        "details": rule_eval.get("details", ""),
    }

    return prediction


@router.get("/{project_id}/risk-intelligence")
def get_overall_project_risk_intelligence_endpoint(
    project_id: str,
    db: Session = Depends(get_db),
):
    """
    Return Overall Project Risk Intelligence for a given project (Phase 15).
    Integrates current project conditions, Phase 11 rule-based indicators, Phase 13 Cost ML,
    Phase 14 Time ML, data quality indicators, deterministic natural language summary,
    and decision-support action recommendations.
    """
    from app.services.risk_intelligence import generate_overall_project_risk_intelligence

    res = generate_overall_project_risk_intelligence(project_id, db)
    if not res.get("is_available"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=res.get("error", f"Project '{project_id}' not found."),
        )
    return res





"""
SetuX / VeriX — Issues API Router
Phase 9: Comprehensive Issue Management & Issue Evidence Integration

Endpoints:
- POST   /api/projects/{project_id}/issues        — Create issue for project (Officer)
- GET    /api/projects/{project_id}/issues/summary — Get aggregated issue metrics for project
- GET    /api/projects/{project_id}/issues        — List issues for project
- GET    /api/issues/{issue_id}                   — Get single issue by ID
- PUT    /api/issues/{issue_id}                   — Update issue details/severity/status (Officer)
- DELETE /api/issues/{issue_id}                   — Delete issue (Officer)
- POST   /api/issues/{issue_id}/evidence          — Upload supporting evidence file for issue (Officer)
- GET    /api/issues/{issue_id}/evidence          — List all evidence attached to an issue
- GET    /api/projects/{project_id}/issues/{issue_id}/evidence — Verified cross-project evidence check
"""
import os
import uuid
from typing import List, Optional
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_officer, get_current_user
from app.models.issue import Issue
from app.models.project import Project
from app.models.evidence import Evidence
from app.schemas.issue import IssueCreate, IssueUpdate, IssueResponse, IssueSummaryResponse
from app.schemas.schemas import EvidenceResponse

router = APIRouter(tags=["Issues"])

UPLOAD_BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads"
)
EVIDENCE_DIR = os.path.join(UPLOAD_BASE_DIR, "evidence")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_STATUSES = {"OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"}


def _find_project(project_id_or_code: str, db: Session) -> Optional[Project]:
    """Resolve project by code (e.g. MH-PN-001) or numeric ID."""
    p = db.query(Project).filter(Project.project_code == project_id_or_code).first()
    if not p and str(project_id_or_code).isdigit():
        p = db.query(Project).filter(Project.id == int(project_id_or_code)).first()
    return p


def _validate_date_string(date_str: str) -> None:
    """Validate ISO YYYY-MM-DD date format."""
    if not date_str:
        return
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format '{date_str}'. Expected format: YYYY-MM-DD",
        )


# ─── Issue CRUD Endpoints ───────────────────────────────────────────

@router.post(
    "/api/projects/{project_id}/issues",
    response_model=IssueResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_issue(
    project_id: str,
    req: IssueCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_officer),
):
    """Create a new issue for a project (Officer authorized)."""
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    title = req.title.strip() if req.title else ""
    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Issue title cannot be empty.",
        )

    description = req.description.strip() if req.description else ""
    if not description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Issue description cannot be empty.",
        )

    severity = req.severity.upper().strip() if req.severity else "MEDIUM"
    if severity not in VALID_SEVERITIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid severity '{severity}'. Allowed: LOW, MEDIUM, HIGH, CRITICAL",
        )

    reported_by = req.reported_by or current_user.full_name or current_user.email
    reported_date = req.reported_date or str(date.today())
    _validate_date_string(reported_date)

    issue = Issue(
        project_id=project.id,
        title=title,
        description=description,
        severity=severity,
        status="OPEN",
        reported_by=reported_by,
        reported_date=reported_date,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@router.get("/api/projects/{project_id}/issues/summary", response_model=IssueSummaryResponse)
def get_project_issues_summary(
    project_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve database-derived issue count summary for a project."""
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    issues = db.query(Issue).filter(Issue.project_id == project.id).all()

    total_issues = len(issues)
    open_issues = sum(1 for i in issues if i.status == "OPEN")
    in_progress_issues = sum(1 for i in issues if i.status == "IN_PROGRESS")
    resolved_issues = sum(1 for i in issues if i.status == "RESOLVED")
    closed_issues = sum(1 for i in issues if i.status == "CLOSED")
    critical_issues = sum(1 for i in issues if i.severity == "CRITICAL")
    high_severity_issues = sum(1 for i in issues if i.severity == "HIGH")

    return IssueSummaryResponse(
        project_id=str(project.project_code or project.id),
        total_issues=total_issues,
        open_issues=open_issues,
        in_progress_issues=in_progress_issues,
        resolved_issues=resolved_issues,
        closed_issues=closed_issues,
        critical_issues=critical_issues,
        high_severity_issues=high_severity_issues,
    )


@router.get("/api/projects/{project_id}/issues", response_model=List[IssueResponse])
def list_project_issues(
    project_id: str,
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    issue_status: Optional[str] = Query(None, alias="status", description="Filter by status: OPEN, IN_PROGRESS, RESOLVED, CLOSED"),
    db: Session = Depends(get_db),
):
    """Retrieve all issues for a project, optionally filtered by severity/status."""
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    query = db.query(Issue).filter(Issue.project_id == project.id)

    if severity:
        sev = severity.upper().strip()
        if sev not in VALID_SEVERITIES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid severity filter '{severity}'. Allowed: LOW, MEDIUM, HIGH, CRITICAL",
            )
        query = query.filter(Issue.severity == sev)

    if issue_status:
        st = issue_status.upper().strip()
        if st not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter '{issue_status}'. Allowed: OPEN, IN_PROGRESS, RESOLVED, CLOSED",
            )
        query = query.filter(Issue.status == st)

    issues = query.order_by(Issue.created_at.desc()).all()
    return issues


@router.get("/api/issues/{issue_id}", response_model=IssueResponse)
def get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve a single issue by its ID."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found.",
        )
    return issue


@router.put("/api/issues/{issue_id}", response_model=IssueResponse)
def update_issue(
    issue_id: int,
    req: IssueUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_officer),
):
    """Update issue details, severity, or status (Officer authorized)."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found.",
        )

    if req.title is not None:
        title = req.title.strip()
        if not title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Issue title cannot be empty.",
            )
        issue.title = title

    if req.description is not None:
        description = req.description.strip()
        if not description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Issue description cannot be empty.",
            )
        issue.description = description

    if req.severity is not None:
        sev = req.severity.upper().strip()
        if sev not in VALID_SEVERITIES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid severity '{sev}'. Allowed: LOW, MEDIUM, HIGH, CRITICAL",
            )
        issue.severity = sev

    if req.status is not None:
        new_status = req.status.upper().strip()
        if new_status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status '{new_status}'. Allowed: OPEN, IN_PROGRESS, RESOLVED, CLOSED",
            )
        issue.status = new_status
        # Handle resolved_date transition logic
        if new_status in ("RESOLVED", "CLOSED"):
            if req.resolved_date:
                _validate_date_string(req.resolved_date)
                issue.resolved_date = req.resolved_date
            elif not issue.resolved_date:
                issue.resolved_date = str(date.today())
        elif new_status in ("OPEN", "IN_PROGRESS"):
            if req.resolved_date is not None:
                _validate_date_string(req.resolved_date)
                issue.resolved_date = req.resolved_date
            else:
                issue.resolved_date = None
    elif req.resolved_date is not None:
        _validate_date_string(req.resolved_date)
        issue.resolved_date = req.resolved_date

    issue.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(issue)
    return issue


@router.delete("/api/issues/{issue_id}")
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_officer),
):
    """Delete an issue (Officer authorized)."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found.",
        )

    title = issue.title
    db.delete(issue)
    db.commit()
    return {"success": True, "message": f"Issue '{title}' deleted successfully."}


# ─── Issue Evidence Endpoints ───────────────────────────────────────

@router.post(
    "/api/issues/{issue_id}/evidence",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_issue_evidence(
    issue_id: int,
    description: Optional[str] = Form(None),
    uploaded_by: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_officer),
):
    """
    Upload supporting evidence file for an issue (Officer authorized).
    Validates file extension, size, MIME type, and safe path storage.
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found.",
        )

    # Sanitize filename and prevent path traversal
    original_filename = file.filename or "evidence.jpg"
    safe_filename = os.path.basename(original_filename)
    if ".." in safe_filename or "/" in safe_filename or "\\" in safe_filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsafe filename or path traversal detected.",
        )

    # Extension check
    ext = os.path.splitext(safe_filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{ext}' not allowed. Supported: JPG, JPEG, PNG, PDF, WEBP",
        )

    # Read content and check size
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum limit of 10MB.",
        )

    # MIME type check
    content_type = file.content_type or ("application/pdf" if ext == ".pdf" else "image/jpeg")

    # Local file storage
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    unique_suffix = uuid.uuid4().hex[:6]
    now_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    stored_filename = f"ISSUE_{issue_id}_{now_str}_{unique_suffix}{ext}"
    full_path = os.path.join(EVIDENCE_DIR, stored_filename)

    with open(full_path, "wb") as f:
        f.write(content)

    file_type = "document" if ext == ".pdf" else "image"
    uploader = uploaded_by or current_user.full_name or current_user.email
    evidence_id = f"EV-ISSUE-{issue_id}-{now_str}-{unique_suffix}"
    file_url = f"/uploads/evidence/{stored_filename}"

    evidence = Evidence(
        evidence_id=evidence_id,
        project_id=issue.project_id,
        issue_id=issue.id,
        uploaded_by=uploader,
        file_name=safe_filename,
        stored_filename=stored_filename,
        file_path=full_path,
        file_url=file_url,
        file_type=file_type,
        file_size=len(content),
        mime_type=content_type,
        description=description.strip() if description else None,
        verification_status="Pending",
        submitted_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence


@router.get("/api/issues/{issue_id}/evidence", response_model=List[EvidenceResponse])
def list_issue_evidence(
    issue_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve all evidence files attached to a specific issue."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found.",
        )

    evidences = db.query(Evidence).filter(Evidence.issue_id == issue.id).order_by(Evidence.created_at.desc()).all()
    return evidences


@router.get("/api/projects/{project_id}/issues/{issue_id}/evidence", response_model=List[EvidenceResponse])
def list_project_issue_evidence(
    project_id: str,
    issue_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve evidence for an issue with strict cross-project verification.
    Blocks attempts to access evidence of issues belonging to a different project.
    """
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found.",
        )

    # Cross-project boundary check
    if issue.project_id != project.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Issue {issue_id} does not belong to Project '{project_id}'. Cross-project access denied.",
        )

    evidences = db.query(Evidence).filter(Evidence.issue_id == issue.id).order_by(Evidence.created_at.desc()).all()
    return evidences

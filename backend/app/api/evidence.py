"""
SetuX / VeriX — Evidence API Router
Phase 9: Enhanced Evidence Upload & Metadata Management

Endpoints:
- POST   /api/evidence/upload      — Upload real image files with metadata & progress for project
- GET    /api/evidence/{identifier} — Get single evidence by ID OR list all evidence for a project
- GET    /api/evidence/item/{id}   — Explicit single evidence lookup by ID
- DELETE /api/evidence/{id}        — Delete an evidence record and its file on disk
"""
import os
import uuid
import json
from typing import List, Optional, Union, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Evidence, Project, AuditLog
from app.schemas.schemas import EvidenceResponse
from app.services.image_analysis import extract_exif_data

router = APIRouter(prefix="/api/evidence", tags=["Evidence"])

UPLOAD_BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads"
)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _find_project(project_id_or_code: str, db: Session) -> Optional[Project]:
    """Resolve project by code (e.g. MH-PN-001) or numeric ID."""
    p = db.query(Project).filter(Project.project_code == project_id_or_code).first()
    if not p and str(project_id_or_code).isdigit():
        p = db.query(Project).filter(Project.id == int(project_id_or_code)).first()
    return p


def _find_evidence(evidence_id_or_id: str, db: Session) -> Optional[Evidence]:
    """Resolve evidence by string evidence_id or integer PK."""
    ev = db.query(Evidence).filter(Evidence.evidence_id == evidence_id_or_id).first()
    if not ev and str(evidence_id_or_id).isdigit():
        ev = db.query(Evidence).filter(Evidence.id == int(evidence_id_or_id)).first()
    return ev


@router.post("/upload", response_model=List[EvidenceResponse])
async def upload_evidence_files(
    project_id: str = Form(...),
    evidence_type: str = Form("Current / After Work"),
    reported_progress: int = Form(0),
    submitted_lat: Optional[float] = Form(None),
    submitted_lng: Optional[float] = Form(None),
    remarks: Optional[str] = Form(""),
    work_status: Optional[str] = Form("In Progress"),
    uploaded_by: Optional[str] = Form("Aarav Patil"),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload real evidence images/documents for a project, store them uniquely on disk,
    extract EXIF metadata, and associate with project.
    """
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per submission.")

    subfolder = "evidence"
    if "before" in evidence_type.lower():
        subfolder = "before"
    elif "after" in evidence_type.lower() or "current" in evidence_type.lower():
        subfolder = "after"

    target_dir = os.path.join(UPLOAD_BASE_DIR, subfolder)
    os.makedirs(target_dir, exist_ok=True)

    saved_evidences = []
    now_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    for idx, file in enumerate(files):
        filename = file.filename or "file.jpg"
        safe_name = os.path.basename(filename)
        if ".." in safe_name or "/" in safe_name or "\\" in safe_name:
            raise HTTPException(status_code=400, detail="Unsafe filename detected.")

        ext = os.path.splitext(safe_name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File {safe_name} has unsupported extension. Allowed: JPG, JPEG, PNG, WEBP, PDF"
            )

        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail=f"File {safe_name} is empty.")

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File {safe_name} exceeds maximum size limit of 10MB."
            )

        unique_id = uuid.uuid4().hex[:6]
        stored_filename = f"{project.project_code}_{now_str}_{idx+1:03d}_{unique_id}{ext}"
        file_path = os.path.join(target_dir, stored_filename)

        with open(file_path, "wb") as f:
            f.write(content)

        exif = {}
        if ext in {".jpg", ".jpeg", ".png", ".webp"}:
            try:
                exif = extract_exif_data(file_path)
            except Exception:
                exif = {}

        lat = submitted_lat or exif.get("latitude") or project.latitude
        lng = submitted_lng or exif.get("longitude") or project.longitude
        ts = exif.get("timestamp") or datetime.utcnow().strftime("%d %b %Y %H:%M")

        evidence_id = f"EV-{project.project_code}-{datetime.utcnow().strftime('%Y%m%d')}-{idx+1:02d}-{unique_id}"
        file_url = f"/uploads/{subfolder}/{stored_filename}"
        file_type = "document" if ext == ".pdf" else "image"

        db_evidence = Evidence(
            evidence_id=evidence_id,
            project_id=project.id,
            uploaded_by=uploaded_by,
            evidence_type=evidence_type,
            file_name=safe_name,
            stored_filename=stored_filename,
            file_path=file_path,
            file_url=file_url,
            file_type=file_type,
            file_size=len(content),
            mime_type=file.content_type or ("application/pdf" if ext == ".pdf" else "image/jpeg"),
            latitude=lat,
            longitude=lng,
            timestamp=ts,
            exif_metadata=json.dumps(exif) if exif else None,
            reported_progress=reported_progress,
            remarks=remarks,
            work_status=work_status,
            verification_status="Pending",
            submitted_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        db.add(db_evidence)
        saved_evidences.append(db_evidence)

    project.physical_progress = float(reported_progress)
    project.last_evidence_date = datetime.utcnow().strftime("%d %b %Y")

    audit = AuditLog(
        project_id=project.project_code,
        user_name=uploaded_by,
        action="UPLOAD_EVIDENCE",
        details=f"{uploaded_by} uploaded {len(saved_evidences)} {evidence_type} files for {project.project_code}",
        timestamp=datetime.utcnow()
    )
    db.add(audit)

    db.commit()
    for ev in saved_evidences:
        db.refresh(ev)

    return saved_evidences


@router.get("/item/{evidence_id}", response_model=EvidenceResponse)
def get_single_evidence(evidence_id: str, db: Session = Depends(get_db)):
    """Retrieve a single evidence record by string ID or integer PK."""
    ev = _find_evidence(evidence_id, db)
    if not ev:
        raise HTTPException(status_code=404, detail=f"Evidence '{evidence_id}' not found.")
    return ev


@router.get("/{identifier}", response_model=Union[EvidenceResponse, List[EvidenceResponse]])
def get_evidence(identifier: str, db: Session = Depends(get_db)):
    """
    Retrieve single evidence record if identifier matches evidence_id/ID,
    or list all evidence records for a project if identifier matches project_code/ID.
    """
    # 1. Try single evidence lookup first
    ev = _find_evidence(identifier, db)
    if ev:
        return ev

    # 2. Try project lookup
    project = _find_project(identifier, db)
    if project:
        return db.query(Evidence).filter(
            (Evidence.project_id == project.id) | (Evidence.project_id == project.project_code)
        ).order_by(Evidence.submitted_at.desc()).all()

    raise HTTPException(status_code=404, detail=f"Evidence or Project '{identifier}' not found.")


@router.delete("/{evidence_id}")
def delete_evidence(evidence_id: str, db: Session = Depends(get_db)):
    """Delete an evidence record and its file on disk."""
    ev = _find_evidence(evidence_id, db)
    if not ev:
        raise HTTPException(status_code=404, detail=f"Evidence '{evidence_id}' not found.")

    if ev.file_path and os.path.exists(ev.file_path):
        try:
            os.remove(ev.file_path)
        except Exception:
            pass

    key_id = ev.evidence_id or str(ev.id)
    db.delete(ev)
    db.commit()
    return {"success": True, "evidence_id": key_id}

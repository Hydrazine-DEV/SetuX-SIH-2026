"""
SetuX / VeriX — Reports & PDF Generation API Router
SIH26103: Integrated Government Project Monitoring & Intelligence Platform
Phase 17: Report Generation & PDF System

Endpoints:
- POST /api/projects/{project_id}/reports          — Generate PDF report for a project (Officer)
- GET  /api/projects/{project_id}/reports          — List all generated reports for a project
- GET  /api/reports/{report_id}                    — Retrieve report metadata
- GET  /api/reports/{report_id}/download           — Download/stream PDF report file
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_officer, get_current_user
from app.models.user import User
from app.models.report import Report
from app.schemas.report import (
    ReportCreate,
    ReportResponse,
    ReportListResponse,
)
from app.services.report_service import (
    generate_project_report,
    get_reports_for_project,
    get_report_by_id,
    get_report_file_path,
    _find_project,
)

router = APIRouter(tags=["Reports"])


def _to_report_response(r: Report) -> ReportResponse:
    """Helper to convert ORM model to Pydantic response."""
    p_code = r.project.project_code if r.project else None
    return ReportResponse(
        id=r.id,
        project_id=r.project_id,
        project_code=p_code,
        report_type=r.report_type,
        file_name=r.file_name,
        file_size=r.file_size or 0,
        status=r.status or "GENERATED",
        generated_by=r.generated_by,
        created_at=r.created_at,
        download_url=f"/api/reports/{r.id}/download",
    )


# ─── 1. Generate Report for Project (Officer Only) ───────────────
@router.post(
    "/api/projects/{project_id}/reports",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a Project PDF Report",
    description="Generate, render, store, and record a government-grade PDF report for a monitored project.",
)
def create_project_report(
    project_id: str,
    payload: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    try:
        report_rec = generate_project_report(
            project_id_or_code=project.id,
            report_type=payload.report_type,
            db=db,
            generated_by=current_user.email or current_user.full_name or "OFFICER",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation error: {str(e)}",
        )

    return _to_report_response(report_rec)


# ─── 2. List Reports for Project ─────────────────────────────────
@router.get(
    "/api/projects/{project_id}/reports",
    response_model=List[ReportResponse],
    summary="List Generated Reports for a Project",
    description="Retrieve all previously generated PDF reports for a project.",
)
def list_project_reports(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    reports = get_reports_for_project(project.id, db)
    return [_to_report_response(r) for r in reports]


# ─── 3. Get Report Metadata ─────────────────────────────────────
@router.get(
    "/api/reports/{report_id}",
    response_model=ReportResponse,
    summary="Get Single Report Metadata",
    description="Retrieve database record and metadata for a specific report ID.",
)
def get_single_report_metadata(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = get_report_by_id(report_id, db)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found.",
        )
    return _to_report_response(report)


# ─── 4. Download Report PDF File ────────────────────────────────
@router.get(
    "/api/reports/{report_id}/download",
    summary="Download Generated PDF Report",
    description="Stream the generated PDF report with appropriate content headers.",
)
def download_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = get_report_by_id(report_id, db)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found.",
        )

    try:
        file_path = get_report_file_path(report_id, db)
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: unsafe path detected.",
        )

    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Physical PDF report file not found on disk.",
        )

    download_filename = report.file_name or f"SetuX_Report_{report.id}.pdf"
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=download_filename,
    )

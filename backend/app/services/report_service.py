"""
SetuX / VeriX — Report Generation Service Layer
SIH26103: Integrated Government Project Monitoring & Intelligence Platform
Phase 17: Report Generation & PDF System

Orchestrates:
- Project Telemetry & Database Record Extraction
- Risk Intelligence & Phase 11 Rule Engine Integration
- Phase 13/14 Machine Learning Forecasts
- Phase 16 Early Warning Alerts
- PDF Generation & Storage in uploads/reports/
- Report Database Tracking & Path Security Validation
"""
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.project import Project
from app.models.milestone import Milestone
from app.models.progress import ProgressUpdate
from app.models.issue import Issue
from app.models.alert import Alert
from app.models.report import Report

from app.services.report_config import ReportType
from app.services.risk_intelligence import generate_overall_project_risk_intelligence
from app.services.cost_analysis import calculate_cost_overrun
from app.services.schedule_analysis import calculate_project_delay
from app.services.pdf_generator import (
    build_project_summary_pdf,
    build_risk_assessment_pdf,
    build_early_warning_pdf,
    build_executive_report_pdf,
)

# ─── Storage Directory ──────────────────────────────────────────
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(BACKEND_ROOT, "uploads", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def _find_project(project_id_or_code: Any, db: Session) -> Optional[Project]:
    """Locate a project by numeric ID or string project_code."""
    if isinstance(project_id_or_code, int) or (isinstance(project_id_or_code, str) and project_id_or_code.isdigit()):
        p = db.query(Project).filter(Project.id == int(project_id_or_code)).first()
        if p:
            return p
    return db.query(Project).filter(Project.project_code == str(project_id_or_code)).first()


def _sanitize_filename(name: str) -> str:
    """Sanitize string to prevent path traversal and unsafe characters."""
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', name)


def _gather_report_data(project: Project, db: Session) -> Dict[str, Any]:
    """Gather all raw project data and existing service metrics without recalculating."""
    milestones = db.query(Milestone).filter(Milestone.project_id == project.id).order_by(Milestone.id).all()
    progress_updates = db.query(ProgressUpdate).filter(ProgressUpdate.project_id == project.id).order_by(desc(ProgressUpdate.id)).all()
    issues = db.query(Issue).filter(Issue.project_id == project.id).order_by(desc(Issue.id)).all()
    alerts = db.query(Alert).filter(Alert.project_id == project.id).order_by(desc(Alert.created_at)).all()

    # Risk Intelligence
    risk_intel = generate_overall_project_risk_intelligence(project.id, db)

    # Cost calculation from existing service
    orig = float(project.original_cost or 0.0)
    rev = float(project.revised_cost if project.revised_cost is not None else orig)
    exp = float(project.total_expenditure or 0.0)
    cost_res = calculate_cost_overrun(orig, rev, exp)

    # Schedule delay from existing service
    sched_res = calculate_project_delay(
        planned_date_str=project.planned_completion_date,
        revised_date_str=project.revised_completion_date,
        actual_date_str=project.actual_completion_date,
        status=project.status,
    )

    return {
        "project": {
            "id": project.id,
            "project_code": project.project_code,
            "name": project.name,
            "department_name": project.department_name,
            "sector": project.sector,
            "district": project.district,
            "taluka": project.taluka,
            "state": project.state,
            "location": project.location,
            "contractor_name": project.contractor_name,
            "status": project.status,
            "original_cost": project.original_cost,
            "revised_cost": project.revised_cost,
            "total_expenditure": project.total_expenditure,
            "financial_progress": project.financial_progress,
            "physical_progress": project.physical_progress,
            "start_date": project.start_date,
            "planned_completion_date": project.planned_completion_date,
            "revised_completion_date": project.revised_completion_date,
            "actual_completion_date": project.actual_completion_date,
            "schedule_status": "Delayed" if sched_res.get("is_delayed") else "On Schedule",
            "delay_days": sched_res.get("delay_days", 0),
        },
        "cost_overrun_pct": cost_res.get("cost_overrun_pct"),
        "milestones": [
            {
                "id": m.id,
                "name": m.name,
                "planned_date": m.planned_date,
                "status": m.status,
                "completion_percentage": m.completion_percentage,
            }
            for m in milestones
        ],
        "progress_updates": [
            {
                "id": p.id,
                "reported_by": p.reported_by,
                "report_date": p.report_date,
                "physical_progress": p.physical_progress,
                "financial_progress": p.financial_progress,
                "remarks": p.remarks,
            }
            for p in progress_updates
        ],
        "issues": [
            {
                "id": i.id,
                "title": i.title,
                "severity": i.severity,
                "status": i.status,
                "reported_date": i.reported_date,
            }
            for i in issues
        ],
        "alerts": [
            {
                "id": a.id,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "status": a.status,
                "source": a.source,
                "title": a.title,
                "message": a.message,
                "risk_score": a.risk_score,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in alerts
        ],
        "risk_intelligence": risk_intel,
    }


def generate_project_report(
    project_id_or_code: Any,
    report_type: str,
    db: Session,
    generated_by: str = "SYSTEM_OFFICER",
) -> Report:
    """
    Generate, render, store, and record a project PDF report.
    """
    project = _find_project(project_id_or_code, db)
    if not project:
        raise ValueError(f"Project '{project_id_or_code}' not found.")

    r_type_upper = report_type.upper().strip()
    valid_types = [t.value for t in ReportType]
    if r_type_upper not in valid_types:
        raise ValueError(f"Invalid report type '{report_type}'. Allowed types: {', '.join(valid_types)}")

    # 1. Gather all structured telemetry
    report_data = _gather_report_data(project, db)

    # 2. Build sanitized filename and filesystem path
    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    clean_code = _sanitize_filename(project.project_code or f"PROJ_{project.id}")
    file_name = f"{clean_code}_{r_type_upper}_{timestamp_str}.pdf"
    file_path = os.path.join(REPORTS_DIR, file_name)

    # 3. Render appropriate PDF based on report type
    if r_type_upper == ReportType.PROJECT_SUMMARY.value:
        build_project_summary_pdf(report_data, file_path)
    elif r_type_upper == ReportType.RISK_ASSESSMENT.value:
        build_risk_assessment_pdf(report_data, file_path)
    elif r_type_upper == ReportType.EARLY_WARNING.value:
        build_early_warning_pdf(report_data, file_path)
    elif r_type_upper == ReportType.EXECUTIVE_PROJECT_REPORT.value:
        build_executive_report_pdf(report_data, file_path)

    # 4. Compute file size
    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

    # 5. Persist Report record in database
    report_record = Report(
        project_id=project.id,
        generated_by=generated_by,
        report_type=r_type_upper,
        file_path=file_path,
        file_name=file_name,
        file_size=file_size,
        status="GENERATED",
        created_at=datetime.utcnow(),
    )
    db.add(report_record)
    db.commit()
    db.refresh(report_record)

    return report_record


def get_reports_for_project(project_id_or_code: Any, db: Session) -> List[Report]:
    """Retrieve all generated reports for a specific project."""
    project = _find_project(project_id_or_code, db)
    if not project:
        return []
    return db.query(Report).filter(Report.project_id == project.id).order_by(desc(Report.created_at)).all()


def get_report_by_id(report_id: int, db: Session) -> Optional[Report]:
    """Retrieve a single report by ID."""
    return db.query(Report).filter(Report.id == report_id).first()


def get_report_file_path(report_id: int, db: Session) -> Optional[str]:
    """
    Safely retrieve the physical file path of a report with path traversal validation.
    """
    report = get_report_by_id(report_id, db)
    if not report or not report.file_path:
        return None

    # Resolve canonical paths and verify the file lives strictly within REPORTS_DIR
    resolved_path = os.path.abspath(report.file_path)
    reports_base = os.path.abspath(REPORTS_DIR)

    if not resolved_path.startswith(reports_base):
        raise PermissionError("Access denied: invalid file path.")

    if not os.path.exists(resolved_path):
        return None

    return resolved_path

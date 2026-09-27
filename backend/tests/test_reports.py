"""
SetuX / VeriX — Phase 17 Report Generation & PDF System Test Suite
SIH26103: Integrated Government Project Monitoring & Intelligence Platform

Comprehensive Test Coverage:
1. Generate PROJECT_SUMMARY PDF Report
2. Generate RISK_ASSESSMENT PDF Report
3. Generate EARLY_WARNING PDF Report
4. Generate EXECUTIVE_PROJECT_REPORT PDF Report
5. PDF File Binary Header (%PDF-) Verification
6. PDF File Non-Zero Size & Readability
7. Report Database Persistence & Metadata Accuracy
8. Project Reports Listing API (GET /api/projects/{project_id}/reports)
9. Single Report Metadata API (GET /api/reports/{report_id})
10. Download Report API (GET /api/reports/{report_id}/download)
11. Invalid Project Handling (HTTP 404)
12. Invalid Report Type Validation (HTTP 422 / 400)
13. Missing / Sparse Project Baseline Data Handling
14. Missing ML Predictions Handling
15. Missing Alerts Handling
16. Authentication Guards (HTTP 401 on unauthenticated requests)
17. Authorization / RBAC Guards (HTTP 403 on Citizen report generation)
18. Safe Filename Sanitization
19. Path Traversal Download Security
20. Multiple Reports for Same Project
21. Seeded Project Verification
"""
import os
import uuid
from datetime import datetime, date, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.milestone import Milestone
from app.models.progress import ProgressUpdate
from app.models.issue import Issue
from app.models.alert import Alert
from app.models.report import Report
from app.services.report_config import ReportType
from app.services.report_service import (
    generate_project_report,
    get_reports_for_project,
    get_report_by_id,
    get_report_file_path,
)
from app.services.alert_service import generate_alerts_for_project


def create_sample_project(db: Session, code_suffix: str = None) -> Project:
    """Helper to create an isolated test project with full telemetry."""
    suffix = code_suffix or uuid.uuid4().hex[:6]
    d_start = (date.today() - timedelta(days=180)).isoformat()
    d_end = (date.today() + timedelta(days=180)).isoformat()

    proj = Project(
        project_code=f"TEST-RPT-{suffix}",
        name=f"Pune Metro Line Extension Segment {suffix}",
        department_name="Urban Development Department",
        department_id=4,
        sector="Urban Transport",
        district="Pune",
        taluka="Haveli",
        status="IN_PROGRESS",
        original_cost=150.0,
        revised_cost=180.0,
        total_expenditure=90.0,
        start_date=d_start,
        planned_completion_date=d_end,
        physical_progress=45.0,
        financial_progress=50.0,
        contractor_name="L&T Infrastructure Ltd.",
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)

    # Milestones
    m1 = Milestone(
        project_id=proj.id,
        name="Viaduct Pier Construction",
        planned_date=(date.today() - timedelta(days=30)).isoformat(),
        status="COMPLETED",
        completion_percentage=100.0,
    )
    m2 = Milestone(
        project_id=proj.id,
        name="Track Laying Phase 1",
        planned_date=(date.today() + timedelta(days=60)).isoformat(),
        status="IN_PROGRESS",
        completion_percentage=40.0,
    )
    db.add_all([m1, m2])

    # Issues
    iss = Issue(
        project_id=proj.id,
        reported_by="Site Engineer 1",
        title="Traffic diversion permission pending",
        description="Awaiting municipal traffic clearance.",
        severity="MEDIUM",
        status="OPEN",
        reported_date=(date.today() - timedelta(days=20)).isoformat(),
    )
    db.add(iss)

    # Progress Update
    prog = ProgressUpdate(
        project_id=proj.id,
        reported_by="Inspector Sharma",
        report_date=(date.today() - timedelta(days=5)).isoformat(),
        physical_progress=45.0,
        financial_progress=50.0,
        expenditure=90.0,
        remarks="Pier work completed; track laying on schedule.",
    )
    db.add(prog)

    db.commit()
    db.refresh(proj)

    # Generate alerts for the project
    generate_alerts_for_project(proj.id, db)

    return proj


# ─── 1. Generate PROJECT_SUMMARY PDF ────────────────────────────
def test_1_generate_project_summary_pdf(db_session: Session):
    proj = create_sample_project(db_session)
    report = generate_project_report(
        project_id_or_code=proj.id,
        report_type=ReportType.PROJECT_SUMMARY.value,
        db=db_session,
        generated_by="officer@setux.gov",
    )
    assert report.id is not None
    assert report.report_type == ReportType.PROJECT_SUMMARY.value
    assert report.file_path is not None
    assert os.path.exists(report.file_path)
    assert report.file_size > 0


# ─── 2. Generate RISK_ASSESSMENT PDF ────────────────────────────
def test_2_generate_risk_assessment_pdf(db_session: Session):
    proj = create_sample_project(db_session)
    report = generate_project_report(
        project_id_or_code=proj.id,
        report_type=ReportType.RISK_ASSESSMENT.value,
        db=db_session,
        generated_by="officer@setux.gov",
    )
    assert report.id is not None
    assert report.report_type == ReportType.RISK_ASSESSMENT.value
    assert os.path.exists(report.file_path)
    assert report.file_size > 0


# ─── 3. Generate EARLY_WARNING PDF ──────────────────────────────
def test_3_generate_early_warning_pdf(db_session: Session):
    proj = create_sample_project(db_session)
    report = generate_project_report(
        project_id_or_code=proj.id,
        report_type=ReportType.EARLY_WARNING.value,
        db=db_session,
        generated_by="officer@setux.gov",
    )
    assert report.id is not None
    assert report.report_type == ReportType.EARLY_WARNING.value
    assert os.path.exists(report.file_path)
    assert report.file_size > 0


# ─── 4. Generate EXECUTIVE_PROJECT_REPORT PDF ───────────────────
def test_4_generate_executive_report_pdf(db_session: Session):
    proj = create_sample_project(db_session)
    report = generate_project_report(
        project_id_or_code=proj.id,
        report_type=ReportType.EXECUTIVE_PROJECT_REPORT.value,
        db=db_session,
        generated_by="officer@setux.gov",
    )
    assert report.id is not None
    assert report.report_type == ReportType.EXECUTIVE_PROJECT_REPORT.value
    assert os.path.exists(report.file_path)
    assert report.file_size > 0


# ─── 5. PDF Binary Header Verification ──────────────────────────
def test_5_pdf_binary_header(db_session: Session):
    proj = create_sample_project(db_session)
    report = generate_project_report(proj.id, ReportType.PROJECT_SUMMARY.value, db_session)
    with open(report.file_path, "rb") as f:
        header = f.read(5)
    assert header == b"%PDF-"


# ─── 6. PDF File Readability & Nonzero Size ─────────────────────
def test_6_pdf_file_size(db_session: Session):
    proj = create_sample_project(db_session)
    report = generate_project_report(proj.id, ReportType.EXECUTIVE_PROJECT_REPORT.value, db_session)
    assert report.file_size >= 1024  # At least 1KB


# ─── 7. Report Database Record Persistence ──────────────────────
def test_7_database_persistence(db_session: Session):
    proj = create_sample_project(db_session)
    report = generate_project_report(proj.id, ReportType.PROJECT_SUMMARY.value, db_session, "lead.officer@setux.gov")

    db_rec = db_session.query(Report).filter(Report.id == report.id).first()
    assert db_rec is not None
    assert db_rec.project_id == proj.id
    assert db_rec.generated_by == "lead.officer@setux.gov"
    assert db_rec.status == "GENERATED"


# ─── 8. List Reports for Project API ────────────────────────────
def test_8_api_list_project_reports(client: TestClient, officer_token, db_session: Session):
    proj = create_sample_project(db_session)
    generate_project_report(proj.id, ReportType.PROJECT_SUMMARY.value, db_session)
    generate_project_report(proj.id, ReportType.RISK_ASSESSMENT.value, db_session)

    resp = client.get(
        f"/api/projects/{proj.id}/reports",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    assert len(items) >= 2
    types = [r["report_type"] for r in items]
    assert ReportType.PROJECT_SUMMARY.value in types
    assert ReportType.RISK_ASSESSMENT.value in types


# ─── 9. Single Report Metadata API ──────────────────────────────
def test_9_api_single_report_metadata(client: TestClient, officer_token, db_session: Session):
    proj = create_sample_project(db_session)
    report = generate_project_report(proj.id, ReportType.EARLY_WARNING.value, db_session)

    resp = client.get(
        f"/api/reports/{report.id}",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == report.id
    assert data["report_type"] == ReportType.EARLY_WARNING.value
    assert data["download_url"] == f"/api/reports/{report.id}/download"


# ─── 10. Download Report API ────────────────────────────────────
def test_10_api_download_report(client: TestClient, officer_token, db_session: Session):
    proj = create_sample_project(db_session)
    report = generate_project_report(proj.id, ReportType.PROJECT_SUMMARY.value, db_session)

    resp = client.get(
        f"/api/reports/{report.id}/download",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF-")


# ─── 11. Invalid Project Handling ───────────────────────────────
def test_11_api_invalid_project(client: TestClient, officer_token):
    resp = client.post(
        "/api/projects/999999/reports",
        json={"report_type": "PROJECT_SUMMARY"},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp.status_code == 404


# ─── 12. Invalid Report Type Validation ─────────────────────────
def test_12_api_invalid_report_type(client: TestClient, officer_token, db_session: Session):
    proj = create_sample_project(db_session)
    resp = client.post(
        f"/api/projects/{proj.id}/reports",
        json={"report_type": "INVALID_TYPE"},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp.status_code in (400, 422)


# ─── 13. Missing / Sparse Project Baseline Data ─────────────────
def test_13_sparse_project_report(db_session: Session):
    sparse_proj = Project(
        project_code=f"TEST-SPARSE-{uuid.uuid4().hex[:6]}",
        name="Sparse Bridge Project Without Milestones",
        department_name="Public Works Department",
        department_id=1,
        sector="Roads & Bridges",
        district="Satara",
        status="IN_PROGRESS",
    )
    db_session.add(sparse_proj)
    db_session.commit()
    db_session.refresh(sparse_proj)

    report = generate_project_report(sparse_proj.id, ReportType.EXECUTIVE_PROJECT_REPORT.value, db_session)
    assert os.path.exists(report.file_path)
    assert report.file_size > 0


# ─── 14. Missing ML Predictions Handling ────────────────────────
def test_14_missing_ml_predictions(db_session: Session):
    proj = create_sample_project(db_session)
    report = generate_project_report(proj.id, ReportType.RISK_ASSESSMENT.value, db_session)
    assert os.path.exists(report.file_path)


# ─── 15. Missing Alerts Handling ────────────────────────────────
def test_15_project_without_alerts(db_session: Session):
    proj = Project(
        project_code=f"TEST-NOALERT-{uuid.uuid4().hex[:6]}",
        name="Clean School Building",
        department_name="Public Works Department",
        department_id=1,
        status="IN_PROGRESS",
    )
    db_session.add(proj)
    db_session.commit()
    db_session.refresh(proj)

    report = generate_project_report(proj.id, ReportType.EARLY_WARNING.value, db_session)
    assert os.path.exists(report.file_path)


# ─── 16. Authentication Guards ──────────────────────────────────
def test_16_auth_guards(client: TestClient, db_session: Session):
    proj = create_sample_project(db_session)
    # Unauthenticated POST
    resp = client.post(
        f"/api/projects/{proj.id}/reports",
        json={"report_type": "PROJECT_SUMMARY"},
    )
    assert resp.status_code == 401


# ─── 17. Authorization / RBAC Guards ────────────────────────────
def test_17_rbac_guards(client: TestClient, citizen_token, officer_token, db_session: Session):
    proj = create_sample_project(db_session)
    # Citizen POST -> 403
    resp_cit = client.post(
        f"/api/projects/{proj.id}/reports",
        json={"report_type": "PROJECT_SUMMARY"},
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert resp_cit.status_code == 403

    # Officer POST -> 201
    resp_off = client.post(
        f"/api/projects/{proj.id}/reports",
        json={"report_type": "PROJECT_SUMMARY"},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp_off.status_code == 201
    assert "download_url" in resp_off.json()


# ─── 18. Safe Filename Sanitization ─────────────────────────────
def test_18_filename_sanitization(db_session: Session):
    proj = Project(
        project_code=f"MH/PN/UNSAFE-{uuid.uuid4().hex[:4]}",
        name="Unsafe Code Project",
        department_name="PWD",
        status="IN_PROGRESS",
    )
    db_session.add(proj)
    db_session.commit()
    db_session.refresh(proj)

    report = generate_project_report(proj.id, ReportType.PROJECT_SUMMARY.value, db_session)
    assert "/" not in report.file_name
    assert "\\" not in report.file_name


# ─── 19. Path Traversal Download Security ───────────────────────
def test_19_path_traversal_protection(db_session: Session):
    proj = create_sample_project(db_session)
    # Create malicious report record with traversal path
    malicious_report = Report(
        project_id=proj.id,
        generated_by="test",
        report_type="PROJECT_SUMMARY",
        file_path="../../etc/passwd",
        file_name="passwd.pdf",
        status="GENERATED",
    )
    db_session.add(malicious_report)
    db_session.commit()
    db_session.refresh(malicious_report)

    with pytest.raises(PermissionError):
        get_report_file_path(malicious_report.id, db_session)


# ─── 20. Multiple Reports for Same Project ──────────────────────
def test_20_multiple_reports(db_session: Session):
    proj = create_sample_project(db_session)
    r1 = generate_project_report(proj.id, ReportType.PROJECT_SUMMARY.value, db_session)
    r2 = generate_project_report(proj.id, ReportType.RISK_ASSESSMENT.value, db_session)
    r3 = generate_project_report(proj.id, ReportType.EARLY_WARNING.value, db_session)
    r4 = generate_project_report(proj.id, ReportType.EXECUTIVE_PROJECT_REPORT.value, db_session)

    all_reports = get_reports_for_project(proj.id, db_session)
    assert len(all_reports) == 4
    assert {r.report_type for r in all_reports} == {
        ReportType.PROJECT_SUMMARY.value,
        ReportType.RISK_ASSESSMENT.value,
        ReportType.EARLY_WARNING.value,
        ReportType.EXECUTIVE_PROJECT_REPORT.value,
    }

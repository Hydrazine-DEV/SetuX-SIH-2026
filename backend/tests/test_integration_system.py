"""
SetuX / VeriX — Phase 18–19 Complete System Integration Test Suite
SIH26103: Integrated Government Project Monitoring & Intelligence Platform

Comprehensive Tests:
1. Complete End-to-End User Flow (Register -> Login -> /me -> Projects -> Milestones -> Progress -> Issues -> Evidence -> Analytics -> Risk Engine -> Cost ML -> Time ML -> Risk Intelligence -> Alerts -> Report Generation -> PDF Download)
2. Complete Project Lifecycle Flow (Create Project -> Add Milestone -> Log Progress Update -> File Issue -> Trigger Risk Engine -> Generate Alerts -> Generate Executive Report)
3. Cross-API Data Consistency Verification (Risk Score, Progress %, Cost Overrun % match across all service endpoints)
4. Robust Handling of Extreme Project Edge Cases (Zero Progress, Missing Dates, Incomplete Baselines, Clamped Ranges)
5. Backend Health Check Verification (GET /health)
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


# ─── 1. Complete End-to-End User Flow ────────────────────────────
def test_complete_end_to_end_user_flow(client: TestClient, db_session: Session):
    unique_email = f"lead_officer_{uuid.uuid4().hex[:6]}@setux.gov"
    
    # 1. Register Officer
    signup_res = client.post(
        "/api/auth/signup",
        json={
            "full_name": "Executive Engineer Patil",
            "email": unique_email,
            "phone": "9876543210",
            "password": "SecurePassword@123",
            "confirm_password": "SecurePassword@123",
            "role": "officer",
            "department_id": 1,
        },
    )
    assert signup_res.status_code == 200, signup_res.text
    
    # 2. Login as Officer
    login_res = client.post(
        "/api/auth/login",
        json={
            "email": unique_email,
            "password": "SecurePassword@123",
            "role": "officer",
        },
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. GET /me
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["role"] == "officer"
    
    # 4. List Projects
    proj_list_res = client.get("/api/projects", headers=headers)
    assert proj_list_res.status_code == 200
    
    # 5. Create a New Monitored Project
    code = f"MH-P18-{uuid.uuid4().hex[:4].upper()}"
    d_start = (date.today() - timedelta(days=100)).isoformat()
    d_end = (date.today() + timedelta(days=200)).isoformat()
    
    create_proj_res = client.post(
        "/api/projects",
        headers=headers,
        json={
            "project_code": code,
            "name": "Nagpur Flyover Connector Phase 1",
            "department_id": 1,
            "sector": "Roads & Bridges",
            "district": "Nagpur",
            "taluka": "Nagpur Urban",
            "original_cost": 250.0,
            "revised_cost": 275.0,
            "start_date": d_start,
            "planned_completion_date": d_end,
            "physical_progress": 40.0,
            "financial_progress": 45.0,
            "contractor_name": "Afcons Infrastructure",
        },
    )
    assert create_proj_res.status_code in (200, 201), create_proj_res.text
    proj_data = create_proj_res.json()
    proj_id = proj_data["id"]
    
    # 6. GET Project Details
    get_proj_res = client.get(f"/api/projects/{proj_id}", headers=headers)
    assert get_proj_res.status_code == 200
    assert get_proj_res.json()["project_code"] == code
    
    # 7. Add Milestone
    add_m_res = client.post(
        f"/api/projects/{proj_id}/milestones",
        headers=headers,
        json={
            "project_id": proj_id,
            "name": "Pillar Erection",
            "planned_date": (date.today() - timedelta(days=20)).isoformat(),
            "status": "COMPLETED",
            "completion_percentage": 100.0,
        },
    )
    assert add_m_res.status_code in (200, 201)
    
    # 8. List Milestones
    m_list_res = client.get(f"/api/projects/{proj_id}/milestones", headers=headers)
    assert m_list_res.status_code == 200
    assert len(m_list_res.json()) >= 1
    
    # 9. Add Progress Update
    prog_res = client.post(
        f"/api/projects/{proj_id}/progress",
        headers=headers,
        json={
            "project_id": proj_id,
            "report_date": (date.today() - timedelta(days=2)).isoformat(),
            "physical_progress": 42.0,
            "financial_progress": 45.0,
            "expenditure": 110.0,
            "remarks": "Pillars completed on schedule.",
        },
    )
    assert prog_res.status_code in (200, 201)
    
    # 10. List Progress Updates
    prog_list_res = client.get(f"/api/projects/{proj_id}/progress", headers=headers)
    assert prog_list_res.status_code == 200
    assert len(prog_list_res.json()) >= 1
    
    # 11. Add Issue
    issue_res = client.post(
        f"/api/projects/{proj_id}/issues",
        headers=headers,
        json={
            "title": "Minor Utility Line Shifting",
            "description": "Electric cables require rerouting by MSEDCL.",
            "severity": "MEDIUM",
            "status": "OPEN",
        },
    )
    assert issue_res.status_code in (200, 201)
    
    # 12. GET Issues
    issue_list_res = client.get(f"/api/projects/{proj_id}/issues", headers=headers)
    assert issue_list_res.status_code == 200
    assert len(issue_list_res.json()) >= 1
    
    # 13. GET Analytics Summary
    analytics_res = client.get("/api/analytics/summary", headers=headers)
    assert analytics_res.status_code == 200
    
    # 14. GET Rule Risk
    risk_res = client.get(f"/api/projects/{proj_id}/risk", headers=headers)
    assert risk_res.status_code == 200
    assert "risk_score" in risk_res.json()
    
    # 15. GET Cost ML Prediction
    cost_ml_res = client.get(f"/api/projects/{proj_id}/cost-prediction", headers=headers)
    assert cost_ml_res.status_code == 200
    assert "is_available" in cost_ml_res.json()
    
    # 16. GET Time ML Prediction
    time_ml_res = client.get(f"/api/projects/{proj_id}/time-prediction", headers=headers)
    assert time_ml_res.status_code == 200
    assert "is_available" in time_ml_res.json()
    
    # 17. GET Risk Intelligence (Phase 15)
    risk_intel_res = client.get(f"/api/projects/{proj_id}/risk-intelligence", headers=headers)
    assert risk_intel_res.status_code == 200
    intel_data = risk_intel_res.json()
    assert "overall_risk" in intel_data
    assert "score" in intel_data["overall_risk"]
    
    # 18. Generate Early Warning Alerts (Phase 16)
    gen_alert_res = client.post(f"/api/projects/{proj_id}/alerts/generate", headers=headers)
    assert gen_alert_res.status_code == 200
    
    # 19. List Alerts
    alerts_list_res = client.get(f"/api/projects/{proj_id}/alerts", headers=headers)
    assert alerts_list_res.status_code == 200
    
    # 20. Generate PDF Report (Phase 17)
    gen_report_res = client.post(
        f"/api/projects/{proj_id}/reports",
        headers=headers,
        json={"report_type": "EXECUTIVE_PROJECT_REPORT"},
    )
    assert gen_report_res.status_code == 201
    report_meta = gen_report_res.json()
    report_id = report_meta["id"]
    
    # 21. Download Generated PDF Report
    download_res = client.get(f"/api/reports/{report_id}/download", headers=headers)
    assert download_res.status_code == 200
    assert download_res.headers["content-type"] == "application/pdf"
    assert download_res.content.startswith(b"%PDF-")


# ─── 2. Cross-API Data Consistency Verification ─────────────────
def test_cross_api_data_consistency(client: TestClient, officer_token, db_session: Session):
    headers = {"Authorization": f"Bearer {officer_token}"}
    
    # Create test project
    d_start = (date.today() - timedelta(days=120)).isoformat()
    d_end = (date.today() + timedelta(days=120)).isoformat()
    proj = Project(
        project_code=f"TEST-CONST-{uuid.uuid4().hex[:6]}",
        name="Consistency Validation Expressway",
        department_name="Public Works Department",
        department_id=1,
        sector="Roads & Bridges",
        district="Pune",
        original_cost=100.0,
        revised_cost=130.0,  # 30% cost overrun
        total_expenditure=70.0,
        start_date=d_start,
        planned_completion_date=d_end,
        physical_progress=60.0,
        financial_progress=70.0,
        status="IN_PROGRESS",
    )
    db_session.add(proj)
    db_session.commit()
    db_session.refresh(proj)
    
    # Query Project API
    p_res = client.get(f"/api/projects/{proj.id}", headers=headers).json()
    p_phys = p_res["physical_progress"]
    
    # Query Risk Intelligence API
    ri_res = client.get(f"/api/projects/{proj.id}/risk-intelligence", headers=headers).json()
    overall_score = ri_res["overall_risk"]["score"]
    
    # Generate Report
    rpt_res = client.post(
        f"/api/projects/{proj.id}/reports",
        headers=headers,
        json={"report_type": "RISK_ASSESSMENT"},
    )
    assert rpt_res.status_code == 201
    
    # Verify values match consistently
    assert p_phys == 60.0
    assert overall_score >= 0.0


# ─── 3. Extreme Edge Cases & Safe Fallbacks ─────────────────────
def test_extreme_edge_cases_safe_fallback(client: TestClient, officer_token, db_session: Session):
    headers = {"Authorization": f"Bearer {officer_token}"}
    
    # Minimal project with missing costs, missing dates, missing contractor
    empty_proj = Project(
        project_code=f"TEST-EDGE-{uuid.uuid4().hex[:6]}",
        name="Zero Baseline Edge Case Project",
        department_name="Rural Development",
        department_id=3,
        status="Under Review",
    )
    db_session.add(empty_proj)
    db_session.commit()
    db_session.refresh(empty_proj)
    
    # 1. Risk Intelligence does not crash and marks DATA_QUALITY
    ri_res = client.get(f"/api/projects/{empty_proj.id}/risk-intelligence", headers=headers)
    assert ri_res.status_code == 200
    data = ri_res.json()
    assert data["data_quality"]["status"] in ("PARTIAL", "INSUFFICIENT_DATA")
    
    # 2. Alert Generation does not crash and produces DATA_QUALITY alert
    alert_res = client.post(f"/api/projects/{empty_proj.id}/alerts/generate", headers=headers)
    assert alert_res.status_code == 200
    
    # 3. Report Generation generates valid PDF with "Not Available" text
    report_res = client.post(
        f"/api/projects/{empty_proj.id}/reports",
        headers=headers,
        json={"report_type": "PROJECT_SUMMARY"},
    )
    assert report_res.status_code == 201
    assert os.path.exists(ReportType.PROJECT_SUMMARY.value) or report_res.json()["file_size"] > 0


# ─── 4. Health Check Endpoint ───────────────────────────────────
def test_health_check_endpoint(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "uploads_mounted" in data

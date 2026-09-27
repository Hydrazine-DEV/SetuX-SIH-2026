"""
SetuX / VeriX — Phase 16 Early Warning & Alert System Test Suite
SIH26103: Integrated Government Project Monitoring & Intelligence Platform
"""
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
from app.services.alert_config import AlertStatus, AlertSeverity, AlertType, AlertSource
from app.services.alert_service import (
    generate_alerts_for_project,
    get_alerts,
    get_alert_by_id,
    update_alert_status,
)


def create_sample_high_risk_project(db: Session, code_suffix: str = None) -> Project:
    suffix = code_suffix or uuid.uuid4().hex[:6]
    d_start = (date.today() - timedelta(days=200)).isoformat()
    d_end = (date.today() - timedelta(days=50)).isoformat()

    proj = Project(
        project_code=f"TEST-EW-{suffix}",
        name=f"Thane Coastal Highway Link {suffix}",
        department_name="Public Works Department",
        department_id=1,
        sector="Roads & Bridges",
        district="Thane",
        taluka="Thane",
        status="DELAYED",
        original_cost=50.0,
        revised_cost=75.0,  # 50% cost overrun
        start_date=d_start,
        planned_completion_date=d_end,
        physical_progress=30.0,
        financial_progress=60.0,
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)

    # Add delayed milestones
    m1_date = (date.today() - timedelta(days=60)).isoformat()
    m2_date = (date.today() - timedelta(days=30)).isoformat()
    m1 = Milestone(
        project_id=proj.id,
        name="Foundation Piles Phase 1",
        planned_date=m1_date,
        status="DELAYED",
        completion_percentage=20.0,
    )
    m2 = Milestone(
        project_id=proj.id,
        name="Superstructure Girders Phase 2",
        planned_date=m2_date,
        status="DELAYED",
        completion_percentage=10.0,
    )
    db.add_all([m1, m2])

    # Add issues
    iss = Issue(
        project_id=proj.id,
        reported_by="Field Officer 1",
        title="Land acquisition ROW clearance dispute",
        description="Pending clearance from local authority.",
        severity="HIGH",
        status="OPEN",
        reported_date=(date.today() - timedelta(days=50)).isoformat(),
    )
    db.add(iss)

    # Add progress update
    prog = ProgressUpdate(
        project_id=proj.id,
        reported_by="Field Officer 1",
        report_date=(date.today() - timedelta(days=10)).isoformat(),
        physical_progress=30.0,
        financial_progress=60.0,
        expenditure=45.0,
        remarks="Slow progress due to monsoon and ROW",
    )
    db.add(prog)

    db.commit()
    db.refresh(proj)
    return proj


# ─── 1. Schedule Delay Alert Generation ─────────────────────────
def test_schedule_delay_alert_generation(db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    res = generate_alerts_for_project(proj.id, db_session)
    types = [a.alert_type for a in res["alerts"]]
    assert AlertType.SCHEDULE_DELAY.value in types

    sched_alert = next(a for a in res["alerts"] if a.alert_type == AlertType.SCHEDULE_DELAY.value)
    assert sched_alert.severity in (AlertSeverity.HIGH.value, AlertSeverity.CRITICAL.value, AlertSeverity.MEDIUM.value)
    assert "Schedule Execution Delay" in sched_alert.title
    assert sched_alert.source == AlertSource.RULE_ENGINE.value


# ─── 2. Cost Overrun Alert Generation ───────────────────────────
def test_cost_overrun_alert_generation(db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    res = generate_alerts_for_project(proj.id, db_session)
    types = [a.alert_type for a in res["alerts"]]
    assert AlertType.COST_OVERRUN.value in types

    cost_alert = next(a for a in res["alerts"] if a.alert_type == AlertType.COST_OVERRUN.value)
    assert cost_alert.severity in (AlertSeverity.HIGH.value, AlertSeverity.CRITICAL.value)
    assert "Cost Overrun" in cost_alert.title


# ─── 3. Low Progress Lag Alert Generation ───────────────────────
def test_low_progress_alert_generation(db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    res = generate_alerts_for_project(proj.id, db_session)
    types = [a.alert_type for a in res["alerts"]]
    assert AlertType.LOW_PROGRESS.value in types

    prog_alert = next(a for a in res["alerts"] if a.alert_type == AlertType.LOW_PROGRESS.value)
    assert prog_alert.severity in (AlertSeverity.HIGH.value, AlertSeverity.CRITICAL.value, AlertSeverity.MEDIUM.value)


# ─── 4. Milestone Delays Alert Generation ───────────────────────
def test_milestone_delay_alert_generation(db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    res = generate_alerts_for_project(proj.id, db_session)
    types = [a.alert_type for a in res["alerts"]]
    assert AlertType.MILESTONE_DELAY.value in types

    mile_alert = next(a for a in res["alerts"] if a.alert_type == AlertType.MILESTONE_DELAY.value)
    assert mile_alert.severity in (AlertSeverity.MEDIUM.value, AlertSeverity.HIGH.value, AlertSeverity.CRITICAL.value)


# ─── 5. High & Critical Risk Alerts ─────────────────────────────
def test_overall_project_risk_alert_generation(db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    res = generate_alerts_for_project(proj.id, db_session)
    types = [a.alert_type for a in res["alerts"]]
    assert (AlertType.HIGH_RISK.value in types) or (AlertType.CRITICAL_RISK.value in types)


# ─── 6 & 7. Predictive ML Overrun Alerts ────────────────────────
def test_predictive_alerts_generation(db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    res = generate_alerts_for_project(proj.id, db_session)
    pred_alerts = [a for a in res["alerts"] if a.source in (AlertSource.COST_PREDICTOR.value, AlertSource.TIME_PREDICTOR.value)]
    for a in pred_alerts:
        assert "Predictive Warning" in a.title
        assert "probability" in a.message.lower() or "%" in a.message


# ─── 8. Data Quality Notice Alert ───────────────────────────────
def test_data_quality_alert_on_sparse_project(db_session: Session):
    sparse_proj = Project(
        project_code=f"TEST-EW-SPARSE-{uuid.uuid4().hex[:6]}",
        name="Sparse Road Project Without Milestones",
        department_name="Public Works Department",
        department_id=1,
        sector="Roads & Bridges",
        district="Nashik",
        status="IN_PROGRESS",
    )
    db_session.add(sparse_proj)
    db_session.commit()
    db_session.refresh(sparse_proj)

    res = generate_alerts_for_project(sparse_proj.id, db_session)
    types = [a.alert_type for a in res["alerts"]]
    assert AlertType.DATA_QUALITY.value in types


# ─── 9. Deduplication Logic ─────────────────────────────────────
def test_alert_deduplication(db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    # First run
    res1 = generate_alerts_for_project(proj.id, db_session)
    count1 = len(res1["alerts"])

    # Second run immediately
    res2 = generate_alerts_for_project(proj.id, db_session)
    assert res2["generated_count"] == 0  # No new rows created
    assert res2["existing_active_count"] == count1

    # Check total DB alert count for this project
    total_db_alerts = db_session.query(Alert).filter(Alert.project_id == proj.id).count()
    assert total_db_alerts == count1


# ─── 10. Update Active Alert on Refresh ─────────────────────────
def test_active_alert_updated_on_refresh(db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    res1 = generate_alerts_for_project(proj.id, db_session)
    assert len(res1["alerts"]) > 0

    # Modify project slightly and re-run
    proj.revised_cost = 120.0  # Even higher overrun
    db_session.commit()

    res2 = generate_alerts_for_project(proj.id, db_session)
    updated_cost_alert = next(a for a in res2["alerts"] if a.alert_type == AlertType.COST_OVERRUN.value)
    assert updated_cost_alert.id is not None
    assert updated_cost_alert.project_id == proj.id


# ─── 11. Lifecycle: UNREAD -> READ ──────────────────────────────
def test_lifecycle_unread_to_read(db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    res = generate_alerts_for_project(proj.id, db_session)
    alert = res["alerts"][0]
    assert alert.status == AlertStatus.UNREAD.value
    assert alert.is_read is False

    updated = update_alert_status(alert.id, AlertStatus.READ.value, db_session, "officer@setux.gov")
    assert updated.status == AlertStatus.READ.value
    assert updated.is_read is True


# ─── 12. Lifecycle: UNREAD/READ -> RESOLVED ─────────────────────
def test_lifecycle_to_resolved(db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    res = generate_alerts_for_project(proj.id, db_session)
    alert = res["alerts"][0]

    updated = update_alert_status(alert.id, AlertStatus.RESOLVED.value, db_session, "lead.engineer@setux.gov")
    assert updated.status == AlertStatus.RESOLVED.value
    assert updated.is_read is True
    assert updated.resolved_at is not None
    assert updated.resolved_by == "lead.engineer@setux.gov"


# ─── 13. Lifecycle: UNREAD/READ -> DISMISSED ────────────────────
def test_lifecycle_to_dismissed(db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    res = generate_alerts_for_project(proj.id, db_session)
    alert = res["alerts"][0]

    updated = update_alert_status(alert.id, AlertStatus.DISMISSED.value, db_session, "lead.engineer@setux.gov")
    assert updated.status == AlertStatus.DISMISSED.value
    assert updated.is_read is True
    assert updated.resolved_at is not None
    assert updated.resolved_by == "lead.engineer@setux.gov"


# ─── 14. Invalid Status Prevention ──────────────────────────────
def test_invalid_status_prevention(db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    res = generate_alerts_for_project(proj.id, db_session)
    alert = res["alerts"][0]

    with pytest.raises(ValueError) as exc:
        update_alert_status(alert.id, "NON_EXISTENT_STATUS", db_session)
    assert "Invalid alert status" in str(exc.value)


# ─── 15. Global List Severity Filter API ────────────────────────
def test_api_list_alerts_severity_filter(client: TestClient, officer_token, db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    generate_alerts_for_project(proj.id, db_session)

    resp = client.get(
        "/api/alerts?severity=CRITICAL",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    for item in data["items"]:
        assert item["severity"] == "CRITICAL"


# ─── 16. Global List Status Filter API ──────────────────────────
def test_api_list_alerts_status_filter(client: TestClient, officer_token, db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    generate_alerts_for_project(proj.id, db_session)

    resp = client.get(
        "/api/alerts?status=UNREAD",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item["status"] == "UNREAD"


# ─── 17. Paginated Global Alerts API ────────────────────────────
def test_api_list_alerts_pagination(client: TestClient, officer_token, db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    generate_alerts_for_project(proj.id, db_session)

    resp = client.get(
        "/api/alerts?page=1&limit=2",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["limit"] == 2
    assert len(data["items"]) <= 2
    assert data["total"] >= len(data["items"])
    assert data["pages"] >= 1


# ─── 18. Project Specific Alerts API ────────────────────────────
def test_api_project_alerts(client: TestClient, officer_token, db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    generate_alerts_for_project(proj.id, db_session)

    resp = client.get(
        f"/api/projects/{proj.id}/alerts",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    assert len(items) > 0
    for item in items:
        assert item["project_id"] == proj.id


# ─── 19. RBAC Enforcement ───────────────────────────────────────
def test_api_rbac_enforcement(client: TestClient, citizen_token, officer_token, db_session: Session):
    proj = create_sample_high_risk_project(db_session)

    # Citizen trying to generate alerts -> 403 Forbidden
    resp_citizen = client.post(
        f"/api/projects/{proj.id}/alerts/generate",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert resp_citizen.status_code == 403

    # Officer generating alerts -> 200 OK
    resp_officer = client.post(
        f"/api/projects/{proj.id}/alerts/generate",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp_officer.status_code == 200
    data = resp_officer.json()
    assert "alerts" in data
    assert data["project_id"] == proj.id


# ─── 20. Single Alert Lookup & Metadata Traceability ────────────
def test_api_single_alert_traceability(client: TestClient, officer_token, db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    res = generate_alerts_for_project(proj.id, db_session)
    alert = res["alerts"][0]

    resp = client.get(
        f"/api/alerts/{alert.id}",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == alert.id
    assert data["alert_type"] == alert.alert_type
    assert data["metadata"] is not None
    assert isinstance(data["metadata"], dict)

    # 404 for non-existent alert
    resp_404 = client.get(
        "/api/alerts/999999",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp_404.status_code == 404


# ─── 21. Bulk Trigger Alert Generation API ───────────────────────
def test_api_bulk_generate_alerts(client: TestClient, officer_token, db_session: Session):
    proj = create_sample_high_risk_project(db_session)
    resp = client.post(
        "/api/alerts/generate-all",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "projects_scanned" in data
    assert data["projects_scanned"] >= 1


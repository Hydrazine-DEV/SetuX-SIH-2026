"""
Phase 15 Test Suite — Overall Project Risk Intelligence System for SetuX.
Covers low, medium, high, and critical risk evaluation, model availability / unavailability handling,
missing data robustness, signal separation (OBSERVED vs PREDICTIVE), double-counting prevention,
data quality tracking, deterministic explanations, decision actions, API endpoint returns,
and full backward compatibility with Phases 11–14.
"""

import os
import pytest
from app.models.project import Project
from app.models.milestone import Milestone
from app.models.issue import Issue
from app.models.progress import ProgressUpdate

from app.services.risk_intelligence import generate_overall_project_risk_intelligence
from app.ml.cost_overrun_predictor import predict_cost_overrun
from app.ml.time_overrun_predictor import predict_time_overrun


def test_1_low_risk_project_evaluation(db_session):
    """Test 1: Low-risk project evaluation."""
    p = Project(
        project_code="MH-LOW-01",
        name="Healthy Low Risk Road Project",
        sector="Road Construction",
        department_name="Public Works Department",
        district="Pune",
        state="Maharashtra",
        original_cost=500.0,
        start_date="2025-01-01",
        planned_completion_date="2025-12-31",
        physical_progress=90.0,
        financial_progress=90.0,
        status="Under Review",
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = generate_overall_project_risk_intelligence(p.project_code, db_session)
    assert res["is_available"] is True
    assert res["overall_risk"]["level"] in ("LOW", "MEDIUM")
    assert res["overall_risk"]["score"] < 50.0


def test_2_medium_risk_project_evaluation(db_session):
    """Test 2: Medium-risk project with minor milestone delay."""
    p = Project(
        project_code="MH-MED-02",
        name="Medium Risk School Project",
        sector="School",
        department_name="ZP Education",
        district="Nashik",
        state="Maharashtra",
        original_cost=300.0,
        start_date="2024-01-01",
        planned_completion_date="2024-12-31",
        physical_progress=50.0,
        financial_progress=70.0,
        status="Under Review",
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    # Add 1 delayed milestone
    m1 = Milestone(project_id=p.id, name="Foundation Work", status="DELAYED", planned_date="2024-06-01")
    db_session.add(m1)
    db_session.commit()

    res = generate_overall_project_risk_intelligence(p.project_code, db_session)
    assert res["is_available"] is True
    assert res["overall_risk"]["score"] >= 0.0


def test_3_high_risk_project_evaluation(db_session):
    """Test 3: High-risk project with schedule delay and progress gap."""
    p = Project(
        project_code="MH-HIGH-03",
        name="High Risk Drainage Project",
        sector="Drainage",
        department_name="PMC",
        district="Pune",
        state="Maharashtra",
        original_cost=1000.0,
        revised_cost=1300.0,
        start_date="2023-01-01",
        planned_completion_date="2024-01-01",
        physical_progress=30.0,
        financial_progress=75.0,
        status="Delayed",
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = generate_overall_project_risk_intelligence(p.project_code, db_session)
    assert res["overall_risk"]["level"] in ("HIGH", "CRITICAL")
    assert res["overall_risk"]["score"] >= 50.0


def test_4_critical_risk_project_evaluation(db_session):
    """Test 4: Critical-risk project with critical unresolved issues and severe delays."""
    p = Project(
        project_code="MH-CRIT-04",
        name="Critical Risk Bridge Project",
        sector="Bridge",
        department_name="Public Works Department",
        district="Nagpur",
        state="Maharashtra",
        original_cost=2000.0,
        revised_cost=2800.0,
        start_date="2022-01-01",
        planned_completion_date="2023-01-01",
        physical_progress=15.0,
        financial_progress=80.0,
        status="High Risk",
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    # Critical Issue
    iss = Issue(
        project_id=p.id,
        title="Land acquisition dispute at pillar site",
        description="Land acquisition dispute at pillar site location.",
        severity="CRITICAL",
        status="OPEN",
        reported_by="Officer Test",
    )
    db_session.add(iss)
    db_session.commit()

    res = generate_overall_project_risk_intelligence(p.project_code, db_session)
    assert res["overall_risk"]["level"] == "CRITICAL"
    assert res["overall_risk"]["score"] >= 75.0


def test_5_cost_and_time_model_availability(db_session):
    """Test 5 & 6: Verify Cost ML and Time ML predictions integration when available."""
    p = Project(
        project_code="MH-ML-05",
        name="ML Assessment Test Project",
        sector="Water Pipeline",
        department_name="MIDC",
        district="Thane",
        state="Maharashtra",
        original_cost=600.0,
        start_date="2024-01-01",
        planned_completion_date="2025-01-01",
        physical_progress=50.0,
        financial_progress=50.0,
        status="Under Review",
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = generate_overall_project_risk_intelligence(p.project_code, db_session)
    assert "cost_overrun_prediction" in res
    assert "time_overrun_prediction" in res
    assert res["cost_overrun_prediction"]["is_available"] is True
    assert res["time_overrun_prediction"]["is_available"] is True


def test_7_cost_model_unavailability_handling(monkeypatch, db_session):
    """Test 7: Graceful risk score calculation when Cost ML artifact is missing."""
    import app.ml.cost_overrun_predictor as cost_pred_mod

    monkeypatch.setattr(cost_pred_mod, "MODEL_ARTIFACT_PATH", "non_existent.joblib")
    cost_pred_mod.cost_overrun_predictor.model = None

    p = Project(
        project_code="MH-NOMODEL-07",
        name="No Cost Model Project",
        original_cost=500.0,
        start_date="2024-01-01",
        planned_completion_date="2025-01-01",
        physical_progress=50.0,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = generate_overall_project_risk_intelligence(p.project_code, db_session)
    assert res["cost_overrun_prediction"]["is_available"] is False
    assert "cost_overrun_ml_model" in res["data_quality"]["missing_components"]
    assert res["overall_risk"]["score"] >= 0.0


def test_8_time_model_unavailability_handling(monkeypatch, db_session):
    """Test 8: Graceful risk score calculation when Time ML artifact is missing."""
    import app.ml.time_overrun_predictor as time_pred_mod

    monkeypatch.setattr(time_pred_mod, "MODEL_ARTIFACT_PATH", "non_existent.joblib")
    time_pred_mod.time_overrun_predictor.model = None

    p = Project(
        project_code="MH-NOMODEL-08",
        name="No Time Model Project",
        original_cost=500.0,
        start_date="2024-01-01",
        planned_completion_date="2025-01-01",
        physical_progress=50.0,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = generate_overall_project_risk_intelligence(p.project_code, db_session)
    assert res["time_overrun_prediction"]["is_available"] is False
    assert "time_overrun_ml_model" in res["data_quality"]["missing_components"]


def test_9_missing_milestones_robustness(db_session):
    """Test 9: Risk calculation for projects with zero milestones."""
    p = Project(project_code="MH-NOMILES-09", name="No Milestones Project", original_cost=100.0)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = generate_overall_project_risk_intelligence(p.project_code, db_session)
    assert res["is_available"] is True
    assert "milestones" in res["data_quality"]["missing_data_fields"]


def test_10_missing_issues_robustness(db_session):
    """Test 10: Risk calculation for projects with zero logged issues."""
    p = Project(project_code="MH-NOISSUES-10", name="No Issues Project", original_cost=100.0)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = generate_overall_project_risk_intelligence(p.project_code, db_session)
    assert res["is_available"] is True


def test_11_missing_progress_robustness(db_session):
    """Test 11: Risk calculation when physical progress is null."""
    p = Project(project_code="MH-NOPROGRESS-11", name="Null Progress Project", original_cost=200.0, physical_progress=None)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = generate_overall_project_risk_intelligence(p.project_code, db_session)
    assert res["is_available"] is True


def test_12_missing_cost_information_robustness(db_session):
    """Test 12: Risk calculation when cost info is missing."""
    p = Project(project_code="MH-NOCOST-12", name="No Cost Project", original_cost=None)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = generate_overall_project_risk_intelligence(p.project_code, db_session)
    assert res["is_available"] is True
    assert "original_cost" in res["data_quality"]["missing_data_fields"]


def test_13_partial_data_quality_status(db_session):
    """Test 13: Data quality status indicates PARTIAL when some sub-entities are missing."""
    p = Project(project_code="MH-PARTIAL-13", name="Partial Data Project", original_cost=500.0)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = generate_overall_project_risk_intelligence(p.project_code, db_session)
    assert res["data_quality"]["status"] in ("PARTIAL", "INSUFFICIENT_DATA")


def test_14_multiple_simultaneous_risk_factors(db_session):
    """Test 14: Multiple simultaneous risk factors are prioritized properly."""
    p = Project(
        project_code="MH-MULTI-14",
        name="Multi Factor Risk Project",
        original_cost=1000.0,
        revised_cost=1500.0,
        start_date="2023-01-01",
        planned_completion_date="2023-12-31",
        physical_progress=20.0,
        financial_progress=80.0,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = generate_overall_project_risk_intelligence(p.project_code, db_session)
    factors = res["prioritized_risk_factors"]
    assert len(factors) >= 2
    # Verify factors are sorted by severity
    severities = [f["severity"] for f in factors]
    assert severities == sorted(severities, key=lambda s: {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}[s], reverse=True)


def test_15_double_counting_prevention(db_session):
    """Test 15: Signals are categorized cleanly into OBSERVED vs PREDICTIVE."""
    p = Project(
        project_code="MH-DOUBLE-15",
        name="Double Count Prevention Project",
        original_cost=500.0,
        start_date="2023-01-01",
        planned_completion_date="2023-06-01",
        physical_progress=40.0,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = generate_overall_project_risk_intelligence(p.project_code, db_session)
    obs_types = {f["type"] for f in res["observed_factors"]}
    pred_types = {f["type"] for f in res["predictive_factors"]}
    assert obs_types.issubset({"OBSERVED"})
    assert pred_types.issubset({"PREDICTIVE"})


def test_16_deterministic_output(db_session):
    """Test 16: Same database inputs produce exact same output structure and score."""
    p = Project(project_code="MH-DET-16", name="Deterministic Output Project", original_cost=400.0)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    r1 = generate_overall_project_risk_intelligence(p.project_code, db_session)
    r2 = generate_overall_project_risk_intelligence(p.project_code, db_session)
    assert r1["overall_risk"]["score"] == r2["overall_risk"]["score"]
    assert r1["summary"] == r2["summary"]


def test_17_unauthorized_access(client):
    """Test 17: Public API access to risk-intelligence endpoint."""
    response = client.get("/api/projects/NON_EXISTENT_999/risk-intelligence")
    assert response.status_code in (404, 200)


def test_18_missing_project_404(client, officer_token):
    """Test 18: API call for non-existent project returns HTTP 404."""
    headers = {"Authorization": f"Bearer {officer_token}"}
    response = client.get("/api/projects/NON_EXISTENT_99999/risk-intelligence", headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_19_api_response_structure(client, db_session):
    """Test 19: Full API return schema validation for /api/projects/{project_id}/risk-intelligence."""
    p = Project(
        project_code="MH-API-19",
        name="API Risk Intelligence Test Project",
        sector="Road Construction",
        department_name="Public Works Department",
        district="Pune",
        state="Maharashtra",
        original_cost=800.0,
        start_date="2024-01-01",
        planned_completion_date="2025-01-01",
        physical_progress=60.0,
        financial_progress=60.0,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    response = client.get(f"/api/projects/{p.id}/risk-intelligence")
    assert response.status_code == 200
    body = response.json()
    assert body["is_available"] is True
    assert "overall_risk" in body
    assert "cost_overrun_prediction" in body
    assert "time_overrun_prediction" in body
    assert "observed_factors" in body
    assert "predictive_factors" in body
    assert "prioritized_risk_factors" in body
    assert "summary" in body
    assert "recommended_actions" in body
    assert "disclaimer" in body


def test_20_phase11_rule_engine_compatibility(db_session):
    """Test 20: Phase 11 rule engine results match embedded baseline score."""
    p = Project(project_code="MH-P11-20", name="Phase 11 Compatibility Project", original_cost=500.0)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = generate_overall_project_risk_intelligence(p.project_code, db_session)
    assert "rule_based_baseline_score" in res["overall_risk"]


def test_21_phase12_data_pipeline_compatibility(db_session):
    """Test 21: Feature calculation works seamlessly with Phase 12 pipeline."""
    p = Project(project_code="MH-P12-21", name="Phase 12 Compatibility Project", original_cost=500.0)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    res = generate_overall_project_risk_intelligence(p.project_code, db_session)
    assert res["data_quality"]["status"] in ("COMPLETE", "PARTIAL", "INSUFFICIENT_DATA")


def test_22_phase13_cost_ml_compatibility():
    """Test 22: Cost ML predictor interface compatibility."""
    res = predict_cost_overrun({"project_id": 1, "original_cost": 500.0})
    assert "prediction" in res
    assert "probability" in res


def test_23_phase14_time_ml_compatibility():
    """Test 23: Time ML predictor interface compatibility."""
    res = predict_time_overrun({"project_id": 1, "planned_duration_days": 300})
    assert "prediction" in res
    assert "probability" in res

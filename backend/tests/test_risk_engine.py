"""
SetuX / VeriX — Rule-Based Risk Engine Test Suite
Phase 11: Unit Tests & API Integration Tests for Project Risk Engine

Covers 22 comprehensive test scenarios:
- Standalone engine evaluation for all 7 factors
- Boundary conditions (0-100 clamping, missing data, 0 original cost, completed project)
- Determinism verification (Same input -> Same output)
- API endpoint integration & 404 handling
"""
from datetime import date
import pytest
from app.services.risk_engine import evaluate_project_risk, RISK_CONFIG


class DummyProject:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", 1)
        self.project_code = kwargs.get("project_code", "MH-PN-001")
        self.name = kwargs.get("name", "Test Project")
        self.status = kwargs.get("status", "Under Review")
        self.start_date = kwargs.get("start_date", "2026-01-01")
        self.planned_completion_date = kwargs.get("planned_completion_date", "2026-12-31")
        self.revised_completion_date = kwargs.get("revised_completion_date", None)
        self.actual_completion_date = kwargs.get("actual_completion_date", None)
        self.original_cost = kwargs.get("original_cost", 1000.0)
        self.revised_cost = kwargs.get("revised_cost", 1000.0)
        self.total_expenditure = kwargs.get("total_expenditure", 200.0)
        self.physical_progress = kwargs.get("physical_progress", 50.0)
        self.financial_progress = kwargs.get("financial_progress", 50.0)


class DummyMilestone:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", 1)
        self.project_id = kwargs.get("project_id", 1)
        self.name = kwargs.get("name", "Milestone Stage")
        self.planned_date = kwargs.get("planned_date", "2026-06-30")
        self.actual_date = kwargs.get("actual_date", None)
        self.status = kwargs.get("status", "IN_PROGRESS")


class DummyIssue:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", 1)
        self.project_id = kwargs.get("project_id", 1)
        self.title = kwargs.get("title", "Issue Title")
        self.severity = kwargs.get("severity", "MEDIUM")
        self.status = kwargs.get("status", "OPEN")


# ─── 1. Standalone Risk Engine Unit Tests ───────────────────────────

def test_1_no_risk_factors():
    """1. Project with no risk factors should yield risk_score = 0 and LOW level."""
    p = DummyProject(
        planned_completion_date="2026-12-31",
        original_cost=1000.0,
        revised_cost=1000.0,
        physical_progress=80.0,
        financial_progress=80.0,
    )
    res = evaluate_project_risk(p, milestones=[], issues=[], reference_date=date(2026, 6, 1))
    assert res["risk_score"] == 0.0
    assert res["risk_level"] == "LOW"
    assert res["triggered_factor_count"] == 0
    assert len(res["warnings"]) == 0


def test_2_schedule_delay_risk():
    """2. Project past planned completion date should trigger SCHEDULE_DELAY."""
    p = DummyProject(
        planned_completion_date="2026-01-01",  # Past target date
        status="Under Review",
    )
    res = evaluate_project_risk(p, reference_date=date(2026, 6, 1))
    sched_factor = next(f for f in res["risk_factors"] if f["factor"] == "SCHEDULE_DELAY")
    assert sched_factor["triggered"] is True
    assert sched_factor["contribution"] > 0
    assert res["risk_score"] > 0


def test_3_cost_overrun_risk():
    """3. Project with revised cost > original cost should trigger COST_OVERRUN."""
    p = DummyProject(
        original_cost=1000.0,
        revised_cost=1300.0,  # 30% overrun
    )
    res = evaluate_project_risk(p, reference_date=date(2026, 6, 1))
    cost_factor = next(f for f in res["risk_factors"] if f["factor"] == "COST_OVERRUN")
    assert cost_factor["triggered"] is True
    assert cost_factor["evidence"]["cost_overrun_pct"] == 30.0


def test_4_low_physical_progress_risk():
    """4. Project with physical progress lagging timeline should trigger LOW_PHYSICAL_PROGRESS."""
    p = DummyProject(
        start_date="2026-01-01",
        planned_completion_date="2026-12-31",
        physical_progress=10.0,  # Halfway through year, only 10% progress
    )
    res = evaluate_project_risk(p, reference_date=date(2026, 7, 1))
    prog_factor = next(f for f in res["risk_factors"] if f["factor"] == "LOW_PHYSICAL_PROGRESS")
    assert prog_factor["triggered"] is True


def test_5_financial_physical_mismatch_risk():
    """5. Financial progress > physical progress should trigger FINANCIAL_PHYSICAL_MISMATCH."""
    p = DummyProject(
        physical_progress=30.0,
        financial_progress=70.0,  # 40% gap
    )
    res = evaluate_project_risk(p, reference_date=date(2026, 6, 1))
    mismatch_factor = next(f for f in res["risk_factors"] if f["factor"] == "FINANCIAL_PHYSICAL_MISMATCH")
    assert mismatch_factor["triggered"] is True
    assert mismatch_factor["evidence"]["mismatch_gap"] == 40.0


def test_6_milestone_delays_risk():
    """6. Delayed milestones should trigger MILESTONE_DELAYS factor."""
    p = DummyProject()
    milestones = [
        DummyMilestone(status="COMPLETED"),
        DummyMilestone(status="DELAYED"),
        DummyMilestone(status="DELAYED"),
    ]
    res = evaluate_project_risk(p, milestones=milestones, reference_date=date(2026, 6, 1))
    m_factor = next(f for f in res["risk_factors"] if f["factor"] == "MILESTONE_DELAYS")
    assert m_factor["triggered"] is True
    assert m_factor["evidence"]["delayed_milestones"] == 2


def test_7_open_issues_risk():
    """7. Multiple open issues should trigger OPEN_ISSUES factor."""
    p = DummyProject()
    issues = [
        DummyIssue(status="OPEN"),
        DummyIssue(status="OPEN"),
        DummyIssue(status="IN_PROGRESS"),
    ]
    res = evaluate_project_risk(p, issues=issues, reference_date=date(2026, 6, 1))
    issues_factor = next(f for f in res["risk_factors"] if f["factor"] == "OPEN_ISSUES")
    assert issues_factor["triggered"] is True


def test_8_critical_issues_risk():
    """8. Unresolved critical issue should trigger CRITICAL_ISSUES factor."""
    p = DummyProject()
    issues = [DummyIssue(severity="CRITICAL", status="OPEN")]
    res = evaluate_project_risk(p, issues=issues, reference_date=date(2026, 6, 1))
    crit_factor = next(f for f in res["risk_factors"] if f["factor"] == "CRITICAL_ISSUES")
    assert crit_factor["triggered"] is True
    assert crit_factor["severity"] == "CRITICAL"


def test_9_multiple_risk_factors_and_10_11_clamping():
    """9, 10, 11. Multiple risk factors sum correctly and normalize to 0-100."""
    p = DummyProject(
        planned_completion_date="2026-01-01",  # Delayed
        original_cost=1000.0,
        revised_cost=1500.0,                  # Overrun
        physical_progress=10.0,
        financial_progress=70.0,               # Mismatch
    )
    milestones = [DummyMilestone(status="DELAYED") for _ in range(5)]
    issues = [DummyIssue(severity="CRITICAL", status="OPEN") for _ in range(5)]

    res = evaluate_project_risk(p, milestones=milestones, issues=issues, reference_date=date(2026, 6, 1))
    assert 0.0 <= res["risk_score"] <= 100.0
    assert res["risk_level"] == "CRITICAL"
    assert res["triggered_factor_count"] >= 5


def test_12_missing_dates():
    """12. Missing completion dates handled gracefully without crashing."""
    p = DummyProject(planned_completion_date=None, start_date=None)
    res = evaluate_project_risk(p, reference_date=date(2026, 6, 1))
    assert res["risk_score"] >= 0.0


def test_13_14_missing_or_zero_cost():
    """13, 14. Missing or zero original cost handled safely without zero division."""
    p = DummyProject(original_cost=0.0, revised_cost=0.0, total_expenditure=0.0)
    res = evaluate_project_risk(p, reference_date=date(2026, 6, 1))
    cost_factor = next(f for f in res["risk_factors"] if f["factor"] == "COST_OVERRUN")
    assert cost_factor["triggered"] is False
    assert res["risk_score"] >= 0.0


def test_15_16_17_missing_progress_milestones_issues():
    """15, 16, 17. Empty milestones and empty issues lists handled safely."""
    p = DummyProject(physical_progress=0.0, financial_progress=0.0)
    res = evaluate_project_risk(p, milestones=[], issues=[], reference_date=date(2026, 6, 1))
    assert res["risk_score"] >= 0.0


def test_18_completed_project():
    """18. Completed project should not trigger low progress rule."""
    p = DummyProject(status="Completed", physical_progress=100.0, financial_progress=100.0)
    res = evaluate_project_risk(p, reference_date=date(2026, 6, 1))
    prog_factor = next(f for f in res["risk_factors"] if f["factor"] == "LOW_PHYSICAL_PROGRESS")
    assert prog_factor["triggered"] is False


def test_19_ongoing_project():
    """19. Ongoing project evaluates properly."""
    p = DummyProject(status="Under Review")
    res = evaluate_project_risk(p, reference_date=date(2026, 6, 1))
    assert "calculation_version" in res


def test_22_determinism():
    """22. Same input -> exact same risk score and factors every time."""
    p = DummyProject(
        planned_completion_date="2026-03-01",
        original_cost=500.0,
        revised_cost=650.0,
        physical_progress=40.0,
        financial_progress=60.0,
    )
    milestones = [DummyMilestone(status="DELAYED")]
    issues = [DummyIssue(severity="CRITICAL", status="OPEN")]
    ref = date(2026, 6, 1)

    res1 = evaluate_project_risk(p, milestones=milestones, issues=issues, reference_date=ref)
    res2 = evaluate_project_risk(p, milestones=milestones, issues=issues, reference_date=ref)

    assert res1["risk_score"] == res2["risk_score"]
    assert res1["risk_level"] == res2["risk_level"]
    assert res1["triggered_factor_count"] == res2["triggered_factor_count"]
    assert [f["factor"] for f in res1["risk_factors"]] == [f["factor"] for f in res2["risk_factors"]]


# ─── 2. API Integration Tests ───────────────────────────────────────

def test_20_21_api_endpoint_risk(client, officer_token):
    """20, 21. GET /api/projects/{project_id}/risk returns 200 for valid project and 404 for missing project."""
    headers = {"Authorization": f"Bearer {officer_token}"}

    # 1. Create project
    proj = client.post(
        "/api/projects/",
        json={
            "name": "Risk Test Highway",
            "sector": "Road Construction",
            "district": "Solapur",
            "original_cost": 2000.0,
            "revised_cost": 2500.0,
            "planned_completion_date": "2026-01-01",
            "physical_progress": 30.0,
            "financial_progress": 60.0,
        },
        headers=headers,
    ).json()

    # 2. Add CRITICAL issue
    client.post(
        f"/api/projects/{proj['id']}/issues",
        json={"title": "Land Dispute", "description": "Court stay order.", "severity": "CRITICAL"},
        headers=headers,
    )

    # 3. Call /api/projects/{project_id}/risk
    resp = client.get(f"/api/projects/{proj['id']}/risk")
    assert resp.status_code == 200
    data = resp.json()

    assert data["project_id"] == proj["project_code"]
    assert data["risk_score"] > 0
    assert data["triggered_factor_count"] >= 2
    assert "disclaimer" in data

    # Call /api/analytics/projects/{project_id}/risk
    resp_analytics = client.get(f"/api/analytics/projects/{proj['id']}/risk")
    assert resp_analytics.status_code == 200
    assert resp_analytics.json()["risk_score"] == data["risk_score"]

    # 4. 404 for non-existent project
    resp_404 = client.get("/api/projects/999999/risk")
    assert resp_404.status_code == 404

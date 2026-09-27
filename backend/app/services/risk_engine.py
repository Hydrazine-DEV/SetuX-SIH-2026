"""
SetuX / VeriX — Rule-Based Project Risk Engine
Phase 11: Production-Quality Deterministic Project Risk Assessment Service

Features:
- Completely deterministic rule-based evaluation (Same inputs -> Exact same output)
- Centralized configuration for weights, thresholds, and risk level boundaries
- Evaluates 7 core risk factors with explicit evidence and contribution tracing
- Decoupled from FastAPI for standalone testability
"""
from datetime import datetime, date
from typing import Dict, Any, List, Optional

from app.services.cost_analysis import calculate_cost_overrun
from app.services.schedule_analysis import calculate_project_delay, calculate_time_overrun, parse_date


# ─── Centralized Risk Configuration ────────────────────────────────
# Baseline engineering defaults. Documented as baseline transparent rule assumptions.
RISK_CONFIG: Dict[str, Any] = {
    "calculation_version": "rule_engine_v1",
    "disclaimer": (
        "This rule-based engine is a transparent baseline risk assessment mechanism. "
        "Its thresholds and weights are engineering assumptions and are not presented as statistically validated predictors. "
        "Future phases will evaluate historical data and compare statistical/ML approaches."
    ),
    "level_thresholds": {
        "LOW": (0.0, 24.99),
        "MEDIUM": (25.0, 49.99),
        "HIGH": (50.0, 74.99),
        "CRITICAL": (75.0, 100.0),
    },
    "factors": {
        "SCHEDULE_DELAY": {
            "weight": 25.0,
            "threshold_days": 15,
            "description": "Project schedule delay exceeding timeline threshold.",
        },
        "LOW_PHYSICAL_PROGRESS": {
            "weight": 20.0,
            "threshold_gap_pct": 15.0,
            "description": "Physical progress significantly below expected schedule timeline.",
        },
        "COST_OVERRUN": {
            "weight": 20.0,
            "threshold_pct": 10.0,
            "description": "Revised cost exceeds original approved budget.",
        },
        "FINANCIAL_PHYSICAL_MISMATCH": {
            "weight": 15.0,
            "threshold_gap_pct": 15.0,
            "description": "Financial expenditure progress significantly leads physical completion progress.",
        },
        "MILESTONE_DELAYS": {
            "weight": 10.0,
            "threshold_delayed_pct": 25.0,
            "description": "Significant proportion of project milestones are delayed.",
        },
        "OPEN_ISSUES": {
            "weight": 5.0,
            "threshold_count": 3,
            "description": "High volume of open or in-progress implementation issues.",
        },
        "CRITICAL_ISSUES": {
            "weight": 15.0,
            "threshold_count": 1,
            "description": "Unresolved critical severity issues present on project.",
        },
    },
}


# ─── Individual Rule Evaluators ─────────────────────────────────────

def eval_schedule_delay(project: Any, reference_date: Optional[date] = None) -> Dict[str, Any]:
    """Rule A: Schedule Delay Evaluation."""
    cfg = RISK_CONFIG["factors"]["SCHEDULE_DELAY"]
    weight = cfg["weight"]
    thresh_days = cfg["threshold_days"]

    planned = getattr(project, "planned_completion_date", None)
    revised = getattr(project, "revised_completion_date", None)
    actual = getattr(project, "actual_completion_date", None)
    status = getattr(project, "status", None)

    delay_res = calculate_project_delay(planned, revised, actual, status, reference_date=reference_date)
    delay_days = delay_res.get("delay_days", 0)
    is_delayed = delay_res.get("is_delayed", False)

    triggered = is_delayed and delay_days >= thresh_days

    if triggered:
        # Scale contribution up to max weight
        scale = min(1.0, delay_days / 90.0)
        contribution = round(weight * scale, 2)
        severity = "CRITICAL" if delay_days >= 90 else ("HIGH" if delay_days >= 45 else "MEDIUM")
        reason = f"Project is {delay_days} days behind scheduled completion timeline."
    else:
        contribution = 0.0
        severity = "LOW"
        reason = "Project schedule is within acceptable timeline boundaries."

    return {
        "factor": "SCHEDULE_DELAY",
        "triggered": triggered,
        "contribution": contribution,
        "max_weight": weight,
        "severity": severity,
        "reason": reason,
        "evidence": {
            "delay_days": delay_days,
            "is_delayed": is_delayed,
            "planned_completion_date": planned,
            "revised_completion_date": revised,
            "actual_completion_date": actual,
            "target_completion_date": delay_res.get("target_completion_date"),
        },
    }


def eval_low_physical_progress(project: Any, reference_date: Optional[date] = None) -> Dict[str, Any]:
    """Rule B: Low Physical Progress / Progress Deviation Evaluation."""
    cfg = RISK_CONFIG["factors"]["LOW_PHYSICAL_PROGRESS"]
    weight = cfg["weight"]
    thresh_gap = cfg["threshold_gap_pct"]

    status = (getattr(project, "status", "") or "").upper().strip()
    actual_phys = float(getattr(project, "physical_progress", 0.0) or 0.0)

    # For completed projects, low progress rule does not trigger
    if status == "COMPLETED":
        return {
            "factor": "LOW_PHYSICAL_PROGRESS",
            "triggered": False,
            "contribution": 0.0,
            "max_weight": weight,
            "severity": "LOW",
            "reason": "Project is completed.",
            "evidence": {"actual_physical_progress": actual_phys, "expected_progress": 100.0, "progress_gap": 0.0},
        }

    time_res = calculate_time_overrun(
        getattr(project, "planned_completion_date", None),
        getattr(project, "revised_completion_date", None),
        getattr(project, "actual_completion_date", None),
        getattr(project, "start_date", None),
        reference_date=reference_date,
    )
    time_elapsed_pct = time_res.get("time_elapsed_pct", 0.0)
    expected_progress = min(100.0, time_elapsed_pct)
    progress_gap = round(expected_progress - actual_phys, 2)

    triggered = progress_gap >= thresh_gap and time_elapsed_pct > 10.0

    if triggered:
        scale = min(1.0, progress_gap / 40.0)
        contribution = round(weight * scale, 2)
        severity = "HIGH" if progress_gap >= 30.0 else "MEDIUM"
        reason = f"Physical progress ({actual_phys}%) lags expected schedule progress ({round(expected_progress, 1)}%) by {progress_gap}%."
    else:
        contribution = 0.0
        severity = "LOW"
        reason = f"Physical progress ({actual_phys}%) is aligned with expected schedule timeline."

    return {
        "factor": "LOW_PHYSICAL_PROGRESS",
        "triggered": triggered,
        "contribution": contribution,
        "max_weight": weight,
        "severity": severity,
        "reason": reason,
        "evidence": {
            "actual_physical_progress": actual_phys,
            "expected_progress": round(expected_progress, 2),
            "progress_gap": progress_gap,
            "time_elapsed_pct": time_elapsed_pct,
        },
    }


def eval_cost_overrun(project: Any) -> Dict[str, Any]:
    """Rule C: Cost Overrun Evaluation."""
    cfg = RISK_CONFIG["factors"]["COST_OVERRUN"]
    weight = cfg["weight"]
    thresh_pct = cfg["threshold_pct"]

    orig = float(getattr(project, "original_cost", 0.0) or 0.0)
    rev = float(getattr(project, "revised_cost", None) if getattr(project, "revised_cost", None) is not None else orig)
    exp = float(getattr(project, "total_expenditure", 0.0) or 0.0)

    cost_res = calculate_cost_overrun(orig, rev, exp)
    overrun_pct = cost_res.get("cost_overrun_pct", 0.0)
    amount = cost_res.get("cost_overrun_amount", 0.0)

    triggered = overrun_pct >= thresh_pct

    if triggered:
        scale = min(1.0, overrun_pct / 30.0)
        contribution = round(weight * scale, 2)
        severity = "CRITICAL" if overrun_pct >= 30.0 else ("HIGH" if overrun_pct >= 15.0 else "MEDIUM")
        reason = f"Revised budget exceeds original cost by {overrun_pct}% (₹{amount:.2f} Lakhs over budget)."
    else:
        contribution = 0.0
        severity = "LOW"
        reason = "Project cost is within approved budget boundaries."

    return {
        "factor": "COST_OVERRUN",
        "triggered": triggered,
        "contribution": contribution,
        "max_weight": weight,
        "severity": severity,
        "reason": reason,
        "evidence": {
            "original_cost": orig,
            "revised_cost": rev,
            "cost_overrun_pct": overrun_pct,
            "cost_overrun_amount": amount,
        },
    }


def eval_financial_physical_mismatch(project: Any) -> Dict[str, Any]:
    """Rule D: Financial vs Physical Progress Mismatch Evaluation."""
    cfg = RISK_CONFIG["factors"]["FINANCIAL_PHYSICAL_MISMATCH"]
    weight = cfg["weight"]
    thresh_gap = cfg["threshold_gap_pct"]

    phys = float(getattr(project, "physical_progress", 0.0) or 0.0)
    fin = float(getattr(project, "financial_progress", 0.0) or 0.0)
    gap = round(fin - phys, 2)

    triggered = gap >= thresh_gap

    if triggered:
        scale = min(1.0, gap / 35.0)
        contribution = round(weight * scale, 2)
        severity = "HIGH" if gap >= 25.0 else "MEDIUM"
        reason = f"Significant financial-physical progress mismatch: Financial progress ({fin}%) leads physical progress ({phys}%) by {gap}%."
    else:
        contribution = 0.0
        severity = "LOW"
        reason = f"Financial progress ({fin}%) and physical progress ({phys}%) are in acceptable balance."

    return {
        "factor": "FINANCIAL_PHYSICAL_MISMATCH",
        "triggered": triggered,
        "contribution": contribution,
        "max_weight": weight,
        "severity": severity,
        "reason": reason,
        "evidence": {
            "physical_progress": phys,
            "financial_progress": fin,
            "mismatch_gap": gap,
        },
    }


def eval_milestone_delays(project: Any, milestones: List[Any], reference_date: Optional[date] = None) -> Dict[str, Any]:
    """Rule E: Milestone Delays Evaluation."""
    cfg = RISK_CONFIG["factors"]["MILESTONE_DELAYS"]
    weight = cfg["weight"]
    thresh_pct = cfg["threshold_delayed_pct"]

    total_m = len(milestones)
    if total_m == 0:
        return {
            "factor": "MILESTONE_DELAYS",
            "triggered": False,
            "contribution": 0.0,
            "max_weight": weight,
            "severity": "LOW",
            "reason": "No milestones configured for project.",
            "evidence": {"total_milestones": 0, "delayed_milestones": 0, "delayed_pct": 0.0},
        }

    ref_date = reference_date or date.today()
    delayed_count = 0

    for m in milestones:
        st = (getattr(m, "status", "") or "").upper().strip()
        if st == "DELAYED":
            delayed_count += 1
        elif st != "COMPLETED":
            target_str = getattr(m, "planned_date", None) or getattr(m, "target_completion_date", None)
            p_date = parse_date(target_str)
            if p_date and p_date < ref_date:
                delayed_count += 1

    delayed_pct = round((delayed_count / total_m) * 100, 2)
    triggered = delayed_count >= 1 and delayed_pct >= thresh_pct

    if triggered:
        scale = min(1.0, delayed_pct / 50.0)
        contribution = round(weight * scale, 2)
        severity = "HIGH" if delayed_pct >= 50.0 else "MEDIUM"
        reason = f"{delayed_count} of {total_m} milestones ({delayed_pct}%) are currently delayed."
    else:
        contribution = 0.0
        severity = "LOW"
        reason = "Milestone completion is progressing on schedule."

    return {
        "factor": "MILESTONE_DELAYS",
        "triggered": triggered,
        "contribution": contribution,
        "max_weight": weight,
        "severity": severity,
        "reason": reason,
        "evidence": {
            "total_milestones": total_m,
            "delayed_milestones": delayed_count,
            "delayed_pct": delayed_pct,
        },
    }


def eval_open_issues(project: Any, issues: List[Any]) -> Dict[str, Any]:
    """Rule F: Open Issues Volume Evaluation."""
    cfg = RISK_CONFIG["factors"]["OPEN_ISSUES"]
    weight = cfg["weight"]
    thresh_count = cfg["threshold_count"]

    open_issues = [
        i for i in issues if (getattr(i, "status", "") or "").upper().strip() in ("OPEN", "IN_PROGRESS")
    ]
    open_count = len(open_issues)
    triggered = open_count >= thresh_count

    if triggered:
        scale = min(1.0, open_count / 6.0)
        contribution = round(weight * scale, 2)
        severity = "HIGH" if open_count >= 5 else "MEDIUM"
        reason = f"High volume of unresolved implementation issues ({open_count} open/in-progress issues)."
    else:
        contribution = 0.0
        severity = "LOW"
        reason = "Open issue volume is within manageable limits."

    return {
        "factor": "OPEN_ISSUES",
        "triggered": triggered,
        "contribution": contribution,
        "max_weight": weight,
        "severity": severity,
        "reason": reason,
        "evidence": {
            "open_issue_count": open_count,
            "total_issue_count": len(issues),
        },
    }


def eval_critical_issues(project: Any, issues: List[Any]) -> Dict[str, Any]:
    """Rule G: Critical Issues Severity Evaluation."""
    cfg = RISK_CONFIG["factors"]["CRITICAL_ISSUES"]
    weight = cfg["weight"]
    thresh_count = cfg["threshold_count"]

    critical_issues = [
        i for i in issues
        if (getattr(i, "status", "") or "").upper().strip() in ("OPEN", "IN_PROGRESS")
        and (getattr(i, "severity", "") or "").upper().strip() == "CRITICAL"
    ]
    crit_count = len(critical_issues)
    triggered = crit_count >= thresh_count

    if triggered:
        scale = min(1.0, crit_count / 2.0)
        contribution = round(weight * scale, 2)
        severity = "CRITICAL"
        reason = f"{crit_count} unresolved CRITICAL severity issue(s) require immediate officer intervention."
    else:
        contribution = 0.0
        severity = "LOW"
        reason = "No unresolved critical issues detected."

    return {
        "factor": "CRITICAL_ISSUES",
        "triggered": triggered,
        "contribution": contribution,
        "max_weight": weight,
        "severity": severity,
        "reason": reason,
        "evidence": {
            "critical_issue_count": crit_count,
        },
    }


# ─── Overall Risk Engine Calculator ────────────────────────────────

def evaluate_project_risk(
    project: Any,
    milestones: Optional[List[Any]] = None,
    progress_history: Optional[List[Any]] = None,
    issues: Optional[List[Any]] = None,
    reference_date: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Run deterministic rule-based risk evaluation on a project instance.

    Returns:
        project_id: str / int identifier
        risk_score: float normalized (0.0 to 100.0)
        risk_level: str ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        risk_factors: List of evaluated factor dictionaries
        warnings: List of warning strings for triggered factors
        summary: Human-readable evaluation summary
        calculation_version: "rule_engine_v1"
        generated_at: ISO timestamp
    """
    if milestones is None:
        milestones = []
    if progress_history is None:
        progress_history = []
    if issues is None:
        issues = []

    ref_date = reference_date or date.today()

    # Run all 7 rule evaluators
    factors = [
        eval_schedule_delay(project, reference_date=ref_date),
        eval_low_physical_progress(project, reference_date=ref_date),
        eval_cost_overrun(project),
        eval_financial_physical_mismatch(project),
        eval_milestone_delays(project, milestones, reference_date=ref_date),
        eval_open_issues(project, issues),
        eval_critical_issues(project, issues),
    ]

    # Calculate total score normalized (0-100)
    raw_score = sum(f["contribution"] for f in factors if f["triggered"])
    risk_score = round(max(0.0, min(100.0, raw_score)), 2)

    # Determine risk level from centralized thresholds
    risk_level = "LOW"
    for level, (low, high) in RISK_CONFIG["level_thresholds"].items():
        if low <= risk_score <= high:
            risk_level = level
            break
    if risk_score >= 75.0:
        risk_level = "CRITICAL"

    # Extract warnings from triggered factors
    triggered_factors = [f for f in factors if f["triggered"]]
    warnings = [f["reason"] for f in triggered_factors]

    # Build human readable summary
    code = getattr(project, "project_code", None) or str(getattr(project, "id", "Unknown"))
    if not warnings:
        summary = f"Project '{code}' is operating normally within baseline schedule, budget, and quality parameters."
    else:
        summary = f"Project '{code}' evaluated with {risk_level} risk (score: {risk_score}/100) due to {len(warnings)} triggered risk indicator(s)."

    project_key = getattr(project, "project_code", None) or getattr(project, "id", None)

    return {
        "project_id": str(project_key),
        "project_name": getattr(project, "name", ""),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": factors,
        "triggered_factor_count": len(triggered_factors),
        "warnings": warnings,
        "summary": summary,
        "calculation_version": RISK_CONFIG["calculation_version"],
        "disclaimer": RISK_CONFIG["disclaimer"],
        "generated_at": datetime.utcnow().isoformat(),
    }

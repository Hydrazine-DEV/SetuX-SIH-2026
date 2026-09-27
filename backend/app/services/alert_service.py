"""
SetuX / VeriX — Early Warning & Alert Service
SIH26103: Integrated Government Project Monitoring & Intelligence Platform
"""
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import json
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.alert import Alert
from app.models.project import Project
from app.models.milestone import Milestone
from app.models.progress import ProgressUpdate
from app.models.issue import Issue

from app.services.alert_config import (
    AlertStatus,
    AlertSeverity,
    AlertType,
    AlertSource,
    ALERT_CONFIG,
)
from app.services.risk_engine import evaluate_project_risk
from app.services.risk_intelligence import generate_overall_project_risk_intelligence


def _find_project(project_id_or_code: Any, db: Session) -> Optional[Project]:
    """Find a project by ID or project_code."""
    if isinstance(project_id_or_code, int) or (isinstance(project_id_or_code, str) and project_id_or_code.isdigit()):
        p = db.query(Project).filter(Project.id == int(project_id_or_code)).first()
        if p:
            return p
    return db.query(Project).filter(Project.project_code == str(project_id_or_code)).first()


def _get_active_alerts_map(project_id: int, db: Session) -> Dict[str, Alert]:
    """
    Get all active (UNREAD or READ) alerts for a project indexed by alert_type.
    """
    active_alerts = (
        db.query(Alert)
        .filter(
            Alert.project_id == project_id,
            Alert.status.in_([AlertStatus.UNREAD.value, AlertStatus.READ.value]),
        )
        .all()
    )
    return {a.alert_type: a for a in active_alerts}


def _evaluate_project_alert_candidates(
    project: Project,
    rule_res: Dict[str, Any],
    risk_intel: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Deterministically evaluate alert rules against rule engine assessment and risk intelligence output.
    Returns a list of candidate alert dictionaries.
    """
    candidates = []

    # Extract intelligence components
    factors = rule_res.get("risk_factors", [])
    factor_map = {f.get("factor"): f for f in factors}

    cost_ml = risk_intel.get("cost_overrun_prediction", {})
    time_ml = risk_intel.get("time_overrun_prediction", {})
    overall_risk_dict = risk_intel.get("overall_risk", {})
    overall_score = float(overall_risk_dict.get("score", rule_res.get("risk_score", 0.0)))
    overall_level = overall_risk_dict.get("level", rule_res.get("risk_level", "LOW"))
    data_quality = risk_intel.get("data_quality", {})

    # 1. SCHEDULE DELAY ALERT
    sched_factor = factor_map.get("SCHEDULE_DELAY")
    if sched_factor and (sched_factor.get("triggered") or sched_factor.get("severity") in ("MEDIUM", "HIGH", "CRITICAL")):
        evidence = sched_factor.get("evidence", {})
        delay_days = evidence.get("delay_days", 0)
        sev_str = sched_factor.get("severity", "LOW")
        
        sev = AlertSeverity.LOW.value
        if delay_days >= ALERT_CONFIG["schedule_delay"]["critical_days"] or sev_str == "CRITICAL":
            sev = AlertSeverity.CRITICAL.value
        elif delay_days >= ALERT_CONFIG["schedule_delay"]["high_days"] or sev_str == "HIGH":
            sev = AlertSeverity.HIGH.value
        elif delay_days >= ALERT_CONFIG["schedule_delay"]["medium_days"] or sev_str == "MEDIUM":
            sev = AlertSeverity.MEDIUM.value

        candidates.append({
            "alert_type": AlertType.SCHEDULE_DELAY.value,
            "severity": sev,
            "source": AlertSource.RULE_ENGINE.value,
            "title": f"Schedule Execution Delay: {delay_days} Days Behind",
            "message": (
                f"Project '{project.name}' is experiencing an execution delay of {delay_days} days "
                f"relative to its baseline schedule."
            ),
            "risk_score": int(sched_factor.get("contribution", 0)),
            "metadata": {
                "delay_days": delay_days,
                "factor": "SCHEDULE_DELAY",
                "evidence": evidence,
                "planned_end_date": str(getattr(project, "planned_completion_date", None) or getattr(project, "planned_end_date", None)),
            },
        })

    # 2. COST OVERRUN ALERT
    cost_factor = factor_map.get("COST_OVERRUN")
    if cost_factor and (cost_factor.get("triggered") or cost_factor.get("severity") in ("MEDIUM", "HIGH", "CRITICAL")):
        evidence = cost_factor.get("evidence", {})
        overrun_pct = evidence.get("cost_overrun_pct", 0.0)
        sev_str = cost_factor.get("severity", "LOW")

        sev = AlertSeverity.LOW.value
        if overrun_pct >= ALERT_CONFIG["cost_overrun"]["critical_pct"] or sev_str == "CRITICAL":
            sev = AlertSeverity.CRITICAL.value
        elif overrun_pct >= ALERT_CONFIG["cost_overrun"]["high_pct"] or sev_str == "HIGH":
            sev = AlertSeverity.HIGH.value
        elif overrun_pct >= ALERT_CONFIG["cost_overrun"]["medium_pct"] or sev_str == "MEDIUM":
            sev = AlertSeverity.MEDIUM.value

        candidates.append({
            "alert_type": AlertType.COST_OVERRUN.value,
            "severity": sev,
            "source": AlertSource.RULE_ENGINE.value,
            "title": f"Budget Cost Overrun: +{round(overrun_pct, 1)}% Over Sanctioned Cost",
            "message": (
                f"Approved revised budget for project '{project.name}' exceeds original sanctioned "
                f"cost by {round(overrun_pct, 1)}%."
            ),
            "risk_score": int(cost_factor.get("contribution", 0)),
            "metadata": {
                "overrun_percentage": overrun_pct,
                "factor": "COST_OVERRUN",
                "evidence": evidence,
                "original_cost": project.original_cost,
                "revised_cost": project.revised_cost,
            },
        })

    # 3. LOW PROGRESS / LAG ALERT
    prog_factor = factor_map.get("LOW_PHYSICAL_PROGRESS")
    if prog_factor and (prog_factor.get("triggered") or prog_factor.get("severity") in ("MEDIUM", "HIGH", "CRITICAL")):
        evidence = prog_factor.get("evidence", {})
        prog_sev = prog_factor.get("severity", "LOW")
        lag_pct = evidence.get("progress_gap", 0.0)
        curr_prog = float(getattr(project, "physical_progress", None) or getattr(project, "progress_percentage", 0.0) or 0.0)

        sev = AlertSeverity.LOW.value
        if prog_sev == "CRITICAL" or lag_pct >= ALERT_CONFIG["progress_lag"]["critical_pct"]:
            sev = AlertSeverity.CRITICAL.value
        elif prog_sev == "HIGH" or lag_pct >= ALERT_CONFIG["progress_lag"]["high_pct"]:
            sev = AlertSeverity.HIGH.value
        elif prog_sev == "MEDIUM" or lag_pct >= ALERT_CONFIG["progress_lag"]["medium_pct"]:
            sev = AlertSeverity.MEDIUM.value

        candidates.append({
            "alert_type": AlertType.LOW_PROGRESS.value,
            "severity": sev,
            "source": AlertSource.RULE_ENGINE.value,
            "title": f"Physical Progress Lag: {round(curr_prog, 1)}% Completed",
            "message": (
                f"Physical execution progress on project '{project.name}' is currently {round(curr_prog, 1)}%, "
                f"lagging significantly behind elapsed time."
            ),
            "risk_score": int(prog_factor.get("contribution", 0)),
            "metadata": {
                "progress_percentage": curr_prog,
                "progress_gap": lag_pct,
                "evidence": evidence,
            },
        })

    # 4. MILESTONE DELAY ALERT
    mile_factor = factor_map.get("MILESTONE_DELAYS")
    if mile_factor and (mile_factor.get("triggered") or mile_factor.get("severity") in ("MEDIUM", "HIGH", "CRITICAL")):
        evidence = mile_factor.get("evidence", {})
        mile_sev = mile_factor.get("severity", "LOW")
        overdue_cnt = evidence.get("delayed_milestones", evidence.get("delayed_count", 0))

        sev = AlertSeverity.MEDIUM.value
        if overdue_cnt >= ALERT_CONFIG["milestone_delay"]["critical_overdue_count"] or mile_sev == "CRITICAL":
            sev = AlertSeverity.CRITICAL.value
        elif overdue_cnt >= ALERT_CONFIG["milestone_delay"]["high_overdue_count"] or mile_sev == "HIGH":
            sev = AlertSeverity.HIGH.value

        candidates.append({
            "alert_type": AlertType.MILESTONE_DELAY.value,
            "severity": sev,
            "source": AlertSource.RULE_ENGINE.value,
            "title": f"Milestone Execution Delays: {overdue_cnt} Milestone(s) Overdue",
            "message": (
                f"Project '{project.name}' has {overdue_cnt} delayed or overdue milestone(s) "
                f"requiring field intervention."
            ),
            "risk_score": int(mile_factor.get("contribution", 0)),
            "metadata": {
                "delayed_milestones_count": overdue_cnt,
                "evidence": evidence,
            },
        })

    # 5. OVERALL HIGH / CRITICAL PROJECT RISK ALERT
    if overall_score >= ALERT_CONFIG["overall_risk_score"]["critical_score"]:
        candidates.append({
            "alert_type": AlertType.CRITICAL_RISK.value,
            "severity": AlertSeverity.CRITICAL.value,
            "source": AlertSource.RISK_INTELLIGENCE.value,
            "title": f"Critical Project Risk Level ({round(overall_score, 1)}/100)",
            "message": (
                f"Project '{project.name}' is exhibiting critical comprehensive risk indicators "
                f"across observed field metrics and predictive signals."
            ),
            "risk_score": int(overall_score),
            "metadata": {
                "overall_risk_score": overall_score,
                "overall_risk_level": overall_level,
                "signal_summary": risk_intel.get("risk_summary", {}),
            },
        })
    elif overall_score >= ALERT_CONFIG["overall_risk_score"]["high_score"]:
        candidates.append({
            "alert_type": AlertType.HIGH_RISK.value,
            "severity": AlertSeverity.HIGH.value,
            "source": AlertSource.RISK_INTELLIGENCE.value,
            "title": f"Elevated Project Risk Level ({round(overall_score, 1)}/100)",
            "message": (
                f"Project '{project.name}' has crossed the high risk threshold ({round(overall_score, 1)}/100). "
                f"Close monitoring and corrective action recommended."
            ),
            "risk_score": int(overall_score),
            "metadata": {
                "overall_risk_score": overall_score,
                "overall_risk_level": overall_level,
                "signal_summary": risk_intel.get("risk_summary", {}),
            },
        })

    # 6. PREDICTED COST OVERRUN (ML)
    if cost_ml.get("is_available") and (float(cost_ml.get("probability", 0.0)) >= ALERT_CONFIG["ml_prediction"]["medium_prob"] or cost_ml.get("prediction") == "OVERRUN_RISK"):
        c_prob = float(cost_ml.get("probability", 0.0))
        if c_prob >= ALERT_CONFIG["ml_prediction"]["medium_prob"]:
            sev = AlertSeverity.MEDIUM.value
            if c_prob >= ALERT_CONFIG["ml_prediction"]["critical_prob"]:
                sev = AlertSeverity.CRITICAL.value
            elif c_prob >= ALERT_CONFIG["ml_prediction"]["high_prob"]:
                sev = AlertSeverity.HIGH.value

            candidates.append({
                "alert_type": AlertType.PREDICTED_COST_OVERRUN.value,
                "severity": sev,
                "source": AlertSource.COST_PREDICTOR.value,
                "title": f"Predictive Warning: Elevated Risk of Cost Overrun ({round(c_prob * 100, 1)}%)",
                "message": (
                    f"Machine Learning models indicate an estimated {round(c_prob * 100, 1)}% probability "
                    f"that project '{project.name}' may encounter budget escalation beyond sanction."
                ),
                "risk_score": int(c_prob * 100),
                "metadata": {
                    "predicted_probability": round(c_prob, 4),
                    "model_version": cost_ml.get("model_version", "v1.0.0"),
                    "top_drivers": cost_ml.get("top_factors", [])[:3],
                    "expected_overrun_percentage": cost_ml.get("expected_overrun_percentage"),
                },
            })

    # 7. PREDICTED TIME OVERRUN (ML)
    if time_ml.get("is_available") and (float(time_ml.get("probability", 0.0)) >= ALERT_CONFIG["ml_prediction"]["medium_prob"] or time_ml.get("prediction") == "OVERRUN_RISK"):
        t_prob = float(time_ml.get("probability", 0.0))
        if t_prob >= ALERT_CONFIG["ml_prediction"]["medium_prob"]:
            sev = AlertSeverity.MEDIUM.value
            if t_prob >= ALERT_CONFIG["ml_prediction"]["critical_prob"]:
                sev = AlertSeverity.CRITICAL.value
            elif t_prob >= ALERT_CONFIG["ml_prediction"]["high_prob"]:
                sev = AlertSeverity.HIGH.value

            candidates.append({
                "alert_type": AlertType.PREDICTED_TIME_OVERRUN.value,
                "severity": sev,
                "source": AlertSource.TIME_PREDICTOR.value,
                "title": f"Predictive Warning: Elevated Risk of Schedule Overrun ({round(t_prob * 100, 1)}%)",
                "message": (
                    f"Machine Learning models indicate an estimated {round(t_prob * 100, 1)}% probability "
                    f"that project '{project.name}' may experience extended schedule overrun."
                ),
                "risk_score": int(t_prob * 100),
                "metadata": {
                    "predicted_probability": round(t_prob, 4),
                    "model_version": time_ml.get("model_version", "v1.0.0"),
                    "top_drivers": time_ml.get("top_factors", [])[:3],
                    "expected_delay_days": time_ml.get("expected_delay_days"),
                },
            })

    # 8. DATA QUALITY ALERT
    dq_status = data_quality.get("status", "COMPLETE")
    missing_fields = data_quality.get("missing_data_fields", [])
    if dq_status in ("PARTIAL", "INSUFFICIENT_DATA") and missing_fields:
        dq_sev = AlertSeverity.HIGH.value if dq_status == "INSUFFICIENT_DATA" else AlertSeverity.LOW.value
        candidates.append({
            "alert_type": AlertType.DATA_QUALITY.value,
            "severity": dq_sev,
            "source": AlertSource.DATA_QUALITY.value,
            "title": f"Data Quality Notice: Missing Fields ({', '.join(missing_fields)})",
            "message": (
                f"Project '{project.name}' has incomplete baseline data for fields: {', '.join(missing_fields)}. "
                f"Risk intelligence computations may have limited accuracy until updated."
            ),
            "risk_score": 10 if dq_status == "PARTIAL" else 30,
            "metadata": {
                "data_quality_status": dq_status,
                "missing_fields": missing_fields,
                "missing_components": data_quality.get("missing_components", []),
            },
        })

    return candidates


def generate_alerts_for_project(
    project_id_or_code: Any,
    db: Session,
    current_user_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate, update, and deduplicate early warning alerts for a given project.
    """
    project = _find_project(project_id_or_code, db)
    if not project:
        return {
            "project_id": 0,
            "generated_count": 0,
            "existing_active_count": 0,
            "alerts": [],
            "summary": {"error": f"Project '{project_id_or_code}' not found."},
        }

    # 1. Retrieve Sub-Entities & Execute Rule Engine Baseline
    milestones = db.query(Milestone).filter(Milestone.project_id == project.id).all()
    progress_updates = db.query(ProgressUpdate).filter(ProgressUpdate.project_id == project.id).all()
    issues = db.query(Issue).filter(Issue.project_id == project.id).all()

    rule_res = evaluate_project_risk(project, milestones, progress_updates, issues)

    # 2. Generate Overall Risk Intelligence (ML + Aggregation)
    risk_intel = generate_overall_project_risk_intelligence(project.id, db)

    # 3. Evaluate Alert Rules
    candidates = _evaluate_project_alert_candidates(project, rule_res, risk_intel)

    # 4. Retrieve Active Alerts for Deduplication
    active_alerts_map = _get_active_alerts_map(project.id, db)

    processed_alerts = []
    generated_count = 0
    updated_count = 0

    candidate_types = set()

    for cand in candidates:
        a_type = cand["alert_type"]
        candidate_types.add(a_type)
        meta_str = json.dumps(cand.get("metadata", {}))

        if a_type in active_alerts_map:
            # DEDUPLICATION: Update existing active alert to keep fresh without duplicating row
            existing_alert = active_alerts_map[a_type]
            existing_alert.severity = cand["severity"]
            existing_alert.title = cand["title"]
            existing_alert.message = cand["message"]
            existing_alert.risk_score = cand["risk_score"]
            existing_alert.metadata_json = meta_str
            existing_alert.source = cand["source"]
            processed_alerts.append(existing_alert)
            updated_count += 1
        else:
            # Create new active alert
            new_alert = Alert(
                project_id=project.id,
                alert_type=cand["alert_type"],
                severity=cand["severity"],
                status=AlertStatus.UNREAD.value,
                source=cand["source"],
                title=cand["title"],
                message=cand["message"],
                risk_score=cand["risk_score"],
                metadata_json=meta_str,
                is_read=False,
                created_at=datetime.utcnow(),
            )
            db.add(new_alert)
            processed_alerts.append(new_alert)
            generated_count += 1

    db.commit()

    # Refresh processed alerts to get database IDs and dates
    for a in processed_alerts:
        db.refresh(a)

    return {
        "project_id": project.id,
        "project_code": project.project_code,
        "generated_count": generated_count,
        "existing_active_count": len(processed_alerts),
        "alerts": processed_alerts,
        "summary": {
            "new_alerts_created": generated_count,
            "existing_alerts_updated": updated_count,
            "total_active_alerts": len(processed_alerts),
            "overall_risk_score": risk_intel.get("overall_risk", {}).get("score", rule_res.get("risk_score", 0.0)),
            "overall_risk_level": risk_intel.get("overall_risk", {}).get("level", rule_res.get("risk_level", "LOW")),
        },
    }


def get_alerts(
    db: Session,
    project_id: Optional[int] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    alert_type: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
) -> Tuple[List[Alert], int]:
    """
    Query alerts with optional filters and pagination.
    """
    query = db.query(Alert)

    if project_id is not None:
        query = query.filter(Alert.project_id == project_id)

    if severity:
        query = query.filter(Alert.severity == severity.upper())

    if status:
        query = query.filter(Alert.status == status.upper())

    if alert_type:
        query = query.filter(Alert.alert_type == alert_type.upper())

    total = query.count()
    offset = max(0, (page - 1) * limit)
    items = query.order_by(desc(Alert.created_at)).offset(offset).limit(limit).all()

    return items, total


def get_alert_by_id(alert_id: int, db: Session) -> Optional[Alert]:
    """Retrieve a single alert by ID."""
    return db.query(Alert).filter(Alert.id == alert_id).first()


def update_alert_status(
    alert_id: int,
    new_status: str,
    db: Session,
    user_identifier: Optional[str] = None,
) -> Optional[Alert]:
    """
    Transition alert lifecycle status and update audit fields.
    Valid statuses: UNREAD, READ, RESOLVED, DISMISSED
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return None

    status_upper = new_status.upper()
    if status_upper not in [s.value for s in AlertStatus]:
        raise ValueError(f"Invalid alert status: '{new_status}'.")

    alert.status = status_upper

    if status_upper in (AlertStatus.READ.value, AlertStatus.RESOLVED.value, AlertStatus.DISMISSED.value):
        alert.is_read = True
    else:
        alert.is_read = False

    if status_upper in (AlertStatus.RESOLVED.value, AlertStatus.DISMISSED.value):
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = user_identifier or "SYSTEM_OFFICER"
    else:
        alert.resolved_at = None
        alert.resolved_by = None

    db.commit()
    db.refresh(alert)
    return alert


def bulk_generate_alerts(db: Session) -> Dict[str, Any]:
    """
    Run alert generation across all non-completed projects in the database.
    """
    projects = db.query(Project).all()
    results = []
    total_new = 0

    for p in projects:
        res = generate_alerts_for_project(p.id, db)
        total_new += res.get("generated_count", 0)
        results.append({
            "project_id": p.id,
            "project_code": p.project_code,
            "generated_count": res.get("generated_count", 0),
            "total_active_alerts": res.get("existing_active_count", 0),
        })

    return {
        "projects_scanned": len(projects),
        "total_new_alerts": total_new,
        "details": results,
    }

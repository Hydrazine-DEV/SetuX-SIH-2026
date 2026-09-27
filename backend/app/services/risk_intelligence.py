"""
SetuX — Overall Project Risk Intelligence Engine (Phase 15).
Combines:
1. Observed operational project conditions
2. Phase 11 Rule-Based Risk Engine baseline
3. Phase 13 Cost-Overrun Machine Learning Prediction
4. Phase 14 Time-Overrun Machine Learning Prediction
5. Database Analytics & Sub-Entity Signals

Provides structured, explainable, and traceable project-level intelligence with:
- Transparent engineering risk score (0-100) & risk level
- Explicit signal separation (OBSERVED vs PREDICTIVE)
- Double-counting prevention & risk factor categorization
- Data quality & component availability tracking
- Deterministic natural language summary & decision-support action recommendations
"""

from typing import Dict, Any, List, Optional, Union
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.milestone import Milestone
from app.models.progress import ProgressUpdate
from app.models.issue import Issue

from app.services.risk_engine import evaluate_project_risk, RISK_CONFIG
from app.services.schedule_analysis import calculate_project_delay, calculate_time_overrun
from app.services.cost_analysis import calculate_cost_overrun, calculate_budget_utilization

from app.ml.cost_overrun_predictor import predict_cost_overrun
from app.ml.time_overrun_predictor import predict_time_overrun


# Centralized Overall Risk Level Configuration
OVERALL_RISK_CONFIG = {
    "calculation_name": "SetuX Overall Risk Intelligence Score",
    "version": "v1.0.0",
    "disclaimer": (
        "The SetuX overall risk score is an engineering decision-support score that combines "
        "observed project indicators and predictive model outputs. It is not presented as a "
        "statistically validated probability of project failure."
    ),
    "level_thresholds": {
        "LOW": (0.0, 24.99),
        "MEDIUM": (25.0, 49.99),
        "HIGH": (50.0, 74.99),
        "CRITICAL": (75.0, 100.0),
    },
    "weights": {
        "observed_rule_weight": 0.70,
        "predictive_ml_weight": 0.30,
    },
}


def _determine_overall_level(score: float) -> str:
    """Map 0-100 overall score to risk level."""
    for level, (low, high) in OVERALL_RISK_CONFIG["level_thresholds"].items():
        if low <= score <= high:
            return level
    return "CRITICAL" if score > 75.0 else "LOW"


def generate_overall_project_risk_intelligence(
    project_id_or_code: str,
    db: Session,
) -> Dict[str, Any]:
    """
    Core Phase 15 Risk Intelligence Service.
    Integrates DB records, sub-entities, Phase 11 rule engine, Phase 13 Cost ML, and Phase 14 Time ML.
    """
    # 1. Locate Project
    p = db.query(Project).filter(Project.project_code == project_id_or_code).first()
    if not p and str(project_id_or_code).isdigit():
        p = db.query(Project).filter(Project.id == int(project_id_or_code)).first()

    if not p:
        return {
            "is_available": False,
            "error": f"Project '{project_id_or_code}' not found.",
        }

    # 2. Retrieve Sub-Entities
    milestones = db.query(Milestone).filter(Milestone.project_id == p.id).all()
    progress_updates = db.query(ProgressUpdate).filter(ProgressUpdate.project_id == p.id).all()
    issues = db.query(Issue).filter(Issue.project_id == p.id).all()

    # 3. Phase 11 Rule Engine Baseline Evaluation
    rule_res = evaluate_project_risk(p, milestones, progress_updates, issues)
    rule_score = float(rule_res.get("risk_score", 0.0))
    rule_level = rule_res.get("risk_level", "LOW")

    # 4. Construct Raw Dictionary for ML Predictors
    raw_dict = {
        "project_id": p.id,
        "project_code": p.project_code,
        "name": p.name,
        "sector": p.sector,
        "department_name": p.department_name,
        "district": p.district,
        "state": p.state,
        "contractor_name": p.contractor_name,
        "original_cost": p.original_cost,
        "revised_cost": p.revised_cost,
        "expenditure": p.total_expenditure if p.total_expenditure is not None else 0.0,
        "start_date": p.start_date,
        "planned_completion_date": p.planned_completion_date,
        "physical_progress": p.physical_progress,
        "financial_progress": p.financial_progress,
        "status": p.status,
        "total_milestones": len(milestones),
        "completed_milestones": sum(1 for m in milestones if (m.status or "").upper() == "COMPLETED"),
        "delayed_milestones": sum(1 for m in milestones if (m.status or "").upper() == "DELAYED"),
        "progress_update_count": len(progress_updates),
        "total_issues": len(issues),
        "open_issues": sum(1 for i in issues if (i.status or "").upper() in ("OPEN", "IN_PROGRESS")),
        "critical_issues": sum(
            1 for i in issues if (i.severity or "").upper() == "CRITICAL" and (i.status or "").upper() in ("OPEN", "IN_PROGRESS")
        ),
    }

    # 5. Model Inference (Cost ML & Time ML)
    cost_ml_res = predict_cost_overrun(raw_dict)
    time_ml_res = predict_time_overrun(raw_dict)

    cost_ml_available = cost_ml_res.get("is_available", False)
    time_ml_available = time_ml_res.get("is_available", False)

    # 6. Data Quality & Availability Audit
    available_components = ["rule_based_risk_engine"]
    missing_components = []
    missing_data_fields = []

    if cost_ml_available:
        available_components.append("cost_overrun_ml_model")
    else:
        missing_components.append("cost_overrun_ml_model")

    if time_ml_available:
        available_components.append("time_overrun_ml_model")
    else:
        missing_components.append("time_overrun_ml_model")

    if p.original_cost is None or p.original_cost <= 0:
        missing_data_fields.append("original_cost")
    if p.planned_completion_date is None:
        missing_data_fields.append("planned_completion_date")
    if len(milestones) == 0:
        missing_data_fields.append("milestones")
    if len(progress_updates) == 0:
        missing_data_fields.append("progress_updates")

    data_quality_status = "COMPLETE"
    if missing_components or missing_data_fields:
        data_quality_status = "PARTIAL"
    if len(missing_data_fields) >= 3:
        data_quality_status = "INSUFFICIENT_DATA"

    # 7. Transparent Engineering Risk Aggregation
    # Calculate Predictive ML Component Score S_ml
    ml_probs = []
    if cost_ml_available and "probability" in cost_ml_res:
        ml_probs.append(float(cost_ml_res["probability"]))
    if time_ml_available and "probability" in time_ml_res:
        ml_probs.append(float(time_ml_res["probability"]))

    if ml_probs:
        s_ml = (sum(ml_probs) / len(ml_probs)) * 100.0
        w_obs = OVERALL_RISK_CONFIG["weights"]["observed_rule_weight"]
        w_pred = OVERALL_RISK_CONFIG["weights"]["predictive_ml_weight"]
        overall_score = round(w_obs * rule_score + w_pred * s_ml, 2)
    else:
        s_ml = None
        overall_score = round(rule_score, 2)

    overall_level = _determine_overall_level(overall_score)

    # 8. Risk Factor Prioritization & Categorization (Double-Counting Safeguard)
    # A. Observed Operational Factors from Phase 11 Rule Engine
    observed_factors = []
    category_map = {
        "SCHEDULE_DELAY": ("SCHEDULE", "Project is experiencing baseline schedule execution delay."),
        "LOW_PHYSICAL_PROGRESS": ("PROGRESS", "Physical progress is lagging significantly behind elapsed timeline."),
        "COST_OVERRUN": ("COST", "Approved revised budget exceeds original sanctioned cost."),
        "FINANCIAL_PHYSICAL_MISMATCH": ("COST", "Financial expenditure progress leads physical completion progress."),
        "MILESTONE_DELAYS": ("MILESTONES", "Multiple project milestones are marked delayed."),
        "OPEN_ISSUES": ("ISSUES", "High volume of open or in-progress implementation issues."),
        "CRITICAL_ISSUES": ("ISSUES", "Unresolved critical severity issues present on project site."),
    }

    for f_item in rule_res.get("factors", []):
        f_key = f_item.get("factor")
        contrib = f_item.get("score_contribution", 0.0)
        cat, default_desc = category_map.get(f_key, ("OTHER", "Observed risk factor."))

        if contrib > 0 or f_item.get("severity") in ("MEDIUM", "HIGH", "CRITICAL"):
            observed_factors.append(
                {
                    "factor": f_key,
                    "category": cat,
                    "type": "OBSERVED",
                    "severity": f_item.get("severity", "LOW"),
                    "source": "rule_based_risk_engine",
                    "score_contribution": contrib,
                    "evidence": f_item.get("evidence", {}),
                    "explanation": f_item.get("details", default_desc),
                }
            )

    # B. Predictive Factors from ML Models
    predictive_factors = []
    if time_ml_available:
        t_prob = float(time_ml_res.get("probability", 0.0))
        t_sev = "CRITICAL" if t_prob >= 0.75 else ("HIGH" if t_prob >= 0.50 else ("MEDIUM" if t_prob >= 0.25 else "LOW"))
        predictive_factors.append(
            {
                "factor": "TIME_OVERRUN_ML_PREDICTION",
                "category": "SCHEDULE",
                "type": "PREDICTIVE",
                "severity": t_sev,
                "source": time_ml_res.get("model_name", "Time Overrun ML Model"),
                "model_version": time_ml_res.get("model_version", "v1.0.0"),
                "evidence": {
                    "predicted_probability": round(t_prob, 4),
                    "prediction_label": time_ml_res.get("prediction"),
                    "top_drivers": time_ml_res.get("top_factors", [])[:3],
                },
                "explanation": f"Machine Learning model predicts {round(t_prob * 100, 1)}% probability of schedule overrun past planned deadline.",
            }
        )

    if cost_ml_available:
        c_prob = float(cost_ml_res.get("probability", 0.0))
        c_sev = "CRITICAL" if c_prob >= 0.75 else ("HIGH" if c_prob >= 0.50 else ("MEDIUM" if c_prob >= 0.25 else "LOW"))
        predictive_factors.append(
            {
                "factor": "COST_OVERRUN_ML_PREDICTION",
                "category": "COST",
                "type": "PREDICTIVE",
                "severity": c_sev,
                "source": cost_ml_res.get("model_name", "Cost Overrun ML Model"),
                "model_version": cost_ml_res.get("model_version", "v1.0.0"),
                "evidence": {
                    "predicted_probability": round(c_prob, 4),
                    "prediction_label": cost_ml_res.get("prediction"),
                    "top_drivers": cost_ml_res.get("top_factors", [])[:3],
                },
                "explanation": f"Machine Learning model predicts {round(c_prob * 100, 1)}% probability of budget cost overrun.",
            }
        )

    # Merge and prioritize top factors by severity rank
    severity_rank = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    all_prioritized_factors = sorted(
        observed_factors + predictive_factors,
        key=lambda x: severity_rank.get(x["severity"], 0),
        reverse=True,
    )

    # 9. Deterministic Explanation Summary Generation (No LLM)
    summary_parts = []
    top_sev_factors = [f for f in all_prioritized_factors if f["severity"] in ("HIGH", "CRITICAL")]
    if top_sev_factors:
        drivers = ", ".join(f["factor"].replace("_", " ").title() for f in top_sev_factors[:3])
        summary_parts.append(
            f"Project overall risk is classified as {overall_level} (Score: {overall_score:.1f}/100) "
            f"driven primarily by {drivers}."
        )
    else:
        summary_parts.append(
            f"Project overall risk is classified as {overall_level} (Score: {overall_score:.1f}/100) "
            "with normal progress metrics and no critical active risk drivers."
        )

    if time_ml_available and time_ml_res.get("has_overrun_risk"):
        summary_parts.append(
            f"Time overrun ML model indicates elevated schedule risk ({round(time_ml_res['probability']*100, 1)}% probability)."
        )

    if cost_ml_available and cost_ml_res.get("has_overrun_risk"):
        summary_parts.append(
            f"Cost overrun ML model indicates potential budget overrun risk ({round(cost_ml_res['probability']*100, 1)}% probability)."
        )

    deterministic_summary = " ".join(summary_parts)

    # 10. Structured Action Recommendations
    recommendations = []
    has_schedule_issue = any(f["category"] == "SCHEDULE" and f["severity"] in ("HIGH", "CRITICAL") for f in all_prioritized_factors)
    has_cost_issue = any(f["category"] == "COST" and f["severity"] in ("HIGH", "CRITICAL") for f in all_prioritized_factors)
    has_milestone_issue = any(f["category"] == "MILESTONES" and f["severity"] in ("MEDIUM", "HIGH", "CRITICAL") for f in all_prioritized_factors)
    has_critical_issues = any(f["factor"] == "CRITICAL_ISSUES" for f in all_prioritized_factors)

    if has_schedule_issue:
        recommendations.append(
            "Review project completion schedule and request an updated milestone recovery plan from contractor."
        )
    if has_cost_issue:
        recommendations.append(
            "Audit financial disbursement progress against verified physical work completed to control cost overspending."
        )
    if has_milestone_issue:
        recommendations.append(
            "Conduct on-site inspection for delayed milestones and verify actual field progress."
        )
    if has_critical_issues:
        recommendations.append(
            "Escalate critical open site issues to department nodal officer for immediate resolution."
        )

    if not recommendations:
        recommendations.append(
            "Continue standard periodic physical and financial progress monitoring."
        )

    return {
        "is_available": True,
        "project_id": p.id,
        "project_code": p.project_code,
        "project_name": p.name,
        "department_name": p.department_name,
        "sector": p.sector,
        "district": p.district,
        "overall_risk": {
            "score": overall_score,
            "level": overall_level,
            "rule_based_baseline_score": rule_score,
            "predictive_ml_score": round(s_ml, 2) if s_ml is not None else None,
            "calculation_name": OVERALL_RISK_CONFIG["calculation_name"],
            "version": OVERALL_RISK_CONFIG["version"],
        },
        "cost_overrun_prediction": {
            "is_available": cost_ml_available,
            "prediction": cost_ml_res.get("prediction", "UNKNOWN"),
            "probability": cost_ml_res.get("probability", 0.0),
            "model_name": cost_ml_res.get("model_name"),
            "error": cost_ml_res.get("error") if not cost_ml_available else None,
        },
        "time_overrun_prediction": {
            "is_available": time_ml_available,
            "prediction": time_ml_res.get("prediction", "UNKNOWN"),
            "probability": time_ml_res.get("probability", 0.0),
            "model_name": time_ml_res.get("model_name"),
            "error": time_ml_res.get("error") if not time_ml_available else None,
        },
        "observed_factors": observed_factors,
        "predictive_factors": predictive_factors,
        "prioritized_risk_factors": all_prioritized_factors,
        "data_quality": {
            "status": data_quality_status,
            "available_components": available_components,
            "missing_components": missing_components,
            "missing_data_fields": missing_data_fields,
        },
        "summary": deterministic_summary,
        "recommended_actions": recommendations,
        "disclaimer": OVERALL_RISK_CONFIG["disclaimer"],
    }

"""
SetuX / VeriX — Cost Analysis Service
Provides exact cost overrun calculations, budget utilization metrics, and cost health assessment.
Handles null/zero-safe computations for incomplete project data.
"""
from typing import Optional, Dict, Any


def calculate_cost_overrun(
    original_cost: Optional[float],
    revised_cost: Optional[float],
    total_expenditure: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Calculate cost overrun metrics for a project.

    Returns:
        cost_overrun_pct: (revised - original) / original * 100
        cost_overrun_amount: revised - original (in Lakhs)
        has_overrun: bool
        expenditure_overrun_pct: expenditure vs original cost
        details: human-readable summary
    """
    orig = original_cost or 0.0
    rev = revised_cost or orig
    exp = total_expenditure or 0.0

    if orig <= 0:
        return {
            "cost_overrun_pct": 0.0,
            "cost_overrun_amount": 0.0,
            "has_overrun": False,
            "budget_utilization_pct": 0.0,
            "expenditure_overrun_pct": 0.0,
            "original_cost": orig,
            "revised_cost": rev,
            "total_expenditure": exp,
            "details": "Original cost not set — cost overrun cannot be calculated.",
        }

    cost_overrun_amount = rev - orig
    cost_overrun_pct = round((cost_overrun_amount / orig) * 100, 2)
    has_overrun = cost_overrun_pct > 0

    budget_utilization_pct = round((exp / orig) * 100, 2) if orig > 0 else 0.0
    expenditure_overrun_pct = round(((exp - orig) / orig) * 100, 2) if orig > 0 else 0.0

    if has_overrun:
        details = f"Cost overrun of {cost_overrun_pct}% (₹{cost_overrun_amount:.2f} Lakhs over original budget)."
    elif cost_overrun_pct < 0:
        details = f"Budget reduced by {abs(cost_overrun_pct)}% from original estimate."
    else:
        details = "No cost overrun — revised cost equals original budget."

    return {
        "cost_overrun_pct": cost_overrun_pct,
        "cost_overrun_amount": round(cost_overrun_amount, 2),
        "has_overrun": has_overrun,
        "budget_utilization_pct": budget_utilization_pct,
        "expenditure_overrun_pct": expenditure_overrun_pct,
        "original_cost": orig,
        "revised_cost": rev,
        "total_expenditure": exp,
        "details": details,
    }


def calculate_budget_utilization(
    original_cost: Optional[float],
    total_expenditure: Optional[float],
) -> Dict[str, Any]:
    """
    Calculate budget utilization rate.

    Returns:
        utilization_pct: (expenditure / original_cost) * 100
        remaining_budget: original - expenditure
        is_over_budget: bool
    """
    orig = original_cost or 0.0
    exp = total_expenditure or 0.0

    if orig <= 0:
        return {
            "utilization_pct": 0.0,
            "remaining_budget": 0.0,
            "is_over_budget": False,
            "details": "Original cost not set.",
        }

    utilization_pct = round((exp / orig) * 100, 2)
    remaining = round(orig - exp, 2)
    is_over = exp > orig

    return {
        "utilization_pct": utilization_pct,
        "remaining_budget": remaining,
        "is_over_budget": is_over,
        "details": f"Budget {'exceeded' if is_over else 'within limits'} — {utilization_pct}% utilized.",
    }


def assess_cost_health(cost_overrun_pct: float) -> str:
    """Map cost overrun percentage to health status."""
    if cost_overrun_pct >= 30:
        return "CRITICAL"
    elif cost_overrun_pct >= 15:
        return "HIGH"
    elif cost_overrun_pct >= 5:
        return "MEDIUM"
    elif cost_overrun_pct > 0:
        return "LOW"
    else:
        return "HEALTHY"

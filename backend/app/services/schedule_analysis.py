"""
SetuX / VeriX — Schedule & Delay Analysis Service
Provides transparent, deterministic delay calculations for milestones and projects.
Handles:
- Planned vs actual dates
- Planned vs current date for ongoing works
- Revised completion dates
- Missing/incomplete date handling without hallucination
"""
from datetime import datetime, date
from typing import Optional, Dict, Any


def parse_date(date_val: Optional[str]) -> Optional[date]:
    """Safely parse date string in YYYY-MM-DD or ISO format."""
    if not date_val:
        return None
    val = date_val.strip()
    # Try ISO or standard YYYY-MM-DD
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(val[:10], fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def calculate_milestone_delay(
    planned_date_str: Optional[str],
    actual_date_str: Optional[str] = None,
    status: Optional[str] = None,
    reference_date: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Calculate schedule delay for a milestone.
    Returns:
      is_delayed: bool
      delay_days: int (>= 0 if delayed, 0 if on time or ahead)
      status_evaluated: str
      details: str
    """
    if reference_date is None:
        reference_date = date.today()

    p_date = parse_date(planned_date_str)
    a_date = parse_date(actual_date_str)

    if not p_date:
        return {
            "is_delayed": False,
            "delay_days": 0,
            "status_evaluated": status or "UNKNOWN",
            "details": "Planned date not set.",
        }

    status_upper = (status or "").upper().strip()

    # 1. Milestone is Completed
    if status_upper == "COMPLETED" or a_date is not None:
        eval_date = a_date if a_date else reference_date
        delta = (eval_date - p_date).days
        is_delayed = delta > 0
        return {
            "is_delayed": is_delayed,
            "delay_days": max(0, delta),
            "status_evaluated": "COMPLETED" if status_upper == "COMPLETED" else status_upper,
            "details": f"Completed with {delta} days delay." if delta > 0 else f"Completed on time ({abs(delta)} days early)." if delta < 0 else "Completed exactly on target date.",
        }

    # 2. Milestone is Ongoing / Pending / In Progress
    delta = (reference_date - p_date).days
    is_delayed = delta > 0
    return {
        "is_delayed": is_delayed,
        "delay_days": max(0, delta),
        "status_evaluated": "DELAYED" if is_delayed else (status_upper or "IN_PROGRESS"),
        "details": f"Target milestone date exceeded by {delta} days." if is_delayed else f"On schedule ({abs(delta)} days remaining until target).",
    }


def calculate_project_delay(
    planned_date_str: Optional[str],
    revised_date_str: Optional[str] = None,
    actual_date_str: Optional[str] = None,
    status: Optional[str] = None,
    reference_date: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Calculate project-level schedule delay.
    Takes into account original planned completion, revised completion, and actual completion dates.
    """
    if reference_date is None:
        reference_date = date.today()

    p_date = parse_date(planned_date_str)
    r_date = parse_date(revised_date_str)
    a_date = parse_date(actual_date_str)

    target_date = r_date if r_date else p_date

    if not target_date:
        return {
            "is_delayed": False,
            "delay_days": 0,
            "has_revised_timeline": False,
            "details": "No planned completion date available.",
        }

    status_upper = (status or "").upper().strip()
    has_revised = r_date is not None and (p_date is None or r_date > p_date)

    # Completed project
    if status_upper == "COMPLETED" or a_date is not None:
        eval_date = a_date if a_date else reference_date
        delta = (eval_date - target_date).days
        is_delayed = delta > 0
        return {
            "is_delayed": is_delayed,
            "delay_days": max(0, delta),
            "has_revised_timeline": has_revised,
            "target_completion_date": str(target_date),
            "actual_completion_date": str(eval_date),
            "details": f"Project completed with {delta} days delay beyond target." if delta > 0 else "Project completed on or before target date.",
        }

    # Ongoing project
    delta = (reference_date - target_date).days
    is_delayed = delta > 0
    return {
        "is_delayed": is_delayed,
        "delay_days": max(0, delta),
        "has_revised_timeline": has_revised,
        "target_completion_date": str(target_date),
        "details": f"Project is {delta} days behind scheduled completion." if is_delayed else f"Project is within schedule ({abs(delta)} days remaining).",
    }


def calculate_time_overrun(
    planned_date_str: Optional[str],
    revised_date_str: Optional[str] = None,
    actual_date_str: Optional[str] = None,
    start_date_str: Optional[str] = None,
    reference_date: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Calculate time overrun metrics for a project.

    Returns:
        time_overrun_days: int (days beyond planned completion)
        time_overrun_pct: float (percentage of planned duration exceeded)
        planned_duration_days: int (total planned days)
        elapsed_days: int (days since start)
        time_elapsed_pct: float (percentage of planned time used)
        has_overrun: bool
        details: str
    """
    if reference_date is None:
        reference_date = date.today()

    p_date = parse_date(planned_date_str)
    r_date = parse_date(revised_date_str)
    a_date = parse_date(actual_date_str)
    s_date = parse_date(start_date_str)

    target_date = r_date if r_date else p_date

    if not target_date:
        return {
            "time_overrun_days": 0,
            "time_overrun_pct": 0.0,
            "planned_duration_days": 0,
            "elapsed_days": 0,
            "time_elapsed_pct": 0.0,
            "has_overrun": False,
            "details": "No completion date available for time overrun calculation.",
        }

    # Calculate planned duration
    if s_date and p_date:
        planned_duration = (p_date - s_date).days
    else:
        planned_duration = 365  # Default assumption: 1 year

    planned_duration = max(1, planned_duration)

    # Calculate elapsed time
    if s_date:
        elapsed_days = max(0, (reference_date - s_date).days)
    else:
        elapsed_days = 0

    time_elapsed_pct = round((elapsed_days / planned_duration) * 100, 2)

    # Completed project
    if a_date:
        overrun = (a_date - target_date).days
        overrun_pct = round((max(0, overrun) / planned_duration) * 100, 2)
        return {
            "time_overrun_days": max(0, overrun),
            "time_overrun_pct": overrun_pct,
            "planned_duration_days": planned_duration,
            "elapsed_days": elapsed_days,
            "time_elapsed_pct": time_elapsed_pct,
            "has_overrun": overrun > 0,
            "details": f"Completed {overrun} days {'late' if overrun > 0 else 'early'}." if overrun != 0 else "Completed on time.",
        }

    # Ongoing project
    overrun = (reference_date - target_date).days
    overrun_pct = round((max(0, overrun) / planned_duration) * 100, 2)
    has_overrun = overrun > 0

    return {
        "time_overrun_days": max(0, overrun),
        "time_overrun_pct": overrun_pct,
        "planned_duration_days": planned_duration,
        "elapsed_days": elapsed_days,
        "time_elapsed_pct": time_elapsed_pct,
        "has_overrun": has_overrun,
        "details": f"Project is {overrun} days past target completion." if has_overrun else f"Project has {abs(overrun)} days remaining.",
    }


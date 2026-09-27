"""
SetuX / VeriX — Analytics & Project Intelligence API Router
Phase 10: Real Database-Derived Infrastructure Analytics & Intelligence

Endpoints:
- GET /api/analytics/overview                         — High-level system overview statistics
- GET /api/analytics/projects                         — Project-level analytical metrics & filters
- GET /api/analytics/cost                             — Cost overrun & budget utilization metrics
- GET /api/analytics/progress                         — Historical progress metrics & trend indicators
- GET /api/analytics/milestones                       — Milestone completion & delay analytics
- GET /api/analytics/issues                           — Issue severity & status breakdown analytics
- GET /api/analytics/departments                      — Department-wise project & financial analytics
- GET /api/analytics/sectors                          — Sector-wise project & financial analytics
- GET /api/analytics/projects/{project_id}/progress-trend — Chronological project progress trend
- GET /api/analytics/projects/{project_id}/intelligence — Deterministic project intelligence summary
- GET /api/analytics/summary                          — Backward compatible summary endpoint
- GET /api/analytics/districts                        — Backward compatible district stats endpoint
- GET /api/analytics/priority                         — Backward compatible priority list endpoint
- GET /api/analytics/trends                           — Backward compatible completion trend endpoint
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, or_

from app.database.database import get_db
from app.models.project import Project
from app.models.milestone import Milestone
from app.models.issue import Issue
from app.models.progress import ProgressUpdate
from app.models.user import Department
from app.schemas.schemas import AnalyticsSummary, DistrictStat, PriorityProject
from app.services.cost_analysis import calculate_cost_overrun, calculate_budget_utilization, assess_cost_health
from app.services.schedule_analysis import calculate_project_delay, calculate_milestone_delay, calculate_time_overrun, parse_date

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


def _find_project(project_id_or_code: str, db: Session) -> Optional[Project]:
    """Helper to locate project by project_code or numeric ID."""
    p = db.query(Project).filter(Project.project_code == project_id_or_code).first()
    if not p and str(project_id_or_code).isdigit():
        p = db.query(Project).filter(Project.id == int(project_id_or_code)).first()
    return p


# ─── Part 1: Analytics Overview ────────────────────────────────────

@router.get("/overview")
def get_analytics_overview(db: Session = Depends(get_db)):
    """
    Return system-wide database-derived analytics overview statistics.
    Handles empty database safely without NaN or zero-division errors.
    """
    total_projects = db.query(Project).count()
    if total_projects == 0:
        return {
            "total_projects": 0,
            "ongoing_projects": 0,
            "completed_projects": 0,
            "delayed_projects": 0,
            "total_original_cost": 0.0,
            "total_revised_cost": 0.0,
            "total_expenditure": 0.0,
            "average_physical_progress": 0.0,
            "average_financial_progress": 0.0,
            "total_open_issues": 0,
            "total_critical_issues": 0,
            "total_delayed_milestones": 0,
        }

    projects = db.query(Project).all()

    completed_projects = sum(1 for p in projects if (p.status or "").upper() == "COMPLETED")
    ongoing_projects = total_projects - completed_projects

    delayed_projects = 0
    for p in projects:
        if (p.status or "").upper() in ("DELAYED", "HIGH RISK"):
            delayed_projects += 1
        else:
            delay_res = calculate_project_delay(
                p.planned_completion_date, p.revised_completion_date, p.actual_completion_date, p.status
            )
            if delay_res.get("is_delayed"):
                delayed_projects += 1

    total_orig_cost = sum(p.original_cost or 0.0 for p in projects)
    total_rev_cost = sum(p.revised_cost if p.revised_cost is not None else (p.original_cost or 0.0) for p in projects)
    total_expenditure = sum(p.total_expenditure or 0.0 for p in projects)

    avg_physical = sum(p.physical_progress or 0.0 for p in projects) / total_projects
    avg_financial = sum(p.financial_progress or 0.0 for p in projects) / total_projects

    total_open_issues = db.query(Issue).filter(Issue.status.in_(["OPEN", "IN_PROGRESS"])).count()
    total_critical_issues = db.query(Issue).filter(
        Issue.severity == "CRITICAL", Issue.status.in_(["OPEN", "IN_PROGRESS"])
    ).count()

    milestones = db.query(Milestone).all()
    today = date.today()
    total_delayed_milestones = 0
    for m in milestones:
        if (m.status or "").upper() == "DELAYED":
            total_delayed_milestones += 1
        elif (m.status or "").upper() != "COMPLETED":
            p_date = parse_date(m.target_completion_date or m.planned_completion_date)
            if p_date and p_date < today:
                total_delayed_milestones += 1

    return {
        "total_projects": total_projects,
        "ongoing_projects": ongoing_projects,
        "completed_projects": completed_projects,
        "delayed_projects": delayed_projects,
        "total_original_cost": round(total_orig_cost, 2),
        "total_revised_cost": round(total_rev_cost, 2),
        "total_expenditure": round(total_expenditure, 2),
        "average_physical_progress": round(avg_physical, 2),
        "average_financial_progress": round(avg_financial, 2),
        "total_open_issues": total_open_issues,
        "total_critical_issues": total_critical_issues,
        "total_delayed_milestones": total_delayed_milestones,
    }


# ─── Part 2: Project Analytics ──────────────────────────────────────

@router.get("/projects")
def get_projects_analytics(
    status_filter: Optional[str] = Query(None, alias="status"),
    department: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Return project-level analytical metrics with optional dimension filtering."""
    query = db.query(Project)

    if status_filter:
        query = query.filter(func.lower(Project.status) == status_filter.lower().strip())
    if department:
        query = query.filter(
            or_(
                func.lower(Project.department_name).contains(department.lower().strip()),
                Project.department_id == (int(department) if department.isdigit() else None)
            )
        )
    if sector:
        query = query.filter(func.lower(Project.sector) == sector.lower().strip())
    if state:
        query = query.filter(func.lower(Project.state) == state.lower().strip())
    if district:
        query = query.filter(func.lower(Project.district) == district.lower().strip())

    projects = query.all()
    results = []

    for p in projects:
        cost_res = calculate_cost_overrun(p.original_cost, p.revised_cost, p.total_expenditure)
        delay_res = calculate_project_delay(
            p.planned_completion_date, p.revised_completion_date, p.actual_completion_date, p.status
        )

        open_issues = db.query(Issue).filter(
            Issue.project_id == p.id, Issue.status.in_(["OPEN", "IN_PROGRESS"])
        ).count()
        critical_issues = db.query(Issue).filter(
            Issue.project_id == p.id, Issue.severity == "CRITICAL", Issue.status.in_(["OPEN", "IN_PROGRESS"])
        ).count()

        milestones = db.query(Milestone).filter(Milestone.project_id == p.id).all()
        today = date.today()
        delayed_m = 0
        for m in milestones:
            if (m.status or "").upper() == "DELAYED":
                delayed_m += 1
            elif (m.status or "").upper() != "COMPLETED":
                p_d = parse_date(m.target_completion_date or m.planned_completion_date)
                if p_d and p_d < today:
                    delayed_m += 1

        sched_status = "Completed" if (p.status or "").upper() == "COMPLETED" else ("Delayed" if delay_res.get("is_delayed") else "On Schedule")
        if not p.planned_completion_date and not p.revised_completion_date:
            sched_status = "Insufficient Data"

        results.append({
            "project_id": p.id,
            "project_code": p.project_code,
            "project_name": p.name,
            "status": p.status,
            "physical_progress": round(p.physical_progress or 0.0, 2),
            "financial_progress": round(p.financial_progress or 0.0, 2),
            "original_cost": round(p.original_cost or 0.0, 2),
            "revised_cost": round(p.revised_cost if p.revised_cost is not None else (p.original_cost or 0.0), 2),
            "expenditure": round(p.total_expenditure or 0.0, 2),
            "cost_overrun_percentage": cost_res.get("cost_overrun_pct", 0.0),
            "open_issue_count": open_issues,
            "critical_issue_count": critical_issues,
            "delayed_milestone_count": delayed_m,
            "schedule_status": sched_status,
        })

    return results


# ─── Part 3: Cost Analytics ─────────────────────────────────────────

@router.get("/cost")
def get_cost_analytics(db: Session = Depends(get_db)):
    """Return system-wide cost overrun metrics, budget utilization, and cost health categories."""
    projects = db.query(Project).all()
    if not projects:
        return {
            "total_original_cost": 0.0,
            "total_revised_cost": 0.0,
            "total_expenditure": 0.0,
            "total_absolute_cost_increase": 0.0,
            "average_cost_overrun_percentage": 0.0,
            "projects_with_cost_increase": 0,
            "projects_with_significant_cost_increase": 0,
            "cost_health_breakdown": {"HEALTHY": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
        }

    total_orig = sum(p.original_cost or 0.0 for p in projects)
    total_rev = sum(p.revised_cost if p.revised_cost is not None else (p.original_cost or 0.0) for p in projects)
    total_exp = sum(p.total_expenditure or 0.0 for p in projects)

    abs_increase = 0.0
    projects_with_inc = 0
    projects_with_sig_inc = 0
    overrun_pcts = []
    health_counts = {"HEALTHY": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}

    for p in projects:
        cost_res = calculate_cost_overrun(p.original_cost, p.revised_cost, p.total_expenditure)
        pct = cost_res.get("cost_overrun_pct", 0.0)
        overrun_pcts.append(pct)

        amount = cost_res.get("cost_overrun_amount", 0.0)
        if amount > 0:
            abs_increase += amount
            projects_with_inc += 1
        if pct >= 15.0:
            projects_with_sig_inc += 1

        health = assess_cost_health(pct)
        health_counts[health] = health_counts.get(health, 0) + 1

    avg_overrun = round(sum(overrun_pcts) / len(overrun_pcts), 2) if overrun_pcts else 0.0

    return {
        "total_original_cost": round(total_orig, 2),
        "total_revised_cost": round(total_rev, 2),
        "total_expenditure": round(total_exp, 2),
        "total_absolute_cost_increase": round(abs_increase, 2),
        "average_cost_overrun_percentage": avg_overrun,
        "projects_with_cost_increase": projects_with_inc,
        "projects_with_significant_cost_increase": projects_with_sig_inc,
        "cost_health_breakdown": health_counts,
    }


# ─── Part 4: Progress Analytics ─────────────────────────────────────

@router.get("/progress")
def get_progress_analytics(db: Session = Depends(get_db)):
    """Return historical progress analysis, progress gaps, and lagging project indicators."""
    projects = db.query(Project).all()
    if not projects:
        return {
            "average_physical_progress": 0.0,
            "average_financial_progress": 0.0,
            "physical_vs_financial_gap": 0.0,
            "total_historical_updates": 0,
            "projects_with_stagnant_progress": 0,
            "projects_with_lagging_progress": 0,
        }

    total = len(projects)
    avg_phys = sum(p.physical_progress or 0.0 for p in projects) / total
    avg_fin = sum(p.financial_progress or 0.0 for p in projects) / total
    gap = round(avg_phys - avg_fin, 2)

    total_updates = db.query(ProgressUpdate).count()

    stagnant_count = 0
    lagging_count = 0

    for p in projects:
        # Check progress stagnation
        updates = db.query(ProgressUpdate).filter(ProgressUpdate.project_id == p.id).order_by(ProgressUpdate.created_at.desc()).limit(2).all()
        if len(updates) >= 2 and updates[0].physical_progress == updates[1].physical_progress:
            stagnant_count += 1
        elif (p.physical_progress or 0.0) == 0 and p.created_at:
            days_since = (datetime.utcnow() - p.created_at).days
            if days_since > 30:
                stagnant_count += 1

        # Check lagging progress relative to schedule time elapsed
        time_res = calculate_time_overrun(
            p.planned_completion_date, p.revised_completion_date, p.actual_completion_date, p.start_date
        )
        elapsed_pct = time_res.get("time_elapsed_pct", 0.0)
        phys = p.physical_progress or 0.0
        if elapsed_pct > 30 and phys < (elapsed_pct * 0.5):
            lagging_count += 1

    return {
        "average_physical_progress": round(avg_phys, 2),
        "average_financial_progress": round(avg_fin, 2),
        "physical_vs_financial_gap": gap,
        "total_historical_updates": total_updates,
        "projects_with_stagnant_progress": stagnant_count,
        "projects_with_lagging_progress": lagging_count,
    }


# ─── Part 5: Milestone Analytics ────────────────────────────────────

@router.get("/milestones")
def get_milestone_analytics(db: Session = Depends(get_db)):
    """Return milestone status breakdowns, completion percentage, and delayed project indicators."""
    total_milestones = db.query(Milestone).count()
    if total_milestones == 0:
        return {
            "total_milestones": 0,
            "completed_milestones": 0,
            "in_progress_milestones": 0,
            "delayed_milestones": 0,
            "not_started_milestones": 0,
            "milestone_completion_percentage": 0.0,
            "projects_with_delayed_milestones": 0,
        }

    milestones = db.query(Milestone).all()
    today = date.today()

    completed = 0
    in_progress = 0
    delayed = 0
    not_started = 0
    delayed_project_ids = set()

    for m in milestones:
        st = (m.status or "").upper().strip()
        if st == "COMPLETED":
            completed += 1
        elif st == "IN_PROGRESS":
            p_d = parse_date(m.target_completion_date or m.planned_completion_date)
            if p_d and p_d < today:
                delayed += 1
                delayed_project_ids.add(m.project_id)
            else:
                in_progress += 1
        elif st == "DELAYED":
            delayed += 1
            delayed_project_ids.add(m.project_id)
        else:
            p_d = parse_date(m.target_completion_date or m.planned_completion_date)
            if p_d and p_d < today:
                delayed += 1
                delayed_project_ids.add(m.project_id)
            else:
                not_started += 1

    completion_pct = round((completed / total_milestones) * 100, 2)

    return {
        "total_milestones": total_milestones,
        "completed_milestones": completed,
        "in_progress_milestones": in_progress,
        "delayed_milestones": delayed,
        "not_started_milestones": not_started,
        "milestone_completion_percentage": completion_pct,
        "projects_with_delayed_milestones": len(delayed_project_ids),
    }


# ─── Part 6: Issue Analytics ────────────────────────────────────────

@router.get("/issues")
def get_issue_analytics(db: Session = Depends(get_db)):
    """Return issue severity, status distributions, and projects with unresolved critical issues."""
    issues = db.query(Issue).all()
    if not issues:
        return {
            "total_issues": 0,
            "open_issues": 0,
            "in_progress_issues": 0,
            "resolved_issues": 0,
            "closed_issues": 0,
            "critical_issues": 0,
            "high_severity_issues": 0,
            "issues_by_severity": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
            "issues_by_status": {"OPEN": 0, "IN_PROGRESS": 0, "RESOLVED": 0, "CLOSED": 0},
            "projects_with_unresolved_critical_issues": 0,
        }

    total_issues = len(issues)
    by_sev = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    by_st = {"OPEN": 0, "IN_PROGRESS": 0, "RESOLVED": 0, "CLOSED": 0}
    critical_project_ids = set()

    for i in issues:
        sev = (i.severity or "MEDIUM").upper().strip()
        st = (i.status or "OPEN").upper().strip()

        by_sev[sev] = by_sev.get(sev, 0) + 1
        by_st[st] = by_st.get(st, 0) + 1

        if sev == "CRITICAL" and st in ("OPEN", "IN_PROGRESS"):
            critical_project_ids.add(i.project_id)

    return {
        "total_issues": total_issues,
        "open_issues": by_st.get("OPEN", 0),
        "in_progress_issues": by_st.get("IN_PROGRESS", 0),
        "resolved_issues": by_st.get("RESOLVED", 0),
        "closed_issues": by_st.get("CLOSED", 0),
        "critical_issues": by_sev.get("CRITICAL", 0),
        "high_severity_issues": by_sev.get("HIGH", 0),
        "issues_by_severity": by_sev,
        "issues_by_status": by_st,
        "projects_with_unresolved_critical_issues": len(critical_project_ids),
    }


# ─── Part 7: Department & Sector Analytics ──────────────────────────

@router.get("/departments")
def get_department_analytics(db: Session = Depends(get_db)):
    """Return aggregated project analytics grouped by Department."""
    departments = db.query(Department).all()
    results = []

    for dept in departments:
        projects = db.query(Project).filter(
            or_(Project.department_id == dept.id, Project.department_name == dept.name)
        ).all()
        if not projects:
            continue

        proj_count = len(projects)
        total_orig = sum(p.original_cost or 0.0 for p in projects)
        total_rev = sum(p.revised_cost if p.revised_cost is not None else (p.original_cost or 0.0) for p in projects)
        total_exp = sum(p.total_expenditure or 0.0 for p in projects)
        avg_prog = sum(p.physical_progress or 0.0 for p in projects) / proj_count

        delayed = 0
        open_issues = 0
        for p in projects:
            if (p.status or "").upper() in ("DELAYED", "HIGH RISK"):
                delayed += 1
            open_issues += db.query(Issue).filter(
                Issue.project_id == p.id, Issue.status.in_(["OPEN", "IN_PROGRESS"])
            ).count()

        results.append({
            "department_id": dept.id,
            "department_name": dept.name,
            "project_count": proj_count,
            "total_original_cost": round(total_orig, 2),
            "total_revised_cost": round(total_rev, 2),
            "total_expenditure": round(total_exp, 2),
            "average_physical_progress": round(avg_prog, 2),
            "delayed_projects_count": delayed,
            "open_issues_count": open_issues,
        })

    return results


@router.get("/sectors")
def get_sector_analytics(db: Session = Depends(get_db)):
    """Return aggregated project analytics grouped by Sector/Infrastructure type."""
    sectors = db.query(distinct(Project.sector)).all()
    results = []

    for (sec_name,) in sectors:
        if not sec_name:
            continue
        projects = db.query(Project).filter(Project.sector == sec_name).all()
        proj_count = len(projects)

        total_orig = sum(p.original_cost or 0.0 for p in projects)
        total_rev = sum(p.revised_cost if p.revised_cost is not None else (p.original_cost or 0.0) for p in projects)
        total_exp = sum(p.total_expenditure or 0.0 for p in projects)
        avg_prog = sum(p.physical_progress or 0.0 for p in projects) / proj_count

        delayed = 0
        open_issues = 0
        for p in projects:
            if (p.status or "").upper() in ("DELAYED", "HIGH RISK"):
                delayed += 1
            open_issues += db.query(Issue).filter(
                Issue.project_id == p.id, Issue.status.in_(["OPEN", "IN_PROGRESS"])
            ).count()

        results.append({
            "sector": sec_name,
            "project_count": proj_count,
            "total_original_cost": round(total_orig, 2),
            "total_revised_cost": round(total_rev, 2),
            "total_expenditure": round(total_exp, 2),
            "average_physical_progress": round(avg_prog, 2),
            "delayed_projects_count": delayed,
            "open_issues_count": open_issues,
        })

    return results


# ─── Part 9: Progress Trend ─────────────────────────────────────────

@router.get("/projects/{project_id}/progress-trend")
def get_project_progress_trend(project_id: str, db: Session = Depends(get_db)):
    """
    Return chronological progress update history and trend analysis for a project.
    """
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    updates = db.query(ProgressUpdate).filter(
        ProgressUpdate.project_id == project.id
    ).order_by(ProgressUpdate.created_at.asc()).all()

    timeline = []
    prev_progress = 0.0
    changes = []

    for idx, u in enumerate(updates):
        curr = float(u.physical_progress or 0.0)
        change = round(curr - prev_progress, 2) if idx > 0 else 0.0
        changes.append(change)

        report_dt = u.report_date or (u.created_at.strftime("%Y-%m-%d") if u.created_at else "")
        timeline.append({
            "id": u.id,
            "report_date": report_dt,
            "physical_progress": curr,
            "financial_progress": float(u.financial_progress or 0.0),
            "expenditure": float(u.expenditure or 0.0),
            "remarks": u.remarks or "",
            "change_from_previous": change,
        })
        prev_progress = curr

    total_reports = len(timeline)
    latest_progress = timeline[-1]["physical_progress"] if timeline else float(project.physical_progress or 0.0)
    previous_progress = timeline[-2]["physical_progress"] if total_reports >= 2 else 0.0
    latest_change = timeline[-1]["change_from_previous"] if timeline else 0.0
    avg_change = round(sum(changes) / len(changes), 2) if changes else 0.0

    stagnant = False
    if total_reports >= 2 and timeline[-1]["physical_progress"] == timeline[-2]["physical_progress"]:
        stagnant = True

    return {
        "project_id": project.project_code,
        "timeline": timeline,
        "total_reports_count": total_reports,
        "latest_physical_progress": latest_progress,
        "previous_physical_progress": previous_progress,
        "progress_change_latest": latest_change,
        "average_progress_change": avg_change,
        "stagnant_progress_indicator": stagnant,
    }


# ─── Part 10: Project Intelligence Summary ──────────────────────────

@router.get("/projects/{project_id}/intelligence")
def get_project_intelligence(project_id: str, db: Session = Depends(get_db)):
    """
    Return deterministic project intelligence summary combining cost, schedule, milestone,
    and issue analytics into transparent rule-based observations.
    """
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    # Cost analysis
    cost_res = calculate_cost_overrun(project.original_cost, project.revised_cost, project.total_expenditure)
    cost_health = assess_cost_health(cost_res.get("cost_overrun_pct", 0.0))

    # Schedule analysis
    delay_res = calculate_project_delay(
        project.planned_completion_date, project.revised_completion_date, project.actual_completion_date, project.status
    )
    time_res = calculate_time_overrun(
        project.planned_completion_date, project.revised_completion_date, project.actual_completion_date, project.start_date
    )

    # Milestone analysis
    milestones = db.query(Milestone).filter(Milestone.project_id == project.id).all()
    total_m = len(milestones)
    completed_m = sum(1 for m in milestones if (m.status or "").upper() == "COMPLETED")
    today = date.today()
    delayed_m = 0
    for m in milestones:
        if (m.status or "").upper() == "DELAYED":
            delayed_m += 1
        elif (m.status or "").upper() != "COMPLETED":
            p_d = parse_date(m.target_completion_date or m.planned_completion_date)
            if p_d and p_d < today:
                delayed_m += 1

    m_completion_pct = round((completed_m / total_m) * 100, 2) if total_m > 0 else 0.0

    # Issue analysis
    issues = db.query(Issue).filter(Issue.project_id == project.id).all()
    total_i = len(issues)
    open_i = sum(1 for i in issues if i.status in ("OPEN", "IN_PROGRESS"))
    critical_i = sum(1 for i in issues if i.severity == "CRITICAL" and i.status in ("OPEN", "IN_PROGRESS"))
    high_i = sum(1 for i in issues if i.severity == "HIGH" and i.status in ("OPEN", "IN_PROGRESS"))

    # Trend data sufficiency
    updates_count = db.query(ProgressUpdate).filter(ProgressUpdate.project_id == project.id).count()
    data_sufficiency = "SUFFICIENT" if updates_count >= 3 else ("PARTIAL" if updates_count > 0 else "INSUFFICIENT")

    # Generate deterministic observations
    observations = []
    if cost_res.get("has_overrun"):
        pct = cost_res.get("cost_overrun_pct")
        amt = cost_res.get("cost_overrun_amount")
        observations.append(f"Cost overrun of {pct}% detected (₹{amt:.2f} Lakhs over original budget).")

    if delay_res.get("is_delayed"):
        days = delay_res.get("delay_days", 0)
        observations.append(f"Project is {days} days behind target completion date.")

    if delayed_m > 0:
        observations.append(f"{delayed_m} milestone(s) are currently delayed beyond target dates.")

    if critical_i > 0:
        observations.append(f"{critical_i} unresolved CRITICAL issue(s) require immediate officer attention.")

    if not observations:
        observations.append("Project is progressing within expected schedule and budget boundaries.")

    return {
        "project_id": project.project_code,
        "project_code": project.project_code,
        "project_name": project.name,
        "status": project.status,
        "progress": {
            "physical": round(project.physical_progress or 0.0, 2),
            "financial": round(project.financial_progress or 0.0, 2),
            "gap": round((project.physical_progress or 0.0) - (project.financial_progress or 0.0), 2),
            "trend": "STEADY" if updates_count > 0 else "STAGNANT",
            "data_sufficiency": data_sufficiency,
        },
        "cost": {
            "original_cost": round(project.original_cost or 0.0, 2),
            "revised_cost": round(project.revised_cost if project.revised_cost is not None else (project.original_cost or 0.0), 2),
            "expenditure": round(project.total_expenditure or 0.0, 2),
            "overrun_percentage": cost_res.get("cost_overrun_pct", 0.0),
            "overrun_amount": cost_res.get("cost_overrun_amount", 0.0),
            "cost_health": cost_health,
        },
        "schedule": {
            "status": "Delayed" if delay_res.get("is_delayed") else ("Completed" if (project.status or "").upper() == "COMPLETED" else "On Schedule"),
            "planned_completion": project.planned_completion_date,
            "revised_completion": project.revised_completion_date,
            "delay_days": delay_res.get("delay_days", 0),
            "has_revised_timeline": delay_res.get("has_revised_timeline", False),
            "details": delay_res.get("details", ""),
        },
        "milestones": {
            "total": total_m,
            "completed": completed_m,
            "delayed": delayed_m,
            "completion_percentage": m_completion_pct,
        },
        "issues": {
            "total": total_i,
            "open": open_i,
            "critical": critical_i,
            "high": high_i,
        },
        "observations": observations,
    }


# ─── Backward-Compatible Endpoints ─────────────────────────────────

@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(db: Session = Depends(get_db)):
    """Return Maharashtra-wide analytics summary."""
    total = db.query(Project).count() or 1
    verified = db.query(Project).filter(Project.status == "Verified").count()
    review = db.query(Project).filter(Project.status == "Review Required").count()
    high_risk = db.query(Project).filter(Project.risk_level == "HIGH").count()
    delayed = db.query(Project).filter(Project.status == "Delayed").count()
    completed = db.query(Project).filter(Project.status == "Completed").count()

    avg_reported = db.query(func.avg(Project.physical_progress)).scalar() or 0
    avg_ai = db.query(func.avg(Project.ai_estimated_progress)).scalar() or 0
    inspection_rate = (review + high_risk) / total * 100

    return AnalyticsSummary(
        total_projects=total,
        verified=verified,
        review_required=review,
        high_risk=high_risk,
        delayed=delayed,
        completed=completed,
        avg_reported_progress=round(float(avg_reported), 1),
        avg_ai_estimated_progress=round(float(avg_ai), 1),
        inspection_rate=round(inspection_rate, 1),
    )


@router.get("/districts", response_model=List[DistrictStat])
def get_district_stats(db: Session = Depends(get_db)):
    """Return per-district statistics."""
    districts = db.query(Project.district).distinct().all()
    stats = []

    for (district,) in districts:
        if not district:
            continue
        projects = db.query(Project).filter(Project.district == district).all()
        total = len(projects)
        high_risk = sum(1 for p in projects if p.risk_level == "HIGH")
        avg_gap = sum(abs((p.physical_progress or 0.0) - (p.ai_estimated_progress or 0.0)) for p in projects) / total if total > 0 else 0

        stats.append(
            DistrictStat(
                district=district,
                total=total,
                high_risk=high_risk,
                avg_progress_gap=round(avg_gap, 1),
            )
        )

    return sorted(stats, key=lambda x: x.high_risk, reverse=True)


@router.get("/priority", response_model=List[PriorityProject])
def get_priority_list(db: Session = Depends(get_db)):
    """Return inspection priority list sorted by anomaly score."""
    projects = (
        db.query(Project)
        .filter(Project.anomaly_score > 40)
        .order_by(Project.anomaly_score.desc())
        .limit(20)
        .all()
    )

    results = []
    for p in projects:
        gap = abs((p.physical_progress or 0) - (p.ai_estimated_progress or 0))
        if gap >= 20:
            reason = f"Reported progress ({p.physical_progress}%) significantly exceeds AI estimate ({p.ai_estimated_progress}%)"
        elif p.anomaly_score >= 75:
            reason = "High anomaly score — multiple verification checks flagged"
        else:
            reason = "GPS or evidence inconsistency detected"

        results.append(
            PriorityProject(
                project_id=p.project_code,
                name=p.name,
                district=p.district or "",
                risk_score=p.anomaly_score or 0,
                reason=reason,
                reported_progress=int(p.physical_progress or 0),
                ai_estimated_progress=int(p.ai_estimated_progress or 0),
            )
        )
    return results


@router.get("/trends")
def get_trends(db: Session = Depends(get_db)):
    """Return completion trend data for dashboard charts."""
    return {
        "monthly_trend": [
            {"month": "Feb 2026", "reported": 62, "ai_estimated": 55},
            {"month": "Mar 2026", "reported": 68, "ai_estimated": 60},
            {"month": "Apr 2026", "reported": 73, "ai_estimated": 65},
            {"month": "May 2026", "reported": 78, "ai_estimated": 68},
            {"month": "Jun 2026", "reported": 81, "ai_estimated": 72},
            {"month": "Jul 2026", "reported": 84, "ai_estimated": 76},
            {"month": "Aug 2026", "reported": 84, "ai_estimated": 76},
        ],
        "type_distribution": [
            {"type": "Road Construction", "count": 8},
            {"type": "Road Repair", "count": 7},
            {"type": "Bridge", "count": 4},
            {"type": "School", "count": 4},
            {"type": "Water Pipeline", "count": 3},
            {"type": "Drainage", "count": 2},
            {"type": "Government Building", "count": 2},
        ],
    }


@router.get("/projects/{project_id}/risk")
def get_project_risk_analytics_endpoint(
    project_id: str,
    db: Session = Depends(get_db),
):
    """Return deterministic rule-based project risk evaluation for a project."""
    project = _find_project(project_id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    from app.models.milestone import Milestone
    from app.models.progress import ProgressUpdate
    from app.models.issue import Issue
    from app.services.risk_engine import evaluate_project_risk

    milestones = db.query(Milestone).filter(Milestone.project_id == project.id).all()
    progress_history = db.query(ProgressUpdate).filter(ProgressUpdate.project_id == project.id).all()
    issues = db.query(Issue).filter(Issue.project_id == project.id).all()

    return evaluate_project_risk(project, milestones, progress_history, issues)


@router.get("/projects/{project_id}/risk-intelligence")
def get_analytics_project_risk_intelligence(
    project_id: str,
    db: Session = Depends(get_db),
):
    """
    Return Overall Project Risk Intelligence for a given project (Phase 15 analytics alias).
    """
    from app.services.risk_intelligence import generate_overall_project_risk_intelligence

    res = generate_overall_project_risk_intelligence(project_id, db)
    if not res.get("is_available"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=res.get("error", f"Project '{project_id}' not found."),
        )
    return res



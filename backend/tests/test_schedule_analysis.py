"""
SetuX / VeriX — Schedule & Delay Analysis Service Unit Tests
Verifies:
- Milestone delay calculation for on-time, delayed, completed, and ongoing milestones
- Project delay calculation with planned, revised, and actual completion dates
- Missing/invalid date handling
"""
from datetime import date
from app.services.schedule_analysis import (
    calculate_milestone_delay,
    calculate_project_delay,
    parse_date,
)


def test_parse_date():
    assert parse_date("2026-10-15") == date(2026, 10, 15)
    assert parse_date(None) is None
    assert parse_date("invalid-date-string") is None


def test_milestone_delay_calculations():
    fixed_ref = date(2026, 9, 15)

    # 1. Ongoing milestone with past target date -> Delayed
    res_delayed = calculate_milestone_delay(
        planned_date_str="2026-08-31",
        status="IN_PROGRESS",
        reference_date=fixed_ref,
    )
    assert res_delayed["is_delayed"] is True
    assert res_delayed["delay_days"] == 15

    # 2. Ongoing milestone with future target date -> On Time
    res_ontime = calculate_milestone_delay(
        planned_date_str="2026-10-31",
        status="IN_PROGRESS",
        reference_date=fixed_ref,
    )
    assert res_ontime["is_delayed"] is False
    assert res_ontime["delay_days"] == 0

    # 3. Completed milestone finished ahead of time
    res_comp_early = calculate_milestone_delay(
        planned_date_str="2026-08-31",
        actual_date_str="2026-08-20",
        status="COMPLETED",
        reference_date=fixed_ref,
    )
    assert res_comp_early["is_delayed"] is False
    assert res_comp_early["delay_days"] == 0

    # 4. Completed milestone finished after target date
    res_comp_late = calculate_milestone_delay(
        planned_date_str="2026-08-01",
        actual_date_str="2026-08-20",
        status="COMPLETED",
        reference_date=fixed_ref,
    )
    assert res_comp_late["is_delayed"] is True
    assert res_comp_late["delay_days"] == 19

    # 5. Missing planned date
    res_missing = calculate_milestone_delay(planned_date_str=None)
    assert res_missing["is_delayed"] is False
    assert res_missing["delay_days"] == 0


def test_project_delay_calculations():
    fixed_ref = date(2026, 9, 15)

    # 1. Ongoing project with planned date in past -> Delayed
    proj_delayed = calculate_project_delay(
        planned_date_str="2026-08-01",
        status="In Progress",
        reference_date=fixed_ref,
    )
    assert proj_delayed["is_delayed"] is True
    assert proj_delayed["delay_days"] == 45

    # 2. Ongoing project with revised timeline
    proj_revised = calculate_project_delay(
        planned_date_str="2026-08-01",
        revised_date_str="2026-10-01",
        status="In Progress",
        reference_date=fixed_ref,
    )
    assert proj_revised["has_revised_timeline"] is True
    assert proj_revised["is_delayed"] is False  # Target is now Oct 1

    # 3. Completed project
    proj_comp = calculate_project_delay(
        planned_date_str="2026-05-01",
        actual_date_str="2026-05-20",
        status="Completed",
        reference_date=fixed_ref,
    )
    assert proj_comp["is_delayed"] is True
    assert proj_comp["delay_days"] == 19

    # 4. Missing dates
    proj_none = calculate_project_delay(planned_date_str=None)
    assert proj_none["is_delayed"] is False
    assert proj_none["delay_days"] == 0

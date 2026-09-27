"""
Data Validation Module for SetuX Data Pipeline.
Validates project schema, types, range constraints, and logical dependencies.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np


def validate_project_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Validates project dataset against defined business and logical rules.
    Returns:
        valid_df: DataFrame with validation status flags attached
        validation_report: Summary dictionary of passed and failed validation rules
    """
    if df.empty:
        return df.copy(), {
            "total_records": 0,
            "valid_records": 0,
            "invalid_records": 0,
            "errors": [],
            "rule_violations": {},
        }

    v_df = df.copy()
    violations = {
        "duplicate_ids": [],
        "invalid_costs": [],
        "invalid_progress": [],
        "invalid_dates": [],
        "logical_date_errors": [],
    }

    v_df["is_valid"] = True
    err_map = {idx: [] for idx in v_df.index}

    # 1. Unique ID check
    if "project_id" in v_df.columns:
        dups = v_df[v_df.duplicated(subset=["project_id"], keep=False)]
        if not dups.empty:
            for idx in dups.index:
                v_df.at[idx, "is_valid"] = False
                err_map[idx].append("Duplicate project_id")
            violations["duplicate_ids"] = dups["project_id"].tolist()

    # 2. Non-negative costs check
    cost_cols = ["original_cost", "revised_cost", "expenditure"]
    for col in cost_cols:
        if col in v_df.columns:
            s = pd.to_numeric(v_df[col], errors="coerce")
            invalid_mask = s.notnull() & (s < 0)
            if invalid_mask.any():
                for idx in v_df[invalid_mask].index:
                    v_df.at[idx, "is_valid"] = False
                    err_map[idx].append(f"Negative cost in {col}")
                    violations["invalid_costs"].append((idx, col, float(s.at[idx])))

    # 3. Progress bounds check (0 to 100)
    prog_cols = ["physical_progress", "financial_progress"]
    for col in prog_cols:
        if col in v_df.columns:
            s = pd.to_numeric(v_df[col], errors="coerce")
            invalid_mask = s.notnull() & ((s < 0) | (s > 100))
            if invalid_mask.any():
                for idx in v_df[invalid_mask].index:
                    v_df.at[idx, "is_valid"] = False
                    err_map[idx].append(f"Invalid progress out of range [0, 100] in {col}")
                    violations["invalid_progress"].append((idx, col, float(s.at[idx])))

    # 4. Date order checks
    if "start_date" in v_df.columns:
        s_date = pd.to_datetime(v_df["start_date"], errors="coerce")
        
        # Check start_date <= planned_completion_date
        if "planned_completion_date" in v_df.columns:
            p_date = pd.to_datetime(v_df["planned_completion_date"], errors="coerce")
            invalid_mask = s_date.notnull() & p_date.notnull() & (s_date > p_date)
            if invalid_mask.any():
                for idx in v_df[invalid_mask].index:
                    v_df.at[idx, "is_valid"] = False
                    err_map[idx].append("start_date > planned_completion_date")
                    violations["logical_date_errors"].append(idx)

        # Check start_date <= revised_completion_date
        if "revised_completion_date" in v_df.columns:
            r_date = pd.to_datetime(v_df["revised_completion_date"], errors="coerce")
            invalid_mask = s_date.notnull() & r_date.notnull() & (s_date > r_date)
            if invalid_mask.any():
                for idx in v_df[invalid_mask].index:
                    v_df.at[idx, "is_valid"] = False
                    err_map[idx].append("start_date > revised_completion_date")
                    violations["logical_date_errors"].append(idx)

        # Check start_date <= actual_completion_date
        if "actual_completion_date" in v_df.columns:
            a_date = pd.to_datetime(v_df["actual_completion_date"], errors="coerce")
            invalid_mask = s_date.notnull() & a_date.notnull() & (s_date > a_date)
            if invalid_mask.any():
                for idx in v_df[invalid_mask].index:
                    v_df.at[idx, "is_valid"] = False
                    err_map[idx].append("start_date > actual_completion_date")
                    violations["logical_date_errors"].append(idx)

    v_df["validation_errors"] = ["; ".join(err_map[idx]) for idx in v_df.index]

    # Summary report
    total_records = len(v_df)
    valid_records = int(v_df["is_valid"].sum())
    invalid_records = total_records - valid_records

    report = {
        "total_records": total_records,
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "rule_violations": {
            "duplicate_ids_count": len(violations["duplicate_ids"]),
            "invalid_costs_count": len(violations["invalid_costs"]),
            "invalid_progress_count": len(violations["invalid_progress"]),
            "logical_date_errors_count": len(set(violations["logical_date_errors"])),
        },
    }

    return v_df, report

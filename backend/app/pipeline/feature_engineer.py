"""
Feature Engineering Module for SetuX Data Pipeline.
Calculates domain-specific features and provides explicit feature definitions.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime


FEATURE_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "original_cost": {
        "definition": "Sanctioned baseline cost of the project in Lakhs/Crores",
        "source": ["original_cost"],
        "type": "float",
        "nullable": False,
        "potential_leakage": False,
        "intended_use": "Baseline magnitude for cost overrun model",
    },
    "revised_cost": {
        "definition": "Latest revised or approved cost of the project",
        "source": ["revised_cost"],
        "type": "float",
        "nullable": False,
        "potential_leakage": True,  # Leakage if predicting cost overrun before revision
        "intended_use": "Intermediate cost feature (Excluded when predicting initial overrun)",
    },
    "expenditure": {
        "definition": "Total financial expenditure disbursed to date",
        "source": ["expenditure"],
        "type": "float",
        "nullable": False,
        "potential_leakage": False,
        "intended_use": "Financial tracking feature",
    },
    "planned_duration_days": {
        "definition": "Total planned execution time in days (planned_completion_date - start_date)",
        "source": ["start_date", "planned_completion_date"],
        "type": "float",
        "nullable": True,
        "potential_leakage": False,
        "intended_use": "Project scale and time duration baseline",
    },
    "elapsed_duration_days": {
        "definition": "Days passed from start_date to snapshot_date (or current date)",
        "source": ["start_date"],
        "type": "float",
        "nullable": True,
        "potential_leakage": False,
        "intended_use": "Temporal progression feature",
    },
    "elapsed_duration_ratio": {
        "definition": "Ratio of elapsed days to total planned duration (elapsed / planned)",
        "source": ["start_date", "planned_completion_date"],
        "type": "float",
        "nullable": True,
        "potential_leakage": False,
        "intended_use": "Normalized project timeline position",
    },
    "physical_progress": {
        "definition": "Reported physical completion percentage (0-100%)",
        "source": ["physical_progress"],
        "type": "float",
        "nullable": False,
        "potential_leakage": False,
        "intended_use": "Core physical completion feature",
    },
    "financial_progress": {
        "definition": "Reported financial expenditure percentage (0-100%)",
        "source": ["financial_progress"],
        "type": "float",
        "nullable": False,
        "potential_leakage": False,
        "intended_use": "Core financial completion feature",
    },
    "progress_gap": {
        "definition": "Expected progress (elapsed_duration_ratio * 100) minus physical_progress",
        "source": ["elapsed_duration_ratio", "physical_progress"],
        "type": "float",
        "nullable": True,
        "potential_leakage": False,
        "intended_use": "Physical slippage indicator",
    },
    "financial_physical_gap": {
        "definition": "Financial progress minus physical progress",
        "source": ["financial_progress", "physical_progress"],
        "type": "float",
        "nullable": False,
        "potential_leakage": False,
        "intended_use": "Financial overspending relative to physical work done",
    },
    "budget_utilization_ratio": {
        "definition": "Expenditure divided by original_cost",
        "source": ["expenditure", "original_cost"],
        "type": "float",
        "nullable": True,
        "potential_leakage": False,
        "intended_use": "Budget burn rate",
    },
    "total_milestones": {
        "definition": "Total count of project milestones",
        "source": ["total_milestones"],
        "type": "int",
        "nullable": False,
        "potential_leakage": False,
        "intended_use": "Milestone complexity feature",
    },
    "delayed_milestone_ratio": {
        "definition": "Ratio of delayed milestones to total milestones",
        "source": ["delayed_milestones", "total_milestones"],
        "type": "float",
        "nullable": False,
        "potential_leakage": False,
        "intended_use": "Milestone delay intensity",
    },
    "unresolved_issue_ratio": {
        "definition": "Ratio of open issues to total issues",
        "source": ["open_issues", "total_issues"],
        "type": "float",
        "nullable": False,
        "potential_leakage": False,
        "intended_use": "Issue resolution efficiency",
    },
    "critical_issue_count": {
        "definition": "Count of critical severity unresolved issues",
        "source": ["critical_issues"],
        "type": "int",
        "nullable": False,
        "potential_leakage": False,
        "intended_use": "High impact risk signal",
    },
}


def engineer_project_features(df: pd.DataFrame, snapshot_date: datetime = None) -> pd.DataFrame:
    """
    Applies feature engineering transformations to cleaned project DataFrame.
    Features are strictly computed using information available at prediction time.
    """
    if df.empty:
        return df.copy()

    f_df = df.copy()
    if snapshot_date is None:
        snapshot_date = pd.Timestamp(datetime.now())
    else:
        snapshot_date = pd.Timestamp(snapshot_date)

    # 1. Base Costs & Financial Ratios
    orig_cost = pd.to_numeric(f_df["original_cost"], errors="coerce").fillna(0.0) if "original_cost" in f_df.columns else pd.Series(0.0, index=f_df.index)
    exp_cost = pd.to_numeric(f_df["expenditure"], errors="coerce").fillna(0.0) if "expenditure" in f_df.columns else pd.Series(0.0, index=f_df.index)
    safe_orig_cost = orig_cost.replace(0, np.nan)
    f_df["budget_utilization_ratio"] = (exp_cost / safe_orig_cost).fillna(0.0)

    # 2. Time & Duration Features
    if "start_date" in f_df.columns and "planned_completion_date" in f_df.columns:
        s_date = pd.to_datetime(f_df["start_date"], errors="coerce")
        p_date = pd.to_datetime(f_df["planned_completion_date"], errors="coerce")

        f_df["planned_duration_days"] = (p_date - s_date).dt.days
        f_df["planned_duration_days"] = f_df["planned_duration_days"].apply(lambda x: float(x) if pd.notnull(x) and float(x) > 0 else np.nan)

        f_df["elapsed_duration_days"] = (snapshot_date - s_date).dt.days
        f_df["elapsed_duration_days"] = f_df["elapsed_duration_days"].apply(lambda x: float(max(0, x)) if pd.notnull(x) else np.nan)

        safe_planned_dur = f_df["planned_duration_days"].replace(0, np.nan)
        f_df["elapsed_duration_ratio"] = (f_df["elapsed_duration_days"] / safe_planned_dur).fillna(0.0)

        # Expected progress assuming linear completion velocity
        f_df["expected_progress"] = (f_df["elapsed_duration_ratio"] * 100.0).clip(upper=100.0)
    else:
        f_df["planned_duration_days"] = np.nan
        f_df["elapsed_duration_days"] = np.nan
        f_df["elapsed_duration_ratio"] = 0.0
        f_df["expected_progress"] = 0.0

    # 3. Progress Gap Features
    phys = pd.to_numeric(f_df["physical_progress"], errors="coerce").fillna(0.0) if "physical_progress" in f_df.columns else pd.Series(0.0, index=f_df.index)
    fin = pd.to_numeric(f_df["financial_progress"], errors="coerce").fillna(0.0) if "financial_progress" in f_df.columns else pd.Series(0.0, index=f_df.index)

    f_df["financial_physical_gap"] = fin - phys
    f_df["progress_gap"] = f_df["expected_progress"] - phys

    # 4. Milestone Features
    tot_ms = pd.to_numeric(f_df["total_milestones"], errors="coerce").fillna(0) if "total_milestones" in f_df.columns else pd.Series(0, index=f_df.index)
    del_ms = pd.to_numeric(f_df["delayed_milestones"], errors="coerce").fillna(0) if "delayed_milestones" in f_df.columns else pd.Series(0, index=f_df.index)

    safe_tot_ms = tot_ms.replace(0, np.nan)
    f_df["delayed_milestone_ratio"] = (del_ms / safe_tot_ms).fillna(0.0)

    # 5. Issue Features
    tot_iss = pd.to_numeric(f_df["total_issues"], errors="coerce").fillna(0) if "total_issues" in f_df.columns else pd.Series(0, index=f_df.index)
    opn_iss = pd.to_numeric(f_df["open_issues"], errors="coerce").fillna(0) if "open_issues" in f_df.columns else pd.Series(0, index=f_df.index)

    safe_tot_iss = tot_iss.replace(0, np.nan)
    f_df["unresolved_issue_ratio"] = (opn_iss / safe_tot_iss).fillna(0.0)

    return f_df

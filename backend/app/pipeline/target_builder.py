"""
Target Engineering & Data Leakage Prevention Module for SetuX Data Pipeline.
Defines machine learning targets and excludes post-outcome leakage features.
"""

from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np


# Central registry of leakage exclusions per prediction target
LEAKAGE_EXCLUSIONS: Dict[str, List[Dict[str, str]]] = {
    "target_cost_overrun_flag": [
        {
            "feature": "revised_cost",
            "reason": "Direct leakage — revised_cost is the outcome variable used to define cost overrun.",
        },
        {
            "feature": "cost_overrun_pct",
            "reason": "Direct leakage — mathematical transform of the target itself.",
        },
        {
            "feature": "actual_completion_date",
            "reason": "Temporal leakage — project completion date is known only after project concludes.",
        },
        {
            "feature": "rule_based_risk_score",
            "reason": "Phase 11 risk score includes revised cost calculations. Excluded to prevent circular baseline leakage.",
        },
    ],
    "target_time_overrun_flag": [
        {
            "feature": "actual_completion_date",
            "reason": "Direct leakage — actual_completion_date is used directly to derive time overrun.",
        },
        {
            "feature": "time_overrun_days",
            "reason": "Direct leakage — exact target representation.",
        },
        {
            "feature": "target_time_overrun_days",
            "reason": "Direct leakage — target variable column representation.",
        },
        {
            "feature": "revised_completion_date",
            "reason": "Potential leakage — updated completion date reflects already acknowledged delays.",
        },
    ],
}


def build_target_variables(
    df: pd.DataFrame,
    cost_overrun_threshold_pct: float = 5.0,
    time_overrun_threshold_days: int = 30,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Constructs ML target variables for Cost Overrun and Time Overrun prediction.
    
    Target 1: Cost Overrun
      - target_cost_overrun_pct = ((revised_cost - original_cost) / original_cost) * 100
      - target_cost_overrun_flag = 1 if target_cost_overrun_pct > cost_overrun_threshold_pct else 0
      
    Target 2: Time Overrun (Defined strictly for completed or milestone-verified projects)
      - target_time_overrun_days = (actual_completion_date - planned_completion_date) in days
      - target_time_overrun_flag = 1 if target_time_overrun_days > time_overrun_threshold_days else 0
    """
    if df.empty:
        t_df = df.copy()
        t_df["target_cost_overrun_pct"] = np.nan
        t_df["target_cost_overrun_flag"] = np.nan
        t_df["target_time_overrun_days"] = np.nan
        t_df["target_time_overrun_flag"] = np.nan
        return t_df, {"total_targets": 0, "cost_overruns": 0, "time_overruns": 0}

    t_df = df.copy()

    # 1. Cost Overrun Targets
    if "revised_cost" in t_df.columns and "original_cost" in t_df.columns:
        orig = pd.to_numeric(t_df["original_cost"], errors="coerce").replace(0, np.nan)
        rev = pd.to_numeric(t_df["revised_cost"], errors="coerce")
        
        t_df["target_cost_overrun_pct"] = (((rev - orig) / orig) * 100.0).fillna(0.0)
        t_df["target_cost_overrun_flag"] = (t_df["target_cost_overrun_pct"] > cost_overrun_threshold_pct).astype(int)
    else:
        t_df["target_cost_overrun_pct"] = 0.0
        t_df["target_cost_overrun_flag"] = 0

    # 2. Time Overrun Targets
    if "start_date" in t_df.columns and "planned_completion_date" in t_df.columns:
        p_date = pd.to_datetime(t_df["planned_completion_date"], errors="coerce")
        
        comp_date = pd.Series([pd.NaT] * len(t_df), index=t_df.index)
        if "actual_completion_date" in t_df.columns:
            comp_date = pd.to_datetime(t_df["actual_completion_date"], errors="coerce")
        if "revised_completion_date" in t_df.columns:
            rev_date = pd.to_datetime(t_df["revised_completion_date"], errors="coerce")
            comp_date = comp_date.fillna(rev_date)

        time_diff = (comp_date - p_date).dt.days
        t_df["target_time_overrun_days"] = time_diff
        
        # Flag valid completed/revised dates
        valid_time_mask = time_diff.notnull()
        t_df["target_time_overrun_flag"] = np.nan
        t_df.loc[valid_time_mask, "target_time_overrun_flag"] = (
            time_diff[valid_time_mask] > time_overrun_threshold_days
        ).astype(int)
    else:
        t_df["target_time_overrun_days"] = np.nan
        t_df["target_time_overrun_flag"] = np.nan

    target_report = {
        "cost_overrun_threshold_pct": cost_overrun_threshold_pct,
        "time_overrun_threshold_days": time_overrun_threshold_days,
        "total_projects": len(t_df),
        "cost_overrun_positives": int((t_df["target_cost_overrun_flag"] == 1).sum()),
        "cost_overrun_negatives": int((t_df["target_cost_overrun_flag"] == 0).sum()),
        "time_overrun_positives": int((t_df["target_time_overrun_flag"] == 1).sum()),
        "time_overrun_negatives": int((t_df["target_time_overrun_flag"] == 0).sum()),
        "time_overrun_missing_targets": int(t_df["target_time_overrun_flag"].isnull().sum()),
    }

    return t_df, target_report


def detect_and_exclude_leakage(
    df: pd.DataFrame, target_name: str
) -> Tuple[pd.DataFrame, List[Dict[str, str]]]:
    """
    Excludes potential target leakage features from the feature matrix before ML consumption.
    Returns:
        clean_features_df: Feature DataFrame with leaked fields safely dropped.
        excluded_log: Detailed log listing dropped features and justifications.
    """
    if df.empty:
        return df.copy(), []

    f_df = df.copy()
    exclusions = LEAKAGE_EXCLUSIONS.get(target_name, [])
    excluded_log = []

    for item in exclusions:
        feat = item["feature"]
        reason = item["reason"]
        if feat in f_df.columns:
            f_df = f_df.drop(columns=[feat])
            excluded_log.append({"feature": feat, "reason": reason})

    return f_df, excluded_log

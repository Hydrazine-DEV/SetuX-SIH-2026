"""
Data Inspection Module for SetuX Data Pipeline.
Provides comprehensive raw data profiling and data quality checks.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


def inspect_raw_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs raw data inspection without altering data.
    Reports row/col counts, data types, missing values, duplicates,
    numeric statistics, categorical cardinality, and suspicious entries.
    """
    if df.empty:
        return {
            "num_rows": 0,
            "num_columns": 0,
            "columns": [],
            "data_types": {},
            "missing_counts": {},
            "missing_percentages": {},
            "unique_value_counts": {},
            "numeric_stats": {},
            "duplicate_rows": 0,
            "suspicious_values": {
                "invalid_physical_progress_count": 0,
                "invalid_financial_progress_count": 0,
                "negative_cost_count": 0,
                "invalid_date_order_count": 0,
            },
        }

    num_rows, num_cols = df.shape
    missing_counts = df.isnull().sum().to_dict()
    missing_percentages = (df.isnull().mean() * 100).round(2).to_dict()
    data_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
    unique_counts = df.nunique().to_dict()
    duplicate_rows = int(df.duplicated().sum())

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_stats = {}
    for col in numeric_cols:
        numeric_stats[col] = {
            "min": float(df[col].min()) if not df[col].isnull().all() else None,
            "max": float(df[col].max()) if not df[col].isnull().all() else None,
            "mean": float(df[col].mean()) if not df[col].isnull().all() else None,
            "std": float(df[col].std()) if not df[col].isnull().all() else None,
            "missing": int(df[col].isnull().sum()),
        }

    # Suspicious value checks
    invalid_phys_prog = 0
    if "physical_progress" in df.columns:
        s = pd.to_numeric(df["physical_progress"], errors="coerce")
        invalid_phys_prog = int(((s < 0) | (s > 100)).sum())

    invalid_fin_prog = 0
    if "financial_progress" in df.columns:
        s = pd.to_numeric(df["financial_progress"], errors="coerce")
        invalid_fin_prog = int(((s < 0) | (s > 100)).sum())

    negative_costs = 0
    cost_cols = [c for c in ["original_cost", "revised_cost", "expenditure"] if c in df.columns]
    for c in cost_cols:
        s = pd.to_numeric(df[c], errors="coerce")
        negative_costs += int((s < 0).sum())

    invalid_date_order = 0
    if "start_date" in df.columns and "planned_completion_date" in df.columns:
        s_date = pd.to_datetime(df["start_date"], errors="coerce")
        p_date = pd.to_datetime(df["planned_completion_date"], errors="coerce")
        valid_both = s_date.notnull() & p_date.notnull()
        invalid_date_order = int((valid_both & (s_date > p_date)).sum())

    return {
        "num_rows": num_rows,
        "num_columns": num_cols,
        "columns": list(df.columns),
        "data_types": data_types,
        "missing_counts": missing_counts,
        "missing_percentages": missing_percentages,
        "unique_value_counts": unique_counts,
        "numeric_stats": numeric_stats,
        "duplicate_rows": duplicate_rows,
        "suspicious_values": {
            "invalid_physical_progress_count": invalid_phys_prog,
            "invalid_financial_progress_count": invalid_fin_prog,
            "negative_cost_count": negative_costs,
            "invalid_date_order_count": invalid_date_order,
        },
    }

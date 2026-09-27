"""
Data Cleaning Module for SetuX Data Pipeline.
Implements controlled, documented data cleaning and imputation.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np


def clean_project_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans raw project DataFrame using documented imputation and normalization strategies.
    
    Imputation Rationale:
    1. Categorical fields (department, sector, contractor, state): Missing values replaced with 'UNKNOWN'.
       WHY: Preserves rows without inventing missing real-world assignments.
    2. Revised Cost: Missing revised_cost imputed with original_cost.
       WHY: If no cost revision occurred, the baseline budget remains the original cost.
    3. Expenditure: Missing expenditure imputed with 0.0.
       WHY: Unreported expenditure safely assumes zero recorded disbursements.
    4. Dates: Preserved as NaT if missing.
       WHY: Never fabricate start or completion dates to avoid temporal corruption.
    5. Progress: Numeric conversion with NaN handling. Impossible values (>100 or <0) clipped to boundary [0.0, 100.0].
    """
    if df.empty:
        return df.copy(), {
            "initial_rows": 0,
            "cleaned_rows": 0,
            "deduplicated_rows": 0,
            "imputations": {},
        }

    c_df = df.copy()
    initial_rows = len(c_df)

    # 1. Deduplicate exact duplicate rows
    c_df = c_df.drop_duplicates()
    deduplicated_rows = initial_rows - len(c_df)

    cleaning_report = {
        "initial_rows": initial_rows,
        "cleaned_rows": len(c_df),
        "deduplicated_rows": deduplicated_rows,
        "imputations": {},
    }

    # 2. String normalization (strip whitespace, upper/lower standardization)
    str_cols = ["department_name", "sector", "state", "contractor_name", "project_status", "risk_level"]
    for col in str_cols:
        if col in c_df.columns:
            c_df[col] = c_df[col].astype(str).str.strip()
            # Replace 'nan', 'None', '' with actual NA
            c_df[col] = c_df[col].replace(["nan", "None", "", "NaN"], np.nan)

    # 3. Categorical imputation with "UNKNOWN"
    cat_imputed_counts = {}
    for col in ["department_name", "sector", "state", "contractor_name"]:
        if col in c_df.columns:
            null_cnt = int(c_df[col].isnull().sum())
            if null_cnt > 0:
                c_df[col] = c_df[col].fillna("UNKNOWN")
                cat_imputed_counts[col] = null_cnt
    cleaning_report["imputations"]["categorical_unknown_imputations"] = cat_imputed_counts

    # 4. Numeric conversion & Cost imputation
    cost_imputations = {}
    if "original_cost" in c_df.columns:
        c_df["original_cost"] = pd.to_numeric(c_df["original_cost"], errors="coerce")

    if "revised_cost" in c_df.columns and "original_cost" in c_df.columns:
        c_df["revised_cost"] = pd.to_numeric(c_df["revised_cost"], errors="coerce")
        missing_revised = c_df["revised_cost"].isnull() & c_df["original_cost"].notnull()
        imputed_cnt = int(missing_revised.sum())
        c_df.loc[missing_revised, "revised_cost"] = c_df.loc[missing_revised, "original_cost"]
        cost_imputations["revised_cost_from_original"] = imputed_cnt

    if "expenditure" in c_df.columns:
        c_df["expenditure"] = pd.to_numeric(c_df["expenditure"], errors="coerce")
        missing_exp = c_df["expenditure"].isnull()
        imputed_exp = int(missing_exp.sum())
        c_df["expenditure"] = c_df["expenditure"].fillna(0.0)
        cost_imputations["expenditure_zero_filled"] = imputed_exp

    cleaning_report["imputations"]["cost_imputations"] = cost_imputations

    # 5. Progress clipping & bounds enforcement
    prog_clipping = {}
    for p_col in ["physical_progress", "financial_progress"]:
        if p_col in c_df.columns:
            c_df[p_col] = pd.to_numeric(c_df[p_col], errors="coerce")
            out_of_bounds = (c_df[p_col] < 0) | (c_df[p_col] > 100)
            clipped_cnt = int(out_of_bounds.sum())
            if clipped_cnt > 0:
                c_df[p_col] = c_df[p_col].clip(lower=0.0, upper=100.0)
            prog_clipping[p_col] = clipped_cnt
            c_df[p_col] = c_df[p_col].fillna(0.0)
    cleaning_report["imputations"]["progress_clipping"] = prog_clipping

    # 6. Date parsing (Preserve NaT if missing - DO NOT FABRICATE DATES)
    date_cols = ["start_date", "planned_completion_date", "revised_completion_date", "actual_completion_date"]
    for d_col in date_cols:
        if d_col in c_df.columns:
            c_df[d_col] = pd.to_datetime(c_df[d_col], errors="coerce")

    return c_df, cleaning_report

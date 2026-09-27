"""
End-to-End Data Pipeline & Dataset Builder for SetuX.
Executes load -> inspect -> validate -> clean -> engineer -> target -> leakage exclusion -> split.
"""

from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from app.pipeline.loader import load_project_data_from_db
from app.pipeline.inspector import inspect_raw_data
from app.pipeline.validator import validate_project_data
from app.pipeline.cleaner import clean_project_data
from app.pipeline.feature_engineer import engineer_project_features
from app.pipeline.target_builder import (
    build_target_variables,
    detect_and_exclude_leakage,
)


def run_historical_pipeline(
    db_session: Optional[Session] = None,
    raw_df: Optional[pd.DataFrame] = None,
    target_name: str = "target_cost_overrun_flag",
) -> Dict[str, Any]:
    """
    Runs the complete reproducible historical project data pipeline.
    Returns:
        Dictionary containing:
        - raw_df: Original uncleaned DataFrame
        - inspection_report: Raw data profiling report
        - valid_df: DataFrame after validation checks
        - validation_report: Validation summary
        - clean_df: Cleaned DataFrame with imputations
        - cleaning_report: Cleaning summary
        - feature_df: Engineered features DataFrame
        - target_df: DataFrame with computed target columns
        - ML_feature_matrix: Final feature matrix with target leakage excluded
        - excluded_leakage_features: List of excluded leakage features
        - quality_report: Comprehensive consolidated quality report
    """
    # 1. Load Data
    if raw_df is None:
        if db_session is None:
            raise ValueError("Either db_session or raw_df must be provided to run_historical_pipeline.")
        raw_df = load_project_data_from_db(db_session)

    # 2. Inspect Raw Data
    inspection_report = inspect_raw_data(raw_df)

    # 3. Validate Data
    validated_df, validation_report = validate_project_data(raw_df)

    # 4. Clean Data
    clean_df, cleaning_report = clean_project_data(validated_df)

    # 5. Engineer Features
    feature_df = engineer_project_features(clean_df)

    # 6. Build Target Variables
    target_df, target_report = build_target_variables(feature_df)

    # 7. Leakage Detection & Exclusion
    ml_feature_matrix, leakage_log = detect_and_exclude_leakage(target_df, target_name)

    # 8. Consolidated Data Quality Report
    quality_report = {
        "dataset_summary": {
            "total_raw_records": inspection_report["num_rows"],
            "usable_records": validation_report["valid_records"],
            "invalid_records": validation_report["invalid_records"],
            "duplicate_rows": inspection_report["duplicate_rows"],
            "engineered_features_count": len(feature_df.columns),
        },
        "inspection": inspection_report,
        "validation": validation_report,
        "cleaning": cleaning_report,
        "target_summary": target_report,
        "leakage_exclusions": leakage_log,
        "data_sufficiency_warning": (
            "Available dataset has fewer than 100 projects. "
            "Insufficient size for training production ML models."
            if inspection_report["num_rows"] < 100
            else None
        ),
    }

    return {
        "raw_df": raw_df,
        "inspection_report": inspection_report,
        "valid_df": validated_df,
        "validation_report": validation_report,
        "clean_df": clean_df,
        "cleaning_report": cleaning_report,
        "feature_df": feature_df,
        "target_df": target_df,
        "ml_feature_matrix": ml_feature_matrix,
        "excluded_leakage_features": leakage_log,
        "quality_report": quality_report,
    }


def split_dataset(
    df: pd.DataFrame,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    chronological: bool = True,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Splits feature matrix into Train / Validation / Test sets.
    Supports chronological splitting (by start_date) to prevent temporal leakage.
    """
    if df.empty:
        return df.copy(), df.copy(), df.copy(), {"total": 0, "train": 0, "val": 0, "test": 0}

    s_df = df.copy()

    if chronological and "start_date" in s_df.columns:
        s_df = s_df.sort_values(by="start_date").reset_index(drop=True)
    else:
        s_df = s_df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)

    n = len(s_df)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)

    train_df = s_df.iloc[:train_end].copy()
    val_df = s_df.iloc[train_end:val_end].copy()
    test_df = s_df.iloc[val_end:].copy()

    split_metrics = {
        "total_records": n,
        "train_count": len(train_df),
        "val_count": len(val_df),
        "test_count": len(test_df),
        "split_mode": "chronological" if chronological and "start_date" in df.columns else "random",
        "small_dataset_limitation": n < 50,
    }

    return train_df, val_df, test_df, split_metrics

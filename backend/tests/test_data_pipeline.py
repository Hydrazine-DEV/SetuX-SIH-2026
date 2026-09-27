"""
Unit and Integration Tests for SetuX Data Pipeline & Feature Engineering (Phase 12).
Covering loader, inspector, validator, cleaner, feature engineering, targets, leakage, splitting, and edge cases.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date

from app.pipeline.loader import (
    load_project_data_from_db,
    load_project_data_from_csv,
    generate_synthetic_dev_dataset,
)
from app.pipeline.inspector import inspect_raw_data
from app.pipeline.validator import validate_project_data
from app.pipeline.cleaner import clean_project_data
from app.pipeline.feature_engineer import engineer_project_features, FEATURE_DEFINITIONS
from app.pipeline.target_builder import build_target_variables, detect_and_exclude_leakage
from app.pipeline.dataset_builder import run_historical_pipeline, split_dataset


def test_1_data_loading_db(db_session):
    """Test 1: Data loading from SQLAlchemy Database session."""
    df = load_project_data_from_db(db_session)
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 0
    if not df.empty:
        assert "project_id" in df.columns
        assert "original_cost" in df.columns


def test_2_data_loading_csv(tmp_path):
    """Test 2: Data loading from CSV file."""
    csv_file = tmp_path / "test_projects.csv"
    dev_df = generate_synthetic_dev_dataset(num_projects=5)
    dev_df.to_csv(csv_file, index=False)

    loaded_df = load_project_data_from_csv(str(csv_file))
    assert len(loaded_df) == 5
    assert "project_id" in loaded_df.columns


def test_3_synthetic_dev_dataset():
    """Test 3: Synthetic development dataset generation."""
    synth_df = generate_synthetic_dev_dataset(num_projects=10, random_seed=42)
    assert len(synth_df) == 10
    assert "project_id" in synth_df.columns
    assert "original_cost" in synth_df.columns


def test_4_data_inspection():
    """Test 4: Raw data inspection and profiling."""
    df = generate_synthetic_dev_dataset(num_projects=10)
    report = inspect_raw_data(df)
    assert report["num_rows"] == 10
    assert report["num_columns"] == len(df.columns)
    assert "original_cost" in report["numeric_stats"]


def test_5_validation_valid_data():
    """Test 5: Validation of clean valid records."""
    df = generate_synthetic_dev_dataset(num_projects=5)
    v_df, report = validate_project_data(df)
    assert report["total_records"] == 5
    assert report["valid_records"] == 5
    assert report["invalid_records"] == 0


def test_6_validation_duplicate_detection():
    """Test 6: Validation rule - Duplicate project IDs."""
    df = generate_synthetic_dev_dataset(num_projects=3)
    # Force duplicate project_id
    df.loc[1, "project_id"] = df.loc[0, "project_id"]
    v_df, report = validate_project_data(df)
    assert report["invalid_records"] >= 2
    assert report["rule_violations"]["duplicate_ids_count"] >= 2


def test_7_validation_invalid_costs():
    """Test 7: Validation rule - Negative costs."""
    df = generate_synthetic_dev_dataset(num_projects=3)
    df.loc[0, "original_cost"] = -500.0
    v_df, report = validate_project_data(df)
    assert report["invalid_records"] >= 1
    assert report["rule_violations"]["invalid_costs_count"] >= 1


def test_8_validation_invalid_progress():
    """Test 8: Validation rule - Progress out of bounds (>100 or <0)."""
    df = generate_synthetic_dev_dataset(num_projects=3)
    df.loc[0, "physical_progress"] = 150.0
    df.loc[1, "financial_progress"] = -10.0
    v_df, report = validate_project_data(df)
    assert report["invalid_records"] >= 2
    assert report["rule_violations"]["invalid_progress_count"] == 2


def test_9_validation_invalid_dates():
    """Test 9: Validation rule - Start date after planned completion date."""
    df = generate_synthetic_dev_dataset(num_projects=3)
    df.loc[0, "start_date"] = "2025-12-31"
    df.loc[0, "planned_completion_date"] = "2025-01-01"
    v_df, report = validate_project_data(df)
    assert report["invalid_records"] >= 1
    assert report["rule_violations"]["logical_date_errors_count"] >= 1


def test_10_cleaning_imputations():
    """Test 10: Cleaning logic - String normalization and missing categoricals."""
    df = generate_synthetic_dev_dataset(num_projects=3)
    df.loc[0, "department_name"] = None
    df.loc[1, "revised_cost"] = None

    c_df, report = clean_project_data(df)
    assert c_df.loc[0, "department_name"] == "UNKNOWN"
    assert c_df.loc[1, "revised_cost"] == c_df.loc[1, "original_cost"]


def test_11_feature_engineering_cost():
    """Test 11: Feature calculation - Cost ratios & budget utilization."""
    df = generate_synthetic_dev_dataset(num_projects=3)
    f_df = engineer_project_features(df)
    assert "budget_utilization_ratio" in f_df.columns
    assert (f_df["budget_utilization_ratio"] >= 0).all()


def test_12_feature_engineering_progress_gaps():
    """Test 12: Feature calculation - Financial vs Physical progress gap."""
    df = generate_synthetic_dev_dataset(num_projects=3)
    df.loc[0, "financial_progress"] = 80.0
    df.loc[0, "physical_progress"] = 50.0

    f_df = engineer_project_features(df)
    assert f_df.loc[0, "financial_physical_gap"] == 30.0


def test_13_feature_engineering_milestone_and_issues():
    """Test 13: Feature calculation - Milestone and issue ratios."""
    df = generate_synthetic_dev_dataset(num_projects=3)
    f_df = engineer_project_features(df)
    assert "delayed_milestone_ratio" in f_df.columns
    assert "unresolved_issue_ratio" in f_df.columns


def test_14_target_cost_overrun():
    """Test 14: Target creation - Cost overrun percentage & flag."""
    df = pd.DataFrame([
        {"original_cost": 100.0, "revised_cost": 120.0},
        {"original_cost": 100.0, "revised_cost": 100.0},
    ])
    t_df, report = build_target_variables(df, cost_overrun_threshold_pct=5.0)
    assert t_df.loc[0, "target_cost_overrun_pct"] == 20.0
    assert t_df.loc[0, "target_cost_overrun_flag"] == 1
    assert t_df.loc[1, "target_cost_overrun_pct"] == 0.0
    assert t_df.loc[1, "target_cost_overrun_flag"] == 0


def test_15_target_time_overrun():
    """Test 15: Target creation - Time overrun days & flag."""
    df = pd.DataFrame([
        {
            "start_date": "2024-01-01",
            "planned_completion_date": "2024-06-01",
            "actual_completion_date": "2024-08-01",
        }
    ])
    t_df, report = build_target_variables(df, time_overrun_threshold_days=30)
    assert t_df.loc[0, "target_time_overrun_days"] == 61
    assert t_df.loc[0, "target_time_overrun_flag"] == 1


def test_16_leakage_detection():
    """Test 16: Leakage exclusion module drops post-outcome features."""
    df = pd.DataFrame([
        {
            "original_cost": 100.0,
            "revised_cost": 150.0,
            "physical_progress": 50.0,
            "cost_overrun_pct": 50.0,
        }
    ])
    ml_df, log = detect_and_exclude_leakage(df, target_name="target_cost_overrun_flag")
    assert "revised_cost" not in ml_df.columns
    assert "cost_overrun_pct" not in ml_df.columns
    assert "original_cost" in ml_df.columns
    assert len(log) == 2


def test_17_empty_dataset_handling():
    """Test 17: Pipeline execution on empty DataFrame."""
    empty_df = pd.DataFrame()
    res = run_historical_pipeline(raw_df=empty_df)
    assert res["quality_report"]["dataset_summary"]["total_raw_records"] == 0


def test_18_dataset_splitting():
    """Test 18: Train/Val/Test splitting (chronological & random)."""
    df = generate_synthetic_dev_dataset(num_projects=20, random_seed=42)
    train_df, val_df, test_df, metrics = split_dataset(df, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    assert len(train_df) == 14
    assert len(val_df) == 3
    assert len(test_df) == 3


def test_19_reproducibility():
    """Test 19: Deterministic feature generation across multiple runs."""
    df1 = generate_synthetic_dev_dataset(num_projects=10, random_seed=123)
    df2 = generate_synthetic_dev_dataset(num_projects=10, random_seed=123)

    f1 = engineer_project_features(df1)
    f2 = engineer_project_features(df2)

    pd.testing.assert_frame_equal(f1, f2)


def test_20_end_to_end_pipeline(db_session):
    """Test 20: Full end-to-end pipeline run from database session."""
    pipeline_res = run_historical_pipeline(db_session=db_session)
    assert "quality_report" in pipeline_res
    assert "ml_feature_matrix" in pipeline_res
    assert isinstance(pipeline_res["ml_feature_matrix"], pd.DataFrame)

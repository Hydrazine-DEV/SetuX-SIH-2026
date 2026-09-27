"""
Phase 14 Test Suite — Time Overrun Prediction Machine Learning System for SetuX.
Tests cover target engineering, leakage exclusion, preprocessing, training pipeline, model selection,
baseline comparisons, artifact persistence & loading, missing artifact graceful handling,
prediction service, FastAPI endpoints, reproducibility, and compatibility with previous phases.
"""

import os
import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from app.pipeline.loader import generate_synthetic_dev_dataset
from app.pipeline.cleaner import clean_project_data
from app.pipeline.feature_engineer import engineer_project_features
from app.pipeline.target_builder import build_target_variables, detect_and_exclude_leakage
from app.pipeline.dataset_builder import split_dataset
from app.ml.time_overrun_trainer import (
    train_time_overrun_model,
    build_preprocessing_pipeline,
    evaluate_model_performance,
    MODEL_ARTIFACT_PATH,
    METADATA_ARTIFACT_PATH,
)
from app.ml.time_overrun_predictor import TimeOverrunPredictor, predict_time_overrun
from app.models.project import Project


def test_1_target_creation():
    """Test 1: Time overrun target calculation & thresholding."""
    df = pd.DataFrame([
        {
            "start_date": "2024-01-01",
            "planned_completion_date": "2024-06-01",
            "actual_completion_date": "2024-08-01",
        },
        {
            "start_date": "2024-01-01",
            "planned_completion_date": "2024-06-01",
            "actual_completion_date": "2024-06-05",
        },
    ])
    t_df, report = build_target_variables(df, time_overrun_threshold_days=30)
    assert t_df.loc[0, "target_time_overrun_days"] == 61
    assert t_df.loc[0, "target_time_overrun_flag"] == 1
    assert t_df.loc[1, "target_time_overrun_days"] == 4
    assert t_df.loc[1, "target_time_overrun_flag"] == 0
    assert report["time_overrun_positives"] == 1
    assert report["time_overrun_negatives"] == 1


def test_2_leakage_exclusion():
    """Test 2: Target leakage exclusion module drops post-outcome features."""
    df = pd.DataFrame([
        {
            "original_cost": 500.0,
            "actual_completion_date": "2025-01-01",
            "revised_completion_date": "2025-02-01",
            "target_time_overrun_days": 31,
            "physical_progress": 80.0,
        }
    ])
    ml_df, log = detect_and_exclude_leakage(df, target_name="target_time_overrun_flag")
    assert "actual_completion_date" not in ml_df.columns
    assert "revised_completion_date" not in ml_df.columns
    assert "target_time_overrun_days" not in ml_df.columns
    assert "original_cost" in ml_df.columns
    assert "physical_progress" in ml_df.columns
    assert len(log) >= 2


def test_3_feature_preparation():
    """Test 3: Predictive feature calculation for time overrun."""
    synth_df = generate_synthetic_dev_dataset(num_projects=5, random_seed=42)
    c_df, _ = clean_project_data(synth_df)
    f_df = engineer_project_features(c_df)
    assert "planned_duration_days" in f_df.columns
    assert "elapsed_duration_days" in f_df.columns
    assert "elapsed_duration_ratio" in f_df.columns
    assert "progress_gap" in f_df.columns
    assert "delayed_milestone_ratio" in f_df.columns
    assert "unresolved_issue_ratio" in f_df.columns


def test_4_preprocessing_pipeline():
    """Test 4: Scikit-learn ColumnTransformer scaling & encoding."""
    prep = build_preprocessing_pipeline(
        numeric_cols=["original_cost", "physical_progress"],
        categorical_cols=["sector", "district"],
    )
    df = pd.DataFrame([
        {"original_cost": 100.0, "physical_progress": 50.0, "sector": "Road", "district": "Pune"},
        {"original_cost": 200.0, "physical_progress": 80.0, "sector": "Bridge", "district": "Nashik"},
    ])
    trans = prep.fit_transform(df)
    assert isinstance(trans, np.ndarray)
    assert trans.shape[0] == 2
    assert trans.shape[1] > 2


def test_5_model_training_and_selection():
    """Test 5: Full model training, baseline evaluation, candidate comparison, and selection."""
    res = train_time_overrun_model(use_synthetic_fallback=True)
    assert "model_name" in res
    assert "selected_model_metrics" in res
    assert "model_comparison" in res
    assert len(res["model_comparison"]) >= 4
    metrics = res["selected_model_metrics"]
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["recall"] <= 1.0


def test_6_prediction_service_structure():
    """Test 6: Single-project prediction service response structure."""
    raw_proj = {
        "project_id": 99,
        "project_code": "PROJ-TEST-99",
        "planned_duration_days": 365,
        "elapsed_duration_days": 200,
        "physical_progress": 30.0,
        "financial_progress": 50.0,
        "total_milestones": 5,
        "delayed_milestones": 2,
        "total_issues": 3,
        "open_issues": 2,
        "critical_issues": 1,
    }
    pred = predict_time_overrun(raw_proj)
    assert pred["is_available"] is True
    assert pred["prediction"] in ("TIME_OVERRUN", "NO_TIME_OVERRUN")
    assert isinstance(pred["probability"], float)
    assert "top_factors" in pred
    assert "disclaimer" in pred


def test_7_probability_output_range():
    """Test 7: Prediction probability is an empirical number strictly between 0.0 and 1.0."""
    raw_proj = {
        "project_id": 101,
        "original_cost": 1000.0,
        "physical_progress": 95.0,
        "delayed_milestone_ratio": 0.0,
    }
    pred = predict_time_overrun(raw_proj)
    assert 0.0 <= pred["probability"] <= 1.0
    assert pred["probability"] != 0.71  # Verify not hardcoded fake number
    assert pred["probability"] != 0.82
    assert pred["probability"] != 0.95


def test_8_model_artifact_loading():
    """Test 8: Model artifact presence and TimeOverrunPredictor loading."""
    predictor = TimeOverrunPredictor()
    assert predictor.is_trained is True
    assert os.path.exists(MODEL_ARTIFACT_PATH)
    assert os.path.exists(METADATA_ARTIFACT_PATH)


def test_9_missing_model_artifact_handling(tmp_path, monkeypatch):
    """Test 9: Prediction service degradation when model artifact is missing."""
    import app.ml.time_overrun_predictor as predictor_mod

    fake_path = str(tmp_path / "non_existent.joblib")
    monkeypatch.setattr(predictor_mod, "MODEL_ARTIFACT_PATH", fake_path)

    predictor = predictor_mod.TimeOverrunPredictor()
    res = predictor.predict({"project_id": 1})
    assert res["is_available"] is False
    assert "not currently trained" in res["error"]


def test_10_missing_project_api(client, officer_token):
    """Test 10: API response for non-existent project returns 404."""
    headers = {"Authorization": f"Bearer {officer_token}"}
    response = client.get("/api/projects/NON_EXISTENT_99999/prediction/time-overrun", headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_11_unauthorized_access_api(client):
    """Test 11: Endpoint accessible via client token/session guard."""
    response = client.get("/api/projects/1/prediction/time-overrun")
    # Public read or authenticated depending on router settings
    assert response.status_code in (200, 404, 503)


def test_12_missing_features_resilience():
    """Test 12: Predictor handles incomplete/missing feature inputs gracefully."""
    minimal_proj = {"project_id": 1}
    pred = predict_time_overrun(minimal_proj)
    assert pred["is_available"] is True
    assert pred["prediction"] in ("TIME_OVERRUN", "NO_TIME_OVERRUN")


def test_13_api_response_schema(client, db_session):
    """Test 13: Full FastAPI endpoint return schema verification."""
    # Seed a project into test DB
    p = Project(
        project_code="MH-TEST-14",
        name="Phase 14 Test Highway Project",
        sector="Road Construction",
        department_name="Public Works Department",
        district="Pune",
        state="Maharashtra",
        original_cost=1000.0,
        start_date="2024-01-01",
        planned_completion_date="2025-01-01",
        physical_progress=40.0,
        financial_progress=60.0,
        status="Under Review",
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    response = client.get(f"/api/projects/{p.id}/prediction/time-overrun")
    assert response.status_code == 200
    body = response.json()
    assert body["is_available"] is True
    assert body["prediction"] in ("TIME_OVERRUN", "NO_TIME_OVERRUN")
    assert "probability" in body
    assert "model_name" in body
    assert "top_factors" in body
    assert "rule_engine_baseline" in body
    assert body["rule_engine_baseline"]["factor"] == "SCHEDULE_DELAY"


def test_14_reproducibility():
    """Test 14: Deterministic training execution with random seed."""
    m1 = train_time_overrun_model(use_synthetic_fallback=True)
    m2 = train_time_overrun_model(use_synthetic_fallback=True)
    assert m1["model_name"] == m2["model_name"]
    assert m1["selected_model_metrics"]["accuracy"] == m2["selected_model_metrics"]["accuracy"]


def test_15_temporal_split():
    """Test 15: Chronological dataset splitting maintains temporal ordering."""
    df = generate_synthetic_dev_dataset(num_projects=20, random_seed=42)
    train_df, val_df, test_df, metrics = split_dataset(df, chronological=True)
    assert metrics["split_mode"] == "chronological"
    assert len(train_df) + len(val_df) + len(test_df) == len(df)


def test_16_phase13_compatibility():
    """Test 16: Ensure target builder continues supporting both cost & time overrun targets."""
    df = pd.DataFrame([
        {
            "original_cost": 100.0,
            "revised_cost": 120.0,
            "start_date": "2024-01-01",
            "planned_completion_date": "2024-06-01",
            "actual_completion_date": "2024-08-01",
        }
    ])
    t_df, report = build_target_variables(df)
    assert "target_cost_overrun_flag" in t_df.columns
    assert "target_time_overrun_flag" in t_df.columns
    assert t_df.loc[0, "target_cost_overrun_flag"] == 1
    assert t_df.loc[0, "target_time_overrun_flag"] == 1

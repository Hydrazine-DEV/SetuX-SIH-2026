"""
SetuX — Cost Overrun ML Model Training Module (Phase 13 / Phase 15 integration).
Handles data loading, leakage prevention, preprocessing pipelines, model candidate evaluation,
baseline comparison, temporal evaluation, artifact persistence, and metric logging.
"""

import os
import json
import joblib
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from app.pipeline.loader import load_project_data_from_db, generate_synthetic_dev_dataset
from app.pipeline.cleaner import clean_project_data
from app.pipeline.feature_engineer import engineer_project_features
from app.pipeline.target_builder import build_target_variables, detect_and_exclude_leakage
from app.pipeline.dataset_builder import split_dataset

# Artifact Directory Setup
ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
MODEL_ARTIFACT_PATH = os.path.join(ARTIFACT_DIR, "cost_overrun_model.joblib")
METADATA_ARTIFACT_PATH = os.path.join(ARTIFACT_DIR, "cost_overrun_metadata.json")

NUMERIC_FEATURES = [
    "original_cost",
    "expenditure",
    "planned_duration_days",
    "elapsed_duration_days",
    "elapsed_duration_ratio",
    "physical_progress",
    "financial_progress",
    "progress_gap",
    "financial_physical_gap",
    "budget_utilization_ratio",
    "total_milestones",
    "completed_milestones",
    "delayed_milestones",
    "delayed_milestone_ratio",
    "total_issues",
    "open_issues",
    "critical_issues",
    "unresolved_issue_ratio",
]

CATEGORICAL_FEATURES = [
    "sector",
    "department_name",
    "district",
    "state",
]


def build_preprocessing_pipeline(
    numeric_cols: List[str], categorical_cols: List[str]
) -> ColumnTransformer:
    """Constructs ColumnTransformer for numerical scaling and categorical encoding."""
    num_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    cat_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="UNKNOWN")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", num_transformer, numeric_cols),
            ("cat", cat_transformer, categorical_cols),
        ]
    )


def evaluate_model_performance(
    model: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    model_name: str,
) -> Dict[str, Any]:
    """Evaluates classifier performance metrics."""
    y_pred = model.predict(X_test)
    y_prob = None

    if hasattr(model, "predict_proba"):
        try:
            probs = model.predict_proba(X_test)
            y_prob = probs[:, 1] if probs.shape[1] == 2 else probs[:, 0]
        except Exception:
            y_prob = None

    acc = float(accuracy_score(y_test, y_pred))

    if len(np.unique(y_test)) < 2:
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        auc = 0.5
    else:
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        auc = float(roc_auc_score(y_test, y_prob)) if y_prob is not None else 0.5

    cm = confusion_matrix(y_test, y_pred, labels=[0, 1]).tolist()

    return {
        "model_name": model_name,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(auc, 4),
        "confusion_matrix": {
            "tn": cm[0][0],
            "fp": cm[0][1],
            "fn": cm[1][0],
            "tp": cm[1][1],
        },
    }


def extract_feature_importances(
    pipeline: Pipeline,
    numeric_cols: List[str],
    categorical_cols: List[str],
) -> List[Dict[str, Any]]:
    """Extracts top feature importances from fitted pipeline."""
    try:
        preprocessor = pipeline.named_steps["preprocessor"]
        classifier = pipeline.named_steps["classifier"]

        cat_encoder = preprocessor.named_transformers_["cat"].named_steps["encoder"]
        cat_feature_names = list(cat_encoder.get_feature_names_out(categorical_cols))

        feature_names = numeric_cols + cat_feature_names

        importances = None
        if hasattr(classifier, "feature_importances_"):
            importances = classifier.feature_importances_
        elif hasattr(classifier, "coef_"):
            importances = np.abs(classifier.coef_[0])

        if importances is not None and len(importances) == len(feature_names):
            pairs = sorted(
                zip(feature_names, importances), key=lambda x: x[1], reverse=True
            )
            return [
                {"feature": name, "importance": round(float(imp), 4)}
                for name, imp in pairs[:15]
            ]
    except Exception:
        pass
    return []


def train_cost_overrun_model(
    df: Optional[pd.DataFrame] = None,
    db_session: Any = None,
    use_synthetic_fallback: bool = True,
    cost_overrun_threshold_pct: float = 5.0,
) -> Dict[str, Any]:
    """
    End-to-end training pipeline for SetuX Cost Overrun ML model.
    """
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    data_source_label = "DATABASE"
    if df is None:
        if db_session is not None:
            df = load_project_data_from_db(db_session)
        else:
            df = pd.DataFrame()

    if df.empty and use_synthetic_fallback:
        df = generate_synthetic_dev_dataset(num_projects=100, random_seed=42)
        data_source_label = "SYNTHETIC_DEVELOPMENT_FIXTURE"

    if df.empty:
        raise ValueError("Cannot train model on an empty dataset.")

    c_df, _ = clean_project_data(df)
    f_df = engineer_project_features(c_df)
    t_df, target_report = build_target_variables(
        f_df, cost_overrun_threshold_pct=cost_overrun_threshold_pct
    )

    valid_mask = t_df["target_cost_overrun_flag"].notnull()
    labeled_df = t_df[valid_mask].copy()

    ml_matrix, excluded_log = detect_and_exclude_leakage(
        labeled_df, target_name="target_cost_overrun_flag"
    )

    num_cols = [c for c in NUMERIC_FEATURES if c in ml_matrix.columns]
    cat_cols = [c for c in CATEGORICAL_FEATURES if c in ml_matrix.columns]
    feature_cols = num_cols + cat_cols

    X = ml_matrix[feature_cols]
    y = ml_matrix["target_cost_overrun_flag"].astype(int)

    total_samples = len(labeled_df)
    overrun_count = int(y.sum())
    non_overrun_count = total_samples - overrun_count
    overrun_pct = round((overrun_count / total_samples) * 100.0, 2) if total_samples > 0 else 0.0

    train_df, val_df, test_df, split_info = split_dataset(
        labeled_df, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, chronological=True
    )

    X_train = train_df[feature_cols]
    y_train = train_df["target_cost_overrun_flag"].astype(int)

    X_test = test_df[feature_cols]
    y_test = test_df["target_cost_overrun_flag"].astype(int)

    if len(X_test) < 2 or len(np.unique(y_train)) < 2:
        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
        )

    # Candidates
    candidates = {
        "Majority Class Baseline": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression": LogisticRegression(
            class_weight="balanced", max_iter=1000, random_state=42
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=5, class_weight="balanced", random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=50, max_depth=6, class_weight="balanced", random_state=42
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=50, max_depth=3, random_state=42
        ),
    }

    eval_results = []
    fitted_pipelines = {}

    for name, clf in candidates.items():
        prep = build_preprocessing_pipeline(num_cols, cat_cols)
        pipe = Pipeline(steps=[("preprocessor", prep), ("classifier", clf)])
        pipe.fit(X_train, y_train)
        metrics = evaluate_model_performance(pipe, X_test, y_test, name)
        eval_results.append(metrics)
        fitted_pipelines[name] = pipe

    # Select best model prioritizing F1 and Recall
    ml_candidates = [m for m in eval_results if m["model_name"] != "Majority Class Baseline"]
    selected_name = max(
        ml_candidates, key=lambda m: (m["f1_score"], m["recall"], m["accuracy"])
    )["model_name"]

    # Final retrain
    final_prep = build_preprocessing_pipeline(num_cols, cat_cols)
    final_classifier = candidates[selected_name]
    final_pipeline = Pipeline(steps=[("preprocessor", final_prep), ("classifier", final_classifier)])
    final_pipeline.fit(X, y)

    top_features = extract_feature_importances(final_pipeline, num_cols, cat_cols)

    artifact_metadata = {
        "model_name": selected_name,
        "model_type": final_pipeline.named_steps["classifier"].__class__.__name__,
        "model_version": "v1.0.0",
        "trained_at": datetime.utcnow().isoformat(),
        "data_source": data_source_label,
        "cost_overrun_threshold_pct": cost_overrun_threshold_pct,
        "target_definition": f"(revised_cost - original_cost) / original_cost * 100 > {cost_overrun_threshold_pct}%",
        "dataset_summary": {
            "total_samples": total_samples,
            "overrun_count": overrun_count,
            "non_overrun_count": non_overrun_count,
            "overrun_pct": overrun_pct,
            "feature_count": len(feature_cols),
        },
        "features_used": {
            "numeric": num_cols,
            "categorical": cat_cols,
        },
        "features_excluded_leakage": excluded_log,
        "split_strategy": split_info,
        "model_comparison": eval_results,
        "selected_model_metrics": next(
            m for m in eval_results if m["model_name"] == selected_name
        ),
        "top_feature_importances": top_features,
        "disclaimer": (
            "This model estimates cost-overrun risk from available historical project data. "
            "Model performance depends on dataset quality, sample size, representativeness, "
            "and the availability of prediction-time information."
        ),
    }

    joblib.dump(final_pipeline, MODEL_ARTIFACT_PATH)
    with open(METADATA_ARTIFACT_PATH, "w") as f:
        json.dump(artifact_metadata, f, indent=2)

    return artifact_metadata


if __name__ == "__main__":
    print("Training SetuX Cost Overrun ML Model...")
    res = train_cost_overrun_model(use_synthetic_fallback=True)
    print("Training Complete!")
    print(f"Selected Model: {res['model_name']}")
    print(f"Metrics: {res['selected_model_metrics']}")

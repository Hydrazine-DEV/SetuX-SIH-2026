"""
SetuX — Time Overrun Prediction Service (Phase 14).
Provides single-project prediction loading, inference execution, probability calculation,
top factor attribution, and error handling for untrained model states.
"""

import os
import json
import joblib
from typing import Dict, Any, Optional

import pandas as pd
import numpy as np

from app.pipeline.cleaner import clean_project_data
from app.pipeline.feature_engineer import engineer_project_features

ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
MODEL_ARTIFACT_PATH = os.path.join(ARTIFACT_DIR, "time_overrun_model.joblib")
METADATA_ARTIFACT_PATH = os.path.join(ARTIFACT_DIR, "time_overrun_metadata.json")


class TimeOverrunPredictor:
    """
    Reusable prediction service for Time / Schedule Overrun ML inference.
    """

    def __init__(self):
        self.model = None
        self.metadata = None
        self.load_model()

    def load_model(self) -> bool:
        """Loads trained scikit-learn pipeline and artifact metadata from disk."""
        if os.path.exists(MODEL_ARTIFACT_PATH) and os.path.exists(METADATA_ARTIFACT_PATH):
            try:
                self.model = joblib.load(MODEL_ARTIFACT_PATH)
                with open(METADATA_ARTIFACT_PATH, "r") as f:
                    self.metadata = json.load(f)
                return True
            except Exception as e:
                self.model = None
                self.metadata = None
                return False
        return False

    @property
    def is_trained(self) -> bool:
        """Returns True if model artifact is successfully loaded."""
        return self.model is not None and self.metadata is not None

    def predict(self, raw_project_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates structured time overrun prediction for a single project input dictionary.
        
        Returns:
            Structured dictionary containing prediction class, probability, model version,
            top predictive factors, and metadata disclaimer.
        """
        if not self.is_trained:
            # Attempt reloading in case artifact was recently generated
            if not self.load_model():
                return {
                    "is_available": False,
                    "error": "Time overrun model is not currently trained.",
                    "prediction": "UNKNOWN",
                    "probability": 0.0,
                }

        try:
            input_df = pd.DataFrame([raw_project_dict])
            c_df, _ = clean_project_data(input_df)
            f_df = engineer_project_features(c_df)

            num_cols = self.metadata["features_used"]["numeric"]
            cat_cols = self.metadata["features_used"]["categorical"]
            all_cols = num_cols + cat_cols

            # Ensure all required features are present in feature frame
            for col in all_cols:
                if col not in f_df.columns:
                    f_df[col] = np.nan if col in num_cols else "UNKNOWN"

            X_input = f_df[all_cols]

            # Probabilities & Prediction
            pred_class = int(self.model.predict(X_input)[0])

            prob = 0.5
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(X_input)[0]
                if len(probs) >= 2:
                    prob = float(probs[1])
                else:
                    prob = float(probs[0])
            elif hasattr(self.model, "decision_function"):
                decision = self.model.decision_function(X_input)[0]
                prob = float(1.0 / (1.0 + np.exp(-decision)))

            label = "TIME_OVERRUN" if pred_class == 1 else "NO_TIME_OVERRUN"

            # Top contributing factors with current input values
            top_factors = []
            raw_top = self.metadata.get("top_feature_importances", [])
            for feat_info in raw_top[:5]:
                f_name = feat_info["feature"]
                val = f_df[f_name].iloc[0] if f_name in f_df.columns else None
                if pd.notnull(val):
                    val = float(val) if isinstance(val, (int, float, np.number)) else str(val)
                else:
                    val = None

                top_factors.append(
                    {
                        "feature": f_name,
                        "importance": feat_info["importance"],
                        "current_value": val,
                    }
                )

            return {
                "is_available": True,
                "project_id": raw_project_dict.get("project_id"),
                "project_code": raw_project_dict.get("project_code"),
                "prediction": label,
                "probability": round(prob, 4),
                "has_overrun_risk": pred_class == 1,
                "time_overrun_threshold_days": self.metadata.get(
                    "time_overrun_threshold_days", 30
                ),
                "model_name": self.metadata.get("model_name", "Time Overrun ML Classifier"),
                "model_version": self.metadata.get("model_version", "v1.0.0"),
                "data_source": self.metadata.get("data_source", "HISTORICAL_DB"),
                "top_factors": top_factors,
                "disclaimer": self.metadata.get(
                    "disclaimer",
                    "This model estimates time-overrun risk from available historical project data.",
                ),
            }

        except Exception as e:
            return {
                "is_available": False,
                "error": f"Prediction failed due to feature calculation error: {str(e)}",
                "prediction": "UNKNOWN",
                "probability": 0.0,
            }


# Singleton Instance
time_overrun_predictor = TimeOverrunPredictor()


def predict_time_overrun(raw_project_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience functional wrapper for TimeOverrunPredictor."""
    return time_overrun_predictor.predict(raw_project_dict)

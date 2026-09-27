"""
SetuX Historical Data Pipeline & Feature Engineering Package (Phase 12).
Provides multi-source loading, raw data inspection, business rule validation,
controlled cleaning, leak-free feature engineering, target generation, and splitting.
"""

from app.pipeline.loader import (
    load_project_data_from_db,
    load_project_data_from_csv,
    load_project_data_from_json,
    generate_synthetic_dev_dataset,
)
from app.pipeline.inspector import inspect_raw_data
from app.pipeline.validator import validate_project_data
from app.pipeline.cleaner import clean_project_data
from app.pipeline.feature_engineer import (
    engineer_project_features,
    FEATURE_DEFINITIONS,
)
from app.pipeline.target_builder import (
    build_target_variables,
    detect_and_exclude_leakage,
    LEAKAGE_EXCLUSIONS,
)
from app.pipeline.dataset_builder import (
    run_historical_pipeline,
    split_dataset,
)

__all__ = [
    "load_project_data_from_db",
    "load_project_data_from_csv",
    "load_project_data_from_json",
    "generate_synthetic_dev_dataset",
    "inspect_raw_data",
    "validate_project_data",
    "clean_project_data",
    "engineer_project_features",
    "FEATURE_DEFINITIONS",
    "build_target_variables",
    "detect_and_exclude_leakage",
    "LEAKAGE_EXCLUSIONS",
    "run_historical_pipeline",
    "split_dataset",
]

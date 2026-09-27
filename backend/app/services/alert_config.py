"""
SetuX / VeriX — Early Warning & Alert System Configuration
SIH26103: Integrated Government Project Monitoring & Intelligence Platform
"""
from enum import Enum
from typing import Dict, Any


class AlertStatus(str, Enum):
    UNREAD = "UNREAD"
    READ = "READ"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(str, Enum):
    SCHEDULE_DELAY = "SCHEDULE_DELAY"
    COST_OVERRUN = "COST_OVERRUN"
    LOW_PROGRESS = "LOW_PROGRESS"
    MILESTONE_DELAY = "MILESTONE_DELAY"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL_RISK = "CRITICAL_RISK"
    PREDICTED_COST_OVERRUN = "PREDICTED_COST_OVERRUN"
    PREDICTED_TIME_OVERRUN = "PREDICTED_TIME_OVERRUN"
    DATA_QUALITY = "DATA_QUALITY"


class AlertSource(str, Enum):
    RULE_ENGINE = "RULE_ENGINE"
    COST_PREDICTOR = "COST_PREDICTOR"
    TIME_PREDICTOR = "TIME_PREDICTOR"
    RISK_INTELLIGENCE = "RISK_INTELLIGENCE"
    DATA_QUALITY = "DATA_QUALITY"


# Centralized threshold and rule configuration for early warning alert generation
ALERT_CONFIG: Dict[str, Any] = {
    "schedule_delay": {
        "critical_days": 60,
        "high_days": 30,
        "medium_days": 15,
        "low_days": 5,
    },
    "cost_overrun": {
        "critical_pct": 25.0,
        "high_pct": 15.0,
        "medium_pct": 5.0,
        "low_pct": 1.0,
    },
    "progress_lag": {
        "critical_pct": 30.0,
        "high_pct": 20.0,
        "medium_pct": 10.0,
        "low_pct": 5.0,
    },
    "milestone_delay": {
        "critical_overdue_count": 3,
        "high_overdue_count": 2,
        "medium_overdue_count": 1,
    },
    "ml_prediction": {
        "critical_prob": 0.80,
        "high_prob": 0.65,
        "medium_prob": 0.50,
    },
    "overall_risk_score": {
        "critical_score": 75.0,
        "high_score": 50.0,
        "medium_score": 25.0,
    },
}

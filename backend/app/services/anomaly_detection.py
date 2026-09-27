"""
SetuX — Anomaly Detection Service
Computes an anomaly score (0-100) based on multiple signals.

⚠ DEMO / SIMULATED MODEL OUTPUT — Not scientifically validated.
"""


def compute_anomaly_score(
    reported_progress: int,
    estimated_progress: int,
    gps_distance_m: float,
    duplicate_image: bool,
    manipulation_risk: str,
) -> int:
    """
    Compute an anomaly score from 0 (normal) to 100 (extreme anomaly).

    Signals considered:
    - Progress gap between reported and AI-estimated
    - GPS location deviation
    - Duplicate image detection
    - Image manipulation risk
    """
    score = 0

    # 1. Progress gap (max 50 points)
    gap = abs(reported_progress - estimated_progress)
    if gap >= 30:
        score += 50
    elif gap >= 20:
        score += 35
    elif gap >= 10:
        score += 20
    elif gap >= 5:
        score += 10

    # 2. GPS deviation (max 25 points)
    if gps_distance_m > 2000:
        score += 25
    elif gps_distance_m > 1000:
        score += 18
    elif gps_distance_m > 500:
        score += 10
    elif gps_distance_m > 200:
        score += 4

    # 3. Duplicate image (max 15 points)
    if duplicate_image:
        score += 15

    # 4. Manipulation risk (max 10 points)
    risk_scores = {"CRITICAL": 10, "HIGH": 7, "MEDIUM": 4, "LOW": 0}
    score += risk_scores.get(manipulation_risk, 0)

    return min(100, score)


def determine_risk_level(anomaly_score: int) -> str:
    """Map anomaly score to risk level."""
    if anomaly_score >= 75:
        return "HIGH"
    elif anomaly_score >= 50:
        return "MEDIUM"
    elif anomaly_score >= 25:
        return "LOW"
    else:
        return "MINIMAL"


def determine_recommendation(risk_level: str, gap: int) -> str:
    """Generate action recommendation based on risk."""
    if risk_level == "HIGH" or gap >= 25:
        return "MANUAL_INSPECTION"
    elif risk_level == "MEDIUM" or gap >= 10:
        return "SUPERVISOR_REVIEW"
    else:
        return "APPROVED"

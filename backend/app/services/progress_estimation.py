"""
SetuX — Progress Estimation Service
Rule-based mock progress estimation for SIH prototype.
In production this would be replaced by a trained computer vision model.

⚠ DEMO / SIMULATED MODEL OUTPUT — Not scientifically validated.
"""
import random
import math
from typing import Tuple


def estimate_progress(
    reported_progress: int,
    project_type: str,
    anomaly_score: int,
    gps_distance_m: float,
) -> int:
    """
    Estimate the actual construction progress from submitted evidence.
    
    For the SIH prototype, this uses a deterministic rule-based model
    that produces realistic discrepancy patterns based on project type
    and reported values.
    
    In production: Replace with CNN-based image analysis model.
    
    Returns: estimated_progress (0-100)
    """
    # Seed with deterministic values so results are reproducible per project
    seed = reported_progress + anomaly_score + int(gps_distance_m)
    rng = random.Random(seed)

    # Project-type discount factors (some project types have more reporting inflation)
    type_discounts = {
        "Road Construction": 0.75,
        "Road Repair": 0.70,
        "Bridge": 0.85,
        "School": 0.88,
        "Government Building": 0.86,
        "Water Pipeline": 0.78,
        "Drainage": 0.72,
        "Public Toilet": 0.90,
        "Streetlight": 0.92,
        "Other": 0.80,
    }
    discount = type_discounts.get(project_type, 0.80)

    # Apply discount + small noise
    noise = rng.uniform(-5, 5)
    estimated = math.floor(reported_progress * discount + noise)

    # GPS anomaly penalty
    if gps_distance_m > 1000:
        estimated = max(0, estimated - 15)
    elif gps_distance_m > 500:
        estimated = max(0, estimated - 8)

    # Clamp to valid range
    return max(0, min(100, estimated))


def compute_progress_gap(reported: int, estimated: int) -> int:
    """Return the absolute gap between reported and AI-estimated progress."""
    return abs(reported - estimated)

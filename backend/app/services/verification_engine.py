"""
SetuX / VeriX — AI Verification Engine
Orchestrates the full AI verification pipeline for submitted project evidence,
supporting both real uploaded files and simulated metadata.

⚠ AI DEMO MODE: Prototype AI Output — Model validation pending
In production, plug in trained YOLOv8-seg / PyTorch models at each stage.
"""
import random
from typing import List, Dict, Any, Optional

from app.services.gps_verification import verify_gps
from app.services.progress_estimation import estimate_progress, compute_progress_gap
from app.services.anomaly_detection import (
    compute_anomaly_score,
    determine_risk_level,
    determine_recommendation,
)
from app.services.image_analysis import extract_exif_data, analyze_image_heuristics


# Infrastructure detection templates per project type
INFRASTRUCTURE_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    "Road Construction": [
        {"item": "Road surface layer", "full": True},
        {"item": "Road edges / kerb lining", "full": True},
        {"item": "Sub-base gravel compaction", "full": False},
        {"item": "Bitumen asphalt coating", "full": False},
        {"item": "Lane marking & signage", "full": False},
    ],
    "Road Repair": [
        {"item": "Pothole milling & filling", "full": True},
        {"item": "Road surface patch", "full": True},
        {"item": "Edge alignment repair", "full": True},
        {"item": "Finished tar seal", "full": False},
    ],
    "Bridge": [
        {"item": "Pier foundation & pile cap", "full": True},
        {"item": "Pillar / support columns", "full": True},
        {"item": "Pre-stressed deck slab", "full": False},
        {"item": "Railing / safety barrier", "full": False},
        {"item": "Approach road connection", "full": False},
    ],
    "School": [
        {"item": "RCC framed structure", "full": True},
        {"item": "Roof slab casting", "full": True},
        {"item": "Doors, windows & grills", "full": False},
        {"item": "Flooring & tiling", "full": False},
        {"item": "Electrical & sanitization", "full": False},
    ],
    "Water Pipeline": [
        {"item": "Pipeline excavation trench", "full": True},
        {"item": "DI / HDPE pipe laying", "full": False},
        {"item": "Air valve & sluice chambers", "full": False},
        {"item": "Backfilling & hydro-testing", "full": False},
    ],
    "Drainage": [
        {"item": "RCC drain channel", "full": True},
        {"item": "Cover slabs & grating", "full": False},
        {"item": "Junction inspection chambers", "full": False},
        {"item": "Outfall connectivity", "full": False},
    ],
    "Government Building": [
        {"item": "Foundation & plinth beam", "full": True},
        {"item": "Superstructure brickwork", "full": True},
        {"item": "Roof casting slab", "full": False},
        {"item": "Plastering & interior", "full": False},
        {"item": "External finishing & paint", "full": False},
    ],
    "Public Toilet": [
        {"item": "Civil structure & partition", "full": True},
        {"item": "Plumbing & sanitary lines", "full": False},
        {"item": "Overhead water tank & doors", "full": False},
        {"item": "Divyang accessibility ramp", "full": False},
    ],
    "Streetlight": [
        {"item": "Octagonal pole erection", "full": True},
        {"item": "Underground arm cabling", "full": False},
        {"item": "Energy-efficient LED fixtures", "full": False},
        {"item": "Timer / smart control panel", "full": False},
    ],
}

DEFAULT_TEMPLATE = [
    {"item": "Primary civil structure", "full": True},
    {"item": "Secondary works & joinery", "full": False},
    {"item": "Finishing & utility integration", "full": False},
]


def _generate_infrastructure_items(
    project_type: str,
    estimated_progress: int,
    reported_progress: int,
    rng: random.Random,
    heuristics: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Generate infrastructure detection checklist based on completion level."""
    template = INFRASTRUCTURE_TEMPLATES.get(project_type, DEFAULT_TEMPLATE)
    items = []

    total = len(template)
    fully_detected = max(1, round((estimated_progress / 100) * total))
    partial = min(1, total - fully_detected)

    for i, t in enumerate(template):
        if i < fully_detected:
            status = "✓ Detected"
            confidence = "HIGH"
            detected = True
        elif i < fully_detected + partial:
            status = "⚠ Partial"
            confidence = "MEDIUM"
            detected = True
        else:
            status = "✗ Not Detected"
            confidence = "LOW"
            detected = False

        items.append({
            "item": t["item"],
            "detected": detected,
            "confidence": confidence,
            "status": status,
        })

    return items


def _build_explanation(
    gap: int,
    risk_level: str,
    gps_distance_m: float,
    duplicate_image: bool,
    manipulation_risk: str,
    exif_found: bool,
) -> str:
    """Generate explainable AI rationale for the anomaly flags."""
    reasons = []

    if gap >= 25:
        reasons.append(
            f"Reported completion ({gap}% gap above visual estimate) significantly exceeds AI-estimated visible work. "
            "High likelihood of premature progress invoicing."
        )
    elif gap >= 10:
        reasons.append(
            f"A moderate progress gap of {gap}% was detected between reported progress and visible physical components."
        )

    if gps_distance_m > 500:
        reasons.append(
            f"Submitted GPS coordinates deviate by {gps_distance_m:.0f}m from registered site bounds (tolerance: 500m)."
        )

    if duplicate_image:
        reasons.append(
            "Image hash similarity check indicates the submitted photo was used in a prior submission."
        )

    if manipulation_risk in ("HIGH", "CRITICAL"):
        reasons.append(
            "Digital forensics metadata indicates potential photo editing or artificial alteration."
        )

    if not reasons:
        reasons.append("Evidence is fully consistent with reported milestones and registered GPS site coordinates.")

    return " | ".join(reasons)


def run_verification(
    project_id: str,
    project_type: str,
    registered_lat: float,
    registered_lng: float,
    submitted_lat: Optional[float] = None,
    submitted_lng: Optional[float] = None,
    reported_progress: int = 0,
    image_paths: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Full AI verification pipeline accepting real uploaded images and site coordinates.
    """
    # Deterministic RNG for consistent demo results
    rng = random.Random(hash(project_id) % 99999)

    # 1. EXIF metadata extraction from real image if available
    exif_data = {"exif_found": False, "has_gps": False}
    heuristics = {"sharpness_score": 80, "surface_texture_score": 75, "manipulation_risk": "LOW"}
    
    if image_paths and len(image_paths) > 0:
        primary_img = image_paths[0]
        exif_data = extract_exif_data(primary_img)
        heuristics = analyze_image_heuristics(primary_img)

        # If EXIF has GPS and no manual GPS was submitted, use EXIF GPS
        if exif_data.get("has_gps") and submitted_lat is None:
            submitted_lat = exif_data.get("latitude")
            submitted_lng = exif_data.get("longitude")

    # Fallback to registered coordinates if GPS not provided
    if submitted_lat is None:
        submitted_lat = registered_lat
    if submitted_lng is None:
        submitted_lng = registered_lng

    # 2. Stage 1 — GPS Verification
    gps_verified, gps_distance_m = verify_gps(
        registered_lat, registered_lng, submitted_lat, submitted_lng
    )

    # 3. Stage 2 — Image Authenticity & Manipulation
    duplicate_image = rng.random() < 0.10
    manipulation_risk = heuristics.get("manipulation_risk", "LOW")
    timestamp_verified = True

    # 4. Stage 3 — Progress Estimation
    anomaly_seed = rng.randint(10, 60)
    estimated_progress = estimate_progress(
        reported_progress, project_type, anomaly_seed, gps_distance_m
    )

    # 5. Stage 4 — Anomaly Score
    gap = compute_progress_gap(reported_progress, estimated_progress)
    anomaly_score = compute_anomaly_score(
        reported_progress, estimated_progress, gps_distance_m, duplicate_image, manipulation_risk
    )

    # 6. Stage 5 — Risk & Recommendation
    risk_level = determine_risk_level(anomaly_score)
    recommendation = determine_recommendation(risk_level, gap)

    # 7. Stage 6 — Infrastructure Detection
    infrastructure_detected = _generate_infrastructure_items(
        project_type, estimated_progress, reported_progress, rng, heuristics
    )

    # 8. Stage 7 — Explanation
    explanation = _build_explanation(
        gap, risk_level, gps_distance_m, duplicate_image, manipulation_risk, exif_data.get("exif_found", False)
    )

    return {
        "project_id": project_id,
        "reported_progress": reported_progress,
        "estimated_progress": estimated_progress,
        "gps_verified": gps_verified,
        "gps_distance_m": gps_distance_m,
        "submitted_lat": submitted_lat,
        "submitted_lng": submitted_lng,
        "timestamp_verified": timestamp_verified,
        "duplicate_image": duplicate_image,
        "manipulation_risk": manipulation_risk,
        "anomaly_score": anomaly_score,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "infrastructure_detected": infrastructure_detected,
        "explanation": explanation,
        "exif_metadata": exif_data,
        "heuristics": heuristics,
        "is_demo": True,
        "ai_demo_mode": True,
        "disclaimer": "Prototype AI Output — Model validation pending",
    }

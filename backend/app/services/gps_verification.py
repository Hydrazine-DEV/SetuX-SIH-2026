"""
SetuX — GPS Verification Service
Uses Haversine formula to calculate distance between coordinates.
"""
import math
from typing import Tuple


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great-circle distance in metres between two GPS points.
    Uses the Haversine formula.
    """
    R = 6_371_000  # Earth radius in metres

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def verify_gps(
    registered_lat: float,
    registered_lng: float,
    submitted_lat: float,
    submitted_lng: float,
    threshold_m: float = 500.0,
) -> Tuple[bool, float]:
    """
    Verify submitted GPS against registered project location.
    Returns (is_verified, distance_in_metres).
    Threshold: 500m tolerance for field conditions.
    """
    distance = haversine_distance(registered_lat, registered_lng, submitted_lat, submitted_lng)
    is_verified = distance <= threshold_m
    return is_verified, round(distance, 1)

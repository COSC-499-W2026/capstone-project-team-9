"""Process 1.1 "Verify location".

The service fetches the campus location from the repository (D3) itself, so
callers only supply the player's coordinates:

    result = verify_location(lat, lon)
    if not result.allowed:
        raise HTTPException(403, result.message)
"""
from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt

from src.repositories.location_repo import get_campus_location

EARTH_RADIUS_M = 6_371_000
BLOCKED_MESSAGE = "You need to be on the UBCO campus to play. Head to campus and try again!"
ALLOWED_MESSAGE = "Location verified."


@dataclass(frozen=True)
class LocationResult:
    allowed: bool
    message: str


def is_within_radius(lat1: float, lon1: float, lat2: float, lon2: float, radius_m: float) -> bool:
    """True if point 1 is within radius_m metres of point 2 (haversine distance)."""
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    distance_m = 2 * EARTH_RADIUS_M * asin(sqrt(a))
    return distance_m <= radius_m


def verify_location(lat: float, lon: float) -> LocationResult:
    """Return allowed/blocked for the player's coordinates."""
    campus = get_campus_location()
    if is_within_radius(lat, lon, campus.latitude, campus.longitude, campus.radius_m):
        return LocationResult(True, ALLOWED_MESSAGE)
    return LocationResult(False, BLOCKED_MESSAGE)
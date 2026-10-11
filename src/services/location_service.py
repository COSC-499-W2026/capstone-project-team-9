"""Process 1.1 "Verify location".
 
This module is deliberately pure: it does NOT read the boundary store itself.
The caller fetches the rings from the repository (D3) and passes them in. That
means nothing here changes when the boundary moves from a file to the database.
 
How the game feature should call it later:
 
    from fastapi import Depends
    from src.repositories.location_repo import get_campus_polygons
    from src.services.location_service import verify_location
 
    def start_game(lat: float, lon: float, rings = Depends(get_campus_polygons)):
        result = verify_location(lat, lon, rings)
        if not result.allowed:
            raise HTTPException(403, result.message)
"""
from dataclasses import dataclass
 
from src.repositories.location_repo import Ring
 
BLOCKED_MESSAGE = "You need to be on the UBCO campus to play. Head to campus and try again!"
ALLOWED_MESSAGE = "Location verified."
 
 
@dataclass(frozen=True)
class LocationResult:
    allowed: bool
    message: str
 
 
def point_in_ring(lat: float, lon: float, ring: Ring) -> bool:
    """Ray-casting point-in-polygon test. Points exactly on an edge may go either way."""
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        lat_i, lon_i = ring[i]
        lat_j, lon_j = ring[j]
        if (lon_i > lon) != (lon_j > lon):
            lat_cross = (lat_j - lat_i) * (lon - lon_i) / (lon_j - lon_i) + lat_i
            if lat < lat_cross:
                inside = not inside
        j = i
    return inside
 
 
def verify_location(lat: float, lon: float, rings: list[Ring]) -> LocationResult:
    """Return allowed/blocked for a coordinate, given the campus boundary rings."""
    if any(point_in_ring(lat, lon, ring) for ring in rings):
        return LocationResult(True, ALLOWED_MESSAGE)
    return LocationResult(False, BLOCKED_MESSAGE)


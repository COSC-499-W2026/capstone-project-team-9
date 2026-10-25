"""Campus location store.

TODAY: the campus is a single hardcoded circle (center point + radius).

WHEN THE DATABASE ARRIVES, this is the file that changes:
  - Add a SQLModel table holding the campus location (e.g. latitude, longitude,
    radius_m, and later a school_id).
  - Make `get_campus_location` query that table and return the same
    `CampusLocation`. Keep the return type stable so the service logic is unchanged.
  - The session will need to reach this function. Either pass it down from the
    router (`Depends(get_session)` -> `verify_location(lat, lon, session)` ->
    `get_campus_location(session)`) or have the repo manage its own session.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class CampusLocation:
    latitude: float
    longitude: float
    radius_m: float


def get_campus_location() -> CampusLocation:
    """Return the campus center point and radius (TEMPORARY hardcoded values)."""
    campus_center_latitude = 49.9394
    campus_center_longitude = -119.3948
    campus_radius_metres = 800  # TODO: tune against real campus coordinates
    return CampusLocation(campus_center_latitude, campus_center_longitude, campus_radius_metres)
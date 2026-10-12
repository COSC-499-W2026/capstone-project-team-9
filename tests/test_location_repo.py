from repositories.location_repo import CampusLocation, get_campus_location


# HARDCODED-ONLY: replace with a DB-backed test when the table exists.
def test_get_campus_location_returns_valid_circle():
    campus = get_campus_location()
    assert isinstance(campus, CampusLocation)
    assert -90 <= campus.latitude <= 90
    assert -180 <= campus.longitude <= 180
    assert campus.radius_m > 0
import pytest

from repositories.location_repo import CampusLocation
from services.location_service import BLOCKED_MESSAGE, is_within_radius, verify_location

# A fake campus so these tests don't depend on the real hardcoded values.
TEST_CAMPUS = CampusLocation(latitude=49.935, longitude=-119.395, radius_m=500)


@pytest.fixture(autouse=True)
def fake_campus(monkeypatch):
    monkeypatch.setattr("services.location_service.get_campus_location", lambda: TEST_CAMPUS)


def test_on_campus_allows_start():
    assert verify_location(49.936, -119.395).allowed is True  # ~111 m from center


def test_campus_center_allows_start():
    assert verify_location(49.935, -119.395).allowed is True


@pytest.mark.parametrize("lat,lon", [(49.2827, -123.1207), (0.0, 0.0), (49.95, -119.395)])
def test_off_campus_blocks_start_with_message(lat, lon):
    result = verify_location(lat, lon)
    assert result.allowed is False
    assert result.message == BLOCKED_MESSAGE


def test_just_inside_and_outside_radius():
    assert verify_location(49.939, -119.395).allowed is True    # ~445 m
    assert verify_location(49.941, -119.395).allowed is False   # ~667 m


# 0.001 degrees of latitude is about 111 m.
def test_is_within_radius_true_when_closer_than_radius():
    assert is_within_radius(49.001, -119.0, 49.0, -119.0, 150) is True


def test_is_within_radius_false_when_farther_than_radius():
    assert is_within_radius(49.001, -119.0, 49.0, -119.0, 100) is False


def test_is_within_radius_same_point():
    assert is_within_radius(49.0, -119.0, 49.0, -119.0, 0) is True
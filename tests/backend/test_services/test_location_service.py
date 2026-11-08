import pytest

from models.location_model import LocationArea
from repositories.location_repo import CampusLocation
from services.location_service import (
    BLOCKED_MESSAGE,
    ALLOWED_MESSAGE,
    WRONG_PLACE_MESSAGE,
    _is_within_radius,
    LocationService
)

# A fake campus so these tests don't depend on the real hardcoded values.
TEST_CAMPUS = CampusLocation(latitude=49.935, longitude=-119.395, radius_m=500)


@pytest.fixture(autouse=True)
def fake_campus(monkeypatch):
    monkeypatch.setattr("services.location_service.get_campus_location", lambda: TEST_CAMPUS)

@pytest.fixture()
def location_service():
    return LocationService()

# TESTS FOR _is_within_radius() ---------------------------------------------

# 0.001 degrees of latitude is about 111 m.
def test_is_within_radius_true_when_closer_than_radius():
    assert _is_within_radius(49.001, -119.0, 49.0, -119.0, 150) is True


def test_is_within_radius_false_when_farther_than_radius():
    assert _is_within_radius(49.001, -119.0, 49.0, -119.0, 100) is False


def test_is_within_radius_same_point():
    assert _is_within_radius(49.0, -119.0, 49.0, -119.0, 0) is True


# TESTS FOR verify_location()  ---------------------------------------------

def test_on_campus_allows_start(location_service):
    assert location_service.verify_location(49.936, -119.395).allowed is True  # ~111 m from center


def test_campus_center_allows_start(location_service):
    assert location_service.verify_location(49.935, -119.395).allowed is True


@pytest.mark.parametrize("lat,lon", [(49.2827, -123.1207), (0.0, 0.0), (49.95, -119.395)])
def test_off_campus_blocks_start_with_message(location_service, lat, lon):
    result = location_service.verify_location(lat, lon)
    assert result.allowed is False
    assert result.message == BLOCKED_MESSAGE


def test_just_inside_and_outside_radius(location_service):
    assert location_service.verify_location(49.939, -119.395).allowed is True    # ~445 m
    assert location_service.verify_location(49.941, -119.395).allowed is False   # ~667 m


# TESTS FOR verify_location_with_target() ---------------------------------------------

TARGET = LocationArea(latitude=49.256, longitude=-123.250, radius=100)

def test_target_at_target_location(location_service):
    """Player is at the target location."""
    result = location_service.verify_location_with_target(49.256, -123.250, TARGET)
    assert result.allowed
    assert result.message == ALLOWED_MESSAGE

def test_target_inside_target_radius(location_service):
    """Player is inside the target radius."""
    result = location_service.verify_location_with_target(49.2561, -123.2501, TARGET)
    assert result.allowed
    assert result.message == ALLOWED_MESSAGE


@pytest.mark.parametrize(
    "lat, lon",
    [
        (49.257, -123.251),  # outside the 100 m radius
        (0, 0),  # outside radius
    ],
)
def test_target_outside_target_radius(location_service, lat, lon):
    """Player is outside the target radius."""
    result = location_service.verify_location_with_target(lat, lon, TARGET)
    assert not result.allowed
    assert result.message == WRONG_PLACE_MESSAGE

def test_target_larger_radius(location_service):
    """Player is outside the target radius, but the target has a larger radius."""
    large_target = LocationArea(latitude=49.256, longitude=-123.250, radius=1000)
    result = location_service.verify_location_with_target(49.257, -123.251, TARGET)
    result_wide = location_service.verify_location_with_target(49.257, -123.251, large_target)
    assert result.allowed is False
    assert result_wide.allowed is True
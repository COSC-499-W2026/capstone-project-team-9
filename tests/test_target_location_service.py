import pytest

from src.services.location_service import (
    ALLOWED_MESSAGE,
    WRONG_PLACE_MESSAGE,
    TargetLocation, 
    is_within_radius,
    verify_location_with_target)

TARGET = TargetLocation(latitude=49.256, longitude=-123.250, radius_m=100)

def test_target_at_target_location():
    """Player is at the target location."""
    result = verify_location_with_target(49.256, -123.250, TARGET)
    assert result.allowed
    assert result.message == ALLOWED_MESSAGE

def test_target_inside_target_radius():
    """Player is inside the target radius."""
    result = verify_location_with_target(49.3561, -123.3501, TARGET)
    assert result.allowed
    assert result.message == ALLOWED_MESSAGE


@pytest.mark.parametrize(
    "lat, lon",
    [
        (49.256, -123.250),  # at target
        (49.2561, -123.2501),  # inside radius
        (0, 0),  # outside radius
    ],
)
def test_target_outside_target_radius(lat, lon):
    """Player is outside the target radius."""
    result = verify_location_with_target(lat, lon, TARGET)
    assert not result.allowed
    assert result.message == WRONG_PLACE_MESSAGE

def test_target_larger_radius():
    """Player is outside the target radius, but the target has a larger radius."""
    large_target = TargetLocation(latitude=49.256, longitude=-123.250, radius_m=1000)
    result = verify_location_with_target(49.257, -123.251, TARGET)
    result_wide = verify_location_with_target(49.257, -123.251, large_target)
    assert result.allowed is False
    assert result_wide.allowed is True
 


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


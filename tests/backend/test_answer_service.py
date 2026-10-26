import pytest

from services.answer_service import verify_answer, CORRECT_MESSAGE, WRONG_MESSAGE
from services.location_service import TargetLocation, WRONG_PLACE_MESSAGE

TARGET = TargetLocation(latitude=49.256, longitude=-123.250, radius_m=100)
AT_TARGET = (49.256, -123.250)
FAR_FROM_TARGET = (49.300, -123.300)

@pytest.fixture
def fake_ocr(monkeypatch):
    """Monkeypatch matches_room to return True for 'room1' and False otherwise."""
    calls = []

    def install(results):
        def fake(image_bytes, expected_room):
            calls.append(expected_room)
            return results
        monkeypatch.setattr("services.answer_service.matches_room", fake)
        return calls
    return install

def test_verify_answer_correct(fake_ocr):
    """Test that verify_answer returns correct for a correct answer at the target location."""
    calls = fake_ocr(True)
    result = verify_answer(b"image", *AT_TARGET, "room1", TARGET)
    assert result.correct is True
    assert result.message == CORRECT_MESSAGE
    assert calls == ["room1"]

def test_verify_answer_wrong(fake_ocr):
    """Test that verify_answer returns wrong for a wrong answer at the target location."""
    calls = fake_ocr(False)
    result = verify_answer(b"image", *AT_TARGET, "room1", TARGET)
    assert result.correct is False
    assert result.message == WRONG_MESSAGE
    assert calls == ["room1"]

def test_verify_answer_wrong_location(fake_ocr):
    """Test that verify_answer returns wrong for a correct answer at the wrong location."""
    calls = fake_ocr(True)
    result = verify_answer(b"image", *FAR_FROM_TARGET, "room1", TARGET)
    assert result.correct is False
    assert result.message == WRONG_PLACE_MESSAGE
    assert calls == []

def test_ocr_skipped_if_location_wrong(fake_ocr):
    """Test that matches_room is not called if the location is wrong."""
    calls = fake_ocr(True)
    result = verify_answer(b"image", *FAR_FROM_TARGET, "room1", TARGET)
    assert result.correct is False
    assert result.message == WRONG_PLACE_MESSAGE
    assert calls == []

def test_unreadable_image(fake_ocr):
    """Test that verify_answer returns wrong for an unreadable image at the target location."""
    calls = fake_ocr(False)
    result = verify_answer(b"unreadable", *AT_TARGET, "room1", TARGET)
    assert result.correct is False
    assert result.message == WRONG_MESSAGE
    assert calls == ["room1"]
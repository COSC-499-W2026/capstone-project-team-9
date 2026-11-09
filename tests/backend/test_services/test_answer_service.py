import pytest

from models import Target
from services import AnswerService, LocationService
from repositories import TargetRepository
from services.answer_service import (
    CORRECT_MESSAGE, WRONG_MESSAGE, ClueNotFoundError, AnswerService
)
from services.location_service import WRONG_PLACE_MESSAGE

TARGET = Target(name="COM 201", latitude=49.256, longitude=-123.250, radius=100)
AT_TARGET = (49.256, -123.250)
FAR_FROM_TARGET = (49.300, -123.300)


@pytest.fixture
def fake_clue(monkeypatch):
    """Fake the clue repo's target lookup."""
    def install(target):
        monkeypatch.setattr("services.answer_service.get_target_by_id", lambda session, clue_id: target)
    return install


@pytest.fixture
def fake_ocr(monkeypatch):
    """Fake matches_room and record which room code it was asked about."""
    calls = []

    def install(result):
        def fake(image_bytes, expected_room):
            calls.append(expected_room)
            return result
        monkeypatch.setattr("services.answer_service.matches_room", fake)
        return calls
    return install


@pytest.fixture
def answer_service(session):
    return AnswerService(LocationService(), TargetRepository(session))


def test_correct_answer_checks_room_code_from_target_name(answer_service, fake_clue, fake_ocr):
    fake_clue(TARGET)
    calls = fake_ocr(True)
    result = answer_service.verify_answer(1, b"image", *AT_TARGET)
    assert result.correct is True
    assert result.message == CORRECT_MESSAGE
    assert calls == ["COM201"]  # space stripped


def test_wrong_photo_at_right_place(answer_service, fake_clue, fake_ocr):
    fake_clue(TARGET)
    fake_ocr(False)
    result = answer_service.verify_answer(1, b"image", *AT_TARGET)
    assert result.correct is False
    assert result.message == WRONG_MESSAGE


def test_wrong_location_skips_ocr(answer_service, fake_clue, fake_ocr):
    fake_clue(TARGET)
    calls = fake_ocr(True)
    result = answer_service.verify_answer(1, b"image", *FAR_FROM_TARGET)
    assert result.correct is False
    assert result.message == WRONG_PLACE_MESSAGE
    assert calls == []


def test_unknown_clue_raises(answer_service, fake_clue, fake_ocr):
    fake_clue(None)
    calls = fake_ocr(True)
    with pytest.raises(ClueNotFoundError):
        answer_service.verify_answer(999, b"image", *AT_TARGET)
    assert calls == []
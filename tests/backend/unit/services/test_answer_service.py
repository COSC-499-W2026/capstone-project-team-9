import pytest

from models import Target
from repositories import TargetRepository
from services import LocationService
from services.answer_service import (
    CORRECT_MESSAGE, WRONG_MESSAGE, AnswerService, ClueNotFoundError
)
from services.location_service import WRONG_PLACE_MESSAGE

TARGET = Target(name="COM 201", latitude=49.256, longitude=-123.250, radius=100)
AT_TARGET = (49.256, -123.250)
FAR_FROM_TARGET = (49.300, -123.300)


@pytest.fixture
def mock_target_repo(mocker):
    """Mock TargetRepository that returns TARGET for any clue by default."""
    repo = mocker.create_autospec(TargetRepository, instance=True)
    repo.get_target_for_clue.return_value = TARGET
    return repo


@pytest.fixture
def mock_matches_room(mocker):
    """Mock the OCR check used by answer_service; returns True by default."""
    return mocker.patch("services.answer_service.matches_room", return_value=True)


@pytest.fixture
def answer_service(mock_target_repo):
    return AnswerService(LocationService(), mock_target_repo)


def test_correct_answer_checks_room_code_from_target_name(
    answer_service, mock_target_repo, mock_matches_room
):
    result = answer_service.verify_answer(1, b"image", *AT_TARGET)
    assert result.correct is True
    assert result.message == CORRECT_MESSAGE
    mock_target_repo.get_target_for_clue.assert_called_once_with(1)
    mock_matches_room.assert_called_once_with(b"image", "COM201")  # space stripped


def test_wrong_photo_at_right_place(answer_service, mock_matches_room):
    mock_matches_room.return_value = False
    result = answer_service.verify_answer(1, b"image", *AT_TARGET)
    assert result.correct is False
    assert result.message == WRONG_MESSAGE


def test_wrong_location_skips_ocr(answer_service, mock_matches_room):
    result = answer_service.verify_answer(1, b"image", *FAR_FROM_TARGET)
    assert result.correct is False
    assert result.message == WRONG_PLACE_MESSAGE
    mock_matches_room.assert_not_called()


def test_unknown_clue_raises(answer_service, mock_target_repo, mock_matches_room):
    mock_target_repo.get_target_for_clue.return_value = None
    with pytest.raises(ClueNotFoundError):
        answer_service.verify_answer(999, b"image", *AT_TARGET)
    mock_target_repo.get_target_for_clue.assert_called_once_with(999)
    mock_matches_room.assert_not_called()
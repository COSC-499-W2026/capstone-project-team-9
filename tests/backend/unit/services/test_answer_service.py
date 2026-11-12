import pytest

from models import Target
from repositories import TargetRepository
from services import LocationService
from services.answer_service import (
    CORRECT_MESSAGE, WRONG_MESSAGE, AnswerService, ClueNotFoundError
)
from services.location_service import LocationResult

TARGET = Target(name="COM 201", latitude=49.256, longitude=-123.250, radius=100)
LAT_LON = (49.256, -123.250)
WRONG_PLACE = "You are not at the right place."


@pytest.fixture
def mock_target_repo(mocker):
    """Mock TargetRepository that returns TARGET for any clue by default."""
    repo = mocker.create_autospec(TargetRepository, instance=True)
    repo.get_target_for_clue.return_value = TARGET
    return repo


@pytest.fixture
def mock_location_service(mocker):
    """Mock LocationService that allows any location by default."""
    service = mocker.create_autospec(LocationService, instance=True)
    service.verify_location_with_target.return_value = LocationResult(True, "ok")
    return service


@pytest.fixture
def mock_matches_room(mocker):
    """Mock the OCR check used by answer_service; returns True by default."""
    return mocker.patch("services.answer_service.matches_room", return_value=True)


@pytest.fixture
def answer_service(mock_location_service, mock_target_repo):
    return AnswerService(mock_location_service, mock_target_repo)


def test_correct_answer_checks_room_code_from_target_name(
    answer_service, mock_target_repo, mock_location_service, mock_matches_room
):
    result = answer_service.verify_answer(1, b"image", *LAT_LON)
    assert result.correct is True
    assert result.message == CORRECT_MESSAGE
    mock_target_repo.get_target_for_clue.assert_called_once_with(1)
    mock_location_service.verify_location_with_target.assert_called_once_with(*LAT_LON, TARGET)
    mock_matches_room.assert_called_once_with(b"image", "COM201")  # space stripped


def test_wrong_photo_at_right_place(answer_service, mock_matches_room):
    mock_matches_room.return_value = False
    result = answer_service.verify_answer(1, b"image", *LAT_LON)
    assert result.correct is False
    assert result.message == WRONG_MESSAGE


def test_wrong_location_skips_ocr(answer_service, mock_location_service, mock_matches_room):
    mock_location_service.verify_location_with_target.return_value = LocationResult(
        False, WRONG_PLACE
    )
    result = answer_service.verify_answer(1, b"image", *LAT_LON)
    assert result.correct is False
    assert result.message == WRONG_PLACE  # location service's message is passed through
    mock_matches_room.assert_not_called()


def test_unknown_clue_raises(
    answer_service, mock_target_repo, mock_location_service, mock_matches_room
):
    mock_target_repo.get_target_for_clue.return_value = None
    with pytest.raises(ClueNotFoundError):
        answer_service.verify_answer(999, b"image", *LAT_LON)
    mock_target_repo.get_target_for_clue.assert_called_once_with(999)
    mock_location_service.verify_location_with_target.assert_not_called()
    mock_matches_room.assert_not_called()
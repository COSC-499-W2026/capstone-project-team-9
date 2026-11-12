import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.dependencies import get_play_service
from routers.answer_router import MAX_IMAGE_BYTES, router
from services import PlayService
from services.answer_service import CORRECT_MESSAGE, WRONG_MESSAGE
from services.play_service import (
    ClueAlreadySolvedError,
    ClueNotCurrentError,
    ClueNotInPlayError,
    PlayAnswerResult,
    PlayNotFoundError,
)

PLAY_ID = 1
CLUE_ID = 2
CORRECT = PlayAnswerResult(correct=True, message=CORRECT_MESSAGE, attempts=1, play_complete=False)


@pytest.fixture
def mock_play_service(mocker):
    """Mock PlayService; every answer is correct by default."""
    service = mocker.create_autospec(PlayService, instance=True)
    service.submit_answer.return_value = CORRECT
    return service


@pytest.fixture
def client(mock_play_service):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_play_service] = lambda: mock_play_service
    return TestClient(app)


def _post(client, play_id=PLAY_ID, clue_id=CLUE_ID, image=b"img", **overrides):
    data = {"latitude": 49.9, "longitude": -119.4} | overrides
    return client.post(
        f"/plays/{play_id}/clues/{clue_id}/answer",
        data=data,
        files={"image": ("p.jpg", image, "image/jpeg")},
    )


def test_correct_answer_returns_200_with_the_result(client, mock_play_service):
    r = _post(client)
    assert r.status_code == 200
    assert r.json() == {"correct": True, "message": CORRECT_MESSAGE, "attempts": 1, "play_complete": False}
    mock_play_service.submit_answer.assert_called_once_with(PLAY_ID, CLUE_ID, b"img", 49.9, -119.4)


def test_completed_play_is_reported(client, mock_play_service):
    mock_play_service.submit_answer.return_value = PlayAnswerResult(True, CORRECT_MESSAGE, 1, True)
    assert _post(client).json()["play_complete"] is True


def test_wrong_answer_is_still_200_with_its_attempt_count(client, mock_play_service):
    mock_play_service.submit_answer.return_value = PlayAnswerResult(False, WRONG_MESSAGE, 2, False)
    r = _post(client)
    assert r.status_code == 200
    assert r.json()["correct"] is False
    assert r.json()["attempts"] == 2


def test_unknown_play_returns_404(client, mock_play_service):
    mock_play_service.submit_answer.side_effect = PlayNotFoundError("Play does not exist")
    r = _post(client, play_id=999)
    assert r.status_code == 404
    assert r.json()["detail"] == "Play does not exist"


def test_clue_not_in_play_returns_404(client, mock_play_service):
    mock_play_service.submit_answer.side_effect = ClueNotInPlayError("Clue is not part of this play")
    r = _post(client, clue_id=999)
    assert r.status_code == 404
    assert r.json()["detail"] == "Clue is not part of this play"


def test_already_solved_clue_returns_409(client, mock_play_service):
    mock_play_service.submit_answer.side_effect = ClueAlreadySolvedError("Clue is already solved")
    assert _post(client).status_code == 409


def test_answering_a_non_current_clue_returns_409(client, mock_play_service):
    mock_play_service.submit_answer.side_effect = ClueNotCurrentError("Clue is not the current clue")
    r = _post(client)
    assert r.status_code == 409
    assert r.json()["detail"] == "Clue is not the current clue"


def test_unreadable_image_returns_422(client, mock_play_service):
    mock_play_service.submit_answer.side_effect = ValueError("Not a readable image")
    assert _post(client).status_code == 422


def test_oversized_image_returns_413(client, mock_play_service):
    assert _post(client, image=b"x" * (MAX_IMAGE_BYTES + 1)).status_code == 413
    mock_play_service.submit_answer.assert_not_called()


@pytest.mark.parametrize("overrides", [{"latitude": 200}, {"longitude": 500}, {"latitude": "x"}])
def test_invalid_form_fields_return_422(client, mock_play_service, overrides):
    assert _post(client, **overrides).status_code == 422
    mock_play_service.submit_answer.assert_not_called()


def test_missing_image_returns_422(client, mock_play_service):
    r = client.post(f"/plays/{PLAY_ID}/clues/{CLUE_ID}/answer", data={"latitude": 1, "longitude": 1})
    assert r.status_code == 422
    mock_play_service.submit_answer.assert_not_called()


def test_non_integer_ids_return_422(client, mock_play_service):
    assert _post(client, play_id="abc").status_code == 422
    assert _post(client, clue_id="abc").status_code == 422
    mock_play_service.submit_answer.assert_not_called()
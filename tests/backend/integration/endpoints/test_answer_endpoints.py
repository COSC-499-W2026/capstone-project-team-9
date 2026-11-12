"""
Integration tests for answer_router.py + play_service.py + repos + session
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.dependencies import get_play_service
from models import Game, Play, PlayClue
from repositories import ClueRepository, GameRepository, PlayRepository
from routers.answer_router import router
from services import PlayService
from services.answer_service import CORRECT_MESSAGE, WRONG_MESSAGE, AnswerResult, AnswerService

NUM_CLUES = 2
CORRECT = AnswerResult(True, CORRECT_MESSAGE)
WRONG = AnswerResult(False, WRONG_MESSAGE)


@pytest.fixture
def mock_answer_service(mocker):
    """Mock AnswerService (OCR + location); every answer is correct by default."""
    service = mocker.create_autospec(AnswerService, instance=True)
    service.verify_answer.return_value = CORRECT
    return service


@pytest.fixture
def play_service(session, mock_answer_service):
    """Real PlayService and repos on the test session; only the answer check is mocked."""
    return PlayService(
        mock_answer_service, PlayRepository(session), GameRepository(session), ClueRepository(session)
    )


@pytest.fixture
def client(play_service):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_play_service] = lambda: play_service
    return TestClient(app)


@pytest.fixture
def started(play_service, session, add_clues):
    """A real play of a game with NUM_CLUES clues (StartedPlay: .play and ordered .clue_ids)."""
    game = Game(num_clues=NUM_CLUES, language_id=1, difficulty_id=1)
    session.add(game)
    session.commit()
    add_clues(NUM_CLUES)
    return play_service.start_play(game.id)


def _post(client, play_id, clue_id, image=b"img"):
    return client.post(
        f"/plays/{play_id}/clues/{clue_id}/answer",
        data={"latitude": 49.9, "longitude": -119.4},
        files={"image": ("p.jpg", image, "image/jpeg")},
    )


def test_correct_answer_is_recorded(client, session, started, mock_answer_service):
    play, clue_ids = started.play, started.clue_ids
    r = _post(client, play.id, clue_ids[0])
    assert r.status_code == 200
    assert r.json() == {"correct": True, "message": CORRECT_MESSAGE, "attempts": 1, "play_complete": False}
    assert session.get(PlayClue, (play.id, clue_ids[0])).solved_at is not None
    mock_answer_service.verify_answer.assert_called_once_with(clue_ids[0], b"img", 49.9, -119.4)


def test_solving_every_clue_completes_the_play(client, session, started):
    play, clue_ids = started.play, started.clue_ids
    results = [_post(client, play.id, clue_id).json() for clue_id in clue_ids]
    assert [r["play_complete"] for r in results] == [False, True]
    assert session.get(Play, play.id).completed_at is not None


def test_next_clue_is_accepted_after_solving_the_current_one(client, started):
    play, clue_ids = started.play, started.clue_ids
    _post(client, play.id, clue_ids[0])
    r = _post(client, play.id, clue_ids[1])
    assert r.status_code == 200
    assert r.json()["correct"] is True


def test_wrong_answers_count_attempts_without_solving(client, session, started, mock_answer_service):
    play, clue_ids = started.play, started.clue_ids
    mock_answer_service.verify_answer.return_value = WRONG
    assert _post(client, play.id, clue_ids[0]).json()["attempts"] == 1
    r = _post(client, play.id, clue_ids[0])
    assert r.status_code == 200
    assert (r.json()["correct"], r.json()["attempts"]) == (False, 2)
    assert session.get(PlayClue, (play.id, clue_ids[0])).solved_at is None


def test_already_solved_clue_returns_409(client, started):
    play, clue_ids = started.play, started.clue_ids
    _post(client, play.id, clue_ids[0])
    assert _post(client, play.id, clue_ids[0]).status_code == 409


def test_answering_a_non_current_clue_returns_409(client, started):
    play, clue_ids = started.play, started.clue_ids
    r = _post(client, play.id, clue_ids[1])
    assert r.status_code == 409
    assert r.json()["detail"] == "Clue is not the current clue"
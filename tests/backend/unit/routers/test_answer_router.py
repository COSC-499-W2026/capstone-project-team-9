import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.db import get_session
from models import Play, PlayClue
from repositories import PlayRepository
from routers.answer_router import MAX_IMAGE_BYTES, router
from services.answer_service import AnswerResult


@pytest.fixture
def client(session):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: session
    return TestClient(app)


@pytest.fixture
def started(session, add_clues):
    """A play with two clues; returns (play, clue_ids)."""
    clue_ids = add_clues(2)
    return PlayRepository(session).add_play_with_clues(Play(), clue_ids), clue_ids


@pytest.fixture
def fake_verify(monkeypatch):
    def install(correct: bool = True, error: Exception | None = None):
        def fake(*args):
            if error:
                raise error
            return AnswerResult(correct, "Correct answer!" if correct else "nope")
        monkeypatch.setattr("services.play_service.verify_answer", fake)
    return install


def _post(client, play_id, clue_id, image=b"img", **overrides):
    data = {"latitude": 49.9, "longitude": -119.4} | overrides
    return client.post(
        f"/plays/{play_id}/clues/{clue_id}/answer",
        data=data,
        files={"image": ("p.jpg", image, "image/jpeg")},
    )


def test_correct_answer_is_recorded(client, session, started, fake_verify):
    play, clue_ids = started
    fake_verify(True)
    r = _post(client, play.id, clue_ids[0])
    assert r.status_code == 200
    assert r.json() == {"correct": True, "message": "Correct answer!", "attempts": 1, "play_complete": False}
    assert session.get(PlayClue, (play.id, clue_ids[0])).solved_at is not None


def test_solving_the_last_clue_completes_the_play(client, started, fake_verify):
    play, clue_ids = started
    fake_verify(True)
    _post(client, play.id, clue_ids[0])
    assert _post(client, play.id, clue_ids[1]).json()["play_complete"] is True


def test_wrong_answer_is_still_200_and_counts_an_attempt(client, session, started, fake_verify):
    play, clue_ids = started
    fake_verify(False)
    r = _post(client, play.id, clue_ids[0])
    assert r.status_code == 200
    assert r.json()["correct"] is False
    assert r.json()["attempts"] == 1
    assert session.get(PlayClue, (play.id, clue_ids[0])).solved_at is None


def test_unknown_play_returns_404(client, fake_verify):
    fake_verify(True)
    r = _post(client, 999, 1)
    assert r.status_code == 404
    assert r.json()["detail"] == "Play does not exist"


def test_clue_not_in_play_returns_404(client, started, fake_verify):
    play, _ = started
    fake_verify(True)
    r = _post(client, play.id, 999)
    assert r.status_code == 404
    assert r.json()["detail"] == "Clue is not part of this play"


def test_already_solved_clue_returns_409(client, started, fake_verify):
    play, clue_ids = started
    fake_verify(True)
    _post(client, play.id, clue_ids[0])
    assert _post(client, play.id, clue_ids[0]).status_code == 409


def test_unreadable_image_returns_422(client, started, fake_verify):
    play, clue_ids = started
    fake_verify(error=ValueError("Not a readable image"))
    assert _post(client, play.id, clue_ids[0]).status_code == 422


def test_oversized_image_returns_413(client, started, fake_verify):
    play, clue_ids = started
    fake_verify(True)
    assert _post(client, play.id, clue_ids[0], image=b"x" * (MAX_IMAGE_BYTES + 1)).status_code == 413


@pytest.mark.parametrize("overrides", [{"latitude": 200}, {"longitude": 500}, {"latitude": "x"}])
def test_invalid_form_fields_return_422(client, started, overrides):
    play, clue_ids = started
    assert _post(client, play.id, clue_ids[0], **overrides).status_code == 422


def test_missing_image_returns_422(client, started):
    play, clue_ids = started
    r = client.post(f"/plays/{play.id}/clues/{clue_ids[0]}/answer", data={"latitude": 1, "longitude": 1})
    assert r.status_code == 422


def test_non_integer_ids_return_422(client):
    assert _post(client, "abc", 1).status_code == 422
    assert _post(client, 1, "abc").status_code == 422

def test_answering_a_non_current_clue_returns_409(client, started, fake_verify):
    play, clue_ids = started
    fake_verify(True)
    r = _post(client, play.id, clue_ids[1])
    assert r.status_code == 409
    assert r.json()["detail"] == "Clue is not the current clue"
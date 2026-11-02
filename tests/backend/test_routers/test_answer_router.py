import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.db import get_session
from routers.answer_router import router
from services.answer_service import AnswerResult, ClueNotFoundError


@pytest.fixture
def client(session):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: session
    return TestClient(app)


def _post(client, **overrides):
    data = {"clue_id": 1, "latitude": 49.9, "longitude": -119.4} | overrides
    return client.post("/answers/verify", data=data, files={"image": ("p.jpg", b"img", "image/jpeg")})


def test_correct_answer(client, monkeypatch):
    monkeypatch.setattr("routers.answer_router.verify_answer",
                        lambda *a: AnswerResult(True, "Correct answer!"))
    r = _post(client)
    assert r.status_code == 200
    assert r.json() == {"correct": True, "message": "Correct answer!"}


def test_wrong_answer_is_still_200(client, monkeypatch):
    monkeypatch.setattr("routers.answer_router.verify_answer",
                        lambda *a: AnswerResult(False, "nope"))
    assert _post(client).json()["correct"] is False


def test_unknown_clue_returns_404(client, monkeypatch):
    def boom(*a): raise ClueNotFoundError("Clue does not exist")
    monkeypatch.setattr("routers.answer_router.verify_answer", boom)
    assert _post(client).status_code == 404


def test_unreadable_image_returns_422(client, monkeypatch):
    def boom(*a): raise ValueError("Not a readable image")
    monkeypatch.setattr("routers.answer_router.verify_answer", boom)
    assert _post(client).status_code == 422


@pytest.mark.parametrize("overrides", [{"latitude": 200}, {"longitude": 500}, {"clue_id": "x"}])
def test_invalid_form_fields_return_422(client, overrides):
    assert _post(client, **overrides).status_code == 422


def test_missing_image_returns_422(client):
    r = client.post("/answers/verify", data={"clue_id": 1, "latitude": 1, "longitude": 1})
    assert r.status_code == 422
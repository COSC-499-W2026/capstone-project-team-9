import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.db import get_session
from models import Difficulty, Game, Language
from routers.game_router import router
from services.game_options_service import MAX_GAME_LENGTH

NUM_CLUES = 3


@pytest.fixture
def client(session):
    session.add_all([Language(name="French"), Difficulty(name="Easy")])
    session.commit()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: session
    return TestClient(app)


def _body(**overrides):
    return {"language_id": 1, "difficulty_id": 1, "num_clues": NUM_CLUES} | overrides


def test_start_game_returns_201_with_game_settings_and_clues(client, session, add_clues):
    available = add_clues(5)
    r = client.post("/games", json=_body())
    assert r.status_code == 201
    data = r.json()
    game = data["game"]
    assert (game["language_id"], game["difficulty_id"], game["num_clues"]) == (1, 1, NUM_CLUES)
    clue_ids = [clue["id"] for clue in data["clues"]]
    assert len(clue_ids) == NUM_CLUES
    assert set(clue_ids) <= set(available)
    assert session.get(Game, game["id"]) is not None


def test_start_game_returns_422_when_not_enough_clues(client, session, add_clues):
    add_clues(NUM_CLUES - 1)
    r = client.post("/games", json=_body())
    assert r.status_code == 422
    assert "Not enough clues" in r.json()["detail"]
    assert session.get(Game, 1) is None


@pytest.mark.parametrize("overrides", [
    {"language_id": 999},
    {"difficulty_id": 999},
    {"num_clues": MAX_GAME_LENGTH + 1},
])
def test_start_game_rejects_unavailable_options_with_422(client, add_clues, overrides):
    add_clues(MAX_GAME_LENGTH + 1)
    r = client.post("/games", json=_body(**overrides))
    assert r.status_code == 422
    assert isinstance(r.json()["detail"], str)


@pytest.mark.parametrize("body", [{}, {"language_id": 1}, _body(num_clues=0), _body(language_id="x")])
def test_start_game_rejects_malformed_body(client, body):
    assert client.post("/games", json=body).status_code == 422
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.db import get_session
from models import Difficulty, Language
from routers.game_options_router import router
from services.game_options_service import MAX_GAME_LENGTH, MIN_GAME_LENGTH


@pytest.fixture
def client(session):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: session
    return TestClient(app)


def test_get_languages_returns_all(client, session):
    session.add_all([Language(name="French"), Language(name="Japanese")])
    session.commit()
    r = client.get("/languages")
    assert r.status_code == 200
    assert r.json() == [{"id": 1, "name": "French"}, {"id": 2, "name": "Japanese"}]


def test_get_difficulties_returns_all(client, session):
    session.add_all([Difficulty(name="Easy"), Difficulty(name="Hard")])
    session.commit()
    r = client.get("/difficulties")
    assert r.status_code == 200
    assert r.json() == [{"id": 1, "name": "Easy"}, {"id": 2, "name": "Hard"}]


@pytest.mark.parametrize("path", ["/languages", "/difficulties"])
def test_empty_tables_return_empty_list(client, path):
    r = client.get(path)
    assert r.status_code == 200
    assert r.json() == []


def test_get_game_length_range(client):
    r = client.get("/game-lengths")
    assert r.status_code == 200
    assert r.json() == {"min": MIN_GAME_LENGTH, "max": MAX_GAME_LENGTH}
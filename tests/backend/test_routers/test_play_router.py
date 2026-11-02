import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import select

from core.db import get_session
from models import Game, Play
from routers.play_router import router

NUM_CLUES = 3


@pytest.fixture
def client(session):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: session
    return TestClient(app)


@pytest.fixture
def game(session):
    game = Game(num_clues=NUM_CLUES, language_id=1, difficulty_id=1)
    session.add(game)
    session.commit()
    return game


def test_start_play_returns_201_with_play_and_ordered_clues(client, game, add_clues):
    available = add_clues(5)
    r = client.post(f"/games/{game.id}/plays")
    assert r.status_code == 201
    data = r.json()
    assert data["play"]["game_id"] == game.id
    assert data["play"]["id"] is not None
    clue_ids = [clue["id"] for clue in data["clues"]]
    assert len(clue_ids) == NUM_CLUES
    assert set(clue_ids) <= set(available)


def test_start_play_saves_the_play(client, session, game, add_clues):
    add_clues(NUM_CLUES)
    play_id = client.post(f"/games/{game.id}/plays").json()["play"]["id"]
    assert session.get(Play, play_id) is not None


def test_start_play_returns_404_for_unknown_game(client, session):
    r = client.post("/games/999/plays")
    assert r.status_code == 404
    assert r.json()["detail"] == "Game does not exist"
    assert session.exec(select(Play)).all() == []


def test_start_play_returns_422_when_not_enough_clues(client, session, game, add_clues):
    add_clues(NUM_CLUES - 1)
    r = client.post(f"/games/{game.id}/plays")
    assert r.status_code == 422
    assert "Not enough clues" in r.json()["detail"]
    assert session.exec(select(Play)).all() == []


def test_start_play_rejects_non_integer_game_id(client):
    assert client.post("/games/abc/plays").status_code == 422
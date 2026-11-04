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

def test_get_play_returns_progress(client, game, add_clues):
    add_clues(5)
    started = client.post(f"/games/{game.id}/plays").json()
    clue_ids = [c["id"] for c in started["clues"]]

    r = client.get(f"/plays/{started['play']['id']}")

    assert r.status_code == 200
    assert r.json() == {
        "id": started["play"]["id"],
        "game_id": game.id,
        "completed": False,
        "current_clue_id": clue_ids[0],
        "total_clues": NUM_CLUES,
        "solved_clues": 0,
    }


def test_get_play_reports_solved_count_and_next_current(client, game, add_clues, solve_clue):
    add_clues(5)
    started = client.post(f"/games/{game.id}/plays").json()
    play_id = started["play"]["id"]
    clue_ids = [c["id"] for c in started["clues"]]
    solve_clue(play_id, clue_ids[0])

    data = client.get(f"/plays/{play_id}").json()

    assert data["solved_clues"] == 1
    assert data["current_clue_id"] == clue_ids[1]


def test_get_play_returns_404_for_unknown_play(client):
    r = client.get("/plays/999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Play does not exist"


def test_get_play_rejects_non_integer_id(client):
    assert client.get("/plays/abc").status_code == 422
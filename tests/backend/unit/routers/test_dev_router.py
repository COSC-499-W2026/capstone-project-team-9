import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.db import get_session
from models import Clue, Target
from routers.dev_router import router


@pytest.fixture
def client(session):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: session
    return TestClient(app)


def test_get_clue_room_returns_the_clue_target_name(client, session):
    target = Target(name="COM 312", latitude=49.94, longitude=-119.39, radius=50)
    session.add(target)
    session.flush()
    clue = Clue(audio=b"audio", language_id=1, difficulty_id=1, target_id=target.id)
    session.add(clue)
    session.commit()

    r = client.get(f"/dev/clues/{clue.id}/room")

    assert r.status_code == 200
    assert r.json() == {"room": "COM 312"}


def test_get_clue_room_404s_for_missing_clue(client):
    assert client.get("/dev/clues/999/room").status_code == 404

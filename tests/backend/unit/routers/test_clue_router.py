import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.dependencies import get_clue_repository
from repositories import ClueRepository
from routers.clue_router import AUDIO_MEDIA_TYPE, router


@pytest.fixture
def mock_clue_repo(mocker):
    return mocker.create_autospec(ClueRepository, instance=True)


@pytest.fixture
def client(mock_clue_repo):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_clue_repository] = lambda: mock_clue_repo
    return TestClient(app)


def test_get_audio_returns_the_bytes_as_mp3(client, mock_clue_repo):
    mock_clue_repo.get_audio.return_value = b"mp3-bytes"
    r = client.get("/clues/5/audio")
    assert r.status_code == 200
    assert r.headers["content-type"] == AUDIO_MEDIA_TYPE
    assert r.content == b"mp3-bytes"
    mock_clue_repo.get_audio.assert_called_once_with(5)


def test_get_audio_404s_when_clue_has_no_audio(client, mock_clue_repo):
    mock_clue_repo.get_audio.return_value = None
    r = client.get("/clues/999/audio")
    assert r.status_code == 404
    assert r.json()["detail"] == "Clue has no audio"


def test_get_audio_rejects_non_integer_id(client, mock_clue_repo):
    assert client.get("/clues/abc/audio").status_code == 422
    mock_clue_repo.get_audio.assert_not_called()
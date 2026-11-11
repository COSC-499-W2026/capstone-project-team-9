import pytest
from models import Game
from repositories import GameRepository

@pytest.fixture
def game_repo(session):
    return GameRepository(session)


def test_add_game_saves_and_assigns_id(game_repo):
    game = game_repo.add_game(Game(num_clues=3, language_id=1, difficulty_id=1))
    assert game.id is not None


def test_get_game_found_and_missing(game_repo):
    saved = game_repo.add_game(Game(num_clues=3, language_id=1, difficulty_id=1))
    assert game_repo.get_game(saved.id).num_clues == 3
    assert game_repo.get_game(999) is None
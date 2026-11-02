from models import Game
from repositories.game_repo import add_game, get_game


def test_add_game_saves_and_assigns_id(session):
    game = add_game(session, Game(num_clues=3, language_id=1, difficulty_id=1))
    assert game.id is not None


def test_get_game_found_and_missing(session):
    saved = add_game(session, Game(num_clues=3, language_id=1, difficulty_id=1))
    assert get_game(session, saved.id).num_clues == 3
    assert get_game(session, 999) is None
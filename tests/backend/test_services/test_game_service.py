import pytest
from sqlmodel import select

from models import Difficulty, Game, Language
from schemas.game_schema import GameCreate
from services.game_options_service import MAX_GAME_LENGTH, MIN_GAME_LENGTH
from services.game_service import start_game

NUM_CLUES = 3


@pytest.fixture
def seeded(session):
    session.add_all([Language(name="French"), Difficulty(name="Easy")])
    session.commit()


def _settings(**overrides):
    values = {"language_id": 1, "difficulty_id": 1, "num_clues": NUM_CLUES} | overrides
    return GameCreate.model_construct(**values)


def _saved_games(session):
    return session.exec(select(Game)).all()


def test_start_game_saves_game_and_returns_requested_number_of_clues(session, seeded, add_clues):
    add_clues(5)
    started = start_game(session, _settings())
    assert started.game.id is not None
    assert (started.game.language_id, started.game.difficulty_id) == (1, 1)
    assert started.game.num_clues == NUM_CLUES
    assert len(started.clue_ids) == NUM_CLUES
    assert len(set(started.clue_ids)) == NUM_CLUES
    assert len(_saved_games(session)) == 1


def test_start_game_only_uses_clues_for_the_chosen_language_and_difficulty(session, seeded, add_clues):
    matching = add_clues(NUM_CLUES, language_id=1, difficulty_id=1)
    add_clues(4, language_id=2, difficulty_id=1)
    assert set(start_game(session, _settings()).clue_ids) == set(matching)


def test_start_game_works_with_exactly_enough_clues(session, seeded, add_clues):
    add_clues(NUM_CLUES)
    assert len(start_game(session, _settings()).clue_ids) == NUM_CLUES


def test_start_game_accepts_the_max_length(session, seeded, add_clues):
    add_clues(MAX_GAME_LENGTH)
    started = start_game(session, _settings(num_clues=MAX_GAME_LENGTH))
    assert len(started.clue_ids) == MAX_GAME_LENGTH


def test_start_game_records_creator_when_given(session, seeded, add_clues):
    add_clues(NUM_CLUES)
    assert start_game(session, _settings(), creator_id=7).game.creator_id == 7


@pytest.mark.parametrize("overrides,message", [
    ({"language_id": 999}, "Language does not exist"),
    ({"difficulty_id": 999}, "Difficulty does not exist"),
    ({"num_clues": MIN_GAME_LENGTH - 1}, "Game length must be between"),
    ({"num_clues": MAX_GAME_LENGTH + 1}, "Game length must be between"),
])
def test_start_game_rejects_unavailable_options(session, seeded, add_clues, overrides, message):
    add_clues(MAX_GAME_LENGTH + 1)
    with pytest.raises(ValueError, match=message):
        start_game(session, _settings(**overrides))
    assert _saved_games(session) == []


def test_start_game_rejects_when_not_enough_clues_and_saves_nothing(session, seeded, add_clues):
    add_clues(NUM_CLUES - 1)
    with pytest.raises(ValueError, match="Not enough clues"):
        start_game(session, _settings())
    assert _saved_games(session) == []
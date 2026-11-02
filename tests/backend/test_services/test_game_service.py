import pytest
from sqlmodel import select

from models import Difficulty, Game, Language
from schemas.game_schema import GameCreate
from services.game_options_service import MAX_GAME_LENGTH, MIN_GAME_LENGTH
from services.game_service import GameService
from repositories import ClueRepository   # TODO: mock ClueRepository instead of importing it

NUM_CLUES = 3


@pytest.fixture
def seeded(session):
    session.add_all([Language(name="French"), Difficulty(name="Easy")])
    session.commit()

@pytest.fixture
def game_service(session):
    return GameService(session, ClueRepository(session))


def _settings(**overrides):
    values = {"language_id": 1, "difficulty_id": 1, "num_clues": NUM_CLUES} | overrides
    return GameCreate.model_construct(**values)


def _saved_games(session):
    return session.exec(select(Game)).all()


def test_create_game_saves_and_returns_the_game(game_service, session, seeded, add_clues):
    add_clues(5)
    game = game_service.create_game(_settings())
    assert game.id is not None
    assert (game.language_id, game.difficulty_id, game.num_clues) == (1, 1, NUM_CLUES)
    assert len(_saved_games(session)) == 1


def test_create_game_only_counts_clues_for_the_chosen_language_and_difficulty(game_service, session, seeded, add_clues):
    add_clues(NUM_CLUES - 1, language_id=1, difficulty_id=1)
    add_clues(4, language_id=2, difficulty_id=1)  # wrong language, must not count
    with pytest.raises(ValueError, match="Not enough clues"):
        game_service.create_game(_settings())
    assert _saved_games(session) == []


def test_create_game_works_with_exactly_enough_clues(game_service, seeded, add_clues):
    add_clues(NUM_CLUES)
    assert game_service.create_game(_settings()).num_clues == NUM_CLUES


def test_create_game_accepts_the_max_length(game_service, seeded, add_clues):
    add_clues(MAX_GAME_LENGTH)
    game = game_service.create_game(_settings(num_clues=MAX_GAME_LENGTH))
    assert game.num_clues == MAX_GAME_LENGTH


def test_create_game_records_creator_when_given(game_service, seeded, add_clues):
    add_clues(NUM_CLUES)
    assert game_service.create_game(_settings(), creator_id=7).creator_id == 7


@pytest.mark.parametrize("overrides,message", [
    ({"language_id": 999}, "Language does not exist"),
    ({"difficulty_id": 999}, "Difficulty does not exist"),
    ({"num_clues": MIN_GAME_LENGTH - 1}, "Game length must be between"),
    ({"num_clues": MAX_GAME_LENGTH + 1}, "Game length must be between"),
])
def test_create_game_rejects_unavailable_options(game_service, session, seeded, add_clues, overrides, message):
    add_clues(MAX_GAME_LENGTH + 1)
    with pytest.raises(ValueError, match=message):
        game_service.create_game(_settings(**overrides))
    assert _saved_games(session) == []


def test_create_game_rejects_when_not_enough_clues_and_saves_nothing(game_service, session, seeded, add_clues):
    add_clues(NUM_CLUES - 1)
    with pytest.raises(ValueError, match="Not enough clues"):
        game_service.create_game(_settings())
    assert _saved_games(session) == []
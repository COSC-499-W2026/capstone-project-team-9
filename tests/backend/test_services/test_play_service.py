import pytest
from sqlmodel import select

from models import Game, Play, PlayClue
from services.play_service import GameNotFoundError, start_play

NUM_CLUES = 3


@pytest.fixture
def game(session):
    game = Game(num_clues=NUM_CLUES, language_id=1, difficulty_id=1)
    session.add(game)
    session.commit()
    return game


def _saved_plays(session):
    return session.exec(select(Play)).all()


def test_start_play_saves_play_for_the_game(session, game, add_clues):
    add_clues(5)
    started = start_play(session, game.id)
    assert started.play.id is not None
    assert started.play.game_id == game.id
    assert len(_saved_plays(session)) == 1


def test_start_play_returns_the_requested_number_of_distinct_clues(session, game, add_clues):
    add_clues(5)
    clue_ids = start_play(session, game.id).clue_ids
    assert len(clue_ids) == NUM_CLUES
    assert len(set(clue_ids)) == NUM_CLUES


def test_start_play_saves_the_clues_in_the_returned_order(session, game, add_clues):
    add_clues(5)
    started = start_play(session, game.id)
    rows = session.exec(
        select(PlayClue).where(PlayClue.play_id == started.play.id).order_by(PlayClue.position)
    ).all()
    assert [r.clue_id for r in rows] == started.clue_ids
    assert [r.position for r in rows] == [1, 2, 3]


def test_start_play_only_uses_clues_for_the_games_language_and_difficulty(session, game, add_clues):
    matching = add_clues(NUM_CLUES, language_id=1, difficulty_id=1)
    add_clues(4, language_id=2, difficulty_id=1)
    add_clues(4, language_id=1, difficulty_id=2)
    assert set(start_play(session, game.id).clue_ids) == set(matching)


def test_start_play_works_with_exactly_enough_clues(session, game, add_clues):
    add_clues(NUM_CLUES)
    assert len(start_play(session, game.id).clue_ids) == NUM_CLUES


def test_start_play_records_user_when_given(session, game, add_clues):
    add_clues(NUM_CLUES)
    assert start_play(session, game.id, user_id=7).play.user_id == 7


def test_start_play_user_is_none_by_default(session, game, add_clues):
    add_clues(NUM_CLUES)
    assert start_play(session, game.id).play.user_id is None


def test_start_play_raises_when_game_does_not_exist_and_saves_nothing(session):
    with pytest.raises(GameNotFoundError):
        start_play(session, 999)
    assert _saved_plays(session) == []


def test_start_play_raises_when_not_enough_clues_and_saves_nothing(session, game, add_clues):
    add_clues(NUM_CLUES - 1)
    with pytest.raises(ValueError, match="Not enough clues"):
        start_play(session, game.id)
    assert _saved_plays(session) == []
    assert session.exec(select(PlayClue)).all() == []
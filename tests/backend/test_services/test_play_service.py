import pytest
from sqlmodel import select

from models import Game, Play, PlayClue
from services.play_service import GameNotFoundError, PlayService, PlayNotFoundError
from repositories import ClueRepository, GameRepository # TODO in future: MOCK these repositories

NUM_CLUES = 3


@pytest.fixture
def game(session):
    game = Game(num_clues=NUM_CLUES, language_id=1, difficulty_id=1)
    session.add(game)
    session.commit()
    return game

@pytest.fixture
def play_service(session):
    return PlayService(session, GameRepository(session), ClueRepository(session))


def _saved_plays(session):
    return session.exec(select(Play)).all()


def test_start_play_saves_play_for_the_game(play_service, session, game, add_clues):
    add_clues(5)
    started = play_service.start_play(game.id)
    assert started.play.id is not None
    assert started.play.game_id == game.id
    assert len(_saved_plays(session)) == 1


def test_start_play_returns_the_requested_number_of_distinct_clues(play_service, game, add_clues):
    add_clues(5)
    clue_ids = play_service.start_play(game.id).clue_ids
    assert len(clue_ids) == NUM_CLUES
    assert len(set(clue_ids)) == NUM_CLUES


def test_start_play_saves_the_clues_in_the_returned_order(play_service, session, game, add_clues):
    add_clues(5)
    started = play_service.start_play(game.id)
    rows = session.exec(
        select(PlayClue).where(PlayClue.play_id == started.play.id).order_by(PlayClue.position)
    ).all()
    assert [r.clue_id for r in rows] == started.clue_ids
    assert [r.position for r in rows] == [1, 2, 3]


def test_start_play_only_uses_clues_for_the_games_language_and_difficulty(play_service, game, add_clues):
    matching = add_clues(NUM_CLUES, language_id=1, difficulty_id=1)
    add_clues(4, language_id=2, difficulty_id=1)
    add_clues(4, language_id=1, difficulty_id=2)
    assert set(play_service.start_play(game.id).clue_ids) == set(matching)


def test_start_play_works_with_exactly_enough_clues(play_service, game, add_clues):
    add_clues(NUM_CLUES)
    assert len(play_service.start_play(game.id).clue_ids) == NUM_CLUES


def test_start_play_records_user_when_given(play_service, game, add_clues):
    add_clues(NUM_CLUES)
    assert play_service.start_play(game.id, user_id=7).play.user_id == 7


def test_start_play_user_is_none_by_default(play_service, game, add_clues):
    add_clues(NUM_CLUES)
    assert play_service.start_play(game.id).play.user_id is None


def test_start_play_raises_when_game_does_not_exist_and_saves_nothing(play_service, session):
    with pytest.raises(GameNotFoundError):
        play_service.start_play(999)
    assert _saved_plays(session) == []


def test_start_play_raises_when_not_enough_clues_and_saves_nothing(play_service, session, game, add_clues):
    add_clues(NUM_CLUES - 1)
    with pytest.raises(ValueError, match="Not enough clues"):
        play_service.start_play(game.id)
    assert _saved_plays(session) == []
    assert session.exec(select(PlayClue)).all() == []

def test_get_play_state_current_clue_is_first_when_nothing_solved(play_service, game, add_clues):
    add_clues(5)
    started = play_service.start_play(game.id)
    state = play_service.get_play_state(started.play.id)
    assert state.current_clue_id == started.clue_ids[0]


def test_get_play_state_current_clue_skips_solved_ones(play_service, game, add_clues, solve_clue):
    add_clues(5)
    started = play_service.start_play(game.id)
    solve_clue(started.play.id, started.clue_ids[0])
    assert play_service.get_play_state(started.play.id).current_clue_id == started.clue_ids[1]


def test_get_play_state_current_clue_is_lowest_unsolved_when_solved_out_of_order(
    play_service, game, add_clues, solve_clue
):
    add_clues(5)
    started = play_service.start_play(game.id)
    solve_clue(started.play.id, started.clue_ids[1])  # solve the 2nd clue first
    assert play_service.get_play_state(started.play.id).current_clue_id == started.clue_ids[0]
    solve_clue(started.play.id, started.clue_ids[0])
    assert play_service.get_play_state(started.play.id).current_clue_id == started.clue_ids[2]


def test_get_play_state_current_clue_is_none_when_all_solved(play_service, game, add_clues, solve_clue):
    add_clues(NUM_CLUES)
    started = play_service.start_play(game.id)
    for clue_id in started.clue_ids:
        solve_clue(started.play.id, clue_id)
    assert play_service.get_play_state(started.play.id).current_clue_id is None


def test_get_play_state_raises_for_unknown_play(play_service):
    with pytest.raises(PlayNotFoundError):
        play_service.get_play_state(999)

def test_get_play_state_counts_total_and_solved(play_service, game, add_clues, solve_clue):
    add_clues(5)
    started = play_service.start_play(game.id)
    state = play_service.get_play_state(started.play.id)
    assert (state.total_clues, state.solved_clues) == (NUM_CLUES, 0)

    solve_clue(started.play.id, started.clue_ids[0])
    solve_clue(started.play.id, started.clue_ids[2])  # out of order on purpose
    state = play_service.get_play_state(started.play.id)
    assert (state.total_clues, state.solved_clues) == (NUM_CLUES, 2)
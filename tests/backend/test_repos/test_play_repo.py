from sqlmodel import select

from models import Play, PlayClue
from repositories.play_repo import (
    add_play_with_clues, get_play, count_play_clues,
    count_solved_play_clues, get_current_clue_id,
    get_play, get_play_clue, mark_play_complete, record_attempt
)

def _rows(session, play_id):
    statement = select(PlayClue).where(PlayClue.play_id == play_id).order_by(PlayClue.position)
    return session.exec(statement).all()


def test_add_play_with_clues_saves_play_and_returns_it_with_id(session):
    play = add_play_with_clues(session, Play(), [1, 2])
    assert play.id is not None
    assert session.get(Play, play.id) is not None


def test_clues_are_saved_in_order_starting_at_one(session):
    play = add_play_with_clues(session, Play(), [30, 10, 20])
    assert [(r.clue_id, r.position) for r in _rows(session, play.id)] == [(30, 1), (10, 2), (20, 3)]


def test_clues_start_unsolved_with_zero_attempts(session):
    play = add_play_with_clues(session, Play(), [1, 2])
    assert all(r.solved_at is None and r.attempts == 0 for r in _rows(session, play.id))


def test_clues_belong_only_to_their_own_play(session):
    first = add_play_with_clues(session, Play(), [1, 2])
    second = add_play_with_clues(session, Play(), [1, 3])
    assert len(_rows(session, first.id)) == 2
    assert [r.clue_id for r in _rows(session, second.id)] == [1, 3]

def test_get_play_found_and_missing(session):
    play = add_play_with_clues(session, Play(), [1])
    assert get_play(session, play.id).id == play.id
    assert get_play(session, 999) is None


def test_count_play_clues_only_counts_the_requested_play(session):
    first = add_play_with_clues(session, Play(), [1, 2, 3])
    add_play_with_clues(session, Play(), [4, 5])
    assert count_play_clues(session, first.id) == 3


def test_count_play_clues_is_zero_for_unknown_play(session):
    assert count_play_clues(session, 999) == 0


def test_count_solved_play_clues_counts_only_solved_ones(session, solve_clue):
    play = add_play_with_clues(session, Play(), [1, 2, 3])
    assert count_solved_play_clues(session, play.id) == 0
    solve_clue(play.id, 1)
    solve_clue(play.id, 3)
    assert count_solved_play_clues(session, play.id) == 2


def test_count_solved_play_clues_ignores_other_plays(session, solve_clue):
    first = add_play_with_clues(session, Play(), [1, 2])
    second = add_play_with_clues(session, Play(), [1, 2])
    solve_clue(second.id, 1)
    assert count_solved_play_clues(session, first.id) == 0


def test_get_current_clue_id_is_the_first_position_when_nothing_solved(session):
    play = add_play_with_clues(session, Play(), [30, 10, 20])
    assert get_current_clue_id(session, play.id) == 30


def test_get_current_clue_id_skips_solved_clues(session, solve_clue):
    play = add_play_with_clues(session, Play(), [30, 10, 20])
    solve_clue(play.id, 30)
    assert get_current_clue_id(session, play.id) == 10


def test_get_current_clue_id_is_lowest_unsolved_when_solved_out_of_order(session, solve_clue):
    play = add_play_with_clues(session, Play(), [30, 10, 20])
    solve_clue(play.id, 10)  # the 2nd clue is solved first
    assert get_current_clue_id(session, play.id) == 30


def test_get_current_clue_id_orders_by_position_not_insertion(session):
    # inserted out of order on purpose, so this fails if the ORDER BY is missing
    session.add_all([
        PlayClue(play_id=1, clue_id=1, position=2),
        PlayClue(play_id=1, clue_id=2, position=1),
    ])
    session.commit()
    assert get_current_clue_id(session, 1) == 2


def test_get_current_clue_id_is_none_when_all_solved(session, solve_clue):
    play = add_play_with_clues(session, Play(), [1, 2])
    solve_clue(play.id, 1)
    solve_clue(play.id, 2)
    assert get_current_clue_id(session, play.id) is None


def test_get_current_clue_id_ignores_other_plays(session, solve_clue):
    first = add_play_with_clues(session, Play(), [1, 2])
    second = add_play_with_clues(session, Play(), [3, 4])
    solve_clue(first.id, 1)
    assert get_current_clue_id(session, second.id) == 3

def test_get_play_clue_found_and_missing(session):
    play = add_play_with_clues(session, Play(), [1, 2])
    assert get_play_clue(session, play.id, 2).position == 2
    assert get_play_clue(session, play.id, 999) is None


def test_get_play_clue_is_scoped_to_its_play(session):
    first = add_play_with_clues(session, Play(), [1])
    second = add_play_with_clues(session, Play(), [2])
    assert get_play_clue(session, first.id, 2) is None
    assert get_play_clue(session, second.id, 2) is not None


def test_record_attempt_wrong_counts_but_does_not_solve(session):
    play = add_play_with_clues(session, Play(), [1])
    play_clue = record_attempt(session, get_play_clue(session, play.id, 1), solved=False)
    assert play_clue.attempts == 1
    assert play_clue.solved_at is None


def test_record_attempt_correct_counts_and_solves(session):
    play = add_play_with_clues(session, Play(), [1])
    play_clue = record_attempt(session, get_play_clue(session, play.id, 1), solved=True)
    assert play_clue.attempts == 1
    assert play_clue.solved_at is not None


def test_record_attempt_accumulates_attempts(session):
    play = add_play_with_clues(session, Play(), [1])
    play_clue = get_play_clue(session, play.id, 1)
    record_attempt(session, play_clue, solved=False)
    record_attempt(session, play_clue, solved=False)
    assert record_attempt(session, play_clue, solved=True).attempts == 3


def test_record_attempt_only_touches_that_clue(session):
    play = add_play_with_clues(session, Play(), [1, 2])
    record_attempt(session, get_play_clue(session, play.id, 1), solved=True)
    other = get_play_clue(session, play.id, 2)
    assert (other.attempts, other.solved_at) == (0, None)


def test_mark_play_complete_sets_completed_at(session):
    play = add_play_with_clues(session, Play(), [1])
    assert play.completed_at is None
    assert mark_play_complete(session, play).completed_at is not None
import pytest

from sqlmodel import select

from models import Play, PlayClue
from repositories import PlayRepository

@pytest.fixture
def play_repo(session):
    return PlayRepository(session)


def _rows(session, play_id):
    statement = select(PlayClue).where(PlayClue.play_id == play_id).order_by(PlayClue.position)
    return session.exec(statement).all()


def test_add_play_with_clues_saves_play_and_returns_it_with_id(session, play_repo):
    play = play_repo.add_play_with_clues(Play(), [1, 2])
    assert play.id is not None
    assert session.get(Play, play.id) is not None


def test_clues_are_saved_in_order_starting_at_one(session, play_repo):
    play = play_repo.add_play_with_clues(Play(), [30, 10, 20])
    assert [(r.clue_id, r.position) for r in _rows(session, play.id)] == [(30, 1), (10, 2), (20, 3)]


def test_clues_start_unsolved_with_zero_attempts(session, play_repo):
    play = play_repo.add_play_with_clues(Play(), [1, 2])
    assert all(r.solved_at is None and r.attempts == 0 for r in _rows(session, play.id))


def test_clues_belong_only_to_their_own_play(session, play_repo):
    first = play_repo.add_play_with_clues(Play(), [1, 2])
    second = play_repo.add_play_with_clues(Play(), [1, 3])
    assert len(_rows(session, first.id)) == 2
    assert [r.clue_id for r in _rows(session, second.id)] == [1, 3]

def test_get_play_found_and_missing(play_repo):
    play = play_repo.add_play_with_clues(Play(), [1])
    assert play_repo.get_play(play.id).id == play.id
    assert play_repo.get_play(999) is None


def test_count_play_clues_only_counts_the_requested_play(play_repo):
    first = play_repo.add_play_with_clues(Play(), [1, 2, 3])
    play_repo.add_play_with_clues(Play(), [4, 5])
    assert play_repo.count_play_clues(first.id) == 3


def test_count_play_clues_is_zero_for_unknown_play(play_repo):
    assert play_repo.count_play_clues(999) == 0


def test_count_solved_play_clues_counts_only_solved_ones(solve_clue, play_repo):
    play = play_repo.add_play_with_clues(Play(), [1, 2, 3])
    assert play_repo.count_solved_play_clues(play.id) == 0
    solve_clue(play.id, 1)
    solve_clue(play.id, 3)
    assert play_repo.count_solved_play_clues(play.id) == 2


def test_count_solved_play_clues_ignores_other_plays(solve_clue, play_repo):
    first = play_repo.add_play_with_clues(Play(), [1, 2])
    second = play_repo.add_play_with_clues(Play(), [1, 2])
    solve_clue(second.id, 1)
    assert play_repo.count_solved_play_clues(first.id) == 0


def test_get_current_clue_id_is_the_first_position_when_nothing_solved(play_repo):
    play = play_repo.add_play_with_clues(Play(), [30, 10, 20])
    assert play_repo.get_current_clue_id(play.id) == 30


def test_get_current_clue_id_skips_solved_clues(solve_clue, play_repo):
    play = play_repo.add_play_with_clues(Play(), [30, 10, 20])
    solve_clue(play.id, 30)
    assert play_repo.get_current_clue_id(play.id) == 10


def test_get_current_clue_id_is_lowest_unsolved_when_solved_out_of_order(solve_clue, play_repo):
    play = play_repo.add_play_with_clues(Play(), [30, 10, 20])
    solve_clue(play.id, 10)  # the 2nd clue is solved first
    assert play_repo.get_current_clue_id(play.id) == 30


def test_get_current_clue_id_orders_by_position_not_insertion(session, play_repo):
    # inserted out of order on purpose, so this fails if the ORDER BY is missing
    session.add_all([
        PlayClue(play_id=1, clue_id=1, position=2),
        PlayClue(play_id=1, clue_id=2, position=1),
    ])
    session.commit()
    assert play_repo.get_current_clue_id(1) == 2


def test_get_current_clue_id_is_none_when_all_solved(solve_clue, play_repo):
    play = play_repo.add_play_with_clues(Play(), [1, 2])
    solve_clue(play.id, 1)
    solve_clue(play.id, 2)
    assert play_repo.get_current_clue_id(play.id) is None


def test_get_current_clue_id_ignores_other_plays(solve_clue, play_repo):
    first = play_repo.add_play_with_clues(Play(), [1, 2])
    second = play_repo.add_play_with_clues(Play(), [3, 4])
    solve_clue(first.id, 1)
    assert play_repo.get_current_clue_id(second.id) == 3

def test_get_play_clue_found_and_missing(play_repo):
    play = play_repo.add_play_with_clues(Play(), [1, 2])
    assert play_repo.get_play_clue(play.id, 2).position == 2
    assert play_repo.get_play_clue(play.id, 999) is None


def test_get_play_clue_is_scoped_to_its_play(play_repo):
    first = play_repo.add_play_with_clues(Play(), [1])
    second = play_repo.add_play_with_clues(Play(), [2])
    assert play_repo.get_play_clue(first.id, 2) is None
    assert play_repo.get_play_clue(second.id, 2) is not None


def test_record_attempt_wrong_counts_but_does_not_solve(play_repo):
    play = play_repo.add_play_with_clues(Play(), [1])
    play_clue = play_repo.record_attempt(play_repo.get_play_clue(play.id, 1), solved=False)
    assert play_clue.attempts == 1
    assert play_clue.solved_at is None


def test_record_attempt_correct_counts_and_solves(play_repo):
    play = play_repo.add_play_with_clues(Play(), [1])
    play_clue = play_repo.record_attempt(play_repo.get_play_clue(play.id, 1), solved=True)
    assert play_clue.attempts == 1
    assert play_clue.solved_at is not None


def test_record_attempt_accumulates_attempts(play_repo):
    play = play_repo.add_play_with_clues(Play(), [1])
    play_clue = play_repo.get_play_clue(play.id, 1)
    play_repo.record_attempt(play_clue, solved=False)
    play_repo.record_attempt(play_clue, solved=False)
    assert play_repo.record_attempt(play_clue, solved=True).attempts == 3


def test_record_attempt_only_touches_that_clue(play_repo):
    play = play_repo.add_play_with_clues(Play(), [1, 2])
    play_repo.record_attempt(play_repo.get_play_clue(play.id, 1), solved=True)
    other = play_repo.get_play_clue(play.id, 2)
    assert (other.attempts, other.solved_at) == (0, None)


def test_mark_play_complete_sets_completed_at(play_repo):
    play = play_repo.add_play_with_clues(Play(), [1])
    assert play.completed_at is None
    assert play_repo.mark_play_complete(play).completed_at is not None
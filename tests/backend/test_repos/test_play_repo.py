from sqlmodel import select

from models import Play, PlayClue
from repositories.play_repo import add_play_with_clues, get_play, get_play_clues


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


def test_get_play_clues_are_ordered_by_position(session):
    # inserted out of order on purpose, so this fails if the ORDER BY is missing
    session.add_all([
        PlayClue(play_id=1, clue_id=1, position=2),
        PlayClue(play_id=1, clue_id=2, position=1),
    ])
    session.commit()
    assert [c.clue_id for c in get_play_clues(session, 1)] == [2, 1]


def test_get_play_clues_only_returns_the_requested_play(session):
    first = add_play_with_clues(session, Play(), [1, 2])
    add_play_with_clues(session, Play(), [3])
    assert [c.clue_id for c in get_play_clues(session, first.id)] == [1, 2]


def test_get_play_clues_empty_for_unknown_play(session):
    assert get_play_clues(session, 999) == []
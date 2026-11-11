import pytest
from sqlalchemy.exc import IntegrityError

from models import Play, PlayClue


def test_play_gets_defaults(session):
    play = Play()
    session.add(play)
    session.commit()
    assert play.id is not None
    assert play.started_at is not None
    assert play.score is None
    assert play.completed_at is None


def test_play_clue_starts_unsolved_with_zero_attempts(session):
    session.add(PlayClue(play_id=1, clue_id=1, position=1))
    session.commit()
    row = session.get(PlayClue, (1, 1))
    assert row.solved_at is None
    assert row.attempts == 0


def test_play_clue_rejects_duplicate_position_in_same_play(session):
    session.add_all([
        PlayClue(play_id=1, clue_id=1, position=1),
        PlayClue(play_id=1, clue_id=2, position=1),
    ])
    with pytest.raises(IntegrityError):
        session.commit()
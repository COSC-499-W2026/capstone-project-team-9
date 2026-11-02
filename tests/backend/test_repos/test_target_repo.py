from models import Clue, Target
from repositories.target_repo import get_target_by_id


def test_get_target_by_id_returns_the_clues_target(session, add_clues):
    clue_id = add_clues(1)[0]
    target = get_target_by_id(session, clue_id)
    assert target is not None
    assert target.id == session.get(Clue, clue_id).target_id


def test_get_target_by_id_picks_the_right_target_for_each_clue(session, add_clues):
    for clue_id in add_clues(3):
        assert get_target_by_id(session, clue_id).id == session.get(Clue, clue_id).target_id


def test_get_target_by_id_takes_a_clue_id_not_a_target_id(session, add_clues):
    # An unused target takes id 1, so the clue's target gets id 2 while the clue itself is id 1.
    session.add(Target(name="unused", latitude=49, longitude=-119, radius=50))
    session.commit()
    clue_id = add_clues(1)[0]
    assert get_target_by_id(session, clue_id).name != "unused"


def test_get_target_by_id_is_none_for_missing_clue(session):
    assert get_target_by_id(session, 999) is None
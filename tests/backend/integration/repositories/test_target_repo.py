import pytest
from models import Clue, Target
from repositories import TargetRepository

@pytest.fixture
def target_repo(session):
    return TargetRepository(session)



def test_get_target_for_clue__returns_target(target_repo, session, add_clues):
    clue_id = add_clues(1)[0]
    target = target_repo.get_target_for_clue(clue_id)
    assert target is not None
    assert target.id == session.get(Clue, clue_id).target_id


def test_get_target_for_clue__correct_for_each_clue(target_repo, session, add_clues):
    for clue_id in add_clues(3):
        assert target_repo.get_target_for_clue(clue_id).id == session.get(Clue, clue_id).target_id


def test_get_target_for_clue__takes_clue_id(target_repo, session, add_clues):
    # An unused target takes id 1, so the clue's target gets id 2 while the clue itself is id 1.
    session.add(Target(name="unused", latitude=49, longitude=-119, radius=50))
    session.commit()
    clue_id = add_clues(1)[0]
    assert target_repo.get_target_for_clue(clue_id).name != "unused"


def test_get_target_for_clue__none_if_clue_missing(target_repo):
    assert target_repo.get_target_for_clue(999) is None

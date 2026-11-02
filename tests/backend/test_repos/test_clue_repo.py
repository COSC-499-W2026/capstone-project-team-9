from repositories.clue_repo import get_random_clue_ids, count_clues, get_target_by_id
from models import Clue, Target

def test_returns_the_requested_number_of_distinct_ids(session, add_clues):
    add_clues(6)
    ids = get_random_clue_ids(session, 1, 1, 4)
    assert len(ids) == 4
    assert len(set(ids)) == 4


def test_only_returns_clues_matching_language_and_difficulty(session, add_clues):
    matching = add_clues(3, language_id=1, difficulty_id=1)
    add_clues(3, language_id=2, difficulty_id=1)
    add_clues(3, language_id=1, difficulty_id=2)
    assert set(get_random_clue_ids(session, 1, 1, 10)) == set(matching)


def test_returns_everything_available_when_fewer_than_count(session, add_clues):
    available = add_clues(2)
    assert set(get_random_clue_ids(session, 1, 1, 5)) == set(available)


def test_returns_empty_list_when_no_clues_match(session):
    assert get_random_clue_ids(session, 1, 1, 5) == []

def test_count_clues_matches_language_and_difficulty_only(session, add_clues):
    add_clues(3, language_id=1, difficulty_id=1)
    add_clues(2, language_id=2, difficulty_id=1)
    add_clues(4, language_id=1, difficulty_id=2)
    assert count_clues(session, 1, 1) == 3


def test_count_clues_is_zero_when_none_match(session):
    assert count_clues(session, 1, 1) == 0



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
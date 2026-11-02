import pytest
from repositories import ClueRepository

@pytest.fixture
def clue_repo(session):
    return ClueRepository(session)


def test_returns_the_requested_number_of_distinct_ids(clue_repo, add_clues):
    add_clues(6)
    ids = clue_repo.get_random_clue_ids(1, 1, 4)
    assert len(ids) == 4
    assert len(set(ids)) == 4


def test_only_returns_clues_matching_language_and_difficulty(clue_repo, add_clues):
    matching = add_clues(3, language_id=1, difficulty_id=1)
    add_clues(3, language_id=2, difficulty_id=1)
    add_clues(3, language_id=1, difficulty_id=2)
    assert set(clue_repo.get_random_clue_ids(1, 1, 10)) == set(matching)


def test_returns_everything_available_when_fewer_than_count(clue_repo, add_clues):
    available = add_clues(2)
    assert set(clue_repo.get_random_clue_ids(1, 1, 5)) == set(available)


def test_returns_empty_list_when_no_clues_match(clue_repo):
    assert clue_repo.get_random_clue_ids(1, 1, 5) == []

def test_count_clues_matches_language_and_difficulty_only(clue_repo, add_clues):
    add_clues(3, language_id=1, difficulty_id=1)
    add_clues(2, language_id=2, difficulty_id=1)
    add_clues(4, language_id=1, difficulty_id=2)
    assert clue_repo.count_clues(1, 1) == 3


def test_count_clues_is_zero_when_none_match(clue_repo):
    assert clue_repo.count_clues(1, 1) == 0
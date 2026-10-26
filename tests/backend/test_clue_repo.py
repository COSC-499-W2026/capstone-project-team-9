from repositories.clue_repo import get_random_clue_ids


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
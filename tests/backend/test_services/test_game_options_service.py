from services.game_options_service import (
    MAX_GAME_LENGTH,
    MIN_GAME_LENGTH,
    get_game_length_range,
)


def test_max_equals_clue_count_when_fewer_than_cap(session, add_clues):
    add_clues(6)
    result = get_game_length_range(session, 1, 1)
    assert (result.min, result.max) == (MIN_GAME_LENGTH, 6)


def test_max_is_capped_by_max_game_length(session, add_clues):
    add_clues(MAX_GAME_LENGTH + 3)
    assert get_game_length_range(session, 1, 1).max == MAX_GAME_LENGTH


def test_no_clues_returns_zero_range(session):
    result = get_game_length_range(session, 1, 1)
    assert (result.min, result.max) == (0, 0)


def test_only_counts_clues_for_the_chosen_combo(session, add_clues):
    add_clues(2, language_id=1, difficulty_id=1)
    add_clues(5, language_id=2, difficulty_id=1)
    assert get_game_length_range(session, 1, 1).max == 2
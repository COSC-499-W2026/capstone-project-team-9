import pytest
from models import Difficulty, Language
from repositories import GameOptionsRepository

@pytest.fixture
def game_options_repo(session):
    return GameOptionsRepository(session)


def test_get_all_languages_returns_them_sorted_by_name(session, game_options_repo):
    session.add_all([Language(name="Spanish"), Language(name="French")])
    session.commit()
    assert [l.name for l in game_options_repo.get_all_languages()] == ["French", "Spanish"]


def test_get_all_languages_empty_table(game_options_repo):
    assert game_options_repo.get_all_languages() == []


def test_get_all_difficulties_keeps_insertion_order(session, game_options_repo):
    session.add_all([Difficulty(name="Easy"), Difficulty(name="Hard"), Difficulty(name="Medium")])
    session.commit()
    assert [d.name for d in game_options_repo.get_all_difficulties()] == ["Easy", "Hard", "Medium"]


def test_get_language_found_and_missing(session, game_options_repo):
    session.add(Language(name="French"))
    session.commit()
    assert game_options_repo.get_language(1).name == "French"
    assert game_options_repo.get_language(999) is None


def test_get_difficulty_found_and_missing(session, game_options_repo):
    session.add(Difficulty(name="Easy"))
    session.commit()
    assert game_options_repo.get_difficulty(1).name == "Easy"
    assert game_options_repo.get_difficulty(999) is None
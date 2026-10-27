from models import Difficulty, Language
from repositories.game_options_repo import (
    get_all_difficulties,
    get_all_languages,
    get_difficulty,
    get_language,
)


def test_get_all_languages_returns_them_sorted_by_name(session):
    session.add_all([Language(name="Spanish"), Language(name="French")])
    session.commit()
    assert [l.name for l in get_all_languages(session)] == ["French", "Spanish"]


def test_get_all_languages_empty_table(session):
    assert get_all_languages(session) == []


def test_get_all_difficulties_keeps_insertion_order(session):
    session.add_all([Difficulty(name="Easy"), Difficulty(name="Hard"), Difficulty(name="Medium")])
    session.commit()
    assert [d.name for d in get_all_difficulties(session)] == ["Easy", "Hard", "Medium"]


def test_get_language_found_and_missing(session):
    session.add(Language(name="French"))
    session.commit()
    assert get_language(session, 1).name == "French"
    assert get_language(session, 999) is None


def test_get_difficulty_found_and_missing(session):
    session.add(Difficulty(name="Easy"))
    session.commit()
    assert get_difficulty(session, 1).name == "Easy"
    assert get_difficulty(session, 999) is None
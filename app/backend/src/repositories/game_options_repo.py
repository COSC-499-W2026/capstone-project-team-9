from sqlmodel import select
from models import Difficulty, Language
from repositories import BaseRepository


class GameOptionsRepository(BaseRepository):
    """
    Repository class that provides methods for accessing data related to game setup
    like languages and difficulty.
    """

    def get_all_languages(self) -> list[Language]:
        return list(self.session.exec(select(Language).order_by(Language.name)).all())


    def get_all_difficulties(self) -> list[Difficulty]:
        """Ordered by id, so seed data listed easiest-first stays in that order."""
        return list(self.session.exec(select(Difficulty).order_by(Difficulty.id)).all())


    def get_language(self, language_id: int) -> Language | None:
        return self.session.get(Language, language_id)


    def get_difficulty(self, difficulty_id: int) -> Difficulty | None:
        return self.session.get(Difficulty, difficulty_id)
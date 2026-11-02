from sqlmodel import Session

class BaseRepository:
    """
    Base repository class providing shared database infrastructure to all child repositories.

    Any entity-specific repository (e.g., UserRepository, ClueRepository) should 
    inherit from this class to automatically gain access to the database session 
    without rewriting boilerplate constructors.

    Usage example:
    ```python
    class UserRepository(BaseRepository):
        def get_by_email(self, email: str):
            return self.session.exec(...)
    ```
    """

    def __init__(self, session: Session):
        """
        Initializes the repository with a request-scoped database session.

        :param session: An active SQLModel/SQLAlchemy database session injected via FastAPI.
        """
        self.session = session
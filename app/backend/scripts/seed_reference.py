"""
Script for seeding reference data like languages and difficulties.

Use:
```
docker compose exec backend python scripts/seed_reference.py
```

The `seed_reference()` function can also be used by other scripts
```
"""
from sqlmodel import Session

from core.db import engine
from models import Difficulty, Language
from seed_helpers import seed_if_empty

DIFFICULTIES = [{"name": "Easy"}, {"name": "Medium"}, {"name": "Hard"}]
LANGUAGES = [{"name": "Spanish"}, {"name": "French"}, {"name": "Japanese"}]


def seed_reference(session: Session) -> None:
    seed_if_empty(session, Difficulty, DIFFICULTIES)
    seed_if_empty(session, Language, LANGUAGES)
    session.commit()


if __name__ == "__main__":
    with Session(engine) as session:
        seed_reference(session)
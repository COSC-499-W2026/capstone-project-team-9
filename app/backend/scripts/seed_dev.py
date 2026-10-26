"""
Script for seeding development-only data that shouldn't end up in prod, like users.

Use:
```
docker compose exec backend python scripts/seed_dev.py
```

The `seed_dev()` function can also be used by other scripts
```
"""
import os
import sys

from sqlmodel import Session

from core.db import engine
from models import User
from seed_helpers import seed_if_empty

FAKE_USERS = [
    {"email": "alice@example.com", "name": "Alice", "hashed_password": "..."},
    {"email": "bob@example.com", "name": "Bob", "hashed_password": "..."},
]

def seed_dev(session: Session) -> None:

    if os.getenv("ENV") != "development":
        sys.exit("Refusing to seed fake data: ENV is not 'development'.")

    seed_if_empty(session, User, FAKE_USERS)

    session.commit()


if __name__ == "__main__":
    with Session(engine) as session:
        seed_dev(session)
"""
Script for resetting the database - drops all tables, reinitializes, and reseeds reference and dev data.
Use:
```
docker compose exec backend python scripts/reset_db.py
```
"""
import os
import sys

from sqlmodel import Session, SQLModel

from core.db import engine, drop_db, init_db
from seed_reference import seed_reference

if __name__ == "__main__":

    if os.getenv("ENV") != "development":
        sys.exit("Refusing to reset: ENV is not 'development'.")

    drop_db()
    init_db()

    with Session(engine) as session:
        seed_reference(session)

    print("Database reset and seeded.")

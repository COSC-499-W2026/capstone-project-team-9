"""
Not a script. Just helper functions for use by the seeding scripts.
"""

import sys
from sqlmodel import Session, SQLModel, select
from sqlalchemy import inspect


def seed_if_empty(session: Session, model: type[SQLModel], rows: list[dict]) -> None:
    """
    Insert rows only if the table is empty, so reruns never overwrite or resurrect data.
    """

    if not _table_in_db(session, model):
        sys.exit(
            f"ERROR. The table for {model.__name__} does not exist. You may have to run scripts/init_db.py first."
        )

    if _table_has_rows(session, model):
        print(f"{model.__name__}: already has rows, skipping.")
        return

    session.add_all(model(**row) for row in rows)
    session.flush()

    print(f"{model.__name__}: added {len(rows)} rows.")


# internal helpers only

def _table_in_db(session: Session, model: type[SQLModel]) -> bool:
    return inspect(session.get_bind()).has_table(model.__tablename__)


def _table_has_rows(session: Session, model: type[SQLModel]) -> bool:
    return session.exec(select(model)).first()
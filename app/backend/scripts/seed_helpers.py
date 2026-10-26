"""
Not a script. Just helper functions for use by the seeding scripts.
"""

from sqlmodel import Session, SQLModel, select

def seed_if_empty(session: Session, model: type[SQLModel], rows: list[dict]) -> None:
    """
    Insert rows only if the table is empty, so reruns never overwrite or resurrect data.
    """
    if session.exec(select(model)).first():
        print(f"{model.__name__}: already has rows, skipping.")
        return
    session.add_all(model(**row) for row in rows)
    session.flush()
    print(f"{model.__name__}: added {len(rows)} rows.")
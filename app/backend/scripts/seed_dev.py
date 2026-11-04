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

from sqlmodel import Session, select

from core.db import engine
from models import User, Clue, Difficulty, Language, Target
from seed_helpers import seed_if_empty

FAKE_USERS = [
    {"email": "alice@example.com", "name": "Alice", "hashed_password": "..."},
    {"email": "bob@example.com", "name": "Bob", "hashed_password": "..."},
]

FAKE_CLUE_COUNTS = {
    ("French", "Medium"): 6,     # slider should show 1-6
    ("Spanish", "Easy"): 12,     # more than MAX_GAME_LENGTH, slider should cap at 10
    ("Japanese", "Hard"): 2,     # slider should show 1-2
}

# Clues that point at real targets (seeded in seed_reference), so the play + answer flow can be tested end to end.
# Kept in a combo with no placeholder clues, so every clue in a play can actually be solved.
REAL_CLUES = [
    ("French", "Easy", "COM 311"),
    ("French", "Easy", "COM 312"),
]


def seed_dev(session: Session) -> None:

    if os.getenv("ENV") != "development":
        sys.exit("Refusing to seed fake data: ENV is not 'development'.")

    seed_if_empty(session, User, FAKE_USERS)
    _seed_fake_clues(session)

    session.commit()

def _seed_fake_clues(session: Session) -> None:
    """Add placeholder targets and clues. Empty bytes stand in for audio/image (columns are NOT NULL)."""
    if session.exec(select(Clue)).first():
        print("Clue: already has rows, skipping.")
        return

    language_ids = {lang.name: lang.id for lang in session.exec(select(Language))}
    difficulty_ids = {diff.name: diff.id for diff in session.exec(select(Difficulty))}

    for (language, difficulty), count in FAKE_CLUE_COUNTS.items():
        if language not in language_ids or difficulty not in difficulty_ids:
            sys.exit(
                f"ERROR. {language}/{difficulty} not found. "
                "You may have to run scripts/seed_reference.py first."
            )
        for n in range(1, count + 1):
            target = Target(name=f"{language} {difficulty} placeholder {n}", latitude=49, longitude=-119, radius=50)
            session.add(target)
            session.flush()  # assigns target.id
            session.add(Clue(
                audio=b"",
                language_id=language_ids[language],
                difficulty_id=difficulty_ids[difficulty],
                target_id=target.id,
            ))

    print(f"Clue: added {sum(FAKE_CLUE_COUNTS.values())} rows (and matching targets).")
    _seed_real_clues(session, language_ids, difficulty_ids)


def _seed_real_clues(session: Session, language_ids: dict[str, int], difficulty_ids: dict[str, int]) -> None:
    """Add clues that point at the real targets from seed_reference (e.g. COM 311)."""
    target_ids = {target.name: target.id for target in session.exec(select(Target))}

    for language, difficulty, target_name in REAL_CLUES:
        if target_name not in target_ids:
            sys.exit(
                f"ERROR. Target {target_name} not found. "
                "Run scripts/reset_db.py so seed_reference can add it."
            )
        session.add(Clue(
            audio=b"",
            language_id=language_ids[language],
            difficulty_id=difficulty_ids[difficulty],
            target_id=target_ids[target_name],
        ))

    print(f"Clue: added {len(REAL_CLUES)} rows for real targets.")


if __name__ == "__main__":
    with Session(engine) as session:
        seed_dev(session)
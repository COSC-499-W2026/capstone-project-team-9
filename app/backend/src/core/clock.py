from datetime import datetime, timezone


def utc_now() -> datetime:
    """Current time in UTC, used as the default for created_at / updated_at columns."""
    return datetime.now(timezone.utc)
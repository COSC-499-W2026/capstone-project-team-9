from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(
        min_length=1,
        max_length=100,
        unique=True,
        index=True,
    )

    email: str = Field(
        max_length=320,
        unique=True,
        index=True,
    )

    hashed_password: str
from sqlmodel import Field, SQLModel

class Difficulty(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
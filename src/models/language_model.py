from sqlmodel import Field, SQLModel

class Language(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
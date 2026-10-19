import os
from dotenv import load_dotenv
from sqlmodel import Session, create_engine

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in the .env file")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

def get_db():
    with Session(engine) as session:
        yield session

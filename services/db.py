import os
from contextlib import contextmanager
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.engine import Engine


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    return "postgresql://postgres:aicooStudent@localhost:5434/app"


engine: Engine = create_engine(
    get_database_url(),
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def close_db() -> None:
    engine.dispose()


# tests/conftest.py
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv

from app.main import app
from app.api.deps import get_db


@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    load_dotenv(".env.test", override=True)
    # ensure env is loaded
    assert os.getenv("DATABASE_URL"), "DATABASE_URL not set"


@pytest.fixture(scope="session")
def test_database_url(load_test_env) -> str:
    # ensure reading this url after env loaded
    return os.environ["DATABASE_URL"]


@pytest.fixture(scope="session")
def engine(test_database_url: str):
    engine = create_engine(test_database_url)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def SessionLocal(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def apply_migrations(test_database_url: str):
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", test_database_url)
    command.upgrade(alembic_cfg, "head")
    yield


@pytest.fixture()
def db_session(engine, SessionLocal) -> Session:
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

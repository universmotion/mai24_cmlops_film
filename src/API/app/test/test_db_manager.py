import conftest
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from unittest.mock import patch
from db_manager import get_db, SessionLocal 

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_password")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test_db")

def test_database_url():
    db_user = os.environ["DB_USER"]
    db_password = os.environ["DB_PASSWORD"]
    db_host = os.environ["DB_HOST"]
    db_port = os.environ["DB_PORT"]
    db_database = os.environ["DB_NAME"]
    
    expected_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
    
    engine = create_engine(expected_url)
    assert engine.url.render_as_string(hide_password=False) == expected_url

def test_get_db_session():
    with patch.object(SessionLocal, "__call__", return_value=SessionLocal()) as mock_session:
        db_generator = get_db()
        db = next(db_generator)

        assert isinstance(db, Session)

        with patch.object(db, "close") as mock_close:
            db_generator.close()
            mock_close.assert_called_once()


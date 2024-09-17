import conftest
import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from jose import jwt, JWTError
from datetime import timedelta, datetime
from passlib.context import CryptContext
from dependancies import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    get_user, 
    get_current_user, 
    authenticate_user
)
from dependancies import SECRET_KEY, ALGORITHM
from db_manager import Client

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture
def db_session():
    """
    Simule une session de base de données pour les tests.
    """
    return MagicMock()

def test_verify_password():
    plain_password = "testpassword"
    hashed_password = pwd_context.hash(plain_password)

    assert verify_password(plain_password, hashed_password) == True
    assert verify_password("wrongpassword", hashed_password) == False

def test_get_password_hash():
    password = "testpassword"
    hashed_password = get_password_hash(password)

    assert pwd_context.verify(password, hashed_password) == True

def test_create_access_token():
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=30)
    token = create_access_token(data, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_token.get("sub") == "testuser"
    assert decoded_token.get("exp") is not None

def test_get_user(db_session):
    db_session.query().filter().first.return_value = Client(username="testuser")

    user = get_user(db_session, "testuser")
    assert user.username == "testuser"

    db_session.query().filter().first.return_value = None
    user = get_user(db_session, "nonexistentuser")
    assert user is None

@pytest.mark.asyncio
async def test_get_current_user(db_session):
    token_data = {"sub": "testuser"}
    token = create_access_token(token_data)

    db_session.query().filter().first.return_value = Client(username="testuser")
    user = get_current_user(token=token, db=db_session)
    assert user.username == "testuser"

    db_session.query().filter().first.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token, db=db_session)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could not validate credentials"

    invalid_token = "invalidtoken"
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=invalid_token, db=db_session)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could not validate credentials"

def test_authenticate_user(db_session):
    hashed_password = get_password_hash("testpassword")
    db_session.query().filter().first.return_value = Client(username="testuser", hashed_password=hashed_password)

    user = authenticate_user(db_session, "testuser", "testpassword")
    assert user.username == "testuser"

    db_session.query().filter().first.return_value = None
    user = authenticate_user(db_session, "wronguser", "testpassword")
    assert user == False

    db_session.query().filter().first.return_value = Client(username="testuser", hashed_password=hashed_password)
    user = authenticate_user(db_session, "testuser", "wrongpassword")
    assert user == False

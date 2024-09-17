import conftest
import pytest
from unittest.mock import MagicMock, Mock
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from datetime import timedelta


from fastapi.security import OAuth2PasswordRequestForm
from datamodel import Client
from dependancies import Token, verify_password, create_access_token
from route.manage_client import create_client, login_for_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture
def db_session():
    """
    Simule une session de base de données pour les tests.
    """
    return MagicMock()

@pytest.mark.asyncio
async def test_create_client(db_session):
    from route.manage_client import ClientCreate

    db_session.query().filter().first.return_value = None
    client_data = ClientCreate(username="testuser", name="Test User", email="testuser@example.com", password="testpassword")

    response = await create_client(client=client_data, db=db_session)
    assert response["message"] == "Client created successfully"
    assert "client_id" in response
    db_session.add.assert_called_once()

    db_session.commit.side_effect = MagicMock(spec=db_session.refresh, side_effect=IntegrityError(statement=None, params=None, orig="some integrity error"))
    with pytest.raises(HTTPException) as excinfo:
        await create_client(client=client_data, db=db_session)
    assert excinfo.value.status_code == 500
    assert excinfo.value.detail == "Error creating the client"

    db_session.query().filter().first.side_effect = lambda: Client(username="testuser")
    with pytest.raises(HTTPException) as excinfo:
        await create_client(client=client_data, db=db_session)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Client with this username already exists"

    db_session.query().filter().first.side_effect = [None, Client(email="testuser@example.com")]
    with pytest.raises(HTTPException) as excinfo:
        await create_client(client=client_data, db=db_session)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Client with this email already exists"



@pytest.mark.asyncio
async def test_login_for_access_token(db_session):
    from route.manage_client import Client

    db_session.query().filter().first.return_value = Client(username="testuser", hashed_password=pwd_context.hash("testpassword"))
    
    form_data = OAuth2PasswordRequestForm(username="testuser", password="testpassword", scope="", client_id=None, client_secret=None)
    token = await login_for_access_token(form_data=form_data, db=db_session)

    assert "access_token" in token
    assert token["token_type"] == "bearer"

    db_session.query().filter().first.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        await login_for_access_token(form_data=form_data, db=db_session)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Incorrect username or password"

    db_session.query().filter().first.return_value = Client(username="testuser", hashed_password=pwd_context.hash("wrongpassword"))
    with pytest.raises(HTTPException) as excinfo:
        await login_for_access_token(form_data=form_data, db=db_session)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Incorrect username or password"

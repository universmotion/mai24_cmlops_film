from sqlalchemy.exc import IntegrityError
from datamodel import Client
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid
from passlib.context import CryptContext
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException
from dependancies import ACCESS_TOKEN_EXPIRATION
from dependancies import Token
from dependancies import verify_password, create_access_token
from datetime import timedelta
from db_manager import get_db

router_client = APIRouter()


class ClientCreate(BaseModel):
    """
    Pydantic model for creating a new client.

    Attributes:
    - username: The client's username.
    - name: The client's name.
    - email: The client's email address.
    - password: The client's plain-text password.
    """
    username: str
    name: str
    email: str
    password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router_client.post("/create-client", tags=["Client"])
async def create_client(
        client: ClientCreate, db: Session = Depends(get_db)):
    """
    Creates a new client in the database.

    This route checks if the username or email already exists. 
    If everything is correct, it adds the new client with a hashed password.

    Arguments:
    - client: An object containing the client's information.

    Exceptions:
    - HTTP 400: If the username or email already exists.
    - HTTP 500: If an error occurs during insertion into the database.

    Returns:
    - A success message and the ID of the newly created client.
    """
    existing_client = db.query(Client).filter(
        Client.username == client.username).first()
    if existing_client:
        raise HTTPException(
            status_code=400, detail="Client with this username already exists")

    existing_email = db.query(Client).filter(
        Client.email == client.email).first()
    if existing_email:
        raise HTTPException(
            status_code=400, detail="Client with this email already exists")

    hashed_password = pwd_context.hash(client.password)
    new_client = Client(
        id=uuid.uuid4(),
        username=client.username,
        name=client.name,
        email=client.email,
        hashed_password=hashed_password
    )

    try:
        db.add(new_client)
        db.commit()
        db.refresh(new_client)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error creating the client")

    return {"message": "Client created successfully", "client_id": new_client.id}


@router_client.post("/token", response_model=Token, tags=["Client"])
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates a user and generates a JWT access token.

    This route allows a user to authenticate by submitting a username and password. 
    If authentication is successful, it returns a valid JWT access token for a defined period.

    Exceptions:
    - HTTP 400: If the username or password is incorrect.

    Returns:
    - A dictionary containing the access token and token type (Bearer).
    """
    user = db.query(Client).filter(
        Client.username == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRATION)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}

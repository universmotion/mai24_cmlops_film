from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime, timedelta
import os

# DB package
from sqlalchemy.orm import Session
from db_manager import Client, get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.environ["SECRET_API"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRATION = 60 * 24 * 15  # 15 days


class Token(BaseModel):
    """
    Pydantic model to represent a JWT authentication token.

    Attributes:
    - access_token: The JWT access token.
    - token_type: The type of token, usually "Bearer".
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Pydantic model for the data contained in the JWT token.

    Attributes:
    - username: The username extracted from the JWT token (optional).
    """
    username: Optional[str] = None

# API functions


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if a plaintext password matches its hashed equivalent.

    Arguments:
    - plain_password: Plaintext password to verify.
    - hashed_password: Hashed password to compare.

    Returns:
    - True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes a password using bcrypt.

    Arguments:
    - password: Password to hash.

    Returns:
    - The hashed password.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Creates an access JWT token with an expiration date.

    Arguments:
    - data: Data to encode in the token.
    - expires_delta: The token's validity duration. Defaults to 15 minutes if not specified.

    Returns:
    - A signed JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user(db: Session, username: str):
    """
    Retrieves a user from the database using their username.

    Arguments:
    - db: Database session.
    - username: Username to search for.

    Returns:
    - The found user, or None if no user is found.
    """
    return db.query(Client).filter(Client.username == username).first()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Retrieves the current user from the JWT token.

    Arguments:
    - token: JWT token obtained via OAuth2.
    - db: Database session.

    Exceptions:
    - HTTP 401: If the credentials are invalid.

    Returns:
    - The current user extracted from the token or raises an exception if the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticates a user by verifying their username and password.

    Arguments:
    - db: Database session.
    - username: Username to authenticate.
    - password: Password to verify.

    Returns:
    - The user if authentication succeeds, False otherwise.
    """
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

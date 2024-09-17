from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime, timedelta
import os

## DB package
from sqlalchemy.orm import Session
from db_manager import Client, get_db


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


SECRET_KEY = os.environ["SECRET_API"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRATION = 60*24*15  # 15 jours


class Token(BaseModel):
    """
    Modèle Pydantic pour représenter un jeton d'authentification JWT.
    
    Attributs :
    - access_token : Jeton d'accès JWT.
    - token_type : Type de jeton, en général "Bearer".
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Modèle Pydantic pour les données contenues dans le jeton JWT.
    
    Attributs :
    - username : Nom d'utilisateur extrait du jeton JWT (optionnel).
    """
    username: Optional[str] = None


## API functions

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si un mot de passe en clair correspond à son équivalent chiffré.

    Arguments :
    - plain_password : Mot de passe en clair à vérifier.
    - hashed_password : Mot de passe chiffré à comparer.

    Retourne :
    - True si les mots de passe correspondent, False sinon.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash un mot de passe en utilisant bcrypt.

    Arguments :
    - password : Mot de passe à chiffrer.

    Retourne :
    - Le mot de passe chiffré.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Crée un jeton JWT d'accès avec une date d'expiration.

    Arguments :
    - data : Données à encoder dans le jeton.
    - expires_delta : Durée de validité du jeton. Si non spécifiée, la durée est de 15 minutes.

    Retourne :
    - Un jeton JWT signé.
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
    Récupère un utilisateur de la base de données à partir de son nom d'utilisateur.

    Arguments :
    - db : Session de base de données.
    - username : Nom d'utilisateur à chercher.

    Retourne :
    - L'utilisateur trouvé ou None s'il n'existe pas.
    """
    return db.query(Client).filter(Client.username == username).first()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Récupère l'utilisateur actuel à partir du jeton JWT.

    Arguments :
    - token : Jeton JWT obtenu via OAuth2.
    - db : Session de base de données.

    Exceptions :
    - HTTP 401 : Si les informations d'identification ne sont pas valides.

    Retourne :
    - L'utilisateur actuel extrait du jeton ou une exception si l'utilisateur n'est pas trouvé.
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
    Authentifie un utilisateur en vérifiant son nom d'utilisateur et son mot de passe.

    Arguments :
    - db : Session de base de données.
    - username : Nom d'utilisateur à authentifier.
    - password : Mot de passe à vérifier.

    Retourne :
    - L'utilisateur si l'authentification est réussie, False sinon.
    """
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
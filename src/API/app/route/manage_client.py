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
    Modèle Pydantic pour la création d'un nouveau client.

    Attributs :
    - username : Nom d'utilisateur du client.
    - name : Nom du client.
    - email : Adresse email du client.
    - password : Mot de passe en clair du client.
    """
    username: str
    name: str
    email: str
    password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router_client.post("/create-client", tags=["client"])
async def create_client(
    client: ClientCreate, db: Session = Depends(get_db)
):
    """
    Crée un nouveau client dans la base de données.

    Cette route vérifie si le nom d'utilisateur ou l'email existent déjà. 
    Si tout est correct, elle ajoute le nouveau client avec un mot de passe haché.

    Arguments :
    - client : Un objet `ClientCreate` contenant les informations du client.
    - db : Session de la base de données (injectée via la dépendance).

    Exceptions :
    - HTTP 400 : Si le nom d'utilisateur ou l'email existent déjà.
    - HTTP 500 : Si une erreur se produit lors de l'insertion dans la base de données.

    Retourne :
    - Un message de succès et l'ID du client nouvellement créé.
    """
    existing_client = db.query(Client).filter(Client.username == client.username).first()
    if existing_client:
        raise HTTPException(status_code=400, detail="Client with this username already exists")

    existing_email = db.query(Client).filter(Client.email == client.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Client with this email already exists")

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
        raise HTTPException(status_code=500, detail="Error creating the client")

    return {"message": "Client created successfully", "client_id": new_client.id}


@router_client.post("/token", response_model=Token, tags=["client"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authentifie un utilisateur et génère un jeton d'accès JWT.

    Cette route permet à un utilisateur de s'authentifier en envoyant un nom d'utilisateur et un mot de passe.
    Si l'authentification est réussie, elle renvoie un jeton d'accès JWT valide pour une durée déterminée.

    Arguments :
    - form_data : Formulaire de requête OAuth2 avec le nom d'utilisateur et le mot de passe.
    - db : Session de la base de données (injectée via la dépendance).

    Exceptions :
    - HTTP 400 : Si le nom d'utilisateur ou le mot de passe sont incorrects.

    Retourne :
    - Un dictionnaire contenant le jeton d'accès et le type de jeton (Bearer).
    """
    user = db.query(Client).filter(Client.username == form_data.username).first()

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")    

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRATION)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}

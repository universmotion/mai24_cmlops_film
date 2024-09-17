import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datamodel import Client

db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]
db_database = os.environ["DB_NAME"]
SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,       
    max_overflow=10,    
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Générateur qui gère la session de base de données.

    Cette fonction crée une session avec la base de données via SQLAlchemy,
    la rend disponible pour les appels suivants via "yield" et s'assure
    que la session est bien fermée une fois l'opération terminée.

    Retourne :
    - db : Une instance de Session permettant d'interagir avec la base de données.
    """
    db = SessionLocal()
    try:
        yield db  
    finally:
        db.close()  
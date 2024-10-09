import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datamodel import Client

# Fetch environment variables for database connection
db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]
db_database = os.environ["DB_NAME"]

# Construct the PostgreSQL database URL
SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"

# Create the engine with a connection pool
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,  # Number of connections to maintain in the pool
    max_overflow=10,  # Extra connections beyond pool size
)

# Create a session factory with custom settings
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Generator that manages the database session.

    This function creates a session with the database via SQLAlchemy, 
    makes it available for the following calls via "yield," and ensures 
    that the session is properly closed once the operation is complete.

    Returns:
    - db: A Session instance to interact with the database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import os
from pathlib import Path
import pandas as pd
from datamodel import Movie, MovieUserRating, User
from sqlalchemy.orm import sessionmaker
from send_to_db import DataSender

if "MAMBA_EXE" in os.environ: ## TODO: remove 
    import dotenv
    dotenv.load_dotenv()
    data_path = Path("data")
else:
    data_path = Path("/app/data/to_ingest")

def load_db():
    db_user = os.environ["DB_USER"]
    db_password = os.environ["DB_PASSWORD"]
    db_host = os.environ["DB_HOST"]
    db_port = os.environ["DB_PORT"]
    db_database = os.environ["DB_NAME"]

    conn_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
    engine = create_engine(conn_string)
    
    Session = sessionmaker(engine)
    return Session()

def main():
    docs_paths = list(data_path.glob("**/*.csv"))

    if len(docs_paths) == 0:
        raise FileNotFoundError("Error: No raw data in directory")

    docs_links_tables = [
        {
            'path_or_df': 'processed/user_matrix.csv', 
            'table_name': 'users', 
            'schema': User ## FIXME: Attention le (no kind listed) produit une erreur à prendre en compte
        }, 
        {
            'path_or_df': 'raw/movies.csv',
            'table_name': 'movies', 
            'schema': Movie
        }, 
        {
            'path_or_df': 'raw/ratings.csv', 
            'table_name': 'movies_users_rating', 
            'schema': MovieUserRating
        }
    ]
    db = load_db()
    
    ds = DataSender(
        docs_links_tables=docs_links_tables, db_engine=db,
        data_path=data_path
        )
    ds()

if __name__ == "__main__":
    print("### Début de injestion des données par la db")
    main()
    print("### Fin de injestion des données par la db")
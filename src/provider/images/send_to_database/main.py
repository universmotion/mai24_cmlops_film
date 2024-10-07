from sqlalchemy import create_engine
import os
from pathlib import Path
from datamodel import Movie, MovieUserRating, User
from send_to_db import DataSender
from sqlalchemy.orm import sessionmaker
from datetime import datetime

if "MAMBA_EXE" in os.environ:
    import dotenv
    dotenv.load_dotenv()
    date = datetime.now()
    data_path = Path("/home/romain/Documents/Formation/mai24_cmlops_film/data")
else:
    date = datetime.strptime(os.environ["DATE_FOLDER"], '%Y-%m-%d')
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
    docs_paths = list(data_path.glob("raw/**/*.csv"))

    if len(docs_paths) == 0:
        raise FileNotFoundError("Error: No raw data in directory")

    schema = "%Y/%m/%d"
    docs_links_tables = [
        {
            'path_or_df': os.path.join(data_path, "processed",
                                       date.strftime(schema), 'user_matrix.csv'),
            'table_name': 'users',
            'schema': User
        },
        {
            'path_or_df': os.path.join(data_path, "raw",
                                       date.strftime(schema), 'movies.csv'),
            'table_name': 'movies',
            'schema': Movie
        },
        {
            'path_or_df': os.path.join(data_path, "raw",
                                       date.strftime(schema),  'ratings.csv'),
            'table_name': 'movies_users_rating',
            "change_col_type": {"timestamp": "timestamp"},
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

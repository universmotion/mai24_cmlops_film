from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import os
from pathlib import Path
import pandas as pd
from datamodel import Movie, MovieUserRating, MatrixUserKind

if "MAMBA_EXE" in os.environ: ## TODO: remove 
    import dotenv
    dotenv.load_dotenv()
    data_path = Path("data")
else:
    data_path = Path("/app/data/to_ingest")

db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]
db_database = os.environ["DB_NAME"]

conn_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
db_engine = create_engine(conn_string)

docs_paths = list(data_path.glob("**/*.csv"))

if len(docs_paths) == 0:
    print(docs_paths)
    raise FileNotFoundError("Error: No raw data in directory")



docs_links_tables = [
    ["processed/user_matrix.csv", "users", MatrixUserKind],
    ["raw/movies.csv", "movies", Movie],
    ['raw/ratings.csv',  'movies_users_rating', MovieUserRating],
]


for d in docs_links_tables: # FIXME: Prendre en compte quand il manque un fichier dans la boucle...
    if isinstance(d[0], str): 
        df = pd.read_csv(os.path.join(data_path, d[0]))
    elif isinstance(d[0], pd.DataFrame):
        df = d[0]
    else:
        raise ValueError(f"Error: Object {type(d[0])} is not a df or a str")
    
    name_table = d[1]
    schema = d[2]
    df = df.drop_duplicates()
    
    for i in range(0, df.index.shape[0]+1, 10):
        try: # FIXME: Revoir une autre façon pour gerer les bug de primarykey, etc...
            df.iloc[i:(i+10)].to_sql(
                name=name_table,
                index=False, con=db_engine, 
                method="multi", if_exists='append'
            )
        except Exception as e:
            print(e)
            print("Error: " + name_table + " indice: " + str(i))

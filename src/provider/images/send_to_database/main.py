from sqlalchemy import create_engine
import os
from pathlib import Path
import pandas as pd
from datamodel import Movie, MovieTag, MatrixUserKind
from datamodel import MovieUserRating, MovieUserTag, Tag 

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

# merge two files to movie_docs
movie_docs = [pd.read_csv(p) for p in docs_paths if p.stem in ["links", "movies"]]
movies_docs = pd.merge(movie_docs[1], movie_docs[0], on="movieId")


docs_links_tables = [
    [movies_docs, "movie", Movie],
    ['raw/genome-tags.csv', 'tag', Tag],
    ['raw/genome-scores.csv',  'movie_tags', MovieTag],
    ['raw/tags.csv',  'movie_user_tag', MovieUserTag],
    ['raw/ratings.csv',  'movie_user_rating', MovieUserRating],
    ["processed/user_matrix.csv", "matrix_user_kind", MatrixUserKind ]
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
        try:
            df.iloc[i:(i+10)].to_sql(
                name=name_table,
                index=False, con=db_engine, 
                method="multi", if_exists='append'
            )
        except ValueError("Error: " + name_table + " indice: " + str(i)) as e:
            print(e)


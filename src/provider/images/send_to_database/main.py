from sqlalchemy import create_engine
import os
from pathlib import Path
import pandas as pd
from datamodel import Movie, MovieTag 
from datamodel import MovieUserRating, MovieUserTag, Tag 

data_path = Path("/app/data/to_ingest")

db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]
db_database = os.environ["DB_NAME"]


docs_links_tables = [
    ['genome-tags', 'tag', Tag],
    ['genome-scores',  'movie_tags', MovieTag],
    ['tags',  'movie_user_tag', MovieUserTag],
    ['ratings',  'movie_user_rating', MovieUserRating],
]


conn_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
print(conn_string)

docs_paths = list(data_path.glob("*.csv"))
print(docs_paths)

db_engine = create_engine(conn_string)
print(db_engine)

# movie_docs = [pd.read_csv(p) for i, p in enumerate(docs_paths) if i in [4, 5]]
# movies_docs = pd.merge(movie_docs[1], movie_docs[0], on="movieId")
# movies_docs.to_sql(name='movie', index=False, con=db_engine, schema=Movie, if_exists='append')

# for d in docs_links_tables:
#     for p in docs_paths[:4]:
#         if p.stem == d[0]:
#             try:
#                 name_table = d[1]
#                 schema = d[2]
#                 df = pd.read_csv(p).drop_duplicates()
#                 df.to_sql(name=name_table, schema=schema, index=False, con=db_engine, if_exists='append')
#             except:
#                 print("ça crash pour:", p.stem)


# pd.read_csv("/home/romain/Documents/Formation/mai24_cmlops_film/data/processed/user_matrix.csv")\
#     .to_sql(name="matrix_user_kind", index=False, con=db_engine, if_exists='append')

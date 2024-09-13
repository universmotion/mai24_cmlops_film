from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException
import mlflow
import os

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="Movies recommandation system API", version="0.2.0", 
    debug=True,
)

db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_host = os.environ["DATABASE_HOST"]
db_port = os.environ["DATABASE_PORT"]
db_database = os.environ["DB_DATABASE"]

conn_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
db_engine = create_engine(conn_string)

## Model part
# model = mlflow.sklearn.load_model("")
# model.predict()


# class UserPrefSchema(BaseModel):
#     userId: int
#     moviesRating: dict
metadata = MetaData()

class MovieSchema(BaseModel): # TODO: Crée un autre schéma basé sur l'utilisateur quand le modèle sera présent
    moviesId: int


@app.post("/userRecommandation")
async def post_recommandation(movie:MovieSchema):
    try:
        with db_engine.connect() as connection:
            results = connection.execute(text(f'select m.title, m.genres  from movie m where m."movieId" = {movie.moviesId}'))
            res = results.fetchall()
            dict_res = {}
            if len(res) > 0:
                dict_res['result'] = {
                    it: {
                        "movie" : str(result[0]), "kind" : str(result[1])
                    } 
                    for it, result in enumerate(res)
                }
            else:
                raise HTTPException(
                    status_code=417,
                    detail="No movie found sorry"
                )
            return dict_res
    except SQLAlchemyError:
        raise HTTPException(
            status_code=404,
            detail='Database dead connection'
        )

import os
from pathlib import Path

if "MAMBA_EXE" in os.environ:
    import dotenv
    dotenv.load_dotenv() 
    model_path = Path("models")
else:
    model_path = Path("/app/data/models")

from datamodel import Movie
from sqlalchemy.exc import SQLAlchemyError
from utils import get_db

import pandas as pd
from sklearn.neighbors import NearestNeighbors
import pickle



def train_model(movie_matrix):
    nbrs = NearestNeighbors(n_neighbors=20, algorithm="ball_tree").fit(
        movie_matrix.drop("movieId", axis=1)
    )
    return nbrs


def main():
    db = get_db()
    try:
        dataset = db.query(Movie.movieId, Movie.genres).all()
        df = pd.DataFrame(dataset, columns=["movieId", "genres"])
        # TODO: Voir si y'as une meilleure façon de faire...
        df["genres"] = df["genres"].str.replace("(", "")\
                                    .str.replace(")", "")\
                                    .str.replace(" ", "_")\
                                    .str.replace("-", "_")
        
        genres = df["genres"].str.get_dummies(sep="|")
        result_df = pd.concat([df[["movieId"]], genres], axis=1)
        
        model = train_model(result_df)
        
        with open(os.path.join(model_path, "model.pkl"), "wb") as f:
            pickle.dump(model, f)

    except SQLAlchemyError:
        db.rollback()
    
    finally:
        db.close()
    


if __name__ == "__main__":
    print("### Début de l'entrainnement du modèle")
    main()
    print("### Fin de l'entrainnement du modèle")
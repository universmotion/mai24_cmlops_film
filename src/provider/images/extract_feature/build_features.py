import pandas as pd
from sklearn.preprocessing import LabelEncoder
import os


def read_ratings(ratings_csv, data_dir="data/raw") -> pd.DataFrame:
    """
    Lit un fichier ratings.csv depuis le dossier data/raw.

    Paramètres
    -------
    ratings_csv : str
        Le fichier CSV qui sera lu. Il doit correspondre à un fichier d'évaluations.
    data_dir : str
        Le répertoire du fichier.

    Renvoie
    -------
    pd.DataFrame
        Un DataFrame contenant les évaluations. Ses colonnes sont, dans l'ordre :
        "userId", "movieId", "rating" et "timestamp".
    """
    data = pd.read_csv(os.path.join(data_dir, ratings_csv))

    temp = pd.DataFrame(LabelEncoder().fit_transform(data["movieId"]))
    data["movieId"] = temp
    return data


def read_movies(movies_csv, data_dir="data/raw") -> pd.DataFrame:
    """
    Lit un fichier movies.csv depuis le dossier data/raw.

    Paramètres
    -------
    movies_csv : str
        Le fichier CSV qui sera lu. Il doit correspondre à un fichier de films.
    data_dir : str
        Le répertoire du fichier.

    Renvoie
    -------
    pd.DataFrame
        Un DataFrame contenant les informations sur les films. Les colonnes sont binaires et représentent les genres des films.
    """
    df = pd.read_csv(os.path.join(data_dir, movies_csv))
    df.genres = df.genres\
        .str.replace("(", "", regex=False)\
        .str.replace(")", "", regex=False)\
        .str.replace("-", "_", regex=False)\
        .str.replace(" ", "_", regex=False)

    genres = df["genres"].str.get_dummies(sep="|")

    result_df = pd.concat([df[["movieId", "title"]], genres], axis=1)
    return result_df


def create_user_matrix(ratings, movies):
    """
    Crée une matrice utilisateur à partir des évaluations et des informations sur les films.

    Paramètres
    -------
    ratings : pd.DataFrame
        DataFrame contenant les évaluations des utilisateurs.
    movies : pd.DataFrame
        DataFrame contenant les informations sur les films.

    Renvoie
    -------
    pd.DataFrame
        Une matrice utilisateur avec les moyennes des genres de films évalués par chaque utilisateur.
    """
    movie_ratings = ratings.merge(movies, on="movieId", how="inner")

    movie_ratings = movie_ratings.drop(
        ["movieId", "timestamp", "title", "rating"], axis=1
    )

    user_matrix = movie_ratings.groupby("userId").agg(
        "mean",
    )

    return user_matrix

import pandas as pd
from sklearn.preprocessing import LabelEncoder
import os


def read_ratings(ratings_csv, data_dir="data/raw") -> pd.DataFrame:
    """
    Reads a ratings.csv file from the data/raw directory.

    Parameters
    -------
    ratings_csv : str
        The CSV file to be read. It should correspond to a ratings file.
    data_dir : str
        The directory of the file.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the ratings. Its columns are, in order:
        "userId", "movieId", "rating", and "timestamp".
    """
    data = pd.read_csv(os.path.join(data_dir, ratings_csv))
    temp = pd.DataFrame(LabelEncoder().fit_transform(data["movieId"]))
    data["movieId"] = temp
    return data


def read_movies(movies_csv, data_dir="data/raw") -> pd.DataFrame:
    """
    Reads a movies.csv file from the data/raw directory.

    Parameters
    -------
    movies_csv : str
        The CSV file to be read. It should correspond to a movies file.
    data_dir : str
        The directory of the file.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing information about the movies. The columns are binary and represent the genres of the movies.
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
    Creates a user matrix from the ratings and movie information.

    Parameters
    -------
    ratings : pd.DataFrame
        DataFrame containing user ratings.
    movies : pd.DataFrame
        DataFrame containing information about the movies.

    Returns
    -------
    pd.DataFrame
        A user matrix with the average ratings of movie genres evaluated by each user.
    """
    movie_ratings = ratings.merge(movies, on="movieId", how="inner")
    movie_ratings = movie_ratings.drop(
        ["movieId", "timestamp", "title", "rating"], axis=1
    )
    user_matrix = movie_ratings.groupby("userId").agg(
        "mean",
    )
    return user_matrix

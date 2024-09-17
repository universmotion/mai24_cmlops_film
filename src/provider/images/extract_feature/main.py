
import os
from pathlib import Path
import pandas as pd
from build_features import create_user_matrix, read_movies, read_ratings


if os.environ["HOME"] == "/home/romain":
    data_path = Path("data")
else:
    data_path = Path("/app/data/to_ingest")
    

def main():
    try:
        print("## Begin task !")
        user_ratings = read_ratings("raw/ratings.csv", data_dir=data_path)
        movies = read_movies("raw/movies.csv", data_dir=data_path)
        user_matrix = create_user_matrix(user_ratings, movies)

        movies = movies.drop("title", axis=1)
        movies.to_csv(os.path.join(data_path, "processed/movie_matrix.csv"), index=False)
        user_matrix.to_csv(os.path.join(data_path, "processed/user_matrix.csv"))

        print("## Task succeed! \n user_matrix shape: ",user_matrix.shape, "\n movies shape: ",movies.shape)
    except Exception:
        return 0
    return 1 


if __name__ == "__main__":
    main()
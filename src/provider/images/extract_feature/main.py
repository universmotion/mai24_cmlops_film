
import os
from pathlib import Path
import pandas as pd
import traceback
from build_features import create_user_matrix, read_movies, read_ratings
from datetime import datetime


if "MAMBA_EXE" in os.environ:
    date = datetime.now()
    data_path = Path("data")
else:
    date = datetime.strptime(os.environ["DATE_FOLDER"], '%Y-%m-%d')
    data_path = Path("/app/data/to_ingest")
    

def main():
    try:
        print("## Begin task !")
        date = date.strftime("%Y/%m/%d")
        data_raw = os.path.join(data_path, "raw", date)
        data_processed = os.path.join(data_path, "processed", date)

        user_ratings = read_ratings("ratings.csv", data_dir=data_raw)
        movies = read_movies("movies.csv", data_dir=data_raw) ## TODO: Que faire s'il n'y a pas de movies.csv
        user_matrix = create_user_matrix(user_ratings, movies)

        os.makedirs(data_processed, exist_ok=True)

        movies = movies.drop("title", axis=1)
        movies.to_csv(os.path.join(data_processed, "movie_matrix.csv"), index=False)
        user_matrix.to_csv(os.path.join(data_processed, "user_matrix.csv"))

        print("## Task succeed! \n user_matrix shape: ",user_matrix.shape, "\n movies shape: ",movies.shape)
    except Exception as e:
        print(traceback.format_exc())
    return 1 


if __name__ == "__main__":
    main()
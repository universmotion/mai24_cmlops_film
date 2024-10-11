# Imports librairies
from mlflow import MlflowClient
import mlflow
from utils import group_set, put_rating
from sklearn.neighbors import NearestNeighbors
import pandas as pd
import numpy as np
import os
from time import time
import sys

# Define tracking_uri
print("Begin task !")

# client = MlflowClient(tracking_uri="http://127.0.0.1:8080")
apple_experiment = mlflow.set_experiment("System_reco")
run_name = "-".join(list(map(str, [a for a in sys.argv])))
print("run_name", run_name)
artifact_path = "model_nearest_neighbors"

# ### ### ### ### ### VAR ### ### ### ### ###


params = {
    "n_neighbors": int(sys.argv[1]),
    "algorithm": str(sys.argv[2])
}
moyenne_ponderer = bool(sys.argv[3])
size_population = 5*10**5


# ### ### ### ### ### ###  DATA ### ### ### ### ###

ts = time()
repo_data = "data"
user_rating = pd.read_csv(
    os.path.join(repo_data, "ratings.csv"), nrows=size_population)
movie_df = pd.read_csv(os.path.join(repo_data, "movies.csv"))
genres = movie_df.genres.str.replace("(", "").str.replace(")", "")\
    .str.replace("-", "_").str.replace(" ", "_").str.get_dummies("|")
movie_matrix = pd.concat([movie_df.movieId, genres], axis=1)
X = movie_matrix.drop("movieId", axis=1)


# Feature eng
if moyenne_ponderer:
    user_rating_movie = pd.read_csv(os.path.join(
        repo_data, "user_rating_movie_ponderate.csv"))
    user_rating_movie[X.columns] = user_rating_movie[X.columns]/5
else:
    user_rating_movie = pd.read_csv(os.path.join(
        repo_data, "user_rating_movie_not_ponderate.csv"))

# Split group
X_train = user_rating_movie.sample(frac=0.7, random_state=42)
X_test = user_rating_movie[~user_rating_movie.index.isin(X_train.index)]


X_train = X_train.groupby("userId").mean()
X_test = X_test.groupby("userId").mean()

model = NearestNeighbors(**params).fit(
    X
)

ts_after_fit = time() - ts
ts1 = time()
# Evaluate model
_, y_pred = model.kneighbors(X_train[X.columns])
matrix_pred = pd.DataFrame(
    [[userId] + [j for j in y_pred[idx]]
        for idx, userId in enumerate(X_train.index)],
    columns=["userId"] + [f"MovieId recommended {n}" for n in range(20)]
)
series_user_rating = user_rating.groupby("userId").apply(group_set)
y_pred = matrix_pred.apply(lambda x: put_rating(x, series_user_rating), axis=1)
y_pred = y_pred.map(lambda x: np.mean(x) if len(x) > 0 else np.nan)

metrics = {
    "mean_after_recommandation": y_pred.mean(),
    "std_after_recommandation": y_pred.std(),
    "number_of_rating_link": y_pred.count(),
    "ts_after_fit": ts_after_fit,
    "ts_predict": time() - ts1,
    "ts_total": time() - ts
}

# Store information in tracking server
with mlflow.start_run(run_name=run_name) as run:
    mlflow.log_params(params)
    mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(
        sk_model=model, input_example=X_train[X.columns],
        artifact_path=artifact_path
    )

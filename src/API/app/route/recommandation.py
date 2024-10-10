from fastapi import Depends, HTTPException
from fastapi import APIRouter

from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import pandas as pd

from db_manager import get_db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func
from dependancies import get_current_user
from datamodel import Movie, MovieUserRating, User
import pickle
import os
from pathlib import Path
from sklearn.neighbors import NearestNeighbors


# Model Path Determination
if "MAMBA_EXE" in os.environ:
    model_path = Path(
        "/home/romain/Documents/Formation/mai24_cmlops_film/models/model.pkl")
elif "CONFIG_MODE" in os.environ and os.environ["CONFIG_MODE"] == "testing":
    model_path = Path(
        "/home/runner/work/mai24_cmlops_film/mai24_cmlops_film/models/model.pkl")
else:
    model_path = Path("/app/data/models/model.pkl")

# Load Model
with open(model_path, mode="rb") as f:
    MODEL = pickle.load(f)

reco_router = APIRouter()


# Schema
class MovieSchema(BaseModel):
    """
    Schema representing a movie and the associated rating (optional).

    Attributes:
    - moviesId: Movie identifier.
    - rating: Rating associated with the movie, default is 0.
    """
    moviesId: int
    rating: Optional[float] = 0.


class ListMovieSchema(BaseModel):
    """
    Schema representing a list of movies with their ratings.

    Attributes:
    - listMovie: List of movies and their ratings (optional).
    """
    listMovie: Optional[List[MovieSchema]]


class UserSchema(BaseModel):
    """
    Schema representing a user.

    Attributes:
    - userId: User identifier (optional).
    """
    userId: Optional[int] = None


class MovieRecommendedSchema(BaseModel):
    """
    Schema representing a movie recommendation.

    Attributes:
    - movieId: Movie identifier.
    - title: Movie title.
    """
    movieId: int
    title: str


class ResponseRecommendationSchema(BaseModel):
    """
    Schema representing a recommendation.

    Attributes:
    - userId: User identifier.
    - recommendation: a movie recommended schema.
    """
    userId: int = None
    recommendation: MovieRecommendedSchema


def create_user(db: Session) -> int:
    """
    Creates a new user in the database by assigning them a new unique ID.

    Arguments:
    - db: Database session.

    Exceptions:
    - HTTP 500: In case of database error.

    Returns:
    - The ID of the newly created user.
    """
    try:
        max_id = db.query(func.max(User.userId)).scalar()
        new_user = User(userId=max_id + 1)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user.userId
    except SQLAlchemyError:
        raise HTTPException(status_code=500,
                            detail="Error creating user in the database")


def get_user_history(db: Session, user_id: int) -> List[int]:
    """
    Retrieves the movie viewing history of a given user.

    Arguments:
    - db: Database session.
    - user_id: User identifier.

    Exceptions:
    - HTTP 500: In case of database error.

    Returns:
    - A list of movie IDs watched by the user.
    """
    try:
        history = db.query(MovieUserRating.movieId).filter(
            MovieUserRating.userId == user_id).all()
        return [row.movieId for row in history]
    except SQLAlchemyError:
        raise HTTPException(status_code=500,
                            detail="Error fetching user history")


def update_failed_insert(db: Session, failed_insert: dict) -> list:
    """
    Updates movie records that failed to insert initially.

    This function attempts to update the failed records in the database.
    If successful, the record is updated with the new rating and timestamp.
    If it fails, the record is added to a list of failed updates.

    Arguments:
    - db: Active database session.
    - failed_insert: Dictionary containing the information of movies and users for which insertion failed.

    Returns:
    - failed_updates: List of records that could not be updated.

    Exceptions:
    - SQLAlchemyError: If a SQLAlchemy error occurs during the update.
    """
    failed_updates = []
    for obj in failed_insert:
        user_id = obj["userId"]
        movie_id = obj["movieId"]
        rating = obj["rating"]
        timestamp = obj["timestamp"]
        try:
            db.query(MovieUserRating).filter_by(userId=user_id, movieId=movie_id).update({
                'rating': rating,
                'timestamp': timestamp
            })
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            failed_updates.append(obj)
    return failed_updates


def add_movies_to_user(db: Session, user_id: int, movies: List[MovieSchema]) -> int:
    """
    Adds movies to a user's viewing history.

    Arguments:
    - db: Database session.
    - user_id: User identifier.
    - movies: List of movies with their ratings.

    Exceptions:
    - HTTP 500: In case of database error.

    Returns:
    - The number of new movies added.
    """
    counter_new_movies = 0
    failed_insert = []
    failed_updates = []

    for movie in movies:
        movie_id = movie.moviesId
        rating = max(0, min(5, movie.rating))
        try:
            data_movie_user_rating = {
                "userId": user_id,
                "movieId": movie_id,
                "rating": rating,
                "timestamp": pd.Timestamp.now().round(freq='s')
            }
            new_rating = MovieUserRating(**data_movie_user_rating)
            db.add(new_rating)
            db.commit()
            counter_new_movies += 1

        except IntegrityError as e:
            db.rollback()
            if "unique constraint" in str(e.orig):
                failed_insert.append(data_movie_user_rating)
            elif "foreign key constraint" in str(e.orig):
                print(
                    f"Foreign key error: the movie {movie_id} or user {user_id} does not exist.")
            else:
                print(f"Integrity error: {str(e.orig)}")

        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=500, detail="Error adding movies to user history")

    failed_updates = update_failed_insert(db, failed_insert)

    if failed_updates:
        df = pd.DataFrame(failed_updates)
        df.to_csv(
            f'failed_movie_updates_{str(int(datetime.now().timestamp()))}.csv', index=False)
        print("Failed update data saved in 'failed_movie_updates.csv'.")

    return counter_new_movies


def set_new_features(db: Session, user_id: int) -> None:
    """
    Updates a user's features (movie genres) based on their viewing history.

    Arguments:
    - db: Database session.
    - user_id: User identifier.

    Exceptions:
    - HTTP 500: In case of database error.
    """
    try:
        result = (
            db.query(User.userId, Movie.genres)
            .join(MovieUserRating, MovieUserRating.movieId == Movie.movieId)
            .filter(MovieUserRating.userId == user_id)
            .all()
        )

        df = pd.DataFrame(result, columns=["userId", "genres"])
        df = pd.concat(
            [df["userId"], df["genres"].str.get_dummies(sep="|")], axis=1)
        user_vector = df.groupby("userId").mean()

        user_features = user_vector.to_dict(orient="index").get(user_id, {})
        if user_features:
            db.query(User).filter(User.userId == user_id).update(user_features)
            db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error setting new features to user")


def recommend_movie(db: Session, seen_movies: List[int], user_id: int) -> Dict:
    """
    Recommends a new movie to a user, avoiding already watched films.

    Arguments:
    - db: Database session.
    - seen_movies: List of movie IDs already watched.
    - user_id: The ID of the user.

    Exceptions:
    - HTTP 404: If no new movies are available for recommendation.
    - HTTP 500: In case of a database error.

    Returns:
    - A dictionary containing the movie ID and title of the recommended movie.
    """
    try:
        users = pd.read_sql(
            db.query(User).filter(User.userId == user_id).statement,
            db.bind
        ).drop(["userId", "count_movies"], axis=1)
        _, indices = MODEL.kneighbors(users[MODEL.feature_names_in_])
        movies_reco_vec = pd.DataFrame(indices, columns=users.columns)
        genre_to_reco = movies_reco_vec.loc[0]\
            .sort_values(ascending=False)[:3].sample()\
            .index.to_list()[:1]
        regex_reco = "|".join(genre_to_reco) + "%"

        movie = db.query(Movie)\
            .filter(~Movie.movieId.in_(seen_movies))\
            .filter(Movie.genres.like(regex_reco))\
            .first()
        if movie:
            return {"movieId": movie.movieId, "title": movie.title}
        else:
            raise HTTPException(
                status_code=404, detail="No new movies to recommend"
            )
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error recommending movie")


def save_recommendation(db: Session, output: Dict) -> bool:
    """
    Saves a movie recommendation to the database.

    Args:
        db (Session): SQLAlchemy database session used to perform operations.
        output (Dict): Dictionary containing user data and the recommended movie.
            - "userId" (int): The user ID.
            - "recommendation" (dict): Contains recommendation information.
                - "movieId" (int): The ID of the recommended movie.

    Returns:
        bool: Returns True if the recommendation was successfully saved, or raises an exception in case of an error.

    Raises:
        HTTPException: Raises a 500 error if an SQLAlchemy error occurs during the saving process.
    """
    try:
        new_rating = MovieUserRating(
            userId=output["userId"],
            movieId=output["recommendation"]["movieId"],
            rating=None,
            timestamp=pd.Timestamp.now().round(freq='s'),
            is_recommended=True
        )
        db.add(new_rating)
        db.commit()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500, detail="Error recording recommendation"
        )


@reco_router.post("/recommendations", tags=["Recommendation"],
                  response_model=ResponseRecommendationSchema)
async def post_recommendation(
    user: UserSchema, list_movie: ListMovieSchema,
    db_engine: Session = Depends(get_db),
    current_client: str = Depends(get_current_user)
) -> Dict:
    """
    This request recommends a movie to a user based on their watched history. If the user doesn't exist, a new user is created, and their movie history is saved before making a recommendation.

    ### Request Parameters

    - **user**: An object representing the user.
        - **userId** (nullable integer): The unique ID of the user. If **null**, a new user will be created.

    - **list_movie**: An object containing the user's watched movies.
        - **listMovie** (array): A list of objects where each object represents a movie with its ID and rating.
            - **moviesId** (integer): The ID of the watched movie. Id is based on our list, see: [List of moviesId](https://github.com/universmotion/mai24_cmlops_film/blob/master/data/external/movies.csv)
            - **rating** (integer): The user's rating for the movie.

    ### Example Requests

    1. **New User with Watch History**
    ```json
    {
        "user": {
            "userId": null
        },
        "list_movie": {
            "listMovie": [
                {
                "moviesId": 1,
                "rating": 5
                }
            ]
        }
    }
    ```

    2. **Existing User Requesting a New Recommendation**
    ```json
    {
        "user": {
            "userId": 138479
            },
            "list_movie": {
                "listMovie": []
        }
    }
    ```

    - **Errors**:
        - HTTP 400: Missing user or movie history.
        - HTTP 422: Validation Error (of json).
        - HTTP 500: Internal database error.

    ### Key Conditions

    - **New user**: When **userId** is **null** and there is at least one movie in the **listMovie**, a user is created and a recommendation is returned.
    - **Existing user**: If **userId** exists, recommendations can be made based on the user's past history or a new set of watched movies.
    """
    try:
        is_new_user = False
        connection = db_engine
        if not user.userId and len(list_movie.listMovie) == 0:
            raise HTTPException(
                status_code=400, detail="Missing movie history"
            )
        elif not user.userId:
            user_id = create_user(connection)
            is_new_user = True
        elif connection.query(User).filter(User.userId == user.userId).first() is not None:
            user_id = user.userId
        else:
            raise HTTPException(status_code=400, detail="User doesn't exist")

        if len(list_movie.listMovie) > 0:
            count_new_movies_added = add_movies_to_user(
                connection, user_id, list_movie.listMovie
            )
        else:
            count_new_movies_added = 0

        if count_new_movies_added == 0 and is_new_user:
            raise HTTPException(
                status_code=400, detail="Missing movie history (Movie IDs provided don't exist)"
            )

        seen_movies = get_user_history(connection, user_id)
        recommendation = recommend_movie(connection, seen_movies, user_id)
        output = {"userId": user_id, "recommendation": recommendation}
        save_recommendation(connection, output)
        return output

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

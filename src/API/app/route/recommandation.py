from fastapi import Depends, HTTPException
from fastapi import APIRouter

from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import pandas as pd

## DB interaction
from db_manager import get_db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func
from dependancies import get_current_user
from datamodel import Movie, MovieUserRating, User

reco_router = APIRouter()

## Schéma Pydantic
class MovieSchema(BaseModel):
    """
    Schéma représentant un film et la note associée (facultative).
    
    Attributs :
    - moviesId : Identifiant du film.
    - rating : Note associée au film, par défaut 0.
    """
    moviesId: int
    rating: Optional[float] = 0.

class ListMovieSchema(BaseModel):
    """
    Schéma représentant une liste de films avec leurs notes.
    
    Attributs :
    - listMovie : Liste de films et de leurs notes (facultative).
    """
    listMovie: Optional[List[MovieSchema]]

class UserSchema(BaseModel):
    """
    Schéma représentant un utilisateur.
    
    Attributs :
    - userId : Identifiant de l'utilisateur (facultatif).
    """
    userId: Optional[int] = None


## Fonctions

def create_user(db: Session) -> int:
    """
    Crée un nouvel utilisateur dans la base de données en lui attribuant un nouvel identifiant unique.

    Arguments :
    - db : Session de la base de données.

    Exceptions :
    - HTTP 500 : En cas d'erreur de base de données.

    Retourne :
    - L'identifiant de l'utilisateur nouvellement créé.
    """
    try:
        max_id = db.query(func.max(User.userId)).scalar()
        new_user = User(userId=max_id + 1)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user.userId
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error creating user in database")


def get_user_history(db: Session, user_id: int) -> List[int]:
    """
    Récupère l'historique des films vus par un utilisateur donné.

    Arguments :
    - db : Session de la base de données.
    - user_id : Identifiant de l'utilisateur.

    Exceptions :
    - HTTP 500 : En cas d'erreur de base de données.

    Retourne :
    - Une liste d'identifiants de films vus par l'utilisateur.
    """
    try:
        history = db.query(MovieUserRating.movieId).filter(MovieUserRating.userId == user_id).all()
        return [row.movieId for row in history]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error fetching user history")


def add_movies_to_user(db: Session, user_id: int, movies: List[MovieSchema]) -> int:
    """
    Ajoute des films à l'historique d'un utilisateur.

    Arguments :
    - db : Session de la base de données.
    - user_id : Identifiant de l'utilisateur.
    - movies : Liste de films avec leurs notes.

    Exceptions :
    - HTTP 500 : En cas d'erreur de base de données.

    Retourne :
    - Le nombre de nouveaux films ajoutés.
    """
    counter_new_movies = 0
    for movie in movies:
        movie_id = movie.moviesId
        rating = movie.rating
        try:
            new_rating = MovieUserRating(
                userId=user_id,
                movieId=movie_id,
                rating=rating,
                timestamp=int(datetime.now().timestamp())
            )
            db.add(new_rating)
            db.commit()
            counter_new_movies += 1
        except IntegrityError as e:
            db.rollback()
            if "unique constraint" in str(e.orig):
                print(f"Erreur d'unicité : le film {movie_id} existe déjà pour l'utilisateur {user_id}.")
            elif "foreign key constraint" in str(e.orig):
                print(f"Erreur de clé étrangère : le film {movie_id} ou l'utilisateur {user_id} n'existe pas.")
            else:
                print(f"Erreur d'intégrité : {str(e.orig)}")
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error adding movies to user history")
    return counter_new_movies


def set_new_features(db: Session, user_id: int) -> None:
    """
    Met à jour les caractéristiques (genres de films) d'un utilisateur en fonction de son historique de films.

    Arguments :
    - db : Session de la base de données.
    - user_id : Identifiant de l'utilisateur.

    Exceptions :
    - HTTP 500 : En cas d'erreur de base de données.
    """
    try:
        result = (
            db.query(User.userId, Movie.genres)
            .join(MovieUserRating, MovieUserRating.movieId == Movie.movieId)
            .filter(MovieUserRating.userId == user_id)
            .all()
        )

        df = pd.DataFrame(result, columns=["userId", "genres"])
        df = pd.concat([df["userId"], df["genres"].str.get_dummies(sep="|")], axis=1)
        user_vector = df.groupby("userId").mean()

        user_features = user_vector.to_dict(orient="index").get(user_id, {})
        if user_features:
            db.query(User).filter(User.userId == user_id).update(user_features)
            db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error setting new features to user")


def recommend_movie(db: Session, seen_movies: List[int]) -> Dict:
    """
    Recommande un nouveau film à un utilisateur en évitant les films déjà vus.

    Arguments :
    - db : Session de la base de données.
    - seen_movies : Liste d'identifiants de films déjà vus.

    Exceptions :
    - HTTP 404 : Si aucun nouveau film n'est disponible pour recommandation.
    - HTTP 500 : En cas d'erreur de base de données.

    Retourne :
    - Un dictionnaire contenant l'identifiant et le titre du film recommandé.
    """
    try:
        movie = db.query(Movie.movieId, Movie.title)\
            .filter(~Movie.movieId.in_(seen_movies))\
            .first()
        if movie:
            return {"movieId": movie.movieId, "title": movie.title}
        else:
            raise HTTPException(status_code=404, detail="No new movies to recommend")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=e)#"Error recommending movie")


####################################################################
#### #### #### #### #### Route recommandation #### #### #### #### ##
####################################################################

@reco_router.post("/recommendations", tags=["recommendation"])
async def post_recommendation(
    user: UserSchema, list_movie: ListMovieSchema, 
    db_engine: Session = Depends(get_db), current_client: str = Depends(get_current_user)
) -> Dict:
    """
    Route permettant de faire une recommandation de film pour un utilisateur.

    Si l'utilisateur n'existe pas, il est créé. Les films vus sont ajoutés à son historique.
    Ensuite, une recommandation de film est effectuée parmi les films non vus.

    Arguments :
    - user : Schéma représentant l'utilisateur (UserSchema).
    - list_movie : Liste de films avec leurs notes (ListMovieSchema).
    - db_engine : Session de la base de données (injectée via dépendance).
    - current_client : Utilisateur authentifié (injecté via dépendance).

    Exceptions :
    - HTTP 400 : Si l'utilisateur ou l'historique de films est manquant.
    - HTTP 500 : En cas d'erreur de base de données.

    Retourne :
    - Un dictionnaire contenant l'identifiant de l'utilisateur et la recommandation de film.
    """
    try:
        is_new_user = False
        connection = db_engine
        if not user.userId and len(list_movie.listMovie) == 0:
            raise HTTPException(status_code=400, detail="Missing movie history")
        elif not user.userId:
            user_id = create_user(connection)
            is_new_user = True
        elif connection.query(User).filter(User.userId == user.userId).first() is not None:
            user_id = user.userId
        else:
            raise HTTPException(status_code=400, detail="User doesn't exist")

        if len(list_movie.listMovie) > 0:
            count_new_movies_added = add_movies_to_user(connection, user_id, list_movie.listMovie)
        else:
            count_new_movies_added = 0
        
        if count_new_movies_added == 0 and is_new_user:
            raise HTTPException(status_code=400, detail="Missing movie history (Movie ids provided doesn't exist)")
        
        seen_movies = get_user_history(connection, user_id)
        recommendation = recommend_movie(connection, seen_movies)
        return {"userId": user_id, "recommendation": recommendation}

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

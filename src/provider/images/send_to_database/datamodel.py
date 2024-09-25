from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base
import uuid

Base = declarative_base()

class Movie(Base):
    """
    Classe représentant les films dans la base de données.

    Attributs :
    - movieId : Identifiant unique du film, auto-incrémenté.
    - title : Titre du film (peut être nul).
    - genres : Liste des genres associés au film sous forme de chaîne de caractères (peut être nul).
    """
    
    __tablename__ = 'movies'

    movieId = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=True)
    genres = Column(String, nullable=True)

class User(Base):
    """
    Classe représentant les utilisateurs avec des préférences de genres.

    Attributs :
    - userId : Identifiant unique de l'utilisateur, auto-incrémenté.
    - count_movies : Nombre de films associés à l'utilisateur.
    - Divers genres de films avec des scores, chaque genre est représenté par une colonne Float.
      Les genres incluent Action, Adventure, Animation, Comedy, etc.
    - no_genres_listed : Colonne représentant les films sans genres listés.
    """
    
    __tablename__ = 'users'

    userId = Column(Integer, primary_key=True, autoincrement=True)
    count_movies = Column(Integer, default=0)
    no_genres_listed = Column(Float, default=0)
    Action = Column(Float, default=0)
    Adventure = Column(Float, default=0)
    Animation = Column(Float, default=0)
    Children = Column(Float, default=0)
    Comedy = Column(Float, default=0)
    Crime = Column(Float, default=0)
    Documentary = Column(Float, default=0)
    Drama = Column(Float, default=0)
    Fantasy = Column(Float, default=0)
    Film_Noir = Column(Float, default=0)
    Horror = Column(Float, default=0)
    IMAX = Column(Float, default=0)
    Musical = Column(Float, default=0)
    Mystery = Column(Float, default=0)
    Romance = Column(Float, default=0)
    Sci_Fi = Column(Float, default=0)
    Thriller = Column(Float, default=0)
    War = Column(Float, default=0)
    Western = Column(Float, default=0)

class MovieUserRating(Base):
    """
    Classe représentant l'association entre les utilisateurs et les films, avec leur note et un timestamp.

    Attributs :
    - userId : Clé étrangère vers la table 'users', identifiant l'utilisateur.
    - movieId : Clé étrangère vers la table 'movies', identifiant le film.
    - rating : Note attribuée par l'utilisateur au film.
    - timestamp : Timestamp de la note donnée par l'utilisateur.
    
    Relations :
    - user : Relation vers la classe User, avec un backref 'movie_ratings'.
    - movie : Relation vers la classe Movie, avec un backref 'user_ratings'.
    """
    
    __tablename__ = 'movies_users_rating'

    userId = Column(Integer, ForeignKey('users.userId', ondelete="CASCADE"), primary_key=True)
    movieId = Column(Integer, ForeignKey('movies.movieId', ondelete="CASCADE"), primary_key=True)
    rating = Column(Float, nullable=True)
    timestamp = Column(Integer, nullable=True)
    is_recommended = Column(Boolean, default=False)
    is_use_to_train = Column(Boolean, default=False)

    user = relationship("User", backref="movie_ratings")
    movie = relationship("Movie", backref="user_ratings")

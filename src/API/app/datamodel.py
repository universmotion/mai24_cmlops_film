from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, TIMESTAMP
from sqlalchemy import func
from sqlalchemy.orm import relationship, declarative_base
import uuid

Base = declarative_base()


class Client(Base):
    """
    Class representing clients in the database.

    Attributes:
    - id: A unique UUID to identify each client.
    - username: Unique username for the client.
    - name: Client's name.
    - email: Client's unique email address.
    - hashed_password: Encrypted password for the client.
    """
    __tablename__ = "clients"
    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)


class Movie(Base):
    """
    Class representing movies in the database.

    Attributes:
    - movieId: Unique identifier for the movie, auto-incremented.
    - title: Title of the movie (can be null).
    - genres: List of genres associated with the movie, stored as a string (can be null).
    """
    __tablename__ = 'movies'
    movieId = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=True)
    genres = Column(String, nullable=True)


class User(Base):
    """
    Class representing users with genre preferences.

    Attributes:
    - userId: Unique identifier for the user, auto-incremented.
    - count_movies: Number of movies associated with the user.
    - Various movie genres, each represented by a Float column.
      The genres include Action, Adventure, Animation, Comedy, etc.
    - no_genres_listed: Column representing movies without listed genres.
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
    Class representing the association between users and movies, with ratings and a timestamp.

    Attributes:
    - userId: Foreign key to the 'users' table, identifying the user.
    - movieId: Foreign key to the 'movies' table, identifying the movie.
    - rating: The rating given by the user to the movie.
    - timestamp: Timestamp of when the rating was given.
    - is_recommended: Indicates if the movie was recommended.
    - is_use_to_train: Indicates if the rating is used for training purposes.

    Relationships:
    - user: Relationship to the User class, with a backref 'movie_ratings'.
    - movie: Relationship to the Movie class, with a backref 'user_ratings'.
    """
    __tablename__ = 'movies_users_rating'
    userId = Column(Integer, ForeignKey(
        'users.userId', ondelete="CASCADE"), primary_key=True)
    movieId = Column(Integer, ForeignKey('movies.movieId',
                     ondelete="CASCADE"), primary_key=True)
    rating = Column(Float, nullable=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    is_recommended = Column(Boolean, default=False)
    is_use_to_train = Column(Boolean, default=False)
    user = relationship("User", backref="movie_ratings")
    movie = relationship("Movie", backref="user_ratings")

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()


class Client(Base):
    __tablename__ = "clients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)

class Movie(Base):
    __tablename__ = 'movies'

    movieId = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=True)
    genres = Column(String, nullable=True)

class User(Base):
    __tablename__ = 'users'

    userId = Column(Integer, primary_key=True, autoincrement=True)
    count_movies = Column(Integer, default=0)
    no_genres_listed = Column(Float, name="(no genres listed)", default=0)
    Action = Column(Float, default=0)
    Adventure = Column(Float, default=0)
    Animation = Column(Float, default=0)
    Children = Column(Float, default=0)
    Comedy = Column(Float, default=0)
    Crime = Column(Float, default=0)
    Documentary = Column(Float, default=0)
    Drama = Column(Float, default=0)
    Fantasy = Column(Float, default=0)
    Film_Noir = Column(Float, name="Film-Noir", default=0)
    Horror = Column(Float, default=0)
    IMAX = Column(Float, default=0)
    Musical = Column(Float, default=0)
    Mystery = Column(Float, default=0)
    Romance = Column(Float, default=0)
    Sci_Fi = Column(Float, name="Sci-Fi", default=0)
    Thriller = Column(Float, default=0)
    War = Column(Float, default=0)
    Western = Column(Float, default=0)

class MovieUserRating(Base):
    __tablename__ = 'movies_users_rating'

    userId = Column(Integer, ForeignKey('users.userId', ondelete="CASCADE"), primary_key=True)
    movieId = Column(Integer, ForeignKey('movies.movieId', ondelete="CASCADE"), primary_key=True)
    rating = Column(Float, nullable=True)
    timestamp = Column(Integer, nullable=True)

    # Relations (facultatives)
    user = relationship("User", backref="movie_ratings")
    movie = relationship("Movie", backref="user_ratings")
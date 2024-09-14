from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Movie(Base):
    __tablename__ = 'movie'

    movieId = Column(Integer, primary_key=True)
    imdbId = Column(Integer, nullable=True)
    tmdbId = Column(Float, nullable=True)
    title = Column(String, nullable=True)
    genres = Column(String, nullable=True)

    tags = relationship("MovieTag", back_populates="movie")
    user_tags = relationship("MovieUserTag", back_populates="movie")
    user_ratings = relationship("MovieUserRating", back_populates="movie")


class Tag(Base):
    __tablename__ = 'tag'

    tagId = Column(Integer, primary_key=True)
    tag = Column(String, nullable=True)

    movie_tags = relationship("MovieTag", back_populates="tag")


class MovieTag(Base):
    __tablename__ = 'movie_tags'

    movieId = Column(Integer, ForeignKey('movie.movieId', ondelete='CASCADE'), primary_key=True)
    tagId = Column(Integer, ForeignKey('tag.tagId', ondelete='CASCADE'), primary_key=True)
    relevance = Column(Float, nullable=True)

    movie = relationship("Movie", back_populates="tags")
    tag = relationship("Tag", back_populates="movie_tags")


class MovieUserTag(Base):
    __tablename__ = 'movie_user_tag'

    userId = Column(Integer, primary_key=True)
    movieId = Column(Integer, ForeignKey('movie.movieId', ondelete='CASCADE'), primary_key=True)
    tag = Column(String, nullable=True)
    timestamp = Column(Integer, nullable=True)

    movie = relationship("Movie", back_populates="user_tags")


class MovieUserRating(Base):
    __tablename__ = 'movie_user_rating'

    userId = Column(Integer, primary_key=True)
    movieId = Column(Integer, ForeignKey('movie.movieId', ondelete='CASCADE'), primary_key=True)
    rating = Column(Float, nullable=True)
    timestamp = Column(Integer, nullable=True)

    movie = relationship("Movie", back_populates="user_ratings")

class MatrixUserKind(Base):
    __tablename__ = 'matrix_user_kind'
    
    userId = Column(Integer, primary_key=True)
    no_genres_listed = Column("no genres listed", Float)
    Action = Column(Float)
    Adventure = Column(Float)
    Animation = Column(Float)
    Children = Column(Float)
    Comedy = Column(Float)
    Crime = Column(Float)
    Documentary = Column(Float)
    Drama = Column(Float)
    Fantasy = Column(Float)
    Film_Noir = Column("Film-Noir", Float)
    Horror = Column(Float)
    IMAX = Column(Float)
    Musical = Column(Float)
    Mystery = Column(Float)
    Romance = Column(Float)
    Sci_Fi = Column("Sci-Fi", Float)
    Thriller = Column(Float)
    War = Column(Float)
    Western = Column(Float)

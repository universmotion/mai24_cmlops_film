import conftest
import pytest
import pandas as pd
import os
from build_features import read_ratings, read_movies, create_user_matrix

TEST_DATA_DIR = "tests/data"

@pytest.fixture
def movies_csv_path():
    return "movies.csv"

@pytest.fixture
def ratings_csv_path():
    return "ratings.csv"

@pytest.fixture
def ratings_df():
    return pd.read_csv(os.path.join(TEST_DATA_DIR, "ratings_readed.csv"))

@pytest.fixture
def movies_df():
    return pd.read_csv(os.path.join(TEST_DATA_DIR, "movies_readed.csv"))

def test_read_ratings(ratings_csv_path, ratings_df):
    result = read_ratings(ratings_csv_path, data_dir=TEST_DATA_DIR)
    
    assert list(result.columns) == ["userId", "movieId", "rating", "timestamp"]

    assert result.isnull().sum().sum() == 0

    assert (result == ratings_df).all().all()  

def test_read_movies(movies_csv_path, movies_df):
    result = read_movies(movies_csv_path, data_dir=TEST_DATA_DIR)

    assert list(result.columns) == list(movies_df.columns)

    assert result.isnull().sum().sum() == 0
    assert (result == movies_df).all().all()   

def test_create_user_matrix(ratings_df, movies_df):
    result = create_user_matrix(ratings_df, movies_df)

    assert not result.empty

    assert 1 in result.index

    assert "Adventure" in result.columns
    assert "Comedy" in result.columns

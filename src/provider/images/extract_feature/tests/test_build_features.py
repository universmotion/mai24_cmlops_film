import conftest
import pytest
import pandas as pd
import os
from build_features import read_ratings, read_movies, create_user_matrix

TEST_DATA_DIR = "./src/provider/images/extract_feature/tests/data"

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

@pytest.fixture
def user_matrix_df():
    return pd.read_csv(os.path.join(TEST_DATA_DIR, "user_matrix.csv"))

def test_read_ratings(ratings_csv_path, ratings_df):
    result = read_ratings(ratings_csv_path, data_dir=TEST_DATA_DIR)
    
    assert list(result.columns).sort() == list(ratings_df.columns).sort()

    assert result.isnull().sum().sum() == 0

    pd.testing.assert_frame_equal(result, ratings_df)  

def test_read_movies(movies_csv_path, movies_df):
    result = read_movies(movies_csv_path, data_dir=TEST_DATA_DIR)

    assert list(result.columns).sort() == list(movies_df.columns).sort()

    assert result.isnull().sum().sum() == 0

    pd.testing.assert_frame_equal(result,  movies_df)   

def test_create_user_matrix(ratings_df, movies_df, user_matrix_df):
    result = create_user_matrix(ratings_df, movies_df)
    
    assert list(result.columns).sort() == list(user_matrix_df.columns).sort()

    assert result.isnull().sum().sum() == 0

    pd.testing.assert_frame_equal(result.reset_index(drop=True), user_matrix_df.reset_index(drop=True))


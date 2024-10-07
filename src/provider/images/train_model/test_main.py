# import conftest
import pytest
from unittest import mock
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from unittest.mock import patch
import os

patch.dict(os.environ, {
    "SECRET_API": "secret_test",
    "DB_USER": "user",
    "DB_PASSWORD": "pass",
    "DB_HOST": "0.0.0.0",
    "DB_PORT": "8000",
    "DB_NAME": "db_name"
}).start()


@pytest.fixture
def mock_db():
    with mock.patch("utils.get_db") as mock_db:
        yield mock_db


def test_train_model():
    movie_matrix = pd.DataFrame({
        "movieId": [1, 2, 3],
        "genre1": [1, 0, 1],
        "genre2": [0, 1, 0]
    })
    from main import train_model
    model = train_model(movie_matrix)
    assert isinstance(model, NearestNeighbors)

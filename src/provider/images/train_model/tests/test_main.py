import conftest
import pytest
from unittest import mock
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from main import train_model #FIXME: pb de chemin


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

    model = train_model(movie_matrix)
    assert isinstance(model, NearestNeighbors)

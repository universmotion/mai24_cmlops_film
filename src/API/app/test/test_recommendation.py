import conftest
import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session

from route.recommandation import create_user, get_user_history, add_movies_to_user
from route.recommandation import recommend_movie, post_recommendation
from sklearn.neighbors import NearestNeighbors


def pytest_namespace():
    return {'MODEL': MagicMock(spec=NearestNeighbors(n_neighbors=20, algorithm="ball_tree"))}


@pytest.fixture
def MODEL():
    pytest.MODEL = MagicMock(spec=NearestNeighbors(
        n_neighbors=20, algorithm="ball_tree"))


@pytest.fixture
def db_session():
    """
    Simule une session de base de données pour les tests.
    """
    session = MagicMock(spec=Session)
    return session


def test_create_user(db_session):
    db_session.query().scalar.return_value = 1
    new_user_id = create_user(db_session)
    assert new_user_id == 2
    db_session.add.assert_called_once()

    db_session.query().scalar.side_effect = SQLAlchemyError
    with pytest.raises(HTTPException) as excinfo:
        create_user(db_session)
    assert excinfo.value.status_code == 500
    assert excinfo.value.detail == "Error creating user in database"


def test_get_user_history(db_session):
    db_session.query().filter().all.return_value = [
        MagicMock(movieId=1), MagicMock(movieId=2)]
    history = get_user_history(db_session, user_id=1)
    assert history == [1, 2]

    db_session.query().filter().all.side_effect = SQLAlchemyError
    with pytest.raises(HTTPException) as excinfo:
        get_user_history(db_session, user_id=1)
    assert excinfo.value.status_code == 500
    assert excinfo.value.detail == "Error fetching user history"


def test_add_movies_to_user(db_session):
    movie_list = [MagicMock(moviesId=1, rating=5.0),
                  MagicMock(moviesId=2, rating=4.0)]

    db_session.commit.return_value = None
    count = add_movies_to_user(db_session, user_id=1, movies=movie_list)
    assert count == 2

    db_session.add.side_effect = IntegrityError(
        statement=None, params=None, orig="unique constraint")
    db_session.commit.side_effect = None
    count = add_movies_to_user(db_session, user_id=1, movies=movie_list)
    assert count == 0

# @patch('pandas.read_sql')
# def test_recommend_movie(db_session, MODEL, mocker):
#     user = User(userId=1)
#     movie = Movie(movieId=101, title="Test Movie", genres="Action|Drama")
#     db_session.add(user)
#     db_session.add(movie)
#     db_session.commit()


#     pytest.MODEL.kneighbors().return_value = (None, [[1, 2, 3]])

#     seen_movies = [101]
#     db_session.bind = Mock(spec=Session)
#     db_session.query().filter().statement = None

#     recommendation = recommend_movie(db_session, seen_movies=seen_movies, user_id=1)
#     assert recommendation == {"movieId": 101, "title": "Test Movie"}

# @patch('pandas.read_sql')
# @pytest.mark.asyncio
# async def test_post_recommendation__without_user_with_movies(db_session):
#     from fastapi.testclient import TestClient
#     from route.recommandation import reco_router

#     client = TestClient(reco_router)

#     user_data = MagicMock(userId=None)
#     movie_data = MagicMock(listMovie= [ MagicMock(moviesId = 1, rating = 5.0)])

#     ## return elif
#     db_session.query().filter().first.return_value = None

#     ## -> create_user
#     db_session.query().scalar.return_value = 1

#     # -> get_user_history
#     db_session.query().filter().all.return_value = [ MagicMock(moviesId = 1) ]

#     # -> recommend_movie
#     db_session.query().filter(
#         ~MagicMock(moviesId = 1).movieId.in_([ 1 ])
#         ).first.return_value = MagicMock(moviesId = 2, title = "test_title")

#     db_session.bind = Mock(spec=Session)

#     response = await post_recommendation(
#         user=user_data,
#         list_movie=movie_data,
#         db_engine=db_session,
#         current_client="test_client"
#     )

#     assert response["userId"] == 2

# @patch('pandas.read_sql')
# @pytest.mark.asyncio
# async def test_post_recommendation_with_user_with_movies(db_session):
#     from fastapi.testclient import TestClient
#     from route.recommandation import reco_router

#     client = TestClient(reco_router)

#     user_data = MagicMock(userId=1)
#     movie_data = MagicMock(listMovie= [ MagicMock(moviesId = 1, rating = 5.0)])

#     ## return elif
#     db_session.query().filter().first.return_value = 1

#     # -> get_user_history
#     db_session.query().filter().all.return_value = [ MagicMock(moviesId = 1) ]

#     # -> recommend_movie
#     db_session.query().filter(
#         ~MagicMock(moviesId = 1).movieId.in_([ 1 ])
#         ).first.return_value = MagicMock(moviesId = 2, title = "test_title")

#     db_session.bind = Mock(spec=Session)

#     response = await post_recommendation(
#         user=user_data,
#         list_movie=movie_data,
#         db_engine=db_session,
#         current_client="test_client"
#     )

#     assert response["userId"] == 1

# @patch('pandas.read_sql')
# @pytest.mark.asyncio
# async def test_post_recommendation_without_user_without_movies(db_session):
#     from fastapi.testclient import TestClient
#     from route.recommandation import reco_router

#     client = TestClient(reco_router)

#     user_data = MagicMock(userId=None)
#     movie_data = MagicMock(listMovie= [])

#     with pytest.raises(HTTPException) as excinfo:
#         await post_recommendation(
#             user=user_data,
#             list_movie=movie_data,
#             db_engine=db_session,
#             current_client="test_client"
#         )
#     assert excinfo.value.detail == "Missing movie history"
#     assert excinfo.value.status_code == 400

# @patch('pandas.read_sql')
# @pytest.mark.asyncio
# async def test_post_recommendation_with_user_without_movies(db_session):
#     from fastapi.testclient import TestClient
#     from route.recommandation import reco_router

#     client = TestClient(reco_router)

#     user_data = MagicMock(userId=1)
#     movie_data = MagicMock(listMovie= [])

#     ## return elif
#     db_session.query().filter().first.return_value = 1

#     # -> get_user_history
#     db_session.query().filter().all.return_value = [ MagicMock(moviesId = 1) ]

#     # -> recommend_movie
#     db_session.query().filter(
#         ~MagicMock(moviesId = 1).movieId.in_([ 1 ])
#         ).first.return_value = MagicMock(moviesId = 2, title = "test_title")

#     db_session.bind = Mock(spec=Session)

#     response = await post_recommendation(
#         user=user_data,
#         list_movie=movie_data,
#         db_engine=db_session,
#         current_client="test_client"
#     )

#     assert response["userId"] == 1

# TODO: Ajouter un test de si user n'existe pas
# TODO: Ajouter un test de si le movie n'existe pas

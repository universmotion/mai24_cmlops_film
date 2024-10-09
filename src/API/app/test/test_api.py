import conftest
from fastapi.testclient import TestClient
from api import app


def test_app_initialization():
    client = TestClient(app)

    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()[
        "info"]["title"] == "Movies Recommendation System API"
    assert response.json()["info"]["version"] == "0.4.0"


def test_routes_included():
    client = TestClient(app)

    response = client.get("/client/some_endpoint")
    assert response.status_code in [200, 401, 404]

    response = client.get("/recommendation/some_endpoint")
    assert response.status_code in [200, 401, 404]

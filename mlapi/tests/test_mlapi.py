import pytest
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from numpy.testing import assert_almost_equal
from src import __version__
from src.main import app


@pytest.fixture
def client():
    FastAPICache.init(InMemoryBackend())
    with TestClient(app) as c:
        yield c


def test_predict(client):
    data = {"text": ["I hate you.", "I love you."]}
    response = client.post(
        "/predict",
        json=data,
    )

    assert response.status_code == 200
    assert type(response.json()["predictions"]) is list
    assert type(response.json()["predictions"][0]) is list
    assert type(response.json()["predictions"][0][0]) is dict
    assert type(response.json()["predictions"][1][0]) is dict
    assert set(response.json()["predictions"][0][0].keys()) == {"label", "score"}
    assert set(response.json()["predictions"][0][1].keys()) == {"label", "score"}
    assert set(response.json()["predictions"][1][0].keys()) == {"label", "score"}
    assert set(response.json()["predictions"][1][1].keys()) == {"label", "score"}
    assert response.json()["predictions"][0][0]["label"] == "NEGATIVE"
    assert response.json()["predictions"][0][1]["label"] == "POSITIVE"
    assert response.json()["predictions"][1][0]["label"] == "POSITIVE"
    assert response.json()["predictions"][1][1]["label"] == "NEGATIVE"
    assert (
        assert_almost_equal(
            response.json()["predictions"][0][0]["score"], 0.936, decimal=3
        )
        is None
    )
    assert (
        assert_almost_equal(
            response.json()["predictions"][0][1]["score"], 0.064, decimal=3
        )
        is None
    )
    assert (
        assert_almost_equal(
            response.json()["predictions"][1][0]["score"], 0.997, decimal=3
        )
        is None
    )
    assert (
        assert_almost_equal(
            response.json()["predictions"][1][1]["score"], 0.003, decimal=3
        )
        is None
    )


def test_predict_count(client):
    data = {"text": ["I love you.", "I hate you."]}
    response = client.post("/predict", json=data)

    assert len(response.json()["predictions"]) == len(data["text"])


def test_predict_type(client):
    data = {"text": ["I love you."]}
    response = client.post("/predict", json=data)

    assert response.status_code == 200
    assert type(response.json()["predictions"][0][0]["label"]) is str
    assert type(response.json()["predictions"][0][1]["label"]) is str
    assert type(response.json()["predictions"][0][0]["score"]) is float
    assert type(response.json()["predictions"][0][1]["score"]) is float


def test_predict_num(client):
    data = {"text": [0]}
    response = client.post("/predict", json=data)

    assert response.status_code == 422


def test_predict_punc(client):
    data = {"text": ["!@#$"]}
    response = client.post("/predict", json=data)

    assert response.status_code == 422


def test_predict_nolist(client):
    data = {"text": "I love you."}
    response = client.post("/predict", json=data)

    assert response.status_code == 422


def test_predict_emptylist(client):
    data = {"text": []}
    response = client.post("/predict", json=data)

    assert response.status_code == 422


def test_predict_emptystr(client):
    data = {"text": [""]}
    response = client.post("/predict", json=data)

    assert response.status_code == 422


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

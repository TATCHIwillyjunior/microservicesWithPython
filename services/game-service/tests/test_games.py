import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

engine_test = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = SessionTest()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


GAME_DATA = {
    "title": "The Legend of Zelda",
    "genre": "Action-Adventure",
    "platform": "Nintendo Switch",
    "release_year": 2017,
    "cover_url": "https://example.com/zelda.jpg",
}


def test_create_game_returns_201(client):
    response = client.post("/v1/games/", json=GAME_DATA)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == GAME_DATA["title"]
    assert "id" in body


def test_get_game_by_id(client):
    created = client.post("/v1/games/", json=GAME_DATA).json()
    response = client.get(f"/v1/games/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == GAME_DATA["title"]


def test_get_game_not_found(client):
    response = client.get("/v1/games/nonexistent-id")
    assert response.status_code == 404


def test_list_games(client):
    client.post("/v1/games/", json=GAME_DATA)
    client.post("/v1/games/", json={**GAME_DATA, "title": "Mario Kart"})
    response = client.get("/v1/games/")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_search_games(client):
    client.post("/v1/games/", json=GAME_DATA)
    client.post("/v1/games/", json={**GAME_DATA, "title": "Mario Kart"})
    response = client.get("/v1/games/search?q=zelda")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "The Legend of Zelda"
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


USER_DATA = {
    "username": "alice",
    "email": "alice@example.com",
    "password": "secret123",
}


def test_create_user_returns_201(client):
    response = client.post("/v1/users/", json=USER_DATA)
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == USER_DATA["username"]
    assert body["email"] == USER_DATA["email"]
    assert "id" in body
    assert "password" not in body


def test_get_user_by_id(client):
    created = client.post("/v1/users/", json=USER_DATA).json()
    response = client.get(f"/v1/users/{created['id']}")
    assert response.status_code == 200
    assert response.json()["username"] == USER_DATA["username"]


def test_get_user_not_found(client):
    response = client.get("/v1/users/nonexistent-id")
    assert response.status_code == 404


def test_list_users(client):
    client.post("/v1/users/", json=USER_DATA)
    client.post("/v1/users/", json={**USER_DATA, "username": "bob", "email": "bob@example.com"})
    response = client.get("/v1/users/")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_list_users_empty(client):
    response = client.get("/v1/users/")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["items"] == []
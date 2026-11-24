import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.database import engine, get_db
from main import app


@pytest.fixture
def client():
    with engine.connect() as connection:
        transaction = connection.begin()
        session = Session(bind=connection, join_transaction_mode="create_savepoint")

        def test_db():
            yield session

        app.dependency_overrides[get_db] = test_db
        try:
            with TestClient(app) as test_client:
                yield test_client
        finally:
            app.dependency_overrides.clear()
            session.close()
            transaction.rollback()


def test_register_and_login(client):
    name = uuid.uuid4().hex[:10]
    data = {
        "username": f"student_{name}",
        "email": f"{name}@example.com",
        "password": "SecurePass123!",
    }

    response = client.post("/users/register", json=data)
    assert response.status_code == 201
    assert response.json()["username"] == data["username"]
    assert "password" not in response.json()
    assert "password_hash" not in response.json()

    response = client.post("/users/login", json={
        "username": data["username"],
        "password": data["password"],
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"

    response = client.post("/users/login", json={
        "username": data["username"],
        "password": "WrongPassword",
    })
    assert response.status_code == 401


def test_registration_errors(client):
    name = uuid.uuid4().hex[:10]
    data = {
        "username": f"student_{name}",
        "email": f"{name}@example.com",
        "password": "SecurePass123!",
    }
    assert client.post("/users/register", json=data).status_code == 201
    assert client.post("/users/register", json=data).status_code == 400

    invalid = {
        "username": "ab",
        "email": "not-an-email",
        "password": "short",
    }
    assert client.post("/users/register", json=invalid).status_code == 400


def test_calculation_bread(client):
    data = {"a": 10, "b": 5, "type": "Add"}

    response = client.post("/calculations", json=data)
    assert response.status_code == 201
    calculation = response.json()
    calculation_id = calculation["id"]
    assert calculation["result"] == 15

    response = client.get("/calculations")
    assert response.status_code == 200
    assert any(item["id"] == calculation_id for item in response.json())

    response = client.get(f"/calculations/{calculation_id}")
    assert response.status_code == 200
    assert response.json()["result"] == 15

    response = client.put(
        f"/calculations/{calculation_id}",
        json={"a": 20, "b": 4, "type": "Divide"},
    )
    assert response.status_code == 200
    assert response.json()["result"] == 5

    response = client.delete(f"/calculations/{calculation_id}")
    assert response.status_code == 204
    assert client.get(f"/calculations/{calculation_id}").status_code == 404


@pytest.mark.parametrize("invalid", [
    {"a": 10, "b": 0, "type": "Divide"},
    {"a": 10, "b": 5, "type": "Power"},
    {"a": "wrong", "b": 5, "type": "Add"},
])
def test_invalid_calculation(client, invalid):
    assert client.post("/calculations", json=invalid).status_code == 400


def test_missing_calculation(client):
    assert client.get("/calculations/999999999").status_code == 404
    assert client.put("/calculations/999999999", json={
        "a": 1, "b": 2, "type": "Add",
    }).status_code == 404
    assert client.delete("/calculations/999999999").status_code == 404


def test_invalid_update(client):
    response = client.post("/calculations", json={
        "a": 10, "b": 2, "type": "Divide",
    })
    assert response.status_code == 201
    calculation_id = response.json()["id"]
    assert client.put(f"/calculations/{calculation_id}", json={
        "a": 10, "b": 0, "type": "Divide",
    }).status_code == 400
    assert client.get(f"/calculations/{calculation_id}").json()["result"] == 5

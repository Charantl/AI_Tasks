from fastapi.testclient import TestClient
from app.main import app
import uuid

def test_register_and_login(monkeypatch):
    client = TestClient(app)
    test_email = f"testuser_{uuid.uuid4()}@example.com"
    test_username = f"testuser_{uuid.uuid4()}"
    test_password = "testpassword123"

    # Register
    response = client.post("/auth/register", json={
        "username": test_username,
        "email": test_email,
        "password": test_password
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_username
    assert data["email"] == test_email
    assert "id" in data

    # Login
    response = client.post("/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Invalid login
    response = client.post("/auth/login", json={
        "email": test_email,
        "password": "wrongpassword"
    })
    assert response.status_code == 401 
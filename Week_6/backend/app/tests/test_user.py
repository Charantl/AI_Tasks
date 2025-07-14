from fastapi.testclient import TestClient
from app.main import app
import uuid

def register_and_login(client, username, email, password):
    # Register
    client.post("/auth/register", json={"username": username, "email": email, "password": password})
    # Login
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]

def test_user_profile_get_and_patch():
    client = TestClient(app)
    username = f"testuser_{uuid.uuid4()}"
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "testpassword123"
    new_username = f"updated_{username}"
    new_email = f"updated_{email}"
    new_password = "newpassword456"

    # Register and login
    token = register_and_login(client, username, email, password)
    headers = {"Authorization": f"Bearer {token}"}

    # GET /users/me
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == username
    assert data["email"] == email

    # PATCH /users/me (update username, email, password)
    response = client.patch("/users/me", headers=headers, json={
        "username": new_username,
        "email": new_email,
        "password": new_password
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == new_username
    assert data["email"] == new_email

    # Login with new password
    response = client.post("/auth/login", json={"email": new_email, "password": new_password})
    assert response.status_code == 200
    assert "access_token" in response.json()

    # GET /users/me without token (should fail)
    response = client.get("/users/me")
    assert response.status_code == 401 
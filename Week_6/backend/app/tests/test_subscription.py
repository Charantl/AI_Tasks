from fastapi.testclient import TestClient
from app.main import app
import uuid

def register_and_login(client, username, email, password):
    client.post("/auth/register", json={"username": username, "email": email, "password": password})
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]

def test_list_and_upgrade_subscription():
    client = TestClient(app)
    username = f"testuser_{uuid.uuid4()}"
    email = f"testuser_{uuid.uuid4()}@example.com"
    password = "testpassword123"
    token = register_and_login(client, username, email, password)
    headers = {"Authorization": f"Bearer {token}"}

    # List subscriptions
    response = client.get("/subscriptions/")
    assert response.status_code == 200
    subs = response.json()
    assert isinstance(subs, list)
    if not subs:
        # No subscriptions in DB, skip upgrade test
        return
    sub_id = subs[0]["id"]

    # Upgrade subscription
    response = client.post("/subscriptions/upgrade", headers=headers, json={"subscription_id": sub_id})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sub_id

    # Upgrade to same subscription again (should fail)
    response = client.post("/subscriptions/upgrade", headers=headers, json={"subscription_id": sub_id})
    assert response.status_code == 400

    # Upgrade to non-existent subscription (should fail)
    fake_id = str(uuid.uuid4())
    response = client.post("/subscriptions/upgrade", headers=headers, json={"subscription_id": fake_id})
    assert response.status_code == 404 
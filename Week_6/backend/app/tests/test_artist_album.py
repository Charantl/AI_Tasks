from fastapi.testclient import TestClient
from app.main import app
import uuid

def test_artist_crud_and_search():
    client = TestClient(app)
    # Create artist
    artist_name = f"Artist {uuid.uuid4()}"
    response = client.post("/artists/", json={"name": artist_name, "bio": "Test bio", "image_url": "http://example.com/img.png"})
    assert response.status_code == 200
    artist = response.json()
    artist_id = artist["id"]
    assert artist["name"] == artist_name
    # Get artist
    response = client.get(f"/artists/{artist_id}")
    assert response.status_code == 200
    # Update artist
    new_name = f"Updated {artist_name}"
    response = client.patch(f"/artists/{artist_id}", json={"name": new_name})
    assert response.status_code == 200
    assert response.json()["name"] == new_name
    # List/search artists
    response = client.get("/artists/?q=Updated")
    assert response.status_code == 200
    assert any(a["id"] == artist_id for a in response.json())

def test_album_crud_and_search():
    client = TestClient(app)
    # Create artist for album
    artist_name = f"Artist {uuid.uuid4()}"
    response = client.post("/artists/", json={"name": artist_name})
    artist_id = response.json()["id"]
    # Create album
    album_title = f"Album {uuid.uuid4()}"
    response = client.post("/albums/", json={"artist_id": artist_id, "title": album_title, "release_date": "2024-01-01", "cover_url": "http://example.com/cover.png"})
    assert response.status_code == 200
    album = response.json()
    album_id = album["id"]
    assert album["title"] == album_title
    # Get album
    response = client.get(f"/albums/{album_id}")
    assert response.status_code == 200
    # Update album
    new_title = f"Updated {album_title}"
    response = client.patch(f"/albums/{album_id}", json={"title": new_title})
    assert response.status_code == 200
    assert response.json()["title"] == new_title
    # List/search albums
    response = client.get("/albums/?q=Updated")
    assert response.status_code == 200
    assert any(a["id"] == album_id for a in response.json()) 
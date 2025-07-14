from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

# Mock song data
def song_payload():
    return {
        "artist_id": str(uuid.uuid4()),
        "title": "Test Song",
        "duration": 180,
        "audio_url": "https://example.com/audio.mp3",
        "lyrics": "Test lyrics",
        "genre": "Pop"
    }

def test_create_and_get_song():
    # Create song
    response = client.post("/songs/", json=song_payload())
    assert response.status_code == 200
    data = response.json()
    song_id = data["id"]
    assert data["title"] == "Test Song"

    # Get song
    response = client.get(f"/songs/{song_id}")
    assert response.status_code == 200
    assert response.json()["id"] == song_id

def test_list_songs():
    response = client.get("/songs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_song():
    # Create song
    response = client.post("/songs/", json=song_payload())
    song_id = response.json()["id"]
    # Update
    response = client.patch(f"/songs/{song_id}", json={"title": "Updated Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"

def test_delete_song():
    # Create song
    response = client.post("/songs/", json=song_payload())
    song_id = response.json()["id"]
    # Delete
    response = client.delete(f"/songs/{song_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Song deleted" 
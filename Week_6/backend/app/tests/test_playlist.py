import uuid
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class DummyUser:
    def __init__(self, id):
        self.id = id
        self.role = "user"

@patch("app.api.playlist.get_current_user")
@patch("app.api.playlist.get_db")
def test_create_playlist(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    playlist_id = uuid.uuid4()
    playlist = MagicMock(id=playlist_id, user_id=user.id, name="My Playlist", is_public=False, created_at="2024-01-01T00:00:00Z")
    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.side_effect = lambda x: x
    db.query.return_value.filter.return_value.all.return_value = [playlist]
    db.query.return_value.filter.return_value.first.return_value = playlist
    # Create
    resp = client.post("/playlists/", json={"name": "My Playlist", "is_public": False})
    assert resp.status_code == 200
    assert resp.json()["name"] == "My Playlist"
    # List
    resp = client.get("/playlists/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    # Get
    resp = client.get(f"/playlists/{playlist_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == str(playlist_id)
    # Update
    resp = client.patch(f"/playlists/{playlist_id}", json={"name": "Updated"})
    assert resp.status_code == 200
    # Delete
    resp = client.delete(f"/playlists/{playlist_id}")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Playlist deleted"

@patch("app.api.playlist.get_current_user")
@patch("app.api.playlist.get_db")
def test_add_remove_song_to_playlist(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    playlist_id = uuid.uuid4()
    song_id = uuid.uuid4()
    playlist = MagicMock(id=playlist_id, user_id=user.id, name="My Playlist", is_public=False, created_at="2024-01-01T00:00:00Z")
    song = MagicMock(id=song_id)
    ps = MagicMock(id=uuid.uuid4(), playlist_id=playlist_id, song_id=song_id, position=1)
    db.query.return_value.filter.return_value.first.side_effect = [playlist, song, playlist, ps, playlist]
    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.side_effect = lambda x: x
    db.query.return_value.filter.return_value.all.return_value = [ps]
    # Add song
    resp = client.post(f"/playlists/{playlist_id}/songs", json={"song_id": str(song_id), "position": 1})
    assert resp.status_code == 200
    assert resp.json()["song_id"] == str(song_id)
    # List songs
    resp = client.get(f"/playlists/{playlist_id}/songs")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    # Remove song
    resp = client.delete(f"/playlists/{playlist_id}/songs/{song_id}")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Song removed from playlist" 
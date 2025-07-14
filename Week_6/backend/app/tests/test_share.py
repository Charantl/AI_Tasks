import uuid
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class DummyUser:
    def __init__(self, id):
        self.id = id
        self.role = "user"

@patch("app.api.share.get_current_user")
@patch("app.api.share.get_db")
def test_share_song(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    song = MagicMock(id=song_id, title="Test Song")
    db.query.return_value.filter.return_value.first.return_value = song
    resp = client.post(f"/songs/{song_id}/share", json={"platform": "twitter", "message": "Check this out!"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["song_id"] == str(song_id)
    assert data["platform"] == "twitter"
    assert "share_url" in data
    assert data["message"] == "Check this out!"

@patch("app.api.share.get_db")
def test_get_share_options(mock_get_db):
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    song = MagicMock(id=song_id, title="Test Song")
    db.query.return_value.filter.return_value.first.return_value = song
    resp = client.get(f"/songs/{song_id}/share")
    assert resp.status_code == 200
    data = resp.json()
    assert data["song_id"] == str(song_id)
    assert data["song_title"] == "Test Song"
    assert "available_platforms" in data
    assert len(data["available_platforms"]) == 4

@patch("app.api.share.get_current_user")
@patch("app.api.share.get_db")
def test_share_song_not_found(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    db.query.return_value.filter.return_value.first.return_value = None  # song not found
    resp = client.post(f"/songs/{song_id}/share", json={"platform": "twitter"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Song not found"

@patch("app.api.share.get_current_user")
@patch("app.api.share.get_db")
def test_share_song_invalid_platform(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    song = MagicMock(id=song_id, title="Test Song")
    db.query.return_value.filter.return_value.first.return_value = song
    resp = client.post(f"/songs/{song_id}/share", json={"platform": "invalid_platform"})
    assert resp.status_code == 400
    assert "Invalid platform" in resp.json()["detail"]

@patch("app.api.share.get_db")
def test_get_share_options_song_not_found(mock_get_db):
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    db.query.return_value.filter.return_value.first.return_value = None  # song not found
    resp = client.get(f"/songs/{song_id}/share")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Song not found" 
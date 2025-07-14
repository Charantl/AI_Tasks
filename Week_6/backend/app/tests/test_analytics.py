import uuid
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class DummyUser:
    def __init__(self, id):
        self.id = id
        self.role = "user"

@patch("app.api.analytics.get_db")
def test_get_song_analytics(mock_get_db):
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    song = MagicMock(id=song_id, title="Test Song")
    db.query.return_value.filter.return_value.first.return_value = song
    db.query.return_value.filter.return_value.count.return_value = 10
    db.query.return_value.filter.return_value.distinct.return_value.count.return_value = 5
    resp = client.get(f"/analytics/song/{song_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["song_id"] == str(song_id)
    assert data["song_title"] == "Test Song"
    assert "total_plays" in data
    assert "unique_listeners" in data
    assert "total_likes" in data
    assert "total_shares" in data

@patch("app.api.analytics.get_db")
def test_get_user_analytics(mock_get_db):
    db = MagicMock()
    mock_get_db.return_value = db
    user_id = uuid.uuid4()
    user = MagicMock(id=user_id, username="testuser")
    db.query.return_value.filter.return_value.first.return_value = user
    db.query.return_value.filter.return_value.count.return_value = 20
    db.query.return_value.filter.return_value.distinct.return_value.count.return_value = 5
    db.query.return_value.join.return_value.filter.return_value.group_by.return_value.order_by.return_value.first.return_value = ["Pop"]
    resp = client.get(f"/analytics/user/{user_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == str(user_id)
    assert data["username"] == "testuser"
    assert "total_songs_played" in data
    assert "total_time_listened" in data
    assert "favorite_genre" in data

@patch("app.api.analytics.get_current_user")
@patch("app.api.analytics.get_db")
def test_track_event(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    song = MagicMock(id=song_id, title="Test Song")
    analytics = MagicMock(id=uuid.uuid4(), song_id=song_id, user_id=user.id, event_type="play", device="web", event_time="2024-01-01T00:00:00Z")
    db.query.return_value.filter.return_value.first.return_value = song
    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.side_effect = lambda x: x
    resp = client.post("/analytics/track", json={"song_id": str(song_id), "event_type": "play", "device": "web"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["song_id"] == str(song_id)
    assert data["event_type"] == "play"
    assert data["device"] == "web"

@patch("app.api.analytics.get_db")
def test_get_song_analytics_not_found(mock_get_db):
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    db.query.return_value.filter.return_value.first.return_value = None  # song not found
    resp = client.get(f"/analytics/song/{song_id}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Song not found"

@patch("app.api.analytics.get_db")
def test_get_user_analytics_not_found(mock_get_db):
    db = MagicMock()
    mock_get_db.return_value = db
    user_id = uuid.uuid4()
    db.query.return_value.filter.return_value.first.return_value = None  # user not found
    resp = client.get(f"/analytics/user/{user_id}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "User not found"

@patch("app.api.analytics.get_current_user")
@patch("app.api.analytics.get_db")
def test_track_event_song_not_found(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    db.query.return_value.filter.return_value.first.return_value = None  # song not found
    resp = client.post("/analytics/track", json={"song_id": str(song_id), "event_type": "play"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Song not found" 
import uuid
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class DummyUser:
    def __init__(self, id):
        self.id = id
        self.role = "user"

@patch("app.api.play_history.get_current_user")
@patch("app.api.play_history.get_db")
def test_list_play_history(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    # Mock play history with song and artist data
    play_history = [MagicMock(id=uuid.uuid4(), song_id=uuid.uuid4(), played_at="2024-01-01T00:00:00Z", device="web")]
    songs = [MagicMock(id=play_history[0].song_id, title="Test Song", artist_id=uuid.uuid4())]
    artists = [MagicMock(id=songs[0].artist_id, name="Test Artist")]
    db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = play_history
    db.query.return_value.filter.return_value.first.side_effect = [songs[0], artists[0]]
    resp = client.get("/me/history/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

@patch("app.api.play_history.get_current_user")
@patch("app.api.play_history.get_db")
def test_add_play_history(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    song = MagicMock(id=song_id, title="Test Song")
    play_history = MagicMock(id=uuid.uuid4(), user_id=user.id, song_id=song_id, played_at="2024-01-01T00:00:00Z", device="mobile")
    db.query.return_value.filter.return_value.first.return_value = song  # song exists
    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.side_effect = lambda x: x
    resp = client.post("/me/history/", json={"song_id": str(song_id), "device": "mobile"})
    assert resp.status_code == 200
    assert resp.json()["song_id"] == str(song_id)

@patch("app.api.play_history.get_current_user")
@patch("app.api.play_history.get_db")
def test_add_play_history_song_not_found(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    db.query.return_value.filter.return_value.first.return_value = None  # song not found
    resp = client.post("/me/history/", json={"song_id": str(song_id), "device": "mobile"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Song not found" 
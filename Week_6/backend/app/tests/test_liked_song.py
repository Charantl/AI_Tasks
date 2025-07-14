import uuid
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class DummyUser:
    def __init__(self, id):
        self.id = id
        self.role = "user"

@patch("app.api.liked_song.get_current_user")
@patch("app.api.liked_song.get_db")
def test_list_liked_songs(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    # Mock liked songs with song and artist data
    liked_songs = [MagicMock(id=uuid.uuid4(), song_id=uuid.uuid4(), liked_at="2024-01-01T00:00:00Z")]
    songs = [MagicMock(id=liked_songs[0].song_id, title="Test Song", artist_id=uuid.uuid4())]
    artists = [MagicMock(id=songs[0].artist_id, name="Test Artist")]
    db.query.return_value.filter.return_value.all.return_value = liked_songs
    db.query.return_value.filter.return_value.first.side_effect = [songs[0], artists[0]]
    resp = client.get("/me/liked-songs/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

@patch("app.api.liked_song.get_current_user")
@patch("app.api.liked_song.get_db")
def test_like_song(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    song = MagicMock(id=song_id, title="Test Song")
    liked_song = MagicMock(id=uuid.uuid4(), user_id=user.id, song_id=song_id, liked_at="2024-01-01T00:00:00Z")
    db.query.return_value.filter.return_value.first.side_effect = [song, None]  # song exists, not already liked
    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.side_effect = lambda x: x
    resp = client.post("/me/liked-songs/", json={"song_id": str(song_id)})
    assert resp.status_code == 200
    assert resp.json()["song_id"] == str(song_id)

@patch("app.api.liked_song.get_current_user")
@patch("app.api.liked_song.get_db")
def test_unlike_song(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    liked_song = MagicMock(id=uuid.uuid4(), user_id=user.id, song_id=song_id)
    db.query.return_value.filter.return_value.first.return_value = liked_song
    resp = client.delete(f"/me/liked-songs/{song_id}")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Song unliked"

@patch("app.api.liked_song.get_current_user")
@patch("app.api.liked_song.get_db")
def test_like_song_already_liked(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    song = MagicMock(id=song_id, title="Test Song")
    existing_like = MagicMock(id=uuid.uuid4(), user_id=user.id, song_id=song_id)
    db.query.return_value.filter.return_value.first.side_effect = [song, existing_like]  # song exists, already liked
    resp = client.post("/me/liked-songs/", json={"song_id": str(song_id)})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Song already liked"

@patch("app.api.liked_song.get_current_user")
@patch("app.api.liked_song.get_db")
def test_unlike_song_not_liked(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    db.query.return_value.filter.return_value.first.return_value = None  # not liked
    resp = client.delete(f"/me/liked-songs/{song_id}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Song not liked" 
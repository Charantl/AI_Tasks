import io
import uuid
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.core.security import hash_password, encode_access_token

client = TestClient(app)

# Helper to create JWT for a user
def make_token(user_id, role="artist"):
    return encode_access_token({"sub": str(user_id), "role": role})

# Mock user dependency
class DummyUser:
    def __init__(self, id, role):
        self.id = id
        self.role = role

@patch("app.api.song.get_s3_client")
def test_upload_audio_artist_only(mock_s3):
    mock_s3.return_value = MagicMock()
    artist = DummyUser(uuid.uuid4(), "artist")
    non_artist = DummyUser(uuid.uuid4(), "user")
    # Patch get_current_user to return artist
    with patch("app.api.song.get_current_user", return_value=artist):
        file = (io.BytesIO(b"audio data"), "test.mp3")
        resp = client.post("/songs/upload/audio", files={"file": file})
        assert resp.status_code == 200
        assert "audio_url" in resp.json()
    # Patch get_current_user to return non-artist
    with patch("app.api.song.get_current_user", return_value=non_artist):
        file = (io.BytesIO(b"audio data"), "test.mp3")
        resp = client.post("/songs/upload/audio", files={"file": file})
        assert resp.status_code == 403

@patch("app.api.song.requests.get")
def test_stream_audio(mock_requests):
    # Insert a song in DB (mocked)
    song_id = str(uuid.uuid4())
    audio_url = "https://bucket.s3.amazonaws.com/audio/test.mp3"
    # Patch DB query
    with patch("app.api.song.Session") as mock_session:
        mock_song = MagicMock()
        mock_song.id = song_id
        mock_song.audio_url = audio_url
        mock_session.return_value.query.return_value.filter.return_value.first.return_value = mock_song
        # Mock requests.get to return a streaming response
        mock_resp = MagicMock()
        mock_resp.status_code = 206
        mock_resp.raw = io.BytesIO(b"audio data")
        mock_resp.headers = {"Content-Range": "bytes 0-9/10", "Content-Type": "audio/mpeg"}
        mock_requests.return_value = mock_resp
        resp = client.get(f"/songs/{song_id}/stream", headers={"range": "bytes=0-9"})
        assert resp.status_code == 206
        assert resp.headers["content-range"] == "bytes 0-9/10"
        assert resp.content == b"audio data" 

@patch("app.api.song.get_s3_client")
def test_upload_audio_missing_file(mock_s3):
    artist = DummyUser(uuid.uuid4(), "artist")
    with patch("app.api.song.get_current_user", return_value=artist):
        resp = client.post("/songs/upload/audio", files={})
        assert resp.status_code == 422  # FastAPI validation error for missing file

@patch("app.api.song.requests.get")
def test_stream_audio_song_not_found(mock_requests):
    song_id = str(uuid.uuid4())
    with patch("app.api.song.Session") as mock_session:
        mock_session.return_value.query.return_value.filter.return_value.first.return_value = None
        resp = client.get(f"/songs/{song_id}/stream")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Song not found"

@patch("app.api.song.requests.get")
def test_stream_audio_invalid_range(mock_requests):
    song_id = str(uuid.uuid4())
    audio_url = "https://bucket.s3.amazonaws.com/audio/test.mp3"
    with patch("app.api.song.Session") as mock_session:
        mock_song = MagicMock()
        mock_song.id = song_id
        mock_song.audio_url = audio_url
        mock_session.return_value.query.return_value.filter.return_value.first.return_value = mock_song
        # Simulate S3 returning 416 for invalid range
        mock_resp = MagicMock()
        mock_resp.status_code = 416
        mock_resp.raw = io.BytesIO(b"")
        mock_resp.headers = {"Content-Range": "bytes */10", "Content-Type": "audio/mpeg"}
        mock_requests.return_value = mock_resp
        resp = client.get(f"/songs/{song_id}/stream", headers={"range": "bytes=100-200"})
        assert resp.status_code == 416 
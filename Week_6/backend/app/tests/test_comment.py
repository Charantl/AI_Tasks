import uuid
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class DummyUser:
    def __init__(self, id):
        self.id = id
        self.role = "user"

@patch("app.api.comment.get_current_user")
@patch("app.api.comment.get_db")
def test_list_song_comments(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    song = MagicMock(id=song_id, title="Test Song")
    comments = [MagicMock(id=uuid.uuid4(), song_id=song_id, content="Great song!", created_at="2024-01-01T00:00:00Z", user_id=user.id)]
    users = [MagicMock(id=user.id, username="testuser")]
    db.query.return_value.filter.return_value.first.return_value = song
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = comments
    db.query.return_value.filter.return_value.first.side_effect = [song, users[0]]
    resp = client.get(f"/songs/{song_id}/comments")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

@patch("app.api.comment.get_current_user")
@patch("app.api.comment.get_db")
def test_create_comment(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    song = MagicMock(id=song_id, title="Test Song")
    comment = MagicMock(id=uuid.uuid4(), user_id=user.id, song_id=song_id, content="Great song!", created_at="2024-01-01T00:00:00Z")
    db.query.return_value.filter.return_value.first.return_value = song
    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.side_effect = lambda x: x
    resp = client.post(f"/songs/{song_id}/comments", json={"content": "Great song!"})
    assert resp.status_code == 200
    assert resp.json()["content"] == "Great song!"

@patch("app.api.comment.get_current_user")
@patch("app.api.comment.get_db")
def test_get_comment(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    comment_id = uuid.uuid4()
    comment = MagicMock(id=comment_id, user_id=user.id, song_id=uuid.uuid4(), content="Great song!", created_at="2024-01-01T00:00:00Z")
    db.query.return_value.filter.return_value.first.return_value = comment
    resp = client.get(f"/comments/{comment_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == str(comment_id)

@patch("app.api.comment.get_current_user")
@patch("app.api.comment.get_db")
def test_update_comment(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    comment_id = uuid.uuid4()
    comment = MagicMock(id=comment_id, user_id=user.id, song_id=uuid.uuid4(), content="Great song!", created_at="2024-01-01T00:00:00Z")
    db.query.return_value.filter.return_value.first.return_value = comment
    db.commit.return_value = None
    db.refresh.side_effect = lambda x: x
    resp = client.patch(f"/comments/{comment_id}", json={"content": "Updated comment!"})
    assert resp.status_code == 200
    assert resp.json()["content"] == "Updated comment!"

@patch("app.api.comment.get_current_user")
@patch("app.api.comment.get_db")
def test_delete_comment(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    comment_id = uuid.uuid4()
    comment = MagicMock(id=comment_id, user_id=user.id, song_id=uuid.uuid4(), content="Great song!", created_at="2024-01-01T00:00:00Z")
    db.query.return_value.filter.return_value.first.return_value = comment
    resp = client.delete(f"/comments/{comment_id}")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Comment deleted"

@patch("app.api.comment.get_current_user")
@patch("app.api.comment.get_db")
def test_create_comment_song_not_found(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    song_id = uuid.uuid4()
    db.query.return_value.filter.return_value.first.return_value = None  # song not found
    resp = client.post(f"/songs/{song_id}/comments", json={"content": "Great song!"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Song not found"

@patch("app.api.comment.get_current_user")
@patch("app.api.comment.get_db")
def test_update_comment_not_owned(mock_get_db, mock_get_user):
    user = DummyUser(uuid.uuid4())
    mock_get_user.return_value = user
    db = MagicMock()
    mock_get_db.return_value = db
    comment_id = uuid.uuid4()
    db.query.return_value.filter.return_value.first.return_value = None  # comment not found or not owned
    resp = client.patch(f"/comments/{comment_id}", json={"content": "Updated comment!"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Comment not found or not owned by user" 
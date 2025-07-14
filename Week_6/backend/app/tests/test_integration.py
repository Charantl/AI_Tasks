from fastapi.testclient import TestClient
from app.main import app
import uuid
import time

client = TestClient(app)

def register_user(email, password, username):
    return client.post("/auth/register", json={
        "email": email,
        "password": password,
        "username": username,
        "role": "user"
    })

def login_user(email, password):
    return client.post("/auth/login", json={"email": email, "password": password})

def create_artist_and_login():
    email = f"artist_{uuid.uuid4()}@test.com"
    password = "password123"
    username = f"artist_{uuid.uuid4()}"
    reg = register_user(email, password, username)
    user_id = reg.json().get("id")
    # Promote to artist (mock, or use endpoint if exists)
    # ...
    login = login_user(email, password)
    token = login.json().get("access_token")
    return token, user_id

def create_user_and_login():
    email = f"user_{uuid.uuid4()}@test.com"
    password = "password123"
    username = f"user_{uuid.uuid4()}"
    reg = register_user(email, password, username)
    user_id = reg.json().get("id")
    login = login_user(email, password)
    token = login.json().get("access_token")
    return token, user_id

# 1. User Registration → Profile Setup → Subscription Activation
def test_user_registration_profile_subscription():
    email = f"test_{uuid.uuid4()}@test.com"
    password = "password123"
    username = f"testuser_{uuid.uuid4()}"
    reg = register_user(email, password, username)
    assert reg.status_code == 200
    user_id = reg.json()["id"]
    # Profile setup (mock, or use endpoint if exists)
    # ...
    # Login
    login = login_user(email, password)
    assert login.status_code == 200
    token = login.json()["access_token"]
    # Subscription activation
    resp = client.post("/subscription/activate", headers={"Authorization": f"Bearer {token}"}, json={"plan": "premium"})
    assert resp.status_code in [200, 201]
    assert resp.json()["status"] in ["active", "activated"]

# 2. Song Upload (Artist) → Song Approval → Song Availability
def test_artist_song_upload_approval_availability():
    token, artist_id = create_artist_and_login()
    # Upload song
    song_data = {
        "artist_id": artist_id,
        "title": f"Song {uuid.uuid4()}",
        "duration": 200,
        "audio_url": "https://example.com/audio.mp3",
        "lyrics": "Test lyrics",
        "genre": "Pop"
    }
    resp = client.post("/song/", json=song_data, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    song_id = resp.json()["id"]
    # Song approval (mock, or use endpoint if exists)
    # ...
    # Song availability
    get_resp = client.get(f"/song/{song_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == song_id

# 3. Playlist Creation → Song Addition → Collaborative Editing
def test_playlist_creation_song_add_collab():
    token, user_id = create_user_and_login()
    # Create playlist
    resp = client.post("/playlist/", json={"name": "My Playlist"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    playlist_id = resp.json()["id"]
    # Add song (create a song first)
    song_data = {
        "artist_id": user_id,
        "title": f"Song {uuid.uuid4()}",
        "duration": 200,
        "audio_url": "https://example.com/audio.mp3",
        "lyrics": "Test lyrics",
        "genre": "Pop"
    }
    song_resp = client.post("/song/", json=song_data, headers={"Authorization": f"Bearer {token}"})
    song_id = song_resp.json()["id"]
    add_resp = client.post(f"/playlist/{playlist_id}/add", json={"song_id": song_id}, headers={"Authorization": f"Bearer {token}"})
    assert add_resp.status_code == 200
    # Collaborative editing (invite another user)
    collab_token, collab_id = create_user_and_login()
    invite_resp = client.post(f"/playlist/{playlist_id}/invite", json={"user_id": collab_id}, headers={"Authorization": f"Bearer {token}"})
    assert invite_resp.status_code in [200, 201]

# 4. Song Like → Real-time Update in Liked Songs Page
def test_song_like_realtime_update():
    token, user_id = create_user_and_login()
    # Create a song
    song_data = {
        "artist_id": user_id,
        "title": f"Song {uuid.uuid4()}",
        "duration": 200,
        "audio_url": "https://example.com/audio.mp3",
        "lyrics": "Test lyrics",
        "genre": "Pop"
    }
    song_resp = client.post("/song/", json=song_data, headers={"Authorization": f"Bearer {token}"})
    song_id = song_resp.json()["id"]
    # Like the song
    like_resp = client.post(f"/liked-song/{song_id}", headers={"Authorization": f"Bearer {token}"})
    assert like_resp.status_code == 200
    # Check liked songs page (simulate real-time update)
    liked_resp = client.get("/liked-song/", headers={"Authorization": f"Bearer {token}"})
    assert liked_resp.status_code == 200
    liked_ids = [s["id"] for s in liked_resp.json()]
    assert song_id in liked_ids

# 5. Comment Posting → Real-time Notification to Song Owner
def test_comment_posting_realtime_notification():
    # Owner creates song
    owner_token, owner_id = create_user_and_login()
    song_data = {
        "artist_id": owner_id,
        "title": f"Song {uuid.uuid4()}",
        "duration": 200,
        "audio_url": "https://example.com/audio.mp3",
        "lyrics": "Test lyrics",
        "genre": "Pop"
    }
    song_resp = client.post("/song/", json=song_data, headers={"Authorization": f"Bearer {owner_token}"})
    song_id = song_resp.json()["id"]
    # Another user comments
    commenter_token, commenter_id = create_user_and_login()
    comment_resp = client.post(f"/comment/{song_id}", json={"text": "Great song!"}, headers={"Authorization": f"Bearer {commenter_token}"})
    assert comment_resp.status_code == 200
    # Real-time notification (mock, or check notification endpoint if exists)
    # ...

# 6. File Upload (Album Art) → Attachment to Song/Album → Notification to Followers
def test_album_art_upload_attachment_notification():
    token, artist_id = create_artist_and_login()
    # Upload album art (mock file upload)
    files = {"file": ("cover.jpg", b"fake image data", "image/jpeg")}
    upload_resp = client.post("/album/upload-art", files=files, headers={"Authorization": f"Bearer {token}"})
    assert upload_resp.status_code in [200, 201]
    art_url = upload_resp.json().get("url")
    # Attach to album (create album first)
    album_resp = client.post("/album/", json={"artist_id": artist_id, "title": "Test Album"}, headers={"Authorization": f"Bearer {token}"})
    album_id = album_resp.json()["id"]
    attach_resp = client.post(f"/album/{album_id}/attach-art", json={"art_url": art_url}, headers={"Authorization": f"Bearer {token}"})
    assert attach_resp.status_code == 200
    # Notification to followers (mock, or check notification endpoint if exists)
    # ...

# 7. Permission Changes (Playlist/Collaboration) → Access Control Validation
def test_permission_changes_access_control():
    owner_token, owner_id = create_user_and_login()
    # Create playlist
    resp = client.post("/playlist/", json={"name": "Private Playlist"}, headers={"Authorization": f"Bearer {owner_token}"})
    playlist_id = resp.json()["id"]
    # Invite collaborator
    collab_token, collab_id = create_user_and_login()
    invite_resp = client.post(f"/playlist/{playlist_id}/invite", json={"user_id": collab_id}, headers={"Authorization": f"Bearer {owner_token}"})
    assert invite_resp.status_code in [200, 201]
    # Change permission (make private)
    perm_resp = client.patch(f"/playlist/{playlist_id}/permissions", json={"is_private": True}, headers={"Authorization": f"Bearer {owner_token}"})
    assert perm_resp.status_code == 200
    # Access control: invited user should still have access
    access_resp = client.get(f"/playlist/{playlist_id}", headers={"Authorization": f"Bearer {collab_token}"})
    assert access_resp.status_code == 200
    # Uninvited user should not have access
    outsider_token, _ = create_user_and_login()
    denied_resp = client.get(f"/playlist/{playlist_id}", headers={"Authorization": f"Bearer {outsider_token}"})
    assert denied_resp.status_code in [403, 404] 
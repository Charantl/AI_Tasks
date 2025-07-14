# API Endpoint Specifications

## User Authentication & Subscription
- `POST /auth/register` — Register new user
- `POST /auth/login` — User login
- `POST /auth/logout` — User logout
- `GET /users/me` — Get current user profile
- `PATCH /users/me` — Update user profile
- `GET /subscriptions` — List subscription tiers
- `POST /subscriptions/upgrade` — Upgrade subscription

## Artist & Album Management
- `GET /artists` — List/search artists
- `POST /artists` — Create artist (admin/artist only)
- `GET /artists/{id}` — Get artist details
- `PATCH /artists/{id}` — Update artist
- `GET /albums` — List/search albums
- `POST /albums` — Create album (artist only)
- `GET /albums/{id}` — Get album details
- `PATCH /albums/{id}` — Update album

## Songs
- `GET /songs` — List/search songs (full-text/semantic)
- `POST /songs` — Upload new song (artist only)
- `GET /songs/{id}` — Get song details
- `PATCH /songs/{id}` — Update song metadata
- `DELETE /songs/{id}` — Delete song (artist/admin)
- `GET /songs/{id}/stream` — Stream audio (with range support)

## Playlists & Liked Songs
- `GET /playlists` — List user playlists
- `POST /playlists` — Create playlist
- `GET /playlists/{id}` — Get playlist details
- `PATCH /playlists/{id}` — Update playlist
- `DELETE /playlists/{id}` — Delete playlist
- `POST /playlists/{id}/songs` — Add song to playlist
- `DELETE /playlists/{id}/songs/{song_id}` — Remove song from playlist
- `GET /me/liked-songs` — List liked songs
- `POST /me/liked-songs/{song_id}` — Like a song
- `DELETE /me/liked-songs/{song_id}` — Unlike a song

## Play History & Analytics
- `GET /me/history` — Get user listening history
- `GET /analytics/song/{id}` — Get analytics for a song
- `GET /analytics/user/{id}` — Get analytics for a user

## Comments & Social
- `GET /songs/{id}/comments` — List comments on a song
- `POST /songs/{id}/comments` — Add comment
- `DELETE /comments/{id}` — Delete comment (owner/moderator)
- `POST /songs/{id}/share` — Share song (social)

## Search & Recommendations
- `GET /search` — Search (songs, artists, albums)
- `GET /recommendations` — Get AI-powered recommendations

## File Upload
- `POST /upload/audio` — Upload audio file (artist only)

## Real-Time (WebSocket)
- `/ws/play-progress` — Real-time play progress updates
- `/ws/listening-room/{room_id}` — Shared listening room

## Example: Song Streaming
- `GET /songs/{id}/stream`
  - **Headers:** `Range: bytes=...` (for scrubbing)
  - **Response:** `audio/mpeg` (streamed)

## Example: Search
- `GET /search?q=love&type=song,artist,album`
  - **Response:**
    ```json
    {
      "songs": [...],
      "artists": [...],
      "albums": [...]
    }
    ``` 
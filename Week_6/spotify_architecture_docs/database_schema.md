# Database Schema Design

## Users
- id (UUID, PK)
- username (string, unique)
- email (string, unique)
- password_hash (string)
- subscription_id (FK)
- created_at (timestamp)
- updated_at (timestamp)

## Subscriptions
- id (UUID, PK)
- name (string: free, premium)
- price (decimal)
- features (jsonb)

## Artists
- id (UUID, PK)
- name (string)
- bio (text)
- image_url (string)
- created_at (timestamp)

## Albums
- id (UUID, PK)
- artist_id (FK)
- title (string)
- release_date (date)
- cover_url (string)

## Songs
- id (UUID, PK)
- album_id (FK)
- artist_id (FK)
- title (string)
- duration (int, seconds)
- audio_url (string)
- lyrics (text)
- genre (string)
- created_at (timestamp)

## Playlists
- id (UUID, PK)
- user_id (FK)
- name (string)
- is_public (bool)
- created_at (timestamp)

## PlaylistSongs
- id (UUID, PK)
- playlist_id (FK)
- song_id (FK)
- position (int)

## LikedSongs
- id (UUID, PK)
- user_id (FK)
- song_id (FK)
- liked_at (timestamp)

## PlayHistory
- id (UUID, PK)
- user_id (FK)
- song_id (FK)
- played_at (timestamp)
- device (string)

## Comments
- id (UUID, PK)
- user_id (FK)
- song_id (FK)
- content (text)
- created_at (timestamp)

## Analytics
- id (UUID, PK)
- song_id (FK)
- user_id (FK, nullable)
- event_type (string: play, skip, like, etc.)
- event_time (timestamp)
- device (string)

## Embeddings (Vector DB)
- id (UUID, PK)
- entity_type (string: song, user)
- entity_id (UUID)
- embedding (vector) 

---

## PostgreSQL DDL Statements

```sql
-- USERS: Registered platform users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    subscription_id UUID REFERENCES subscriptions(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- SUBSCRIPTIONS: Free, premium, etc.
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL, -- e.g., 'free', 'premium'
    price NUMERIC(10,2) NOT NULL,
    features JSONB
);

-- ARTISTS: Music creators
CREATE TABLE artists (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    bio TEXT,
    image_url TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ALBUMS: Groupings of songs
CREATE TABLE albums (
    id UUID PRIMARY KEY,
    artist_id UUID NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    release_date DATE,
    cover_url TEXT
);

-- SONGS: Individual tracks
CREATE TABLE songs (
    id UUID PRIMARY KEY,
    album_id UUID REFERENCES albums(id) ON DELETE SET NULL,
    artist_id UUID NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    duration INTEGER NOT NULL, -- seconds
    audio_url TEXT NOT NULL,
    lyrics TEXT,
    genre TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- PLAYLISTS: User-created collections
CREATE TABLE playlists (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- PLAYLISTSONGS: Many-to-many between playlists and songs
CREATE TABLE playlist_songs (
    id UUID PRIMARY KEY,
    playlist_id UUID NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    UNIQUE (playlist_id, song_id)
);

-- LIKEDSONGS: User likes for songs
CREATE TABLE liked_songs (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    liked_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, song_id)
);

-- PLAYHISTORY: User listening history
CREATE TABLE play_history (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    played_at TIMESTAMP NOT NULL DEFAULT NOW(),
    device TEXT
);

-- COMMENTS: User comments on songs
CREATE TABLE comments (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ANALYTICS: Song events (play, skip, like, etc.)
CREATE TABLE analytics (
    id UUID PRIMARY KEY,
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL, -- e.g., 'play', 'skip', 'like'
    event_time TIMESTAMP NOT NULL DEFAULT NOW(),
    device TEXT
);

-- EMBEDDINGS: Vector DB for recommendations
CREATE TABLE embeddings (
    id UUID PRIMARY KEY,
    entity_type TEXT NOT NULL, -- 'song', 'user'
    entity_id UUID NOT NULL,
    embedding FLOAT8[], -- Use appropriate extension (e.g., pgvector)
    UNIQUE (entity_type, entity_id)
);

-- Indexes for performance on frequently queried fields
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_songs_artist_id ON songs(artist_id);
CREATE INDEX idx_songs_album_id ON songs(album_id);
CREATE INDEX idx_playlists_user_id ON playlists(user_id);
CREATE INDEX idx_playlist_songs_playlist_id ON playlist_songs(playlist_id);
CREATE INDEX idx_playlist_songs_song_id ON playlist_songs(song_id);
CREATE INDEX idx_liked_songs_user_id ON liked_songs(user_id);
CREATE INDEX idx_liked_songs_song_id ON liked_songs(song_id);
CREATE INDEX idx_play_history_user_id ON play_history(user_id);
CREATE INDEX idx_play_history_song_id ON play_history(song_id);
CREATE INDEX idx_comments_song_id ON comments(song_id);
CREATE INDEX idx_analytics_song_id ON analytics(song_id);
CREATE INDEX idx_analytics_user_id ON analytics(user_id);
``` 
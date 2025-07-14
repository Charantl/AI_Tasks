-- Migration DDL for PostgreSQL (ordered for Flyway)
-- Embedding uses FLOAT8[] for compatibility

-- 1. Subscriptions (no dependencies)
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL, -- e.g., 'free', 'premium'
    price NUMERIC(10,2) NOT NULL,
    features JSONB
);

-- 2. Users (depends on subscriptions)
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    subscription_id UUID REFERENCES subscriptions(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 3. Artists (no dependencies)
CREATE TABLE artists (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    bio TEXT,
    image_url TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 4. Albums (depends on artists)
CREATE TABLE albums (
    id UUID PRIMARY KEY,
    artist_id UUID NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    release_date DATE,
    cover_url TEXT
);

-- 5. Songs (depends on albums, artists)
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

-- 6. Playlists (depends on users)
CREATE TABLE playlists (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 7. PlaylistSongs (depends on playlists, songs)
CREATE TABLE playlist_songs (
    id UUID PRIMARY KEY,
    playlist_id UUID NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    UNIQUE (playlist_id, song_id)
);

-- 8. LikedSongs (depends on users, songs)
CREATE TABLE liked_songs (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    liked_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, song_id)
);

-- 9. PlayHistory (depends on users, songs)
CREATE TABLE play_history (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    played_at TIMESTAMP NOT NULL DEFAULT NOW(),
    device TEXT
);

-- 10. Comments (depends on users, songs)
CREATE TABLE comments (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 11. Analytics (depends on songs, users)
CREATE TABLE analytics (
    id UUID PRIMARY KEY,
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL, -- e.g., 'play', 'skip', 'like'
    event_time TIMESTAMP NOT NULL DEFAULT NOW(),
    device TEXT
);

-- 12. Embeddings (no FK, but unique constraint)
CREATE TABLE embeddings (
    id UUID PRIMARY KEY,
    entity_type TEXT NOT NULL, -- 'song', 'user'
    entity_id UUID NOT NULL,
    embedding FLOAT8[],
    UNIQUE (entity_type, entity_id)
);

-- Indexes for performance
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
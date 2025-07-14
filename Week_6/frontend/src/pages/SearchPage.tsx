import React, { useState } from 'react';
import axios from 'axios';
import { AudioPlayer } from '../components/AudioPlayer';

interface SearchResult {
  id: string;
  type: 'song' | 'artist' | 'album';
  name: string;
  album_art?: string;
  artist?: { id: string; name: string };
  album?: { id: string; name: string; album_art?: string };
  // ...other fields
}

export const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [playingSongId, setPlayingSongId] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get('/search', { params: { q: query }, withCredentials: true });
      setResults(res.data.results || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handlePlay = (songId: string) => {
    setPlayingSongId(songId);
  };

  return (
    <div>
      <h2>Search</h2>
      <form onSubmit={handleSearch} style={{ marginBottom: 16 }}>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search for songs, artists, albums..."
        />
        <button type="submit" disabled={loading}>Search</button>
      </form>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {loading && <div>Loading...</div>}
      <ul>
        {results.map(r => (
          <li key={r.type + '-' + r.id} style={{ marginBottom: 16, display: 'flex', alignItems: 'center' }}>
            {r.type === 'song' && (
              <>
                {r.album_art && <img src={r.album_art} alt="album art" style={{ width: 40, height: 40, marginRight: 8 }} />}
                <span style={{ fontWeight: 'bold' }}>{r.name}</span>
                {r.artist && (
                  <span style={{ marginLeft: 8 }}>
                    by <a href={'/artist/' + r.artist.id}>{r.artist.name}</a>
                  </span>
                )}
                <button style={{ marginLeft: 8 }} onClick={() => handlePlay(r.id)}>
                  {playingSongId === r.id ? 'Playing...' : 'Play'}
                </button>
                {playingSongId === r.id && (
                  <div style={{ marginLeft: 16 }}>
                    <AudioPlayer songUrl={`/songs/${r.id}/stream`} songName={r.name} />
                  </div>
                )}
              </>
            )}
            {r.type === 'album' && (
              <>
                {r.album_art && <img src={r.album_art} alt="album art" style={{ width: 40, height: 40, marginRight: 8 }} />}
                <a href={'/album/' + r.id}><b>{r.name}</b></a>
              </>
            )}
            {r.type === 'artist' && (
              <a href={'/artist/' + r.id}><b>{r.name}</b></a>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}; 
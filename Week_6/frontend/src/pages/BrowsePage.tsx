import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Song {
  id: string;
  name: string;
  album_art?: string;
  artist?: { id: string; name: string };
}

export const BrowsePage: React.FC = () => {
  const [genres, setGenres] = useState<string[]>([]);
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null);
  const [trending, setTrending] = useState<Song[]>([]);
  const [genreSongs, setGenreSongs] = useState<Song[]>([]);

  useEffect(() => {
    // Fetch genres and trending songs
    const fetchData = async () => {
      try {
        const genresRes = await axios.get('/search', { params: { suggest: 'genre' }, withCredentials: true });
        setGenres(genresRes.data.genres || []);
        const trendingRes = await axios.get('/songs/trending', { withCredentials: true });
        setTrending(trendingRes.data.songs || []);
      } finally {
        // setLoading(false); // This line was removed as per the edit hint.
      }
    };
    fetchData();
  }, []);

  const handleGenreClick = async (genre: string) => {
    setSelectedGenre(genre);
    try {
      const res = await axios.get('/search', { params: { genre }, withCredentials: true });
      setGenreSongs(res.data.results || []);
    } finally {
      // setLoading(false); // This line was removed as per the edit hint.
    }
  };

  return (
    <div>
      <h2>Browse</h2>
      <div>
        <h3>Genres</h3>
        {genres.map(g => (
          <button key={g} onClick={() => handleGenreClick(g)} style={{ marginRight: 8 }}>{g}</button>
        ))}
      </div>
      {selectedGenre && (
        <div>
          <h4>Songs in {selectedGenre}</h4>
          <ul>
            {genreSongs.map(song => (
              <li key={song.id}>
                {song.album_art && <img src={song.album_art} alt="album art" style={{ width: 32, height: 32, marginRight: 8 }} />}
                {song.name} {song.artist && <>by {song.artist.name}</>}
              </li>
            ))}
          </ul>
        </div>
      )}
      <div>
        <h3>Trending Songs</h3>
        <ul>
          {trending.map(song => (
            <li key={song.id}>
              {song.album_art && <img src={song.album_art} alt="album art" style={{ width: 32, height: 32, marginRight: 8 }} />}
              {song.name} {song.artist && <>by {song.artist.name}</>}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}; 
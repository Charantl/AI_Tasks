import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { usePlayer } from '../context/PlayerContext';
import type { Song } from '../context/PlayerContext';

interface Artist {
  id: string;
  name: string;
  bio?: string;
  avatar?: string;
}

export const ArtistPage: React.FC = () => {
  const { id } = useParams();
  const [artist, setArtist] = useState<Artist | null>(null);
  const [songs, setSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(true);
  const { play } = usePlayer();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const artistRes = await axios.get(`/artists/${id}`);
      setArtist(artistRes.data);
      const songsRes = await axios.get('/songs', { params: { artist_id: id } });
      setSongs(songsRes.data);
      setLoading(false);
    };
    fetchData();
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (!artist) return <div>Artist not found</div>;

  const handlePlayAll = () => {
    if (songs.length) play(songs[0], songs);
  };

  return (
    <div>
      <h2>{artist.name}</h2>
      {artist.avatar && <img src={artist.avatar} alt="avatar" style={{ width: 80, borderRadius: '50%' }} />}
      {artist.bio && <p>{artist.bio}</p>}
      <button onClick={handlePlayAll} disabled={!songs.length}>Play All</button>
      <ul>
        {songs.map(song => (
          <li key={song.id}>
            {song.album_art && <img src={song.album_art} alt="album art" style={{ width: 32, height: 32, marginRight: 8 }} />}
            {song.name}
            <button style={{ marginLeft: 8 }} onClick={() => play(song, songs)}>Play</button>
          </li>
        ))}
      </ul>
    </div>
  );
}; 
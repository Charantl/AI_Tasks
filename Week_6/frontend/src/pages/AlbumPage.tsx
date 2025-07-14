import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { usePlayer } from '../context/PlayerContext';
import type { Song } from '../context/PlayerContext';

interface Album {
  id: string;
  title: string;
  cover_art?: string;
  description?: string;
}

export const AlbumPage: React.FC = () => {
  const { id } = useParams();
  const [album, setAlbum] = useState<Album | null>(null);
  const [songs, setSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(true);
  const { play } = usePlayer();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const albumRes = await axios.get(`/albums/${id}`);
      setAlbum(albumRes.data);
      const songsRes = await axios.get('/songs', { params: { album_id: id } });
      setSongs(songsRes.data);
      setLoading(false);
    };
    fetchData();
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (!album) return <div>Album not found</div>;

  const handlePlayAll = () => {
    if (songs.length) play(songs[0] as Song, songs as Song[]);
  };

  return (
    <div>
      <h2>{album.title}</h2>
      {album.cover_art && <img src={album.cover_art} alt="cover art" style={{ width: 80 }} />}
      {album.description && <p>{album.description}</p>}
      <button onClick={handlePlayAll} disabled={!songs.length}>Play All</button>
      <ul>
        {songs.map(song => (
          <li key={song.id}>
            {song.album_art && <img src={song.album_art} alt="album art" style={{ width: 32, height: 32, marginRight: 8 }} />}
            {song.name}
            <button style={{ marginLeft: 8 }} onClick={() => play(song as Song, songs as Song[])}>Play</button>
          </li>
        ))}
      </ul>
    </div>
  );
}; 
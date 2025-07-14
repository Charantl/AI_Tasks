import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { usePlayer } from '../context/PlayerContext';
import type { Song } from '../context/PlayerContext';

interface Playlist {
  id: string;
  name: string;
  description?: string;
}

export const PlaylistDetailPage: React.FC = () => {
  const { id } = useParams();
  const [playlist, setPlaylist] = useState<Playlist | null>(null);
  const [songs, setSongs] = useState<Song[]>([]);
  const [allSongs, setAllSongs] = useState<Song[]>([]);
  const [addSongId, setAddSongId] = useState('');
  const [loading, setLoading] = useState(true);
  const { play } = usePlayer();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const plRes = await axios.get(`/playlists/${id}`, { withCredentials: true });
      setPlaylist(plRes.data);
      const songsRes = await axios.get(`/playlists/${id}/songs`, { withCredentials: true });
      setSongs(songsRes.data.map((s: any) => ({ id: s.song_id, name: s.song_title, album_art: s.album_art })));
      const allSongsRes = await axios.get('/songs', { withCredentials: true });
      setAllSongs(allSongsRes.data);
      setLoading(false);
    };
    fetchData();
  }, [id]);

  const handleAddSong = async (e: React.FormEvent) => {
    e.preventDefault();
    await axios.post(`/playlists/${id}/songs`, { song_id: addSongId, position: songs.length }, { withCredentials: true });
    setAddSongId('');
    const songsRes = await axios.get(`/playlists/${id}/songs`, { withCredentials: true });
    setSongs(songsRes.data.map((s: any) => ({ id: s.song_id, name: s.song_title, album_art: s.album_art })));
  };

  const handleRemoveSong = async (songId: string) => {
    await axios.delete(`/playlists/${id}/songs/${songId}`, { withCredentials: true });
    const songsRes = await axios.get(`/playlists/${id}/songs`, { withCredentials: true });
    setSongs(songsRes.data.map((s: any) => ({ id: s.song_id, name: s.song_title, album_art: s.album_art })));
  };

  const handlePlayAll = () => {
    if (songs.length) play(songs[0], songs);
  };

  if (loading) return <div>Loading...</div>;
  if (!playlist) return <div>Playlist not found</div>;

  return (
    <div>
      <h2>{playlist.name}</h2>
      {playlist.description && <p>{playlist.description}</p>}
      <button onClick={handlePlayAll} disabled={!songs.length}>Play All</button>
      <form onSubmit={handleAddSong} style={{ marginTop: 16 }}>
        <select value={addSongId} onChange={e => setAddSongId(e.target.value)} required>
          <option value="">Add song...</option>
          {allSongs.filter(s => !songs.find(ps => ps.id === s.id)).map(s => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>
        <button type="submit">Add</button>
      </form>
      <ul>
        {songs.map(song => (
          <li key={song.id}>
            {song.album_art && <img src={song.album_art} alt="album art" style={{ width: 32, height: 32, marginRight: 8 }} />}
            {song.name}
            <button style={{ marginLeft: 8 }} onClick={() => play(song, songs)}>Play</button>
            <button style={{ marginLeft: 8 }} onClick={() => handleRemoveSong(song.id)}>Remove</button>
          </li>
        ))}
      </ul>
    </div>
  );
}; 
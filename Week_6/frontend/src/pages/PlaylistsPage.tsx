import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

interface Playlist {
  id: string;
  name: string;
  description?: string;
}

export const PlaylistsPage: React.FC = () => {
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchPlaylists = async () => {
    setLoading(true);
    const res = await axios.get('/playlists', { withCredentials: true });
    setPlaylists(res.data);
    setLoading(false);
  };

  useEffect(() => { fetchPlaylists(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await axios.post('/playlists', { name, description }, { withCredentials: true });
    setName(''); setDescription('');
    fetchPlaylists();
  };

  const handleDelete = async (id: string) => {
    await axios.delete(`/playlists/${id}`, { withCredentials: true });
    fetchPlaylists();
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Your Playlists</h2>
      <form onSubmit={handleCreate} style={{ marginBottom: 16 }}>
        <input value={name} onChange={e => setName(e.target.value)} placeholder="Playlist name" required />
        <input value={description} onChange={e => setDescription(e.target.value)} placeholder="Description" />
        <button type="submit">Create</button>
      </form>
      <ul>
        {playlists.map(pl => (
          <li key={pl.id}>
            <Link to={`/playlist/${pl.id}`}>{pl.name}</Link>
            <button onClick={() => handleDelete(pl.id)} style={{ marginLeft: 8 }}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}; 
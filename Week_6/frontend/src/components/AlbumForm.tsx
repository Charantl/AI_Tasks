import React, { useState } from 'react';
import axios from 'axios';

export const AlbumForm: React.FC<{ onCreate: () => void }> = ({ onCreate }) => {
  const [title, setTitle] = useState('');
  const [coverArt, setCoverArt] = useState('');
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    setError(null);
    try {
      await axios.post('/albums', { title, cover_art: coverArt }, { withCredentials: true });
      setTitle(''); setCoverArt('');
      onCreate();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Album creation failed');
    } finally {
      setCreating(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginTop: 24 }}>
      <h4>Create New Album</h4>
      <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Album title" required />
      <input value={coverArt} onChange={e => setCoverArt(e.target.value)} placeholder="Cover art URL (optional)" />
      <button type="submit" disabled={creating}>{creating ? 'Creating...' : 'Create Album'}</button>
      {error && <div style={{ color: 'red' }}>{error}</div>}
    </form>
  );
}; 
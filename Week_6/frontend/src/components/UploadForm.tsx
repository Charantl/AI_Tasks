import React, { useState } from 'react';
import axios from 'axios';

export const UploadForm: React.FC<{ onUpload: () => void }> = ({ onUpload }) => {
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState('');
  const [albumId, setAlbumId] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return setError('Please select an audio file');
    setUploading(true);
    setError(null);
    try {
      // Upload audio
      const formData = new FormData();
      formData.append('file', file);
      const audioRes = await axios.post('/songs/upload/audio', formData, { withCredentials: true, headers: { 'Content-Type': 'multipart/form-data' } });
      // Create song
      await axios.post('/songs', { name, album_id: albumId, audio_url: audioRes.data.audio_url }, { withCredentials: true });
      setFile(null); setName(''); setAlbumId('');
      onUpload();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginTop: 24 }}>
      <h4>Upload New Song</h4>
      <div>
        <label htmlFor="upload-audio">Audio File</label>
        <input id="upload-audio" type="file" accept="audio/*" onChange={e => setFile(e.target.files?.[0] || null)} />
      </div>
      <div>
        <label htmlFor="upload-song-name">Song name</label>
        <input id="upload-song-name" value={name} onChange={e => setName(e.target.value)} placeholder="Song name" required />
      </div>
      <div>
        <label htmlFor="upload-album-id">Album ID (optional)</label>
        <input id="upload-album-id" value={albumId} onChange={e => setAlbumId(e.target.value)} placeholder="Album ID (optional)" />
      </div>
      <button type="submit" disabled={uploading}>{uploading ? 'Uploading...' : 'Upload'}</button>
      {error && <div style={{ color: 'red' }}>{error}</div>}
    </form>
  );
}; 
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { UploadForm } from '../components/UploadForm';
import { AlbumForm } from '../components/AlbumForm';
import type { Song } from '../context/PlayerContext';

interface Album {
  id: string;
  title: string;
  cover_art?: string;
  artistId?: string; // Add artistId if needed
}

export const ArtistDashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [albums, setAlbums] = useState<Album[]>([]);
  const [songs, setSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    const albumsRes = await axios.get('/albums', { withCredentials: true });
    setAlbums(albumsRes.data.filter((a: Album) => a.artist_id === user?.id));
    const songsRes = await axios.get('/songs', { withCredentials: true });
    setSongs(songsRes.data.filter((s: Song) => s.artist_id === user?.id));
    setLoading(false);
  };

  useEffect(() => {
    if (user?.id) fetchData();
  }, [user]);

  if (!user || user.role !== 'artist') return <div>Only artists can access this page.</div>;
  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Artist Dashboard</h2>
      <h3>Your Albums</h3>
      <ul>
        {albums.map(album => (
          <li key={album.id}>{album.title}</li>
        ))}
      </ul>
      <AlbumForm onCreate={fetchData} />
      <h3>Your Songs</h3>
      <ul>
        {songs.map(song => (
          <li key={song.id}>{song.name}</li>
        ))}
      </ul>
      <UploadForm onUpload={fetchData} />
    </div>
  );
}; 
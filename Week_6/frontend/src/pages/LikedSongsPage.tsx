import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { usePlayer } from '../context/PlayerContext';
import type { Song } from '../context/PlayerContext';
import { LikeButton } from '../components/LikeButton';

interface LikedSong {
  song_id: string;
  song_title: string;
  artist_name?: string;
}

export const LikedSongsPage: React.FC = () => {
  const [songs, setSongs] = useState<LikedSong[]>([]);
  const { play } = usePlayer();

  const fetchLiked = async () => {
    const res = await axios.get('/me/liked-songs');
    setSongs(Array.isArray(res.data) ? res.data : res.data?.songs || []);
  };

  useEffect(() => { fetchLiked(); }, []);

  const handlePlayAll = () => {
    if (songs.length) play({ id: songs[0].song_id, name: songs[0].song_title } as Song, songs.map(s => ({ id: s.song_id, name: s.song_title }) as Song));
  };

  return (
    <div>
      <h2>Liked Songs</h2>
      <button onClick={handlePlayAll} disabled={!songs.length}>Play All</button>
      <ul>
        {songs.map(song => (
          <li key={song.song_id}>
            {song.song_title} {song.artist_name && <>by {song.artist_name}</>}
            <button style={{ marginLeft: 8 }} onClick={() => play({ id: song.song_id, name: song.song_title } as Song, songs.map(s => ({ id: s.song_id, name: s.song_title }) as Song[]))}>Play</button>
            <LikeButton songId={song.song_id} />
          </li>
        ))}
      </ul>
    </div>
  );
}; 
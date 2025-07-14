import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { usePlayer } from '../context/PlayerContext';
import type { Song } from '../context/PlayerContext';

interface HistoryItem {
  song_id: string;
  song_title: string;
  artist_name?: string;
  played_at: string;
}

export const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const { play } = usePlayer();

  useEffect(() => {
    const fetchHistory = async () => {
      const res = await axios.get('/me/history');
      setHistory(Array.isArray(res.data) ? res.data : res.data?.history || []);
    };
    fetchHistory();
  }, []);

  const handlePlayAll = () => {
    if (history.length) play({ id: history[0].song_id, name: history[0].song_title } as Song, history.map(h => ({ id: h.song_id, name: h.song_title }) as Song));
  };

  return (
    <div>
      <h2>Play History</h2>
      <button onClick={handlePlayAll} disabled={!history.length}>Play All</button>
      <ul>
        {history.map(item => (
          <li key={item.song_id + item.played_at}>
            {item.song_title} {item.artist_name && <>by {item.artist_name}</>} <span style={{ color: '#888', marginLeft: 8 }}>{new Date(item.played_at).toLocaleString()}</span>
            <button style={{ marginLeft: 8 }} onClick={() => play({ id: item.song_id, name: item.song_title } as Song, history.map(h => ({ id: h.song_id, name: h.song_title }) as Song[]))}>Play</button>
          </li>
        ))}
      </ul>
    </div>
  );
}; 
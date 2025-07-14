import React, { useEffect, useState } from 'react';
import axios from 'axios';

export const LikeButton: React.FC<{ songId: string }> = ({ songId }) => {
  const [liked, setLiked] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const checkLiked = async () => {
      try {
        const res = await axios.get('/me/liked-songs', { withCredentials: true });
        setLiked(res.data.some((s: any) => s.song_id === songId));
      } catch {}
    };
    checkLiked();
  }, [songId]);

  const handleLike = async () => {
    setLoading(true);
    try {
      if (liked) {
        await axios.delete(`/me/liked-songs/${songId}`, { withCredentials: true });
        setLiked(false);
      } else {
        await axios.post('/me/liked-songs', { song_id: songId }, { withCredentials: true });
        setLiked(true);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <button onClick={handleLike} disabled={loading} style={{ marginLeft: 8 }}>
      {liked ? '♥' : '♡'}
    </button>
  );
}; 
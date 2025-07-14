import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { usePlayer } from '../context/PlayerContext';
import type { Song } from '../context/PlayerContext';
import { LikeButton } from '../components/LikeButton';
import { ShareButton } from '../components/ShareButton';

interface Recommendation {
  id: string;
  type: 'song' | 'album' | 'artist';
  name: string;
  album_art?: string;
  artist?: { id: string; name: string };
}

export const RecommendationsPage: React.FC = () => {
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const { play } = usePlayer();

  useEffect(() => {
    const fetchRecs = async () => {
      setLoading(true);
      const res = await axios.get('/recommendations', { withCredentials: true });
      setRecs(res.data.results || []);
      setLoading(false);
    };
    fetchRecs();
  }, []);

  return (
    <div>
      <h2>Recommended for You</h2>
      {loading ? <div>Loading...</div> : (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
          {recs.map(r => (
            <div key={r.type + '-' + r.id} style={{ border: '1px solid #ccc', borderRadius: 8, padding: 12, width: 220 }}>
              {r.album_art && <img src={r.album_art} alt="art" style={{ width: '100%', borderRadius: 4 }} />}
              <div style={{ fontWeight: 'bold', marginTop: 8 }}>{r.name}</div>
              <div style={{ color: '#888' }}>{r.type.toUpperCase()}</div>
              {r.artist && <div>by <a href={'/artist/' + r.artist.id}>{r.artist.name}</a></div>}
              {r.type === 'song' && (
                <>
                  <button style={{ marginTop: 8 }} onClick={() => play(r as Song, [r as Song])}>Play</button>
                  <LikeButton songId={r.id} />
                  <ShareButton songId={r.id} />
                </>
              )}
              {r.type === 'album' && <a href={'/album/' + r.id}><button style={{ marginTop: 8 }}>View Album</button></a>}
              {r.type === 'artist' && <a href={'/artist/' + r.id}><button style={{ marginTop: 8 }}>View Artist</button></a>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}; 
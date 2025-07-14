import React, { useState } from 'react';
import axios from 'axios';

export const AnalyticsDashboard: React.FC = () => {
  const [type, setType] = useState<'song' | 'user'>('song');
  const [id, setId] = useState('');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`/analytics/${type}/${id}`, { withCredentials: true });
      setData(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch analytics');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Analytics Dashboard</h2>
      <div style={{ marginBottom: 16 }}>
        <select value={type} onChange={e => setType(e.target.value as 'song' | 'user')}>
          <option value="song">Song</option>
          <option value="user">User</option>
        </select>
        <input value={id} onChange={e => setId(e.target.value)} placeholder={type === 'song' ? 'Song ID' : 'User ID'} />
        <button onClick={fetchAnalytics} disabled={loading || !id}>Fetch</button>
      </div>
      {loading && <div>Loading...</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {data && (
        <div>
          <h4>Stats</h4>
          <pre>{JSON.stringify(data, null, 2)}</pre>
          {/* Simple chart placeholder */}
          {data.history && (
            <div style={{ marginTop: 16 }}>
              <b>History (last 7 days):</b>
              <div style={{ display: 'flex', gap: 8 }}>
                {data.history.map((v: number, i: number) => (
                  <div key={i} style={{ background: '#4af', width: 24, height: v, transition: 'height 0.3s' }} title={`Day ${i + 1}: ${v}`}></div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}; 
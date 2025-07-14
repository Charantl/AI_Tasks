import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Metrics {
  api?: any;
  activeUsers?: any;
  db?: any;
  cache?: any;
  system?: any;
}

const AdminDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<Metrics>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      setLoading(true);
      setError(null);
      try {
        const [activeUsers, db, cache, system] = await Promise.all([
          axios.get('/analytics/monitoring/active_users'),
          axios.get('/analytics/monitoring/db_performance'),
          axios.get('/analytics/monitoring/cache'),
          axios.get('/analytics/monitoring/system'),
        ]);
        setMetrics({
          activeUsers: activeUsers.data,
          db: db.data,
          cache: cache.data,
          system: system.data,
        });
      } catch (err: any) {
        setError(err.message || 'Failed to load metrics');
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Loading dashboard...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: 24 }}>
      <h1>Admin Monitoring Dashboard</h1>
      <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 220, background: '#f6f8fa', padding: 16, borderRadius: 8 }}>
          <h3>Active Users (10 min)</h3>
          <div style={{ fontSize: 32 }}>{metrics.activeUsers?.active_users_last_10min ?? '-'}</div>
        </div>
        <div style={{ flex: 1, minWidth: 220, background: '#f6f8fa', padding: 16, borderRadius: 8 }}>
          <h3>Database Stats</h3>
          <div>Songs: {metrics.db?.song_count ?? '-'}</div>
          <div>Users: {metrics.db?.user_count ?? '-'}</div>
          <div>Plays: {metrics.db?.play_count ?? '-'}</div>
        </div>
        <div style={{ flex: 1, minWidth: 220, background: '#f6f8fa', padding: 16, borderRadius: 8 }}>
          <h3>Cache Metrics</h3>
          <div>Hits: {metrics.cache?.hits ?? '-'}</div>
          <div>Misses: {metrics.cache?.misses ?? '-'}</div>
          <div>Sets: {metrics.cache?.sets ?? '-'}</div>
          <div>Invalidations: {metrics.cache?.invalidations ?? '-'}</div>
          <div>Hit Rate: {metrics.cache?.hit_rate ? (metrics.cache.hit_rate * 100).toFixed(1) + '%' : '-'}</div>
        </div>
        <div style={{ flex: 1, minWidth: 220, background: '#f6f8fa', padding: 16, borderRadius: 8 }}>
          <h3>System Usage</h3>
          <div>CPU: {metrics.system?.cpu_percent ?? '-'}%</div>
          <div>Memory: {metrics.system?.memory_percent ?? '-'}%</div>
          <div>Used: {metrics.system?.memory_used_mb ?? '-'} MB</div>
          <div>Total: {metrics.system?.memory_total_mb ?? '-'} MB</div>
        </div>
      </div>
      <div style={{ marginTop: 32 }}>
        <h3>API Performance</h3>
        <p>For detailed API metrics, see <a href="/metrics" target="_blank" rel="noopener noreferrer">/metrics</a> (Prometheus format)</p>
      </div>
    </div>
  );
};

export default AdminDashboard; 
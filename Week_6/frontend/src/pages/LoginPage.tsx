import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { AuthForm } from '../components/AuthForm';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const { fetchUser } = useAuth();

  const handleLogin = async (data: { email: string; password: string }) => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      const res = await axios.post('/auth/login', data); // no withCredentials
      const token = res.data.access_token;
      localStorage.setItem('access_token', token);
      await fetchUser();
      setSuccess(true);
      setTimeout(() => navigate('/'), 1000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const bgStyle = {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    width: '100vw',
    height: '100vh',
    zIndex: -1,
    background: 'url(/music-bg.jpg) no-repeat center center fixed',
    backgroundSize: 'cover',
    backgroundRepeat: 'no-repeat',
    backgroundPosition: 'center center',
  };

  return (
    <div style={{ height: '100vh', width: '100vw', position: 'relative', overflow: 'hidden' }}>
      {/* Fullscreen Image */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          background: 'url(/music-bg.jpg) no-repeat center center',
          backgroundSize: 'cover',
          zIndex: 1,
        }}
      />
      {/* Login Form Box (overlapping, right side) */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          right: '6vw',
          transform: 'translateY(-50%)',
          zIndex: 2,
          minWidth: 350,
          maxWidth: 420,
          width: '100%',
          background: 'linear-gradient(135deg, rgba(120,60,180,0.35) 0%, rgba(255,255,255,0.10) 100%)',
          boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.18)',
          borderRadius: 22,
          border: '2px solid rgba(255,255,255,0.45)',
          backdropFilter: 'blur(18px)',
          WebkitBackdropFilter: 'blur(18px)',
          padding: '2.5rem 2.5rem',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <h2 style={{ marginBottom: 32, color: '#fff', fontWeight: 700, fontSize: 36, letterSpacing: 1 }}>Login</h2>
        {success && <div style={{ color: 'lightgreen', marginBottom: 16 }}>Login successful! Redirecting...</div>}
        <div style={{ width: '100%' }}>
          {/* Placeholder for username, password, and social login buttons */}
          <form
            style={{ display: 'flex', flexDirection: 'column', gap: 24 }}
            onSubmit={e => {
              e.preventDefault();
              handleLogin({ email: username, password });
            }}
          >
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
              <label htmlFor="username" style={{ color: '#fff', fontWeight: 600, marginBottom: 8 }}>Username</label>
              <input
                id="username"
                type="text"
                placeholder="Username"
                style={{ color: '#fff', borderBottom: '2px solid #fff', background: 'transparent', marginBottom: 8, fontSize: 18, padding: '10px 0', width: '100%', '::placeholder': { color: '#ffffffcc', opacity: 1 } }}
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
              />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
              <label htmlFor="password" style={{ color: '#fff', fontWeight: 600, marginBottom: 8 }}>Password</label>
              <input
                id="password"
                type="password"
                placeholder="Password"
                style={{ color: '#fff', borderBottom: '2px solid #fff', background: 'transparent', marginBottom: 8, fontSize: 18, padding: '10px 0', width: '100%', '::placeholder': { color: '#ffffffcc', opacity: 1 } }}
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" style={{ background: '#fff', color: '#222', fontWeight: 700, borderRadius: 24, fontSize: 20, margin: '36px 0 0 0', padding: '14px 0', cursor: 'pointer' }} disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </button>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 24 }}>
              <button type="button" style={{ background: '#1DB954', color: '#fff', fontWeight: 700, borderRadius: 24, fontSize: 18, padding: '12px 0', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, cursor: 'not-allowed', opacity: 0.7 }} disabled>
                {/* Spotify Icon Placeholder */}
                <span style={{ fontSize: 20 }}>🎵</span> Continue with Spotify
              </button>
              <button type="button" style={{ background: '#fff', color: '#222', fontWeight: 700, borderRadius: 24, fontSize: 18, padding: '12px 0', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, cursor: 'not-allowed', opacity: 0.7 }} disabled>
                {/* Google Icon Placeholder */}
                <span style={{ fontSize: 20 }}>🔵</span> Continue with Google
              </button>
              <button type="button" style={{ background: '#1877F2', color: '#fff', fontWeight: 700, borderRadius: 24, fontSize: 18, padding: '12px 0', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, cursor: 'not-allowed', opacity: 0.7 }} disabled>
                {/* Facebook Icon Placeholder */}
                <span style={{ fontSize: 20 }}>📘</span> Continue with Facebook
              </button>
            </div>
          </form>
        </div>
        <div style={{ marginTop: '2rem', textAlign: 'center', width: '100%' }}>
          <span style={{ color: '#fff', fontWeight: 400 }}>Don't have an account</span>
          <a href="/register" style={{ marginLeft: 8, color: '#fff', fontWeight: 700, textDecoration: 'underline', cursor: 'pointer', letterSpacing: 0.5 }}>Register</a>
        </div>
      </div>
    </div>
  );
}; 
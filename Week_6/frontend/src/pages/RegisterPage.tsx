import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { AuthForm } from '../components/AuthForm';

export const RegisterPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (data: { email: string; password: string; username: string }) => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await axios.post('/auth/register', data, { withCredentials: true });
      setSuccess(true);
      setTimeout(() => navigate('/login'), 1200);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
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
      {/* Register Form Box (overlapping, right side) */}
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
        <h2 style={{ marginBottom: 32, color: '#fff', fontWeight: 700, fontSize: 36, letterSpacing: 1 }}>Register</h2>
        {success && <div style={{ color: 'lightgreen', marginBottom: 16 }}>Registration successful! Redirecting...</div>}
        <div style={{ width: '100%' }}>
          <AuthForm 
            mode="register" 
            onSubmit={handleRegister} 
            loading={loading} 
            error={error || undefined} 
            inputStyle={{ color: '#fff', borderBottom: '2px solid #fff', background: 'transparent', marginBottom: 32, fontSize: 18, padding: '10px 0' }} 
            labelStyle={{ color: '#fff', fontWeight: 600, marginBottom: 12 }} 
            buttonStyle={{ background: '#fff', color: '#222', fontWeight: 700, borderRadius: 24, fontSize: 20, margin: '36px 0 0 0', padding: '14px 0' }} 
            linkStyle={{ color: '#fff', fontWeight: 600, textDecoration: 'underline', marginLeft: 8 }} 
          />
        </div>
        <div style={{ marginTop: '2rem', textAlign: 'center', width: '100%' }}>
          <span style={{ color: '#fff', fontWeight: 400 }}>Already have an account?</span>
          <a href="/login" style={{ marginLeft: 8, color: '#fff', fontWeight: 700, textDecoration: 'underline', cursor: 'pointer', letterSpacing: 0.5 }}>Login</a>
        </div>
      </div>
    </div>
  );
}; 
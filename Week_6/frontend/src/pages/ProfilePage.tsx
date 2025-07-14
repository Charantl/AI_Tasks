import React, { useEffect, useState } from 'react';
import axios from '../api/axiosInstance';
import { useAuth } from '../context/AuthContext';

export const ProfilePage: React.FC = () => {
  const { user, fetchUser } = useAuth();
  const [showEditModal, setShowEditModal] = useState(false);
  const [showPwModal, setShowPwModal] = useState(false);
  const [email, setEmail] = useState(user?.email || '');
  const [displayName, setDisplayName] = useState(user?.display_name || user?.username || '');
  const [avatar, setAvatar] = useState(user?.avatar || '');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Password change state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [pwLoading, setPwLoading] = useState(false);
  const [pwSuccess, setPwSuccess] = useState(false);
  const [pwError, setPwError] = useState<string | null>(null);

  useEffect(() => {
    setEmail(user?.email || '');
    setDisplayName(user?.display_name || user?.username || '');
    setAvatar(user?.avatar || '');
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await axios.patch('/users/profile', { email, username: displayName, avatar });
      setSuccess(true);
      fetchUser();
      setShowEditModal(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Update failed');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setPwSuccess(false);
    setPwError(null);
    setPwLoading(true);
    if (newPassword !== confirmNewPassword) {
      setPwError('New passwords do not match');
      setPwLoading(false);
      return;
    }
    try {
      await axios.patch('/users/profile', { password: newPassword });
      setPwSuccess(true);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmNewPassword('');
      setShowPwModal(false);
    } catch (err: any) {
      setPwError(err.response?.data?.detail || 'Password change failed');
    } finally {
      setPwLoading(false);
    }
  };

  if (!user) return <div style={{ color: '#fff', textAlign: 'center', marginTop: 40 }}>Please log in to view your profile.</div>;

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(180deg, #181818 0%, #282828 100%)', color: '#fff' }}>
      {/* Banner */}
      <div style={{
        height: 240,
        background: 'linear-gradient(135deg, #3a3a3a 60%, #1db954 100%)',
        position: 'relative',
        display: 'flex',
        alignItems: 'flex-end',
        padding: '0 0 48px 0',
        justifyContent: 'center',
      }}>
        {/* Avatar */}
        <div style={{
          position: 'absolute',
          left: '50%',
          bottom: -64,
          transform: 'translateX(-50%)',
          boxShadow: '0 4px 32px 0 rgba(0,0,0,0.4)',
          borderRadius: '50%',
          border: '6px solid #181818',
          width: 128,
          height: 128,
          overflow: 'hidden',
          background: '#222',
          zIndex: 2,
        }}>
          <img src={avatar || '/vite.svg'} alt="avatar" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        </div>
      </div>
      {/* Profile Info */}
      <div style={{
        marginTop: 96,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 8,
        maxWidth: 480,
        marginLeft: 'auto',
        marginRight: 'auto',
        background: 'rgba(24,24,24,0.85)',
        borderRadius: 18,
        boxShadow: '0 2px 16px 0 rgba(0,0,0,0.18)',
        padding: '32px 32px 40px 32px',
        position: 'relative',
      }}>
        <div style={{ color: '#1db954', fontWeight: 700, fontSize: 16, letterSpacing: 1, marginBottom: 4 }}>USER</div>
        <h2 style={{ fontSize: 36, fontWeight: 700, margin: 0 }}>{displayName || 'User'}</h2>
        <div style={{ color: '#b3b3b3', fontSize: 18, marginBottom: 8 }}>{email}</div>
        <div style={{ width: '100%', borderBottom: '1px solid #333', margin: '18px 0 18px 0' }} />
        <div style={{ display: 'flex', gap: 16, marginTop: 8 }}>
          <button
            onClick={() => setShowEditModal(true)}
            style={{
              background: '#fff',
              color: '#181818',
              border: 'none',
              borderRadius: 24,
              padding: '10px 32px',
              fontWeight: 700,
              fontSize: 18,
              cursor: 'pointer',
              boxShadow: '0 2px 8px 0 rgba(0,0,0,0.12)',
              transition: 'background 0.2s',
            }}
          >
            Edit Profile
          </button>
          <button
            onClick={() => setShowPwModal(true)}
            style={{
              background: '#181818',
              color: '#fff',
              border: '1px solid #444',
              borderRadius: 24,
              padding: '10px 32px',
              fontWeight: 700,
              fontSize: 18,
              cursor: 'pointer',
              boxShadow: '0 2px 8px 0 rgba(0,0,0,0.12)',
              transition: 'background 0.2s',
            }}
          >
            Change Password
          </button>
        </div>
        {success && <div style={{ color: '#1db954', marginTop: 12 }}>Profile updated!</div>}
        {error && <div style={{ color: 'red', marginTop: 12 }}>{error}</div>}
      </div>
      {/* Edit Modal */}
      {showEditModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          background: 'rgba(0,0,0,0.7)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <div style={{
            background: '#222',
            borderRadius: 18,
            padding: '2.5rem 2.5rem',
            minWidth: 340,
            maxWidth: 400,
            width: '100%',
            boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.18)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            position: 'relative',
          }}>
            <button
              onClick={() => setShowEditModal(false)}
              style={{
                position: 'absolute',
                top: 16,
                right: 16,
                background: 'transparent',
                border: 'none',
                color: '#fff',
                fontSize: 24,
                cursor: 'pointer',
              }}
              aria-label="Close"
            >
              &times;
            </button>
            <h3 style={{ marginBottom: 24, color: '#fff', fontWeight: 700, fontSize: 28 }}>Edit Profile</h3>
            <form onSubmit={handleSubmit} style={{ width: '100%' }}>
              <div style={{ marginBottom: 18 }}>
                <label style={{ color: '#b3b3b3', fontWeight: 600 }}>Display Name</label>
                <input
                  value={displayName}
                  onChange={e => setDisplayName(e.target.value)}
                  type="text"
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: 8,
                    border: '1px solid #444',
                    background: '#181818',
                    color: '#fff',
                    fontSize: 18,
                    marginTop: 6,
                  }}
                />
              </div>
              <div style={{ marginBottom: 18 }}>
                <label style={{ color: '#b3b3b3', fontWeight: 600 }}>Email</label>
                <input
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  type="email"
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: 8,
                    border: '1px solid #444',
                    background: '#181818',
                    color: '#fff',
                    fontSize: 18,
                    marginTop: 6,
                  }}
                />
              </div>
              <div style={{ marginBottom: 24 }}>
                <label style={{ color: '#b3b3b3', fontWeight: 600 }}>Avatar URL</label>
                <input
                  value={avatar}
                  onChange={e => setAvatar(e.target.value)}
                  type="text"
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: 8,
                    border: '1px solid #444',
                    background: '#181818',
                    color: '#fff',
                    fontSize: 18,
                    marginTop: 6,
                  }}
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                style={{
                  width: '100%',
                  background: '#1db954',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 24,
                  padding: '12px 0',
                  fontWeight: 700,
                  fontSize: 20,
                  cursor: 'pointer',
                  marginTop: 8,
                  boxShadow: '0 2px 8px 0 rgba(0,0,0,0.12)',
                  transition: 'background 0.2s',
                }}
              >
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
              {error && <div style={{ color: 'red', marginTop: 12 }}>{error}</div>}
            </form>
          </div>
        </div>
      )}
      {/* Password Modal */}
      {showPwModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          background: 'rgba(0,0,0,0.7)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <div style={{
            background: '#222',
            borderRadius: 18,
            padding: '2.5rem 2.5rem',
            minWidth: 340,
            maxWidth: 400,
            width: '100%',
            boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.18)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            position: 'relative',
          }}>
            <button
              onClick={() => setShowPwModal(false)}
              style={{
                position: 'absolute',
                top: 16,
                right: 16,
                background: 'transparent',
                border: 'none',
                color: '#fff',
                fontSize: 24,
                cursor: 'pointer',
              }}
              aria-label="Close"
            >
              &times;
            </button>
            <h3 style={{ marginBottom: 24, color: '#fff', fontWeight: 700, fontSize: 28 }}>Change Password</h3>
            <form onSubmit={handlePasswordChange} style={{ width: '100%' }}>
              <div style={{ marginBottom: 18 }}>
                <label style={{ color: '#b3b3b3', fontWeight: 600 }}>Current Password</label>
                <input
                  type="password"
                  value={currentPassword}
                  onChange={e => setCurrentPassword(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: 8,
                    border: '1px solid #444',
                    background: '#181818',
                    color: '#fff',
                    fontSize: 18,
                    marginTop: 6,
                  }}
                />
              </div>
              <div style={{ marginBottom: 18 }}>
                <label style={{ color: '#b3b3b3', fontWeight: 600 }}>New Password</label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={e => setNewPassword(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: 8,
                    border: '1px solid #444',
                    background: '#181818',
                    color: '#fff',
                    fontSize: 18,
                    marginTop: 6,
                  }}
                />
              </div>
              <div style={{ marginBottom: 24 }}>
                <label style={{ color: '#b3b3b3', fontWeight: 600 }}>Confirm New Password</label>
                <input
                  type="password"
                  value={confirmNewPassword}
                  onChange={e => setConfirmNewPassword(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: 8,
                    border: '1px solid #444',
                    background: '#181818',
                    color: '#fff',
                    fontSize: 18,
                    marginTop: 6,
                  }}
                />
              </div>
              <button
                type="submit"
                disabled={pwLoading}
                style={{
                  width: '100%',
                  background: '#1db954',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 24,
                  padding: '12px 0',
                  fontWeight: 700,
                  fontSize: 20,
                  cursor: 'pointer',
                  marginTop: 8,
                  boxShadow: '0 2px 8px 0 rgba(0,0,0,0.12)',
                  transition: 'background 0.2s',
                }}
              >
                {pwLoading ? 'Saving...' : 'Change Password'}
              </button>
              {pwError && <div style={{ color: 'red', marginTop: 12 }}>{pwError}</div>}
              {pwSuccess && <div style={{ color: '#1db954', marginTop: 12 }}>Password changed!</div>}
            </form>
          </div>
        </div>
      )}
    </div>
  );
}; 
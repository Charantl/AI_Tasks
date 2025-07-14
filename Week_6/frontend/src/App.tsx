import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ProfilePage } from './pages/ProfilePage';
import { SubscriptionPage } from './pages/SubscriptionPage';
import { SearchPage } from './pages/SearchPage';
import { BrowsePage } from './pages/BrowsePage';
import { ArtistPage } from './pages/ArtistPage';
import { AlbumPage } from './pages/AlbumPage';
import { PlaylistsPage } from './pages/PlaylistsPage';
import { PlaylistDetailPage } from './pages/PlaylistDetailPage';
import { LikedSongsPage } from './pages/LikedSongsPage';
import { HistoryPage } from './pages/HistoryPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { AnalyticsDashboard } from './pages/AnalyticsDashboard';
import { ListeningRoomPage } from './pages/ListeningRoomPage';
import { AuthProvider, useAuth } from './context/AuthContext';
import { PlayerProvider } from './context/PlayerContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { SubscriptionTier } from './components/SubscriptionTier';
import { PlayerBar } from './components/PlayerBar';
import { ErrorBoundary } from './components/ErrorBoundary';
import AdminDashboard from './pages/AdminDashboard';

const Nav: React.FC = () => {
  const { user, loading, logout } = useAuth();
  return (
    <nav>
      {loading ? (
        <span>Loading...</span>
      ) : user ? (
        <>
          <span>Welcome, {user.display_name || user.email}!</span>
          <SubscriptionTier />
          <Link to="/search" style={{ marginLeft: 8 }}>Search</Link>
          <Link to="/browse" style={{ marginLeft: 8 }}>Browse</Link>
          <Link to="/playlists" style={{ marginLeft: 8 }}>Playlists</Link>
          <Link to="/liked-songs" style={{ marginLeft: 8 }}>Liked Songs</Link>
          <Link to="/history" style={{ marginLeft: 8 }}>History</Link>
          <Link to="/profile" style={{ marginLeft: 8 }}>Profile</Link>
          <Link to="/subscription" style={{ marginLeft: 8 }}>Subscription</Link>
          {user.role === 'admin' && (
            <Link to="/admin" style={{ marginLeft: 8, color: 'red' }}>Admin Dashboard</Link>
          )}
          <button onClick={logout} style={{ marginLeft: 8 }}>Logout</button>
        </>
      ) : (
        <>
          <Link to="/login">Login</Link> | <Link to="/register">Register</Link>
        </>
      )}
    </nav>
  );
};

const HomePage: React.FC = () => {
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
      <div style={bgStyle}></div>
      <div style={{
        position: 'relative',
        zIndex: 1,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        width: '100vw',
      }}>
        <h1 style={{
          color: '#222',
          background: 'rgba(255,255,255,0.7)',
          padding: '2rem 3rem',
          borderRadius: '16px',
        }}>
          Welcome to the Music App
        </h1>
      </div>
    </div>
  );
};

const spotifyBg = {
  minHeight: '100vh',
  background: 'linear-gradient(180deg, #181818 0%, #282828 100%)',
  color: '#fff',
};

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <PlayerProvider>
          <Router>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/*" element={
                <div style={spotifyBg}>
                  <Routes>
                    <Route path="profile" element={<ProtectedRoute><><Nav /><ProfilePage /></></ProtectedRoute>} />
                    <Route path="subscription" element={<ProtectedRoute><><Nav /><SubscriptionPage /></></ProtectedRoute>} />
                    <Route path="search" element={<ProtectedRoute><><Nav /><SearchPage /></></ProtectedRoute>} />
                    <Route path="browse" element={<ProtectedRoute><><Nav /><BrowsePage /></></ProtectedRoute>} />
                    <Route path="artist/:id" element={<ProtectedRoute><><Nav /><ArtistPage /></></ProtectedRoute>} />
                    <Route path="album/:id" element={<ProtectedRoute><><Nav /><AlbumPage /></></ProtectedRoute>} />
                    <Route path="playlists" element={<ProtectedRoute><><Nav /><PlaylistsPage /></></ProtectedRoute>} />
                    <Route path="playlist/:id" element={<ProtectedRoute><><Nav /><PlaylistDetailPage /></></ProtectedRoute>} />
                    <Route path="liked-songs" element={<ProtectedRoute><><Nav /><LikedSongsPage /></></ProtectedRoute>} />
                    <Route path="history" element={<ProtectedRoute><><Nav /><HistoryPage /></></ProtectedRoute>} />
                    <Route path="recommendations" element={<ProtectedRoute><><Nav /><RecommendationsPage /></></ProtectedRoute>} />
                    <Route path="analytics" element={<ProtectedRoute><><Nav /><AnalyticsDashboard /></></ProtectedRoute>} />
                    <Route path="listening-room/:roomId" element={<ProtectedRoute><><Nav /><ListeningRoomPage /></></ProtectedRoute>} />
                    <Route path="admin" element={<ProtectedRoute adminOnly><><Nav /><AdminDashboard /></></ProtectedRoute>} />
                    <Route path="/" element={<ProtectedRoute><><Nav /><HomePage /></></ProtectedRoute>} />
                  </Routes>
                </div>
              } />
            </Routes>
            <PlayerBar />
          </Router>
        </PlayerProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;

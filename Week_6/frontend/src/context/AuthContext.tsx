import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import axios from '../api/axiosInstance';

interface User {
  id: string;
  email: string;
  display_name?: string;
  avatar?: string;
  role?: string; // Add role for admin check
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  fetchUser: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUser = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get('/users/me');
      setUser(res.data); // Assumes backend returns 'role' in user object
    } catch (err: any) {
      setUser(null);
      setError(err.response?.data?.detail || 'Not authenticated');
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    localStorage.removeItem('access_token');
    setUser(null);
  };

  useEffect(() => {
    fetchUser();
    // eslint-disable-next-line
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, error, fetchUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}; 
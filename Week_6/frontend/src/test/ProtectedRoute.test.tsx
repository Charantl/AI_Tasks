import { render, screen } from '@testing-library/react';
import React from 'react';
import { vi } from 'vitest';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';

describe('ProtectedRoute', () => {
  afterEach(() => {
    vi.resetModules();
  });

  it('renders children if user exists', async () => {
    vi.doMock('../context/AuthContext', () => ({
      useAuth: () => ({ user: { role: 'user' }, loading: false })
    }));
    const { ProtectedRoute } = await import('../components/ProtectedRoute');
    render(<MemoryRouter><ProtectedRoute><div>Protected</div></ProtectedRoute></MemoryRouter>);
    expect(screen.getByText('Protected')).toBeInTheDocument();
  });

  it('shows loading if loading', async () => {
    vi.doMock('../context/AuthContext', () => ({
      useAuth: () => ({ loading: true })
    }));
    const { ProtectedRoute } = await import('../components/ProtectedRoute');
    render(<MemoryRouter><ProtectedRoute><div>Protected</div></ProtectedRoute></MemoryRouter>);
    expect(screen.getByText(/Loading/)).toBeInTheDocument();
  });

  it('redirects if no user', async () => {
    vi.doMock('../context/AuthContext', () => ({
      useAuth: () => ({ user: null, loading: false })
    }));
    const { ProtectedRoute } = await import('../components/ProtectedRoute');
    render(<MemoryRouter><ProtectedRoute><div>Protected</div></ProtectedRoute></MemoryRouter>);
    expect(screen.queryByText('Protected')).not.toBeInTheDocument();
  });

  it('redirects if adminOnly and not admin', async () => {
    vi.doMock('../context/AuthContext', () => ({
      useAuth: () => ({ user: { role: 'user' }, loading: false })
    }));
    const { ProtectedRoute } = await import('../components/ProtectedRoute');
    render(<MemoryRouter><ProtectedRoute adminOnly><div>Admin</div></ProtectedRoute></MemoryRouter>);
    expect(screen.queryByText('Admin')).not.toBeInTheDocument();
  });
}); 
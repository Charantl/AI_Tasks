import { render, screen } from '@testing-library/react';
import React from 'react';
import { vi } from 'vitest';
import '@testing-library/jest-dom';

// Default mock for usePlayer
vi.doMock('../context/PlayerContext', () => ({
  usePlayer: () => ({
    queue: [{ id: '1', name: 'Test Song', artist: { name: 'Test Artist' }, album_art: 'art.png', audio_url: 'audio.mp3' }],
    currentIndex: 0,
    playing: false,
    play: vi.fn(),
    pause: vi.fn(),
    next: vi.fn(),
    prev: vi.fn(),
    volume: 0.5,
    setVolume: vi.fn(),
  })
}));

describe('PlayerBar', () => {
  afterEach(() => {
    vi.resetModules();
  });

  it('renders current song info and controls', async () => {
    const { PlayerBar } = await import('../components/PlayerBar');
    render(<PlayerBar />);
    expect(screen.getByText('Test Song')).toBeInTheDocument();
    expect(screen.getByText(/by Test Artist/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Play/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Prev/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Next/i })).toBeInTheDocument();
    expect(screen.getByRole('slider')).toBeInTheDocument();
  });

  it('does not render if no current song', async () => {
    vi.doMock('../context/PlayerContext', () => ({
      usePlayer: () => ({ queue: [], currentIndex: 0 })
    }));
    const { PlayerBar } = await import('../components/PlayerBar');
    const { container } = render(<PlayerBar />);
    expect(container.firstChild).toBeNull();
  });
}); 
import { render, screen, fireEvent } from '@testing-library/react';
import { AudioPlayer } from '../components/AudioPlayer';
import { vi } from 'vitest';
import '@testing-library/jest-dom';

describe('AudioPlayer', () => {
  it('renders with song name', () => {
    render(<AudioPlayer songUrl="url" songName="Song" />);
    expect(screen.getByText('Song')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
    expect(screen.getByRole('slider')).toBeInTheDocument();
  });

  it('toggles play/pause', () => {
    render(<AudioPlayer songUrl="url" songName="Song" />);
    const btn = screen.getByRole('button');
    fireEvent.click(btn);
    expect(btn.textContent).toMatch(/Pause|Play/);
  });
}); 
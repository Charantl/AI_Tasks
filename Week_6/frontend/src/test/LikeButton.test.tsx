import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LikeButton } from '../components/LikeButton';
import axios from 'axios';
import { vi } from 'vitest';
import '@testing-library/jest-dom';

vi.mock('axios');

describe('LikeButton', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders and checks liked state', async () => {
    (axios.get as any).mockResolvedValueOnce({ data: [{ song_id: '1' }] });
    render(<LikeButton songId="1" />);
    await waitFor(() => expect(screen.getByText('♥')).toBeInTheDocument());
  });

  it('likes a song', async () => {
    (axios.get as any).mockResolvedValueOnce({ data: [] });
    (axios.post as any).mockResolvedValueOnce({});
    render(<LikeButton songId="1" />);
    fireEvent.click(screen.getByRole('button'));
    await waitFor(() => expect((axios.post as any)).toHaveBeenCalled());
  });

  it('unlikes a song', async () => {
    (axios.get as any).mockResolvedValueOnce({ data: [{ song_id: '1' }] });
    (axios.delete as any).mockResolvedValueOnce({});
    render(<LikeButton songId="1" />);
    await waitFor(() => expect(screen.getByText('♥')).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button'));
    await waitFor(() => expect((axios.delete as any)).toHaveBeenCalled());
  });
}); 
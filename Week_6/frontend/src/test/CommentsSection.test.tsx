import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CommentsSection } from '../components/CommentsSection';
import axios from 'axios';
import { vi } from 'vitest';
import '@testing-library/jest-dom';

vi.mock('axios');

describe('CommentsSection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders and loads comments', async () => {
    (axios.get as any).mockResolvedValueOnce({ data: [{ id: '1', user_id: 'u', content: 'hi', created_at: new Date().toISOString() }] });
    render(<CommentsSection songId="1" currentUserId="u" />);
    await waitFor(() => expect(screen.getByText('hi')).toBeInTheDocument());
  });

  it('shows loading and error', async () => {
    (axios.get as any).mockRejectedValueOnce({ response: { data: { detail: 'fail' } } });
    render(<CommentsSection songId="1" />);
    expect(screen.getByText(/Loading/)).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText(/fail/)).toBeInTheDocument());
  });

  it('adds a comment', async () => {
    (axios.get as any).mockResolvedValue({ data: [] });
    (axios.post as any).mockResolvedValue({});
    render(<CommentsSection songId="1" currentUserId="u" />);
    fireEvent.change(screen.getByPlaceholderText(/Add a comment/), { target: { value: 'new comment' } });
    fireEvent.click(screen.getByRole('button', { name: /Post/i }));
    await waitFor(() => expect((axios.post as any)).toHaveBeenCalled());
  });

  it('deletes a comment', async () => {
    (axios.get as any).mockResolvedValue({ data: [{ id: '1', user_id: 'u', content: 'hi', created_at: new Date().toISOString() }] });
    (axios.delete as any).mockResolvedValue({});
    render(<CommentsSection songId="1" currentUserId="u" />);
    await waitFor(() => expect(screen.getByText('hi')).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', { name: /Delete/i }));
    await waitFor(() => expect((axios.delete as any)).toHaveBeenCalled());
  });
}); 
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AlbumForm } from '../components/AlbumForm';
import axios from 'axios';
import { vi } from 'vitest';
import '@testing-library/jest-dom';

vi.mock('axios');

describe('AlbumForm', () => {
  it('renders form', () => {
    render(<AlbumForm onCreate={vi.fn()} />);
    expect(screen.getByPlaceholderText(/Album title/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Create Album/i })).toBeInTheDocument();
  });

  it('submits form and calls onCreate', async () => {
    (axios.post as any).mockResolvedValue({});
    const onCreate = vi.fn();
    render(<AlbumForm onCreate={onCreate} />);
    fireEvent.change(screen.getByPlaceholderText(/Album title/), { target: { value: 'A' } });
    fireEvent.click(screen.getByRole('button'));
    await waitFor(() => expect((axios.post as any)).toHaveBeenCalled());
    await waitFor(() => expect(onCreate).toHaveBeenCalled());
  });

  it('shows error on failure', async () => {
    (axios.post as any).mockRejectedValueOnce({ response: { data: { detail: 'fail' } } });
    render(<AlbumForm onCreate={vi.fn()} />);
    fireEvent.change(screen.getByPlaceholderText(/Album title/), { target: { value: 'A' } });
    fireEvent.click(screen.getByRole('button'));
    await waitFor(() => expect(screen.getByText(/fail/)).toBeInTheDocument());
  });
}); 
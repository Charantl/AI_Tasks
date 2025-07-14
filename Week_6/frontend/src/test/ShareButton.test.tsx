import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ShareButton } from '../components/ShareButton';
import axios from 'axios';
import { vi } from 'vitest';
import '@testing-library/jest-dom';

vi.mock('axios');

describe('ShareButton', () => {
  it('renders share button', () => {
    render(<ShareButton songId="1" />);
    expect(screen.getByRole('button', { name: /Share/i })).toBeInTheDocument();
  });

  it('fetches and displays share links', async () => {
    (axios.get as any).mockResolvedValueOnce({ data: { url: 'link', twitter: 'tw', facebook: 'fb', whatsapp: 'wa' } });
    render(<ShareButton songId="1" />);
    fireEvent.click(screen.getByRole('button', { name: /Share/i }));
    await waitFor(() => expect(screen.getByText(/Copy Link/)).toBeInTheDocument());
    expect(screen.getByText(/Share on Twitter/)).toBeInTheDocument();
    expect(screen.getByText(/Share on Facebook/)).toBeInTheDocument();
    expect(screen.getByText(/Share on WhatsApp/)).toBeInTheDocument();
  });

  it('shows error on API failure', async () => {
    (axios.get as any).mockRejectedValueOnce({ response: { data: { detail: 'fail' } } });
    render(<ShareButton songId="1" />);
    fireEvent.click(screen.getByRole('button', { name: /Share/i }));
    await waitFor(() => expect(screen.getByText(/fail/)).toBeInTheDocument());
  });
}); 
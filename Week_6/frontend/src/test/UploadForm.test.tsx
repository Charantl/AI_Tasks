import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UploadForm } from '../components/UploadForm';
import axios from 'axios';
import { vi } from 'vitest';
import '@testing-library/jest-dom';

vi.mock('axios');

describe('UploadForm', () => {
  it('renders form', () => {
    render(<UploadForm onUpload={vi.fn()} />);
    expect(screen.getByLabelText(/Audio File/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Song name/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Upload/i })).toBeInTheDocument();
  });

  it('shows error if no file', async () => {
    const { container } = render(<UploadForm onUpload={vi.fn()} />);
    fireEvent.click(screen.getByRole('button'));
    await waitFor(() => {
      expect(container.textContent).toMatch(/Please select an audio file/);
    });
  });

  it('submits form and calls onUpload', async () => {
    (axios.post as any).mockResolvedValueOnce({ data: { audio_url: 'url' } });
    (axios.post as any).mockResolvedValueOnce({});
    const onUpload = vi.fn();
    render(<UploadForm onUpload={onUpload} />);
    const file = new File(['audio'], 'audio.mp3', { type: 'audio/mp3' });
    fireEvent.change(screen.getByLabelText(/Audio File/i), { target: { files: [file] } });
    fireEvent.change(screen.getByLabelText(/Song name/i), { target: { value: 'Song' } });
    fireEvent.click(screen.getByRole('button'));
    await waitFor(() => expect((axios.post as any)).toHaveBeenCalled());
    await waitFor(() => expect(onUpload).toHaveBeenCalled());
  });

  it('shows error on failure', async () => {
    (axios.post as any).mockRejectedValueOnce({ response: { data: { detail: 'fail' } } });
    render(<UploadForm onUpload={vi.fn()} />);
    const file = new File(['audio'], 'audio.mp3', { type: 'audio/mp3' });
    fireEvent.change(screen.getByLabelText(/Audio File/i), { target: { files: [file] } });
    fireEvent.change(screen.getByLabelText(/Song name/i), { target: { value: 'Song' } });
    fireEvent.click(screen.getByRole('button'));
    expect(await screen.findByText(/fail/)).toBeInTheDocument();
  });
}); 
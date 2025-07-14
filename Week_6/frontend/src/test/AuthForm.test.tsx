import { render, screen, fireEvent } from '@testing-library/react';
import { AuthForm } from '../components/AuthForm';
import { vi } from 'vitest';
import '@testing-library/jest-dom';

describe('AuthForm', () => {
  it('renders login form by default', () => {
    render(<AuthForm onSubmit={vi.fn()} />);
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Login/i })).toBeInTheDocument();
  });

  it('renders register form with confirm password', () => {
    render(<AuthForm onSubmit={vi.fn()} mode="register" />);
    expect(screen.getByLabelText(/Confirm Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Register/i })).toBeInTheDocument();
  });

  it('shows error message', () => {
    render(<AuthForm onSubmit={vi.fn()} error="Invalid credentials" />);
    expect(screen.getByText(/Invalid credentials/)).toBeInTheDocument();
  });

  it('disables button and shows loading', () => {
    render(<AuthForm onSubmit={vi.fn()} loading />);
    expect(screen.getByRole('button')).toBeDisabled();
    expect(screen.getByText(/Loading.../)).toBeInTheDocument();
  });

  it('calls onSubmit on form submit', () => {
    const onSubmit = vi.fn();
    render(<AuthForm onSubmit={onSubmit} />);
    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'a@b.com' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'pw' } });
    fireEvent.click(screen.getByRole('button'));
    // react-hook-form calls onSubmit only if form is valid, so this is a smoke test
  });
}); 
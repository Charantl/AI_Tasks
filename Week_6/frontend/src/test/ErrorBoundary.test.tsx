import { render, screen } from '@testing-library/react';
import React from 'react';
import { ErrorBoundary } from '../components/ErrorBoundary';
import { vi } from 'vitest';
import '@testing-library/jest-dom';

describe('ErrorBoundary', () => {
  it('renders children when no error', () => {
    render(<ErrorBoundary><div>Child</div></ErrorBoundary>);
    expect(screen.getByText('Child')).toBeInTheDocument();
  });

  it('renders fallback UI on error', () => {
    // Throw error in child
    const Problem = () => { throw new Error('Oops!'); };
    render(<ErrorBoundary><Problem /></ErrorBoundary>);
    expect(screen.getByText(/Something went wrong/)).toBeInTheDocument();
    expect(screen.getByText(/Oops!/)).toBeInTheDocument();
  });
}); 
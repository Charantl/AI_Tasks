import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<{ children: React.ReactNode }, ErrorBoundaryState> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to console or external service
    console.error('ErrorBoundary caught:', error, errorInfo);
    // Optionally send to Sentry or similar
  }

  render() {
    if (this.state.hasError) {
      return <div style={{ color: 'red' }}>Something went wrong: {this.state.error?.message}</div>;
    }
    return this.props.children;
  }
} 
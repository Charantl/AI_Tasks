import React from 'react';
import { useForm } from 'react-hook-form';
import type { SubmitHandler } from 'react-hook-form';

interface AuthFormProps {
  onSubmit: SubmitHandler<{ email: string; password: string; confirmPassword?: string; username?: string }>;
  mode?: 'login' | 'register';
  loading?: boolean;
  error?: string;
}

const AuthForm: React.FC<AuthFormProps> = ({ onSubmit, mode = 'login', loading = false, error }) => {
  const { register, handleSubmit } = useForm<{ email: string; password: string; confirmPassword?: string; username?: string }>();
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {mode === 'register' && (
        <div>
          <label htmlFor="auth-username">Username</label>
          <input id="auth-username" type="text" {...register('username', { required: 'Username is required' })} />
        </div>
      )}
      <div>
        <label htmlFor="auth-email">Email</label>
        <input id="auth-email" type="email" {...register('email', { required: 'Email is required' })} />
      </div>
      <div>
        <label htmlFor="auth-password">Password</label>
        <input id="auth-password" type="password" {...register('password', { required: 'Password is required' })} />
      </div>
      {mode === 'register' && (
        <div>
          <label htmlFor="auth-confirm-password">Confirm Password</label>
          <input id="auth-confirm-password" type="password" {...register('confirmPassword', { required: 'Please confirm your password' })} />
        </div>
      )}
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <button type="submit" disabled={loading}>
        {loading ? 'Loading...' : mode === 'login' ? 'Login' : 'Register'}
      </button>
    </form>
  );
};

export { AuthForm }; 
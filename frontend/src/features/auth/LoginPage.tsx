import { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { Alert, Box, Button, Link, TextField, Typography } from '@mui/material';
import { useForm } from 'react-hook-form';
import { AuthLayout } from './components/AuthLayout';
import { useAuth } from '@/context/AuthContext';
import { getApiErrorMessage } from '@/shared/utils/format';

interface LoginForm {
  email: string;
  password: string;
}

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { register, handleSubmit } = useForm<LoginForm>();

  const onSubmit = handleSubmit(async (data) => {
    setError(null);
    setLoading(true);
    try {
      await login(data.email, data.password);
      navigate('/');
    } catch (err) {
      setError(getApiErrorMessage(err, 'Invalid email or password'));
    } finally {
      setLoading(false);
    }
  });

  return (
    <AuthLayout title="Sign in" subtitle="Enter your credentials to access your PG dashboard">
      <Box component="form" onSubmit={onSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {error && <Alert severity="error">{error}</Alert>}
        <TextField
          label="Email"
          type="email"
          autoComplete="email"
          fullWidth
          {...register('email', { required: true })}
        />
        <TextField
          label="Password"
          type="password"
          autoComplete="current-password"
          fullWidth
          {...register('password', { required: true })}
        />
        <Button type="submit" variant="contained" size="large" disabled={loading} fullWidth>
          {loading ? 'Signing in…' : 'Sign in'}
        </Button>
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
          Don&apos;t have an account?{' '}
          <Link component={RouterLink} to="/signup">
            Create one
          </Link>
        </Typography>
      </Box>
    </AuthLayout>
  );
}

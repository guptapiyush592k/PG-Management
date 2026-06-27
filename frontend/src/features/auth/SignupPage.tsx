import { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { Alert, Box, Button, Link, TextField, Typography } from '@mui/material';
import { useForm } from 'react-hook-form';
import { AuthLayout } from './components/AuthLayout';
import { useAuth } from '@/context/AuthContext';
import { getApiErrorMessage } from '@/shared/utils/format';

interface SignupForm {
  full_name: string;
  email: string;
  password: string;
}

export function SignupPage() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { register, handleSubmit } = useForm<SignupForm>();

  const onSubmit = handleSubmit(async (data) => {
    setError(null);
    setLoading(true);
    try {
      await signup(data.full_name, data.email, data.password);
      navigate('/');
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not create account'));
    } finally {
      setLoading(false);
    }
  });

  return (
    <AuthLayout
      title="Create account"
      subtitle="Sign up to start managing your PG on the demo tenant"
    >
      <Box component="form" onSubmit={onSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {error && <Alert severity="error">{error}</Alert>}
        <TextField label="Full name" fullWidth {...register('full_name', { required: true })} />
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
          autoComplete="new-password"
          helperText="Min 8 chars with uppercase, lowercase, and a digit"
          fullWidth
          {...register('password', { required: true, minLength: 8 })}
        />
        <Button type="submit" variant="contained" size="large" disabled={loading} fullWidth>
          {loading ? 'Creating account…' : 'Create account'}
        </Button>
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
          Already have an account?{' '}
          <Link component={RouterLink} to="/login">
            Sign in
          </Link>
        </Typography>
      </Box>
    </AuthLayout>
  );
}

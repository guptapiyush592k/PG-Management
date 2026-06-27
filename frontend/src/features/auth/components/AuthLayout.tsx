import { Box, Container, Paper, Typography } from '@mui/material';
import ApartmentIcon from '@mui/icons-material/Apartment';
import type { ReactNode } from 'react';

interface AuthLayoutProps {
  title: string;
  subtitle: string;
  children: ReactNode;
}

export function AuthLayout({ title, subtitle, children }: AuthLayoutProps) {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        p: 2,
      }}
    >
      <Container maxWidth="sm">
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Box
            sx={{
              width: 56,
              height: 56,
              borderRadius: 2,
              bgcolor: 'primary.main',
              color: 'primary.contrastText',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              mb: 2,
            }}
          >
            <ApartmentIcon />
          </Box>
          <Typography variant="h4" fontWeight={700}>
            PG Manager
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Paying Guest property management
          </Typography>
        </Box>

        <Paper elevation={0} sx={{ p: 4, borderRadius: 2, border: 1, borderColor: 'divider' }}>
          <Typography variant="h5" fontWeight={600} gutterBottom>
            {title}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            {subtitle}
          </Typography>
          {children}
        </Paper>
      </Container>
    </Box>
  );
}

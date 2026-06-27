import { Box, Skeleton, Typography, useTheme } from '@mui/material';
import type { ReactNode } from 'react';
import { BaseCard } from './BaseCard';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  loading?: boolean;
}

export function StatCard({ title, value, subtitle, icon, loading }: StatCardProps) {
  const theme = useTheme();

  if (loading) {
    return (
      <BaseCard>
        <Skeleton width="60%" />
        <Skeleton width="40%" height={36} sx={{ mt: 1 }} />
      </BaseCard>
    );
  }

  return (
    <BaseCard
      sx={{
        transition: 'box-shadow 0.2s',
        '&:hover': { boxShadow: theme.shadows[2] ?? theme.shadows[1] },
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 2 }}>
        <Box sx={{ minWidth: 0, flex: 1 }}>
          <Typography variant="body2" color="text.secondary" fontWeight={500}>
            {title}
          </Typography>
          <Typography variant="h5" fontWeight={700} sx={{ mt: 0.5 }} noWrap>
            {value}
          </Typography>
          {subtitle && (
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
              {subtitle}
            </Typography>
          )}
        </Box>
        {icon && (
          <Box
            sx={{
              width: 44,
              height: 44,
              borderRadius: 1.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: 'action.selected',
              color: 'primary.main',
            }}
          >
            {icon}
          </Box>
        )}
      </Box>
    </BaseCard>
  );
}

import { Box, Skeleton } from '@mui/material';
import { BaseCard } from './BaseCard';

interface SkeletonLoaderProps {
  rows?: number;
  variant?: 'card' | 'table' | 'chart' | 'stats';
}

export function SkeletonLoader({ rows = 3, variant = 'card' }: SkeletonLoaderProps) {
  if (variant === 'table') {
    return (
      <BaseCard>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          {Array.from({ length: rows }).map((_, i) => (
            <Skeleton key={i} height={48} variant="rounded" />
          ))}
        </Box>
      </BaseCard>
    );
  }

  if (variant === 'chart') {
    return (
      <BaseCard sx={{ p: 3 }}>
        <Skeleton width="40%" height={24} />
        <Skeleton height={280} variant="rounded" sx={{ mt: 2 }} />
      </BaseCard>
    );
  }

  if (variant === 'stats') {
    return (
      <Box
        sx={{
          display: 'grid',
          gap: 2,
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            xl: 'repeat(3, 1fr)',
          },
        }}
      >
        {Array.from({ length: rows }).map((_, i) => (
          <BaseCard key={i}>
            <Skeleton width="60%" />
            <Skeleton width="40%" height={36} sx={{ mt: 1 }} />
          </BaseCard>
        ))}
      </Box>
    );
  }

  return (
    <Box
      sx={{
        display: 'grid',
        gap: 2,
        gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' },
      }}
    >
      {Array.from({ length: rows }).map((_, i) => (
        <BaseCard key={i}>
          <Skeleton width="60%" />
          <Skeleton width="40%" height={36} sx={{ mt: 1 }} />
        </BaseCard>
      ))}
    </Box>
  );
}

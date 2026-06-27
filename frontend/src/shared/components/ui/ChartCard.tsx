import { Box, Typography } from '@mui/material';
import type { ReactNode } from 'react';
import { BaseCard } from './BaseCard';

interface ChartCardProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
}

export function ChartCard({ title, subtitle, children }: ChartCardProps) {
  return (
    <BaseCard sx={{ p: 3 }}>
      <Typography variant="h6" fontWeight={600}>
        {title}
      </Typography>
      {subtitle && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          {subtitle}
        </Typography>
      )}
      <Box sx={{ mt: 2, height: 280 }}>{children}</Box>
    </BaseCard>
  );
}

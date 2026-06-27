import InboxOutlinedIcon from '@mui/icons-material/InboxOutlined';
import { Box, Typography } from '@mui/material';
import type { ReactNode } from 'react';
import { BaseCard } from './BaseCard';

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: ReactNode;
  action?: ReactNode;
}

export function EmptyState({ title, description, icon, action }: EmptyStateProps) {
  return (
    <BaseCard
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
        px: 3,
        textAlign: 'center',
        borderStyle: 'dashed',
        bgcolor: 'action.hover',
      }}
    >
      <Box
        sx={{
          mb: 2,
          width: 56,
          height: 56,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'action.selected',
          color: 'text.secondary',
        }}
      >
        {icon ?? <InboxOutlinedIcon fontSize="large" />}
      </Box>
      <Typography variant="h6" fontWeight={600}>
        {title}
      </Typography>
      {description && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, maxWidth: 360 }}>
          {description}
        </Typography>
      )}
      {action && <Box sx={{ mt: 2 }}>{action}</Box>}
    </BaseCard>
  );
}

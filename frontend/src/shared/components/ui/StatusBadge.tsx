import { Chip } from '@mui/material';

const colorMap: Record<string, 'success' | 'warning' | 'info' | 'error' | 'default'> = {
  paid: 'success',
  pending: 'warning',
  partial: 'info',
  overdue: 'error',
  occupied: 'success',
  vacant: 'default',
  maintenance: 'warning',
  active: 'success',
  completed: 'default',
  cancelled: 'error',
};

interface StatusBadgeProps {
  status: string;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const key = status.toLowerCase();
  return (
    <Chip
      label={status}
      size="small"
      color={colorMap[key] ?? 'default'}
      sx={{ textTransform: 'capitalize', fontWeight: 500 }}
    />
  );
}

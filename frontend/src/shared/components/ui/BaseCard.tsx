import { Card, type CardProps } from '@mui/material';

export function BaseCard({ children, sx, ...props }: CardProps) {
  return (
    <Card
      elevation={0}
      {...props}
      sx={{
        p: 2,
        borderRadius: 2,
        boxShadow: 1,
        bgcolor: 'background.paper',
        border: 1,
        borderColor: 'divider',
        ...sx,
      }}
    >
      {children}
    </Card>
  );
}

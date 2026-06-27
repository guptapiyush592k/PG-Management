import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import type { ReactNode } from 'react';

interface ModalFormProps {
  open: boolean;
  title: string;
  onClose: () => void;
  onSubmit?: () => void;
  submitLabel?: string;
  loading?: boolean;
  children: ReactNode;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg';
}

export function ModalForm({
  open,
  title,
  onClose,
  onSubmit,
  submitLabel = 'Save',
  loading,
  children,
  maxWidth = 'sm',
}: ModalFormProps) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth={maxWidth} fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', pr: 1 }}>
        {title}
        <IconButton size="small" onClick={onClose} aria-label="close">
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers>{children}</DialogContent>
      {onSubmit && (
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={onClose} color="inherit">
            Cancel
          </Button>
          <Button variant="contained" onClick={onSubmit} disabled={loading}>
            {submitLabel}
          </Button>
        </DialogActions>
      )}
    </Dialog>
  );
}

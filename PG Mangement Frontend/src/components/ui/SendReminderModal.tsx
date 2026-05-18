import { MenuItem, TextField } from '@mui/material';
import { useForm } from 'react-hook-form';
import { ModalForm } from './ModalForm';
import type { Tenant } from '@/types';

interface SendReminderForm {
  tenantId: string;
  message: string;
}

interface SendReminderModalProps {
  open: boolean;
  onClose: () => void;
  tenants: Tenant[];
  onSend: (data: SendReminderForm) => void;
}

export function SendReminderModal({ open, onClose, tenants, onSend }: SendReminderModalProps) {
  const { register, handleSubmit, reset } = useForm<SendReminderForm>({
    defaultValues: { message: 'Hi, this is a friendly reminder that your rent is due soon. Please pay at your earliest convenience.' },
  });

  const submit = handleSubmit((data) => {
    onSend(data);
    reset();
    onClose();
  });

  return (
    <ModalForm open={open} title="Send WhatsApp reminder" onClose={onClose} onSubmit={submit} submitLabel="Send">
      <form className="flex flex-col gap-4 pt-2">
        <TextField select label="Tenant" fullWidth defaultValue="" {...register('tenantId', { required: true })}>
          {tenants.map((t) => (
            <MenuItem key={t.id} value={t.id}>
              {t.name} — {t.phone}
            </MenuItem>
          ))}
        </TextField>
        <TextField label="Message" fullWidth multiline rows={4} {...register('message', { required: true })} />
      </form>
    </ModalForm>
  );
}

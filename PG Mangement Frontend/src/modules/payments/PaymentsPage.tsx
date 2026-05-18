import { useMemo, useState } from 'react';
import { Button, MenuItem, TextField } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useForm } from 'react-hook-form';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatCard } from '@/components/ui/StatCard';
import { DataTable } from '@/components/ui/DataTable';
import { ModalForm } from '@/components/ui/ModalForm';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { formatCurrency, formatDate } from '@/lib/format';
import { useAppDispatch, useAppSelector } from '@/hooks/useAppDispatch';
import { addPayment } from '@/app/slices/pgDataSlice';
import type { Payment, PaymentStatus } from '@/types';

interface PaymentForm {
  tenantName: string;
  amount: number;
  dueDate: string;
  paymentMode: string;
}

export function PaymentsPage() {
  const paymentList = useAppSelector((s) => s.pgData.payments);
  const dispatch = useAppDispatch();
  const [filter, setFilter] = useState<PaymentStatus | 'all'>('all');
  const [modalOpen, setModalOpen] = useState(false);
  const { register, handleSubmit, reset } = useForm<PaymentForm>();

  const filtered = useMemo(
    () => (filter === 'all' ? paymentList : paymentList.filter((p) => p.status === filter)),
    [paymentList, filter]
  );

  const totalCollected = paymentList.filter((p) => p.status === 'paid').reduce((s, p) => s + p.amount, 0);
  const pendingAmount = paymentList.filter((p) => p.status === 'pending' || p.status === 'partial').reduce((s, p) => s + p.amount, 0);
  const overdueAmount = paymentList.filter((p) => p.status === 'overdue').reduce((s, p) => s + p.amount, 0);

  const onSubmit = handleSubmit((data) => {
    dispatch(
      addPayment({
        id: `p${Date.now()}`,
        tenantId: '',
        tenantName: data.tenantName,
        amount: data.amount,
        dueDate: data.dueDate,
        status: 'pending',
        paymentMode: data.paymentMode,
        flatName: '—',
      })
    );
    setModalOpen(false);
  });

  const columns = [
    { id: 'tenantName', label: 'Tenant' },
    { id: 'flatName', label: 'Flat' },
    { id: 'amount', label: 'Amount', render: (r: Payment) => formatCurrency(r.amount) },
    { id: 'dueDate', label: 'Due', render: (r: Payment) => formatDate(r.dueDate) },
    { id: 'paidDate', label: 'Paid', render: (r: Payment) => (r.paidDate ? formatDate(r.paidDate) : '—') },
    { id: 'status', label: 'Status', render: (r: Payment) => <StatusBadge status={r.status} /> },
    { id: 'paymentMode', label: 'Mode', render: (r: Payment) => r.paymentMode ?? '—' },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Payments"
        description="Rent collection and dues tracking"
        actions={
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => { reset(); setModalOpen(true); }}>
            Record payment
          </Button>
        }
      />

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard title="Total collected" value={formatCurrency(totalCollected)} />
        <StatCard title="Pending amount" value={formatCurrency(pendingAmount)} />
        <StatCard title="Overdue amount" value={formatCurrency(overdueAmount)} />
      </div>

      <TextField
        select
        size="small"
        label="Filter by status"
        value={filter}
        onChange={(e) => setFilter(e.target.value as PaymentStatus | 'all')}
        className="w-48"
      >
        <MenuItem value="all">All</MenuItem>
        <MenuItem value="paid">Paid</MenuItem>
        <MenuItem value="pending">Pending</MenuItem>
        <MenuItem value="partial">Partial</MenuItem>
        <MenuItem value="overdue">Overdue</MenuItem>
      </TextField>

      <DataTable columns={columns} rows={filtered} getRowId={(r) => r.id} />

      <ModalForm open={modalOpen} title="Record payment" onClose={() => setModalOpen(false)} onSubmit={onSubmit}>
        <form className="flex flex-col gap-4 pt-2">
          <TextField label="Tenant name" fullWidth {...register('tenantName', { required: true })} />
          <TextField label="Amount" type="number" fullWidth {...register('amount', { valueAsNumber: true })} />
          <TextField label="Due date" type="date" fullWidth InputLabelProps={{ shrink: true }} {...register('dueDate')} />
          <TextField label="Payment mode" fullWidth {...register('paymentMode')} />
        </form>
      </ModalForm>
    </div>
  );
}

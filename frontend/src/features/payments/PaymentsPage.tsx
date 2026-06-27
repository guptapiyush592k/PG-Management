import { useMemo, useState } from 'react';
import { Alert, Box, Button, MenuItem, TextField } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useForm } from 'react-hook-form';
import { PageHeader } from '@/shared/components/ui/PageHeader';
import { StatCard } from '@/shared/components/ui/StatCard';
import { DataTable } from '@/shared/components/ui/DataTable';
import { ModalForm } from '@/shared/components/ui/ModalForm';
import { StatusBadge } from '@/shared/components/ui/StatusBadge';
import { SkeletonLoader } from '@/shared/components/ui/SkeletonLoader';
import { formatCurrency, formatDate, getApiErrorMessage } from '@/shared/utils/format';
import { usePaymentsQuery, usePaymentSummaryQuery, useCreatePaymentMutation, useUpdatePaymentMutation } from '@/shared/hooks/queries/usePayments';
import { useResidentsQuery } from '@/shared/hooks/queries/useResidents';
import { usePermissions } from '@/context/AuthContext';
import type { Payment, PaymentStatus } from '@/shared/types/api.types';

interface PaymentForm {
  resident_id: string;
  amount: number;
  due_date: string;
  payment_mode: string;
}

export function PaymentsPage() {
  const permissions = usePermissions();
  const [filter, setFilter] = useState<PaymentStatus | 'all'>('all');
  const [modalOpen, setModalOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const paymentsQuery = usePaymentsQuery(filter === 'all' ? undefined : { status: filter });
  const summaryQuery = usePaymentSummaryQuery();
  const residentsQuery = useResidentsQuery();
  const createMutation = useCreatePaymentMutation();
  const updateMutation = useUpdatePaymentMutation();

  const { register, handleSubmit, reset } = useForm<PaymentForm>();

  const payments = paymentsQuery.data?.items ?? [];
  const summary = summaryQuery.data;
  const residents = residentsQuery.data?.items ?? [];
  const residentMap = useMemo(
    () => new Map(residents.map((r) => [r.id, r.name])),
    [residents]
  );

  const loading = paymentsQuery.isLoading || summaryQuery.isLoading;

  const onSubmit = handleSubmit(async (data) => {
    setError(null);
    try {
      await createMutation.mutateAsync({
        resident_id: data.resident_id,
        amount: data.amount,
        due_date: data.due_date,
        payment_mode: data.payment_mode || null,
      });
      setModalOpen(false);
      reset();
    } catch (err) {
      setError(getApiErrorMessage(err));
    }
  });

  const markAsPaid = async (payment: Payment) => {
    try {
      await updateMutation.mutateAsync({
        id: payment.id,
        payload: {
          status: 'paid',
          paid_date: new Date().toISOString().slice(0, 10),
        },
      });
    } catch {
      /* handled by query error state */
    }
  };

  const columns = [
    {
      id: 'resident',
      label: 'Resident',
      render: (r: Payment) => residentMap.get(r.resident_id) ?? '—',
    },
    { id: 'amount', label: 'Amount', render: (r: Payment) => formatCurrency(r.amount) },
    { id: 'due_date', label: 'Due', render: (r: Payment) => formatDate(r.due_date) },
    {
      id: 'paid_date',
      label: 'Paid',
      render: (r: Payment) => (r.paid_date ? formatDate(r.paid_date) : '—'),
    },
    { id: 'status', label: 'Status', render: (r: Payment) => <StatusBadge status={r.status} /> },
    { id: 'payment_mode', label: 'Mode', render: (r: Payment) => r.payment_mode ?? '—' },
    ...(permissions?.manage_payments
      ? [
          {
            id: 'actions',
            label: '',
            render: (r: Payment) =>
              r.status !== 'paid' ? (
                <Button size="small" onClick={() => markAsPaid(r)}>
                  Mark paid
                </Button>
              ) : null,
          },
        ]
      : []),
  ];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <PageHeader
        title="Payments"
        description="Rent collection and dues tracking"
        actions={
          permissions?.manage_payments ? (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => {
                reset();
                setError(null);
                setModalOpen(true);
              }}
            >
              Record payment
            </Button>
          ) : undefined
        }
      />

      {loading ? (
        <SkeletonLoader variant="stats" rows={3} />
      ) : (
        <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { sm: 'repeat(3, 1fr)' } }}>
          <StatCard title="Total collected" value={formatCurrency(summary?.total_collected ?? 0)} />
          <StatCard title="Pending amount" value={formatCurrency(summary?.pending_amount ?? 0)} />
          <StatCard title="Overdue amount" value={formatCurrency(summary?.overdue_amount ?? 0)} />
        </Box>
      )}

      <TextField
        select
        size="small"
        label="Filter by status"
        value={filter}
        onChange={(e) => setFilter(e.target.value as PaymentStatus | 'all')}
        sx={{ width: 200 }}
      >
        <MenuItem value="all">All</MenuItem>
        <MenuItem value="paid">Paid</MenuItem>
        <MenuItem value="pending">Pending</MenuItem>
        <MenuItem value="partial">Partial</MenuItem>
        <MenuItem value="overdue">Overdue</MenuItem>
      </TextField>

      {paymentsQuery.isError && (
        <Alert severity="error">Could not load payments. Please try again.</Alert>
      )}

      <DataTable
        columns={columns}
        rows={payments}
        getRowId={(r) => r.id}
        loading={paymentsQuery.isLoading}
        emptyTitle="No payments recorded"
        emptyDescription="Record rent payments to track collection and dues"
        emptyAction={
          permissions?.manage_payments ? (
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => setModalOpen(true)}>
              Record payment
            </Button>
          ) : undefined
        }
      />

      <ModalForm
        open={modalOpen}
        title="Record payment"
        onClose={() => setModalOpen(false)}
        onSubmit={onSubmit}
        loading={createMutation.isPending}
      >
        <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
          {error && <Alert severity="error">{error}</Alert>}
          <TextField select label="Resident" fullWidth {...register('resident_id', { required: true })}>
            {residents.map((r) => (
              <MenuItem key={r.id} value={r.id}>
                {r.name}
              </MenuItem>
            ))}
          </TextField>
          <TextField label="Amount" type="number" fullWidth {...register('amount', { valueAsNumber: true, required: true })} />
          <TextField
            label="Due date"
            type="date"
            fullWidth
            InputLabelProps={{ shrink: true }}
            {...register('due_date', { required: true })}
          />
          <TextField label="Payment mode" placeholder="UPI, Cash, Bank transfer" fullWidth {...register('payment_mode')} />
        </Box>
      </ModalForm>
    </Box>
  );
}

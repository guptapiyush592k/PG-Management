import { useMemo, useState } from 'react';
import {
  Button,
  Drawer,
  IconButton,
  MenuItem,
  Tab,
  Tabs,
  TextField,
  InputAdornment,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import CloseIcon from '@mui/icons-material/Close';
import { useForm } from 'react-hook-form';
import { PageHeader } from '@/components/ui/PageHeader';
import { DataTable } from '@/components/ui/DataTable';
import { ModalForm } from '@/components/ui/ModalForm';
import { formatCurrency, formatDate } from '@/lib/format';
import { useAppDispatch, useAppSelector } from '@/hooks/useAppDispatch';
import { addTenant } from '@/app/slices/pgDataSlice';
import { StatusBadge } from '@/components/ui/StatusBadge';
import type { PaymentStatus, Tenant } from '@/types';

interface TenantForm {
  name: string;
  phone: string;
  aadhaar: string;
  joiningDate: string;
  dueDate: string;
  rentAmount: number;
  deposit: number;
}

export function TenantsPage() {
  const tenantList = useAppSelector((s) => s.pgData.tenants);
  const payments = useAppSelector((s) => s.pgData.payments);
  const beds = useAppSelector((s) => s.pgData.beds);
  const dispatch = useAppDispatch();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<PaymentStatus | 'all'>('all');
  const [modalOpen, setModalOpen] = useState(false);
  const [profile, setProfile] = useState<Tenant | null>(null);
  const [tab, setTab] = useState(0);

  const { register, handleSubmit, reset } = useForm<TenantForm>();

  const filtered = useMemo(() => {
    return tenantList.filter((t) => {
      const matchSearch =
        t.name.toLowerCase().includes(search.toLowerCase()) ||
        t.phone.includes(search) ||
        t.assignedBedLabel.toLowerCase().includes(search.toLowerCase());
      const matchStatus = statusFilter === 'all' || t.paymentStatus === statusFilter;
      return matchSearch && matchStatus;
    });
  }, [tenantList, search, statusFilter]);

  const tenantPayments = profile ? payments.filter((p) => p.tenantId === profile.id) : [];
  const tenantBed = profile ? beds.find((b) => b.id === profile.assignedBedId) : undefined;

  const openAdd = () => {
    reset({
      name: '',
      phone: '',
      aadhaar: '',
      joiningDate: new Date().toISOString().slice(0, 10),
      dueDate: '',
      rentAmount: 8500,
      deposit: 17000,
    });
    setModalOpen(true);
  };

  const onSubmit = handleSubmit((data) => {
    const newTenant: Tenant = {
      id: `t${Date.now()}`,
      ...data,
      assignedBedId: '',
      assignedBedLabel: 'Unassigned',
      flatName: '—',
      paymentStatus: 'pending',
    };
    dispatch(addTenant(newTenant));
    setModalOpen(false);
  });

  const columns = [
    { id: 'name', label: 'Name' },
    { id: 'phone', label: 'Phone' },
    { id: 'assignedBedLabel', label: 'Bed' },
    { id: 'rentAmount', label: 'Rent', render: (r: Tenant) => formatCurrency(r.rentAmount) },
    { id: 'dueDate', label: 'Due', render: (r: Tenant) => formatDate(r.dueDate) },
    { id: 'paymentStatus', label: 'Status', render: (r: Tenant) => <StatusBadge status={r.paymentStatus} /> },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Tenants"
        description="Tenant records and profiles"
        actions={
          <Button variant="contained" startIcon={<AddIcon />} onClick={openAdd}>
            Add tenant
          </Button>
        }
      />

      <div className="flex flex-col gap-3 sm:flex-row">
        <TextField
          size="small"
          placeholder="Search by name, phone, bed..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1"
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
        />
        <TextField
          select
          size="small"
          label="Payment status"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as PaymentStatus | 'all')}
          className="w-full sm:w-48"
        >
          <MenuItem value="all">All</MenuItem>
          <MenuItem value="paid">Paid</MenuItem>
          <MenuItem value="pending">Pending</MenuItem>
          <MenuItem value="partial">Partial</MenuItem>
          <MenuItem value="overdue">Overdue</MenuItem>
        </TextField>
      </div>

      <DataTable
        columns={columns}
        rows={filtered}
        getRowId={(r) => r.id}
        onRowClick={setProfile}
        emptyTitle="No tenants found"
        emptyDescription="Try adjusting your search or filters"
      />

      <ModalForm open={modalOpen} title="Add tenant" onClose={() => setModalOpen(false)} onSubmit={onSubmit}>
        <form className="grid gap-4 pt-2 sm:grid-cols-2">
          <TextField label="Full name" fullWidth {...register('name', { required: true })} />
          <TextField label="Phone" fullWidth {...register('phone', { required: true })} />
          <TextField label="Aadhaar" fullWidth {...register('aadhaar')} />
          <TextField label="Joining date" type="date" fullWidth InputLabelProps={{ shrink: true }} {...register('joiningDate')} />
          <TextField label="Due date" type="date" fullWidth InputLabelProps={{ shrink: true }} {...register('dueDate')} />
          <TextField label="Rent" type="number" fullWidth {...register('rentAmount', { valueAsNumber: true })} />
          <TextField label="Deposit" type="number" fullWidth {...register('deposit', { valueAsNumber: true })} />
        </form>
      </ModalForm>

      <Drawer
        anchor="right"
        open={!!profile}
        onClose={() => setProfile(null)}
        slotProps={{
          paper: {
            sx: {
              width: { xs: '100%', sm: 420 },
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
            },
          },
        }}
      >
        {profile && (
          <div className="flex min-h-0 flex-1 flex-col">
            <div className="flex items-center justify-between border-b border-slate-200 p-4 dark:border-slate-700">
              <h2 className="text-xl font-bold">{profile.name}</h2>
              <IconButton onClick={() => setProfile(null)}><CloseIcon /></IconButton>
            </div>

            <Tabs value={tab} onChange={(_, v) => setTab(v)} className="border-b border-slate-200 px-4 dark:border-slate-700" variant="scrollable">
              <Tab label="Details" />
              <Tab label="Occupancy" />
              <Tab label="Payments" />
              <Tab label="Notes" />
            </Tabs>

            <div className="min-h-0 flex-1 overflow-y-auto p-4">
              {tab === 0 && (
                <dl className="space-y-3 text-sm">
                  <div><dt className="text-slate-500">Phone</dt><dd className="font-medium">{profile.phone}</dd></div>
                  <div><dt className="text-slate-500">Aadhaar</dt><dd>{profile.aadhaar}</dd></div>
                  <div><dt className="text-slate-500">Flat</dt><dd>{profile.flatName}</dd></div>
                  <div><dt className="text-slate-500">Bed</dt><dd>{profile.assignedBedLabel}</dd></div>
                  <div><dt className="text-slate-500">Rent</dt><dd>{formatCurrency(profile.rentAmount)}</dd></div>
                  <div><dt className="text-slate-500">Deposit</dt><dd>{formatCurrency(profile.deposit)}</dd></div>
                  <div><dt className="text-slate-500">Status</dt><dd><StatusBadge status={profile.paymentStatus} /></dd></div>
                  <div><dt className="text-slate-500">Joining</dt><dd>{formatDate(profile.joiningDate)}</dd></div>
                  <div><dt className="text-slate-500">Due date</dt><dd>{formatDate(profile.dueDate)}</dd></div>
                </dl>
              )}
              {tab === 1 && (
                <div className="space-y-3 text-sm">
                  {profile.assignedBedId && tenantBed ? (
                    <>
                      <div className="rounded-lg border border-slate-200 p-4 dark:border-slate-700">
                        <p className="font-semibold text-slate-900 dark:text-white">{tenantBed.bedId}</p>
                        <p className="text-slate-500">{tenantBed.flatName} · Room {tenantBed.roomNumber}</p>
                        <div className="mt-3 flex items-center justify-between">
                          <span className="text-slate-500">Rent</span>
                          <span className="font-medium">{formatCurrency(tenantBed.rentAmount)}</span>
                        </div>
                        <div className="mt-2 flex items-center justify-between">
                          <span className="text-slate-500">Status</span>
                          <StatusBadge status={tenantBed.status} />
                        </div>
                      </div>
                      <p className="text-slate-500">Joined {formatDate(profile.joiningDate)}</p>
                    </>
                  ) : (
                    <p className="text-slate-500">No bed assigned. Assign from the Properties page.</p>
                  )}
                </div>
              )}
              {tab === 2 && (
                <ul className="space-y-3">
                  {tenantPayments.length === 0 ? (
                    <p className="text-sm text-slate-500">No payment history</p>
                  ) : (
                    tenantPayments.map((p) => (
                      <li key={p.id} className="rounded-lg border border-slate-200 p-3 dark:border-slate-700">
                        <div className="flex justify-between">
                          <span className="font-medium">{formatCurrency(p.amount)}</span>
                          <StatusBadge status={p.status} />
                        </div>
                        <p className="text-xs text-slate-500">Due {formatDate(p.dueDate)}{p.paidDate && ` · Paid ${formatDate(p.paidDate)}`}</p>
                      </li>
                    ))
                  )}
                </ul>
              )}
              {tab === 3 && (
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  {profile.notes || 'No notes added for this tenant.'}
                </p>
              )}
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}

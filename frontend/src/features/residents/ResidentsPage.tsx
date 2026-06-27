import { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Drawer,
  IconButton,
  InputAdornment,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import CloseIcon from '@mui/icons-material/Close';
import { useForm } from 'react-hook-form';
import { PageHeader } from '@/shared/components/ui/PageHeader';
import { DataTable } from '@/shared/components/ui/DataTable';
import { ModalForm } from '@/shared/components/ui/ModalForm';
import { StatusBadge } from '@/shared/components/ui/StatusBadge';
import { SkeletonLoader } from '@/shared/components/ui/SkeletonLoader';
import { formatCurrency, formatDate, getApiErrorMessage } from '@/shared/utils/format';
import {
  useResidentsQuery,
  useCreateResidentMutation,
} from '@/shared/hooks/queries/useResidents';
import { usePaymentsQuery } from '@/shared/hooks/queries/usePayments';
import { useBookingsQuery } from '@/shared/hooks/queries/useBookings';
import { useBedsQuery } from '@/shared/hooks/queries/useBeds';
import { useRoomsQuery } from '@/shared/hooks/queries/useRooms';
import { useFlatsQuery } from '@/shared/hooks/queries/useFlats';
import { usePermissions } from '@/context/AuthContext';
import type { Resident } from '@/shared/types/api.types';

interface ResidentForm {
  name: string;
  phone: string;
  email: string;
  aadhaar: string;
  joining_date: string;
  deposit: number;
  notes: string;
}

export function ResidentsPage() {
  const permissions = usePermissions();
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [profile, setProfile] = useState<Resident | null>(null);
  const [tab, setTab] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const residentsQuery = useResidentsQuery(search ? { search } : undefined);
  const createMutation = useCreateResidentMutation();
  const paymentsQuery = usePaymentsQuery(
    profile ? { resident_id: profile.id } : undefined,
    { enabled: !!profile }
  );
  const bookingsQuery = useBookingsQuery({ status: 'active' });
  const bedsQuery = useBedsQuery();
  const roomsQuery = useRoomsQuery();
  const flatsQuery = useFlatsQuery();

  const { register, handleSubmit, reset } = useForm<ResidentForm>();

  const residents = residentsQuery.data?.items ?? [];
  const beds = bedsQuery.data?.items ?? [];
  const rooms = roomsQuery.data?.items ?? [];
  const flats = flatsQuery.data?.items ?? [];
  const bookings = bookingsQuery.data?.items ?? [];
  const residentPayments = paymentsQuery.data?.items ?? [];

  const activeBooking = profile
    ? bookings.find((b) => b.resident_id === profile.id)
    : undefined;
  const assignedBed = activeBooking
    ? beds.find((b) => b.id === activeBooking.bed_id)
    : undefined;
  const assignedRoom = assignedBed
    ? rooms.find((r) => r.id === assignedBed.room_id)
    : undefined;
  const assignedFlat = assignedRoom
    ? flats.find((f) => f.id === assignedRoom.flat_id)
    : undefined;

  const openAdd = () => {
    reset({
      name: '',
      phone: '',
      email: '',
      aadhaar: '',
      joining_date: new Date().toISOString().slice(0, 10),
      deposit: 0,
      notes: '',
    });
    setError(null);
    setModalOpen(true);
  };

  const onSubmit = handleSubmit(async (data) => {
    setError(null);
    try {
      await createMutation.mutateAsync({
        name: data.name,
        phone: data.phone,
        email: data.email || null,
        aadhaar: data.aadhaar || null,
        joining_date: data.joining_date,
        deposit: data.deposit,
        notes: data.notes || null,
      });
      setModalOpen(false);
    } catch (err) {
      setError(getApiErrorMessage(err));
    }
  });

  const columns = [
    { id: 'name', label: 'Name' },
    { id: 'phone', label: 'Phone' },
    {
      id: 'bed',
      label: 'Bed',
      render: (r: Resident) => {
        const booking = bookings.find((b) => b.resident_id === r.id);
        if (!booking) return 'Unassigned';
        const bed = beds.find((b) => b.id === booking.bed_id);
        return bed?.bed_label ?? '—';
      },
    },
    { id: 'joining_date', label: 'Joined', render: (r: Resident) => formatDate(r.joining_date) },
    {
      id: 'deposit',
      label: 'Deposit',
      render: (r: Resident) => formatCurrency(r.deposit),
    },
    {
      id: 'is_active',
      label: 'Status',
      render: (r: Resident) => (
        <StatusBadge status={r.is_active ? 'active' : 'cancelled'} />
      ),
    },
  ];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <PageHeader
        title="Residents"
        description="Resident records and profiles"
        actions={
          permissions?.manage_residents ? (
            <Button variant="contained" startIcon={<AddIcon />} onClick={openAdd}>
              Add resident
            </Button>
          ) : undefined
        }
      />

      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2 }}>
        <TextField
          size="small"
          placeholder="Search by name, phone..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          sx={{ flex: 1 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      {residentsQuery.isError && (
        <Alert severity="error">Could not load residents. Please try again.</Alert>
      )}

      <DataTable
        columns={columns}
        rows={residents}
        getRowId={(r) => r.id}
        onRowClick={setProfile}
        loading={residentsQuery.isLoading || bookingsQuery.isLoading}
        emptyTitle="No residents yet"
        emptyDescription="Add residents to manage bookings and rent payments"
        emptyAction={
          permissions?.manage_residents ? (
            <Button variant="contained" startIcon={<AddIcon />} onClick={openAdd}>
              Add resident
            </Button>
          ) : undefined
        }
      />

      <ModalForm
        open={modalOpen}
        title="Add resident"
        onClose={() => setModalOpen(false)}
        onSubmit={onSubmit}
        loading={createMutation.isPending}
        maxWidth="md"
      >
        <Box
          component="form"
          sx={{
            display: 'grid',
            gap: 2,
            pt: 1,
            gridTemplateColumns: { sm: '1fr 1fr' },
          }}
        >
          {error && (
            <Alert severity="error" sx={{ gridColumn: '1 / -1' }}>
              {error}
            </Alert>
          )}
          <TextField label="Full name" fullWidth {...register('name', { required: true })} />
          <TextField label="Phone" fullWidth {...register('phone', { required: true })} />
          <TextField label="Email" type="email" fullWidth {...register('email')} />
          <TextField label="Aadhaar (12 digits)" fullWidth {...register('aadhaar')} />
          <TextField
            label="Joining date"
            type="date"
            fullWidth
            InputLabelProps={{ shrink: true }}
            {...register('joining_date', { required: true })}
          />
          <TextField
            label="Deposit"
            type="number"
            fullWidth
            {...register('deposit', { valueAsNumber: true })}
          />
          <TextField
            label="Notes"
            fullWidth
            multiline
            rows={2}
            sx={{ gridColumn: '1 / -1' }}
            {...register('notes')}
          />
        </Box>
      </ModalForm>

      <Drawer
        anchor="right"
        open={!!profile}
        onClose={() => setProfile(null)}
        PaperProps={{
          sx: { width: { xs: '100%', sm: 420 }, display: 'flex', flexDirection: 'column' },
        }}
      >
        {profile && (
          <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                p: 2,
                borderBottom: 1,
                borderColor: 'divider',
              }}
            >
              <Typography variant="h6" fontWeight={700}>
                {profile.name}
              </Typography>
              <IconButton onClick={() => setProfile(null)}>
                <CloseIcon />
              </IconButton>
            </Box>

            <Tabs value={tab} onChange={(_, v) => setTab(v)} variant="scrollable" sx={{ px: 2, borderBottom: 1, borderColor: 'divider' }}>
              <Tab label="Details" />
              <Tab label="Occupancy" />
              <Tab label="Payments" />
            </Tabs>

            <Box sx={{ flex: 1, overflowY: 'auto', p: 2 }}>
              {tab === 0 && (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {[
                    ['Phone', profile.phone],
                    ['Email', profile.email ?? '—'],
                    ['Aadhaar', profile.aadhaar ?? '—'],
                    ['Deposit', formatCurrency(profile.deposit)],
                    ['Joined', formatDate(profile.joining_date)],
                  ].map(([label, value]) => (
                    <Box key={label}>
                      <Typography variant="caption" color="text.secondary">
                        {label}
                      </Typography>
                      <Typography fontWeight={500}>{value}</Typography>
                    </Box>
                  ))}
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Status
                    </Typography>
                    <Box sx={{ mt: 0.5 }}>
                      <StatusBadge status={profile.is_active ? 'active' : 'cancelled'} />
                    </Box>
                  </Box>
                  {profile.notes && (
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Notes
                      </Typography>
                      <Typography>{profile.notes}</Typography>
                    </Box>
                  )}
                </Box>
              )}

              {tab === 1 && (
                assignedBed ? (
                  <Box sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 2 }}>
                    <Typography fontWeight={600}>{assignedBed.bed_label}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {assignedFlat?.name} · Room {assignedRoom?.room_number}
                    </Typography>
                    <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">
                        Rent
                      </Typography>
                      <Typography fontWeight={500}>{formatCurrency(assignedBed.rent_amount)}</Typography>
                    </Box>
                    <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" color="text.secondary">
                        Status
                      </Typography>
                      <StatusBadge status={assignedBed.status} />
                    </Box>
                  </Box>
                ) : (
                  <Typography color="text.secondary">
                    No bed assigned. Assign from the Properties page.
                  </Typography>
                )
              )}

              {tab === 2 && (
                paymentsQuery.isLoading ? (
                  <SkeletonLoader variant="table" rows={3} />
                ) : residentPayments.length === 0 ? (
                  <Typography color="text.secondary">No payment history</Typography>
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                    {residentPayments.map((p) => (
                      <Box key={p.id} sx={{ p: 1.5, border: 1, borderColor: 'divider', borderRadius: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography fontWeight={500}>{formatCurrency(p.amount)}</Typography>
                          <StatusBadge status={p.status} />
                        </Box>
                        <Typography variant="caption" color="text.secondary">
                          Due {formatDate(p.due_date)}
                          {p.paid_date && ` · Paid ${formatDate(p.paid_date)}`}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                )
              )}
            </Box>
          </Box>
        )}
      </Drawer>
    </Box>
  );
}

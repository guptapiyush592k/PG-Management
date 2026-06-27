import { useMemo } from 'react';
import HotelIcon from '@mui/icons-material/Hotel';
import PeopleIcon from '@mui/icons-material/People';
import EventAvailableIcon from '@mui/icons-material/EventAvailable';
import PercentIcon from '@mui/icons-material/Percent';
import PendingActionsIcon from '@mui/icons-material/PendingActions';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import { Alert, Box, Typography } from '@mui/material';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { PageHeader } from '@/shared/components/ui/PageHeader';
import { StatCard } from '@/shared/components/ui/StatCard';
import { ChartCard } from '@/shared/components/ui/ChartCard';
import { DataTable } from '@/shared/components/ui/DataTable';
import { StatusBadge } from '@/shared/components/ui/StatusBadge';
import { SkeletonLoader } from '@/shared/components/ui/SkeletonLoader';
import { EmptyState } from '@/shared/components/ui/EmptyState';
import { formatCurrency, formatDate, formatPercent } from '@/shared/utils/format';
import { useBedsQuery } from '@/shared/hooks/queries/useBeds';
import { useFlatsQuery } from '@/shared/hooks/queries/useFlats';
import { useRoomsQuery } from '@/shared/hooks/queries/useRooms';
import { usePaymentsQuery, usePaymentSummaryQuery } from '@/shared/hooks/queries/usePayments';
import { useResidentsQuery } from '@/shared/hooks/queries/useResidents';
import type { Payment } from '@/shared/types/api.types';

export function DashboardPage() {
  const bedsQuery = useBedsQuery();
  const flatsQuery = useFlatsQuery();
  const roomsQuery = useRoomsQuery();
  const paymentsQuery = usePaymentsQuery();
  const summaryQuery = usePaymentSummaryQuery();
  const residentsQuery = useResidentsQuery();

  const loading =
    bedsQuery.isLoading ||
    summaryQuery.isLoading ||
    paymentsQuery.isLoading;

  const beds = bedsQuery.data?.items ?? [];
  const flats = flatsQuery.data?.items ?? [];
  const rooms = roomsQuery.data?.items ?? [];
  const payments = paymentsQuery.data?.items ?? [];
  const residents = residentsQuery.data?.items ?? [];
  const summary = summaryQuery.data;

  const stats = useMemo(() => {
    const totalBeds = beds.length;
    const occupiedBeds = beds.filter((b) => b.status === 'occupied').length;
    const vacantBeds = beds.filter((b) => b.status === 'vacant').length;
    const occupancyPercent = totalBeds > 0 ? (occupiedBeds / totalBeds) * 100 : 0;
    return { totalBeds, occupiedBeds, vacantBeds, occupancyPercent };
  }, [beds]);

  const flatOccupancy = useMemo(() => {
    return flats.map((flat) => {
      const flatRooms = rooms.filter((r) => r.flat_id === flat.id);
      const flatRoomIds = new Set(flatRooms.map((r) => r.id));
      const flatBeds = beds.filter((b) => flatRoomIds.has(b.room_id));
      return {
        name: flat.name,
        occupied: flatBeds.filter((b) => b.status === 'occupied').length,
        vacant: flatBeds.filter((b) => b.status === 'vacant').length,
      };
    });
  }, [flats, rooms, beds]);

  const residentMap = useMemo(
    () => new Map(residents.map((r) => [r.id, r.name])),
    [residents]
  );

  const recentPayments = useMemo(
    () => payments.filter((p) => p.status === 'paid').slice(0, 5),
    [payments]
  );

  const overduePayments = useMemo(
    () => payments.filter((p) => p.status === 'overdue').slice(0, 5),
    [payments]
  );

  const upcomingDue = useMemo(
    () => payments.filter((p) => p.status === 'pending' || p.status === 'partial').slice(0, 5),
    [payments]
  );

  const paymentColumns = [
    {
      id: 'resident',
      label: 'Resident',
      render: (r: Payment) => residentMap.get(r.resident_id) ?? r.resident_id.slice(0, 8),
    },
    { id: 'amount', label: 'Amount', render: (r: Payment) => formatCurrency(r.amount) },
    {
      id: 'paid_date',
      label: 'Paid',
      render: (r: Payment) => (r.paid_date ? formatDate(r.paid_date) : '—'),
    },
    { id: 'status', label: 'Status', render: (r: Payment) => <StatusBadge status={r.status} /> },
  ];

  if (loading) {
    return (
      <Box>
        <PageHeader title="Dashboard" description="Overview of your PG properties" />
        <SkeletonLoader variant="stats" rows={6} />
        <Box sx={{ mt: 3 }}>
          <SkeletonLoader variant="chart" />
        </Box>
      </Box>
    );
  }

  const hasData = beds.length > 0 || payments.length > 0;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <PageHeader
        title="Dashboard"
        description="Welcome back! Here's what's happening across your properties."
      />

      {(bedsQuery.isError || summaryQuery.isError) && (
        <Alert severity="error">Could not load dashboard data. Please refresh the page.</Alert>
      )}

      <Box
        sx={{
          display: 'grid',
          gap: 2,
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            xl: 'repeat(3, 1fr)',
          },
        }}
      >
        <StatCard title="Total Beds" value={stats.totalBeds} icon={<HotelIcon />} />
        <StatCard title="Occupied" value={stats.occupiedBeds} icon={<PeopleIcon />} />
        <StatCard title="Vacant" value={stats.vacantBeds} icon={<EventAvailableIcon />} />
        <StatCard
          title="Occupancy"
          value={formatPercent(stats.occupancyPercent)}
          icon={<PercentIcon />}
        />
        <StatCard
          title="Pending"
          value={formatCurrency(summary?.pending_amount ?? 0)}
          icon={<PendingActionsIcon />}
        />
        <StatCard
          title="Total Collected"
          value={formatCurrency(summary?.total_collected ?? 0)}
          icon={<AccountBalanceWalletIcon />}
        />
      </Box>

      {!hasData ? (
        <EmptyState
          title="No data yet"
          description="Add properties, beds, and residents to see your dashboard come to life."
        />
      ) : (
        <>
          {flatOccupancy.length > 0 && (
            <ChartCard title="Flat-wise occupancy">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={flatOccupancy}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="occupied" fill="#0c8ee6" name="Occupied" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="vacant" fill="#94a3b8" name="Vacant" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          )}

          <Box sx={{ display: 'grid', gap: 3, gridTemplateColumns: { lg: '1fr 1fr' } }}>
            <Box>
              <Typography variant="h6" fontWeight={600} sx={{ mb: 1.5 }}>
                Recent payments
              </Typography>
              <DataTable
                columns={paymentColumns}
                rows={recentPayments}
                getRowId={(r) => r.id}
                emptyTitle="No recent payments"
                emptyDescription="Paid payments will appear here"
              />
            </Box>
            <Box>
              <Typography variant="h6" fontWeight={600} sx={{ mb: 1.5 }}>
                Overdue payments
              </Typography>
              <DataTable
                columns={paymentColumns}
                rows={overduePayments}
                getRowId={(r) => r.id}
                emptyTitle="No overdue payments"
                emptyDescription="Great — all dues are on track"
              />
            </Box>
          </Box>

          <Box sx={{ p: 2.5, borderRadius: 2, border: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              Upcoming due payments
            </Typography>
            {upcomingDue.length === 0 ? (
              <EmptyState
                title="No upcoming dues"
                description="Pending and partial payments will show here"
              />
            ) : (
              <Box component="ul" sx={{ m: 0, p: 0, listStyle: 'none' }}>
                {upcomingDue.map((p) => (
                  <Box
                    component="li"
                    key={p.id}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      py: 1.5,
                      borderBottom: 1,
                      borderColor: 'divider',
                      '&:last-child': { borderBottom: 0 },
                    }}
                  >
                    <Box>
                      <Typography fontWeight={500}>
                        {residentMap.get(p.resident_id) ?? 'Unknown'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Due {formatDate(p.due_date)}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                      <Typography fontWeight={600}>{formatCurrency(p.amount)}</Typography>
                      <StatusBadge status={p.status} />
                    </Box>
                  </Box>
                ))}
              </Box>
            )}
          </Box>
        </>
      )}
    </Box>
  );
}

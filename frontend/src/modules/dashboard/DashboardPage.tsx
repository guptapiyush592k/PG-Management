import { useMemo } from 'react';
import HotelIcon from '@mui/icons-material/Hotel';
import PeopleIcon from '@mui/icons-material/People';
import EventAvailableIcon from '@mui/icons-material/EventAvailable';
import PercentIcon from '@mui/icons-material/Percent';
import PendingActionsIcon from '@mui/icons-material/PendingActions';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatCard } from '@/components/ui/StatCard';
import { ChartCard } from '@/components/ui/ChartCard';
import { DataTable } from '@/components/ui/DataTable';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { SkeletonLoader } from '@/components/ui/SkeletonLoader';
import { formatCurrency, formatDate, formatPercent } from '@/lib/format';
import { dashboardStats, flatWiseOccupancy, occupancyTrend } from '@/mock-data';
import { useMockFetch } from '@/hooks/useMockFetch';
import { useAppSelector } from '@/hooks/useAppDispatch';
import type { Payment, Tenant } from '@/types';

export function DashboardPage() {
  const pgData = useAppSelector((s) => s.pgData);
  const stats = dashboardStats;
  const { loading } = useMockFetch('dashboard', 600);

  const recentPayments = useMemo(
    () => pgData.payments.filter((p) => p.status === 'paid').slice(0, 5),
    [pgData.payments]
  );
  const overdueTenants = useMemo(
    () => pgData.tenants.filter((t) => t.paymentStatus === 'overdue'),
    [pgData.tenants]
  );
  const upcomingDuePayments = useMemo(
    () => pgData.payments.filter((p) => p.status === 'pending' || p.status === 'partial').slice(0, 5),
    [pgData.payments]
  );

  const paymentColumns = [
    { id: 'tenantName', label: 'Tenant' },
    { id: 'amount', label: 'Amount', render: (r: Payment) => formatCurrency(r.amount) },
    { id: 'paidDate', label: 'Paid', render: (r: Payment) => (r.paidDate ? formatDate(r.paidDate) : '—') },
    { id: 'status', label: 'Status', render: (r: Payment) => <StatusBadge status={r.status} /> },
  ];

  const overdueColumns = [
    { id: 'name', label: 'Tenant' },
    { id: 'flatName', label: 'Flat' },
    { id: 'rentAmount', label: 'Rent', render: (r: Tenant) => formatCurrency(r.rentAmount) },
    { id: 'dueDate', label: 'Due', render: (r: Tenant) => formatDate(r.dueDate) },
    { id: 'paymentStatus', label: 'Status', render: (r: Tenant) => <StatusBadge status={r.paymentStatus} /> },
  ];

  if (loading) {
    return (
      <div>
        <PageHeader title="Dashboard" description="Overview of your PG properties" />
        <SkeletonLoader rows={6} />
        <SkeletonLoader variant="chart" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description="Welcome back! Here's what's happening across your properties."
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6">
        <StatCard title="Total Beds" value={stats.totalBeds} icon={<HotelIcon />} />
        <StatCard title="Occupied" value={stats.occupiedBeds} icon={<PeopleIcon />} trend={{ value: '+3 this month', positive: true }} />
        <StatCard title="Vacant" value={stats.vacantBeds} icon={<EventAvailableIcon />} />
        <StatCard title="Occupancy" value={formatPercent(stats.occupancyPercent)} icon={<PercentIcon />} />
        <StatCard title="Pending" value={formatCurrency(stats.pendingAmount)} icon={<PendingActionsIcon />} />
        <StatCard title="Monthly Collection" value={formatCurrency(stats.monthlyCollection)} icon={<AccountBalanceWalletIcon />} trend={{ value: '+6.2% vs last month', positive: true }} />
      </div>

      <ChartCard title="Occupancy trend" subtitle="Last 6 months">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={occupancyTrend}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-slate-700" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Area type="monotone" dataKey="occupancy" stroke="#0c8ee6" fill="#0c8ee6" fillOpacity={0.15} name="Occupancy %" />
            </AreaChart>
          </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Flat-wise occupancy">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={flatWiseOccupancy}>
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

      <div className="grid gap-4 lg:grid-cols-2">
        <div>
          <h3 className="mb-3 font-semibold text-slate-900 dark:text-white">Recent payments</h3>
          <DataTable columns={paymentColumns} rows={recentPayments} getRowId={(r) => r.id} />
        </div>
        <div>
          <h3 className="mb-3 font-semibold text-slate-900 dark:text-white">Overdue tenants</h3>
          <DataTable columns={overdueColumns} rows={overdueTenants} getRowId={(r) => r.id} emptyTitle="No overdue tenants" />
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
        <h3 className="mb-4 font-semibold text-slate-900 dark:text-white">Upcoming due payments</h3>
        <ul className="divide-y divide-slate-100 dark:divide-slate-700">
          {upcomingDuePayments.map((p) => (
            <li key={p.id} className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
              <div>
                <p className="font-medium text-slate-900 dark:text-white">{p.tenantName}</p>
                <p className="text-sm text-slate-500">{p.flatName} · Due {formatDate(p.dueDate)}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-semibold text-slate-900 dark:text-white">{formatCurrency(p.amount)}</span>
                <StatusBadge status={p.status} />
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

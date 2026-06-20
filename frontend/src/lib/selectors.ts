import type { RootState } from '@/app/store';
import type { DashboardStats } from '@/types';

export const selectDashboardStats = (state: RootState): DashboardStats => {
  const { beds, payments } = state.pgData;
  const totalBeds = beds.length;
  const occupiedBeds = beds.filter((b) => b.status === 'occupied').length;
  const vacantBeds = beds.filter((b) => b.status === 'vacant').length;
  const pendingAmount = payments
    .filter((p) => p.status === 'pending' || p.status === 'partial' || p.status === 'overdue')
    .reduce((s, p) => s + p.amount, 0);
  const monthlyCollection = payments
    .filter((p) => p.status === 'paid')
    .reduce((s, p) => s + p.amount, 0);

  return {
    totalBeds,
    occupiedBeds,
    vacantBeds,
    occupancyPercent: totalBeds ? (occupiedBeds / totalBeds) * 100 : 0,
    pendingAmount,
    monthlyCollection,
  };
};

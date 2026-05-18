import type { ChartDataPoint, DashboardStats } from '@/types';

export const dashboardStats: DashboardStats = {
  totalBeds: 48,
  occupiedBeds: 39,
  vacantBeds: 9,
  occupancyPercent: 81.25,
  pendingAmount: 124500,
  monthlyCollection: 387200,
};

export const occupancyTrend: ChartDataPoint[] = [
  { name: 'Jan', occupancy: 72, revenue: 320000 },
  { name: 'Feb', occupancy: 75, revenue: 335000 },
  { name: 'Mar', occupancy: 78, revenue: 350000 },
  { name: 'Apr', occupancy: 76, revenue: 342000 },
  { name: 'May', occupancy: 80, revenue: 365000 },
  { name: 'Jun', occupancy: 81, revenue: 387200 },
];

export const flatWiseOccupancy: ChartDataPoint[] = [
  { name: 'Sunrise PG', occupied: 14, vacant: 2 },
  { name: 'Green Valley', occupied: 12, vacant: 4 },
  { name: 'City Heights', occupied: 13, vacant: 3 },
];

export const monthlyRevenue: ChartDataPoint[] = [
  { name: 'Jan', revenue: 320000 },
  { name: 'Feb', revenue: 335000 },
  { name: 'Mar', revenue: 350000 },
  { name: 'Apr', revenue: 342000 },
  { name: 'May', revenue: 365000 },
  { name: 'Jun', revenue: 387200 },
];


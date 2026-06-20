export {
  dashboardStats,
  occupancyTrend,
  flatWiseOccupancy,
  monthlyRevenue,
} from './dashboard';

export { flats, rooms, beds, tenants, payments } from './entities';

import { payments } from './entities';
import { tenants } from './entities';

export const upcomingDuePayments = payments
  .filter((p) => p.status === 'pending' || p.status === 'partial')
  .slice(0, 5);

export const overdueTenants = tenants.filter((t) => t.paymentStatus === 'overdue');

export const recentPayments = payments.filter((p) => p.status === 'paid').slice(0, 5);

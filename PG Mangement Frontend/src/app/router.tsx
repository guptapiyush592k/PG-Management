import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { DashboardPage } from '@/modules/dashboard/DashboardPage';
import { PropertiesPage } from '@/modules/properties/PropertiesPage';
import { TenantsPage } from '@/modules/tenants/TenantsPage';
import { PaymentsPage } from '@/modules/payments/PaymentsPage';
export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'properties', element: <PropertiesPage /> },
      { path: 'flats', element: <Navigate to="/properties" replace /> },
      { path: 'rooms', element: <Navigate to="/properties" replace /> },
      { path: 'beds', element: <Navigate to="/properties" replace /> },
      { path: 'tenants', element: <TenantsPage /> },
      { path: 'payments', element: <PaymentsPage /> },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
]);

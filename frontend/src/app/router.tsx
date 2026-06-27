import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppLayout } from '@/shared/components/layout/AppLayout';
import { ProtectedRoute, PublicRoute } from '@/shared/components/layout/ProtectedRoute';
import { LoginPage } from '@/features/auth/LoginPage';
import { SignupPage } from '@/features/auth/SignupPage';
import { DashboardPage } from '@/features/dashboard/DashboardPage';
import { PropertiesPage } from '@/features/properties/PropertiesPage';
import { ResidentsPage } from '@/features/residents/ResidentsPage';
import { PaymentsPage } from '@/features/payments/PaymentsPage';

export const router = createBrowserRouter([
  {
    element: <PublicRoute />,
    children: [
      { path: '/login', element: <LoginPage /> },
      { path: '/signup', element: <SignupPage /> },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        path: '/',
        element: <AppLayout />,
        children: [
          { index: true, element: <DashboardPage /> },
          { path: 'properties', element: <PropertiesPage /> },
          { path: 'residents', element: <ResidentsPage /> },
          { path: 'payments', element: <PaymentsPage /> },
          { path: 'flats', element: <Navigate to="/properties" replace /> },
          { path: 'rooms', element: <Navigate to="/properties" replace /> },
          { path: 'beds', element: <Navigate to="/properties" replace /> },
          { path: 'tenants', element: <Navigate to="/residents" replace /> },
          { path: '*', element: <Navigate to="/" replace /> },
        ],
      },
    ],
  },
]);

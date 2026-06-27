import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Provider } from 'react-redux';
import { useMemo } from 'react';
import { store } from './store';
import { createAppTheme } from '@/shared/utils/theme';
import { useAppSelector } from '@/shared/hooks/useAppDispatch';
import { AuthProvider } from '@/context/AuthContext';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: (failureCount, error) => {
        const status = (error as { response?: { status?: number } })?.response?.status;
        if (status && status >= 400 && status < 500) return false;
        return failureCount < 2;
      },
    },
    mutations: { retry: false },
  },
});

function MuiThemeWrapper({ children }: { children: React.ReactNode }) {
  const themeMode = useAppSelector((s) => s.ui.theme);
  const theme = useMemo(() => createAppTheme(themeMode), [themeMode]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <Provider store={store}>
        <MuiThemeWrapper>
          <AuthProvider>{children}</AuthProvider>
        </MuiThemeWrapper>
      </Provider>
    </QueryClientProvider>
  );
}

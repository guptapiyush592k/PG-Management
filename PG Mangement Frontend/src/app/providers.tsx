import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Provider } from 'react-redux';
import { useMemo } from 'react';
import { store } from './store';
import { createAppTheme } from '@/lib/theme';
import { useAppSelector } from '@/hooks/useAppDispatch';

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
    <Provider store={store}>
      <MuiThemeWrapper>{children}</MuiThemeWrapper>
    </Provider>
  );
}

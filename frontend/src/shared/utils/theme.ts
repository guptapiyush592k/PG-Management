import { createTheme, type Theme } from '@mui/material/styles';

export function createAppTheme(mode: 'light' | 'dark'): Theme {
  return createTheme({
    palette: {
      mode,
      primary: {
        main: '#0c8ee6',
        dark: '#0070c4',
        light: '#36aaf5',
        contrastText: '#ffffff',
      },
      success: {
        main: '#059669',
        light: mode === 'light' ? '#d1fae5' : '#064e3b',
      },
      warning: {
        main: '#d97706',
        light: mode === 'light' ? '#fef3c7' : '#78350f',
      },
      error: {
        main: '#dc2626',
        light: mode === 'light' ? '#fee2e2' : '#7f1d1d',
      },
      background: {
        default: mode === 'light' ? '#f8fafc' : '#0f172a',
        paper: mode === 'light' ? '#ffffff' : '#1e293b',
      },
      divider: mode === 'light' ? '#e2e8f0' : '#334155',
      text: {
        primary: mode === 'light' ? '#0f172a' : '#f1f5f9',
        secondary: mode === 'light' ? '#64748b' : '#94a3b8',
      },
    },
    shape: { borderRadius: 10 },
    spacing: 8,
    typography: {
      fontFamily: '"Inter", system-ui, sans-serif',
      h1: { fontSize: '1.75rem', fontWeight: 700 },
      h2: { fontSize: '1.25rem', fontWeight: 600 },
      body2: { fontSize: '0.875rem' },
    },
    shadows: [
      'none',
      mode === 'light' ? '0 1px 3px rgba(15,23,42,0.08)' : '0 1px 3px rgba(0,0,0,0.3)',
      ...Array(23).fill('none'),
    ] as Theme['shadows'],
    components: {
      MuiButton: {
        styleOverrides: {
          root: { textTransform: 'none', fontWeight: 600, borderRadius: 8 },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: { borderRadius: 12 },
        },
      },
      MuiDialog: {
        styleOverrides: {
          paper: { borderRadius: 12 },
        },
      },
      MuiTableCell: {
        styleOverrides: {
          head: { fontWeight: 600 },
        },
      },
    },
  });
}

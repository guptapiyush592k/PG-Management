import {
  AppBar,
  Avatar,
  Box,
  IconButton,
  Toolbar,
  Tooltip,
  Typography,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import DarkModeOutlinedIcon from '@mui/icons-material/DarkModeOutlined';
import LightModeOutlinedIcon from '@mui/icons-material/LightModeOutlined';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import { useAppDispatch, useAppSelector } from '@/shared/hooks/useAppDispatch';
import { setTheme, toggleMobileSidebar } from '@/app/store';
import { useAuth } from '@/context/AuthContext';
import type { ThemeMode } from '@/shared/types/api.types';

export function TopNavbar() {
  const dispatch = useAppDispatch();
  const themeMode = useAppSelector((s) => s.ui.theme);
  const { context, logout } = useAuth();

  const toggleTheme = () => {
    const next: ThemeMode = themeMode === 'light' ? 'dark' : 'light';
    dispatch(setTheme(next));
  };

  const initials = context?.user.name
    ?.split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase() ?? '?';

  return (
    <AppBar
      position="sticky"
      elevation={0}
      color="inherit"
      sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}
    >
      <Toolbar sx={{ gap: 2, px: { xs: 2, lg: 3 } }}>
        <IconButton
          edge="start"
          sx={{ display: { lg: 'none' } }}
          onClick={() => dispatch(toggleMobileSidebar())}
          aria-label="open menu"
        >
          <MenuIcon />
        </IconButton>

        <Box sx={{ flex: 1 }} />

        <Tooltip title={themeMode === 'light' ? 'Dark mode' : 'Light mode'}>
          <IconButton onClick={toggleTheme} size="small">
            {themeMode === 'light' ? <DarkModeOutlinedIcon /> : <LightModeOutlinedIcon />}
          </IconButton>
        </Tooltip>

        <Tooltip title="Logout">
          <IconButton onClick={() => logout()} size="small">
            <LogoutOutlinedIcon />
          </IconButton>
        </Tooltip>

        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            border: 1,
            borderColor: 'divider',
            borderRadius: 1.5,
            px: 1,
            py: 0.5,
          }}
        >
          <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main', fontSize: 14 }}>
            {initials}
          </Avatar>
          <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
            <Typography variant="body2" fontWeight={600} lineHeight={1.2}>
              {context?.user.name ?? 'User'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {context?.user.email}
            </Typography>
          </Box>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

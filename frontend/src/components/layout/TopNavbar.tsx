import {
  AppBar,
  Avatar,
  IconButton,
  InputAdornment,
  TextField,
  Toolbar,
  Tooltip,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import SearchIcon from '@mui/icons-material/Search';
import DarkModeOutlinedIcon from '@mui/icons-material/DarkModeOutlined';
import LightModeOutlinedIcon from '@mui/icons-material/LightModeOutlined';
import { useAppDispatch, useAppSelector } from '@/hooks/useAppDispatch';
import { setTheme, toggleMobileSidebar } from '@/app/store';
import type { ThemeMode } from '@/types';

export function TopNavbar() {
  const dispatch = useAppDispatch();
  const theme = useAppSelector((s) => s.ui.theme);

  const toggleTheme = () => {
    const next: ThemeMode = theme === 'light' ? 'dark' : 'light';
    dispatch(setTheme(next));
  };

  return (
    <AppBar
      position="sticky"
      elevation={0}
      color="inherit"
      className="border-b border-slate-200 bg-white/80 backdrop-blur-md dark:border-slate-700 dark:bg-slate-900/80"
    >
      <Toolbar className="gap-3 px-4 lg:px-6">
        <IconButton
          edge="start"
          className="lg:hidden"
          onClick={() => dispatch(toggleMobileSidebar())}
          aria-label="open menu"
        >
          <MenuIcon />
        </IconButton>

        <TextField
          size="small"
          placeholder="Search tenants, beds, payments..."
          className="hidden max-w-md flex-1 sm:block"
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" className="text-slate-400" />
              </InputAdornment>
            ),
            className: 'rounded-lg bg-slate-50 dark:bg-slate-800',
          }}
        />

        <div className="ml-auto flex items-center gap-1">
          <Tooltip title={theme === 'light' ? 'Dark mode' : 'Light mode'}>
            <IconButton onClick={toggleTheme} size="small">
              {theme === 'light' ? <DarkModeOutlinedIcon /> : <LightModeOutlinedIcon />}
            </IconButton>
          </Tooltip>

          <div className="ml-2 flex items-center gap-2 rounded-lg border border-slate-200 px-2 py-1 dark:border-slate-700">
            <Avatar sx={{ width: 32, height: 32, bgcolor: '#0c8ee6', fontSize: 14 }}>RK</Avatar>
            <div className="hidden sm:block">
              <p className="text-sm font-medium leading-tight text-slate-900 dark:text-white">Rajesh Kumar</p>
              <p className="text-xs text-slate-500">PG Owner</p>
            </div>
          </div>
        </div>
      </Toolbar>
    </AppBar>
  );
}

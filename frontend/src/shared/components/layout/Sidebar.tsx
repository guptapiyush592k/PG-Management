import { NavLink } from 'react-router-dom';
import {
  Apartment,
  ChevronLeft,
  ChevronRight,
  Dashboard,
  HomeWork,
  Payment,
  People,
} from '@mui/icons-material';
import { Box, IconButton, Typography } from '@mui/material';
import { useAppDispatch, useAppSelector } from '@/shared/hooks/useAppDispatch';
import { setMobileSidebarOpen, toggleSidebar } from '@/app/store';
import { useAuth } from '@/context/AuthContext';

const navItems = [
  { path: '/', label: 'Dashboard', icon: Dashboard },
  { path: '/properties', label: 'Properties', icon: HomeWork },
  { path: '/residents', label: 'Residents', icon: People },
  { path: '/payments', label: 'Payments', icon: Payment },
];

interface SidebarProps {
  mobile?: boolean;
}

export function Sidebar({ mobile }: SidebarProps) {
  const dispatch = useAppDispatch();
  const collapsed = useAppSelector((s) => s.ui.sidebarCollapsed);
  const { context } = useAuth();
  const showLabels = mobile || !collapsed;
  const width = collapsed && !mobile ? 72 : 256;

  return (
    <Box
      component="aside"
      sx={{
        width,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderRight: 1,
        borderColor: 'divider',
        bgcolor: 'background.paper',
        transition: 'width 0.3s',
      }}
    >
      <Box
        sx={{
          height: 64,
          px: 2,
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Box
          sx={{
            width: 36,
            height: 36,
            borderRadius: 1.5,
            bgcolor: 'primary.main',
            color: 'primary.contrastText',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <Apartment fontSize="small" />
        </Box>
        {showLabels && (
          <Box sx={{ minWidth: 0 }}>
            <Typography variant="subtitle2" fontWeight={700} noWrap>
              {context?.tenant.name ?? 'PG Manager'}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap>
              Admin Dashboard
            </Typography>
          </Box>
        )}
      </Box>

      <Box component="nav" sx={{ flex: 1, p: 1.5, overflowY: 'auto' }}>
        {navItems.map(({ path, label, icon: Icon }) => (
          <Box
            key={path}
            component={NavLink}
            to={path}
            end={path === '/'}
            onClick={() => mobile && dispatch(setMobileSidebarOpen(false))}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
              px: 1.5,
              py: 1.25,
              mb: 0.5,
              borderRadius: 1.5,
              textDecoration: 'none',
              fontSize: '0.875rem',
              fontWeight: 500,
              color: 'text.secondary',
              '&.active': {
                bgcolor: 'action.selected',
                color: 'primary.main',
              },
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          >
            <Icon fontSize="small" sx={{ flexShrink: 0 }} />
            {showLabels && <span>{label}</span>}
          </Box>
        ))}
      </Box>

      {!mobile && (
        <IconButton
          onClick={() => dispatch(toggleSidebar())}
          sx={{ m: 1.5, border: 1, borderColor: 'divider', borderRadius: 1.5 }}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight fontSize="small" /> : <ChevronLeft fontSize="small" />}
        </IconButton>
      )}
    </Box>
  );
}

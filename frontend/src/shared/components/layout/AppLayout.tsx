import { Drawer } from '@mui/material';
import { Box } from '@mui/material';
import { Outlet } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '@/shared/hooks/useAppDispatch';
import { setMobileSidebarOpen } from '@/app/store';
import { Sidebar } from './Sidebar';
import { TopNavbar } from './TopNavbar';

export function AppLayout() {
  const dispatch = useAppDispatch();
  const mobileOpen = useAppSelector((s) => s.ui.mobileSidebarOpen);
  const collapsed = useAppSelector((s) => s.ui.sidebarCollapsed);
  const sidebarWidth = collapsed ? 72 : 256;

  return (
    <Box sx={{ height: '100vh', overflow: 'hidden', bgcolor: 'background.default' }}>
      <Box sx={{ position: 'fixed', inset: 0, left: 0, width: sidebarWidth, zIndex: 30, display: { xs: 'none', lg: 'block' } }}>
        <Sidebar />
      </Box>

      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={() => dispatch(setMobileSidebarOpen(false))}
        ModalProps={{ keepMounted: true }}
        sx={{ display: { lg: 'none' }, '& .MuiDrawer-paper': { width: 256 } }}
      >
        <Sidebar mobile />
      </Drawer>

      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
          minWidth: 0,
          pl: { lg: `${sidebarWidth}px` },
          transition: 'padding-left 0.3s',
        }}
      >
        <TopNavbar />
        <Box component="main" sx={{ flex: 1, minHeight: 0, overflowY: 'auto', p: { xs: 2, lg: 3 } }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}

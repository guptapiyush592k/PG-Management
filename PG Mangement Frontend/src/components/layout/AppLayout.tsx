import { Drawer } from '@mui/material';
import { Outlet } from 'react-router-dom';
import { cn } from '@/lib/format';
import { useAppDispatch, useAppSelector } from '@/hooks/useAppDispatch';
import { setMobileSidebarOpen } from '@/app/store';
import { Sidebar } from './Sidebar';
import { TopNavbar } from './TopNavbar';

export function AppLayout() {
  const dispatch = useAppDispatch();
  const mobileOpen = useAppSelector((s) => s.ui.mobileSidebarOpen);
  const collapsed = useAppSelector((s) => s.ui.sidebarCollapsed);

  const sidebarWidth = collapsed ? 'lg:pl-[72px]' : 'lg:pl-64';

  return (
    <div className="h-dvh overflow-hidden bg-slate-50 dark:bg-slate-950">
      <div className="fixed inset-y-0 left-0 z-30 hidden lg:block">
        <Sidebar />
      </div>

      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={() => dispatch(setMobileSidebarOpen(false))}
        ModalProps={{ keepMounted: true }}
        sx={{ display: { lg: 'none' }, '& .MuiDrawer-paper': { width: 256 } }}
      >
        <Sidebar mobile />
      </Drawer>

      <div
        className={cn(
          'flex h-dvh min-w-0 flex-col overflow-hidden transition-[padding] duration-300',
          sidebarWidth
        )}
      >
        <TopNavbar />
        <main className="flex-1 min-h-0 overflow-y-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

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
import { cn } from '@/lib/format';
import { useAppDispatch, useAppSelector } from '@/hooks/useAppDispatch';
import { setMobileSidebarOpen, toggleSidebar } from '@/app/store';

const navItems = [
  { path: '/', label: 'Dashboard', icon: Dashboard },
  { path: '/properties', label: 'Properties', icon: HomeWork },
  { path: '/tenants', label: 'Tenants', icon: People },
  { path: '/payments', label: 'Payments', icon: Payment },
];

interface SidebarProps {
  mobile?: boolean;
}

export function Sidebar({ mobile }: SidebarProps) {
  const dispatch = useAppDispatch();
  const collapsed = useAppSelector((s) => s.ui.sidebarCollapsed);

  const width = collapsed && !mobile ? 'w-[72px]' : 'w-64';

  return (
    <aside
      className={cn(
        'flex h-full flex-col border-r border-slate-200 bg-white transition-all duration-300 dark:border-slate-700 dark:bg-slate-900',
        width,
        mobile ? 'w-64' : 'hidden lg:flex'
      )}
    >
      <div className="flex h-16 items-center gap-2 border-b border-slate-200 px-4 dark:border-slate-700">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-600 text-white">
          <Apartment fontSize="small" />
        </div>
        {(!collapsed || mobile) && (
          <div className="min-w-0">
            <p className="truncate font-bold text-slate-900 dark:text-white">PG Manager</p>
            <p className="truncate text-xs text-slate-500">Admin Dashboard</p>
          </div>
        )}
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-3 scrollbar-thin">
        {navItems.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            end={path === '/'}
            onClick={() => mobile && dispatch(setMobileSidebarOpen(false))}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-300'
                  : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'
              )
            }
          >
            <Icon fontSize="small" className="shrink-0" />
            {(!collapsed || mobile) && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {!mobile && (
        <button
          type="button"
          onClick={() => dispatch(toggleSidebar())}
          className="m-3 flex items-center justify-center rounded-lg border border-slate-200 py-2 text-slate-500 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight fontSize="small" /> : <ChevronLeft fontSize="small" />}
        </button>
      )}
    </aside>
  );
}

import type { ReactNode } from 'react';
import { Skeleton } from '@mui/material';
import { cn } from '@/lib/format';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  trend?: { value: string; positive?: boolean };
  loading?: boolean;
  className?: string;
}

export function StatCard({ title, value, subtitle, icon, trend, loading, className }: StatCardProps) {
  if (loading) {
    return (
      <div className={cn('rounded-xl border border-slate-200 bg-white p-5 shadow-card dark:border-slate-700 dark:bg-slate-800', className)}>
        <Skeleton width="60%" />
        <Skeleton width="40%" height={36} className="mt-2" />
      </div>
    );
  }

  return (
    <div className={cn(
      'rounded-xl border border-slate-200 bg-white p-5 shadow-card transition-shadow hover:shadow-card-hover dark:border-slate-700 dark:bg-slate-800',
      className
    )}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</p>
          <p className="mt-1 truncate text-2xl font-bold text-slate-900 dark:text-white">{value}</p>
          {subtitle && <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">{subtitle}</p>}
          {trend && (
            <p className={cn('mt-1 text-xs font-medium', trend.positive ? 'text-emerald-600' : 'text-red-600')}>
              {trend.value}
            </p>
          )}
        </div>
        {icon && (
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand-600 dark:bg-brand-950 dark:text-brand-400">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}

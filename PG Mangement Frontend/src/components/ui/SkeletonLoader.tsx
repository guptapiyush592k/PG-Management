import { Skeleton } from '@mui/material';

interface SkeletonLoaderProps {
  rows?: number;
  variant?: 'card' | 'table' | 'chart';
}

export function SkeletonLoader({ rows = 3, variant = 'card' }: SkeletonLoaderProps) {
  if (variant === 'table') {
    return (
      <div className="space-y-2 rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
        {Array.from({ length: rows }).map((_, i) => (
          <Skeleton key={i} height={48} variant="rounded" />
        ))}
      </div>
    );
  }

  if (variant === 'chart') {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <Skeleton width="40%" height={24} />
        <Skeleton height={280} variant="rounded" className="mt-4" />
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
          <Skeleton width="60%" />
          <Skeleton width="40%" height={36} className="mt-2" />
        </div>
      ))}
    </div>
  );
}

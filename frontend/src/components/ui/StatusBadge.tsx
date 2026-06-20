import { cn } from '@/lib/format';

const variants: Record<string, string> = {
  paid: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300',
  pending: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300',
  partial: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300',
  overdue: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300',
  occupied: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300',
  vacant: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-200',
  maintenance: 'bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300',
};

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const key = status.toLowerCase();
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize',
        variants[key] ?? variants.pending,
        className
      )}
    >
      {status}
    </span>
  );
}

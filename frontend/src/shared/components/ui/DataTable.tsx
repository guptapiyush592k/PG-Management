import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import type { ReactNode } from 'react';
import { EmptyState } from './EmptyState';
import { SkeletonLoader } from './SkeletonLoader';

export interface Column<T> {
  id: string;
  label: string;
  minWidth?: number;
  align?: 'left' | 'right' | 'center';
  render?: (row: T) => ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  rows: T[];
  getRowId: (row: T) => string;
  emptyTitle?: string;
  emptyDescription?: string;
  emptyAction?: ReactNode;
  onRowClick?: (row: T) => void;
  loading?: boolean;
}

export function DataTable<T>({
  columns,
  rows,
  getRowId,
  emptyTitle = 'No data found',
  emptyDescription,
  emptyAction,
  onRowClick,
  loading,
}: DataTableProps<T>) {
  if (loading) {
    return <SkeletonLoader variant="table" rows={5} />;
  }

  if (rows.length === 0) {
    return (
      <EmptyState title={emptyTitle} description={emptyDescription} action={emptyAction} />
    );
  }

  return (
    <TableContainer
      component={Paper}
      elevation={0}
      sx={{ borderRadius: 2, border: 1, borderColor: 'divider', overflow: 'hidden' }}
    >
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow sx={{ bgcolor: 'action.hover' }}>
            {columns.map((col) => (
              <TableCell key={col.id} align={col.align} sx={{ minWidth: col.minWidth, fontWeight: 600 }}>
                {col.label}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow
              key={getRowId(row)}
              hover
              onClick={onRowClick ? () => onRowClick(row) : undefined}
              sx={{ cursor: onRowClick ? 'pointer' : 'default' }}
            >
              {columns.map((col) => (
                <TableCell key={col.id} align={col.align}>
                  {col.render
                    ? col.render(row)
                    : String((row as Record<string, unknown>)[col.id] ?? '')}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

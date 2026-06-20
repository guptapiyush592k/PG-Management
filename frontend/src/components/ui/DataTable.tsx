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
  onRowClick?: (row: T) => void;
}

export function DataTable<T>({
  columns,
  rows,
  getRowId,
  emptyTitle = 'No data found',
  emptyDescription,
  onRowClick,
}: DataTableProps<T>) {
  if (rows.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <TableContainer
      component={Paper}
      elevation={0}
      className="overflow-hidden rounded-xl border border-slate-200 dark:border-slate-700"
    >
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow className="bg-slate-50 dark:bg-slate-800/80">
            {columns.map((col) => (
              <TableCell
                key={col.id}
                align={col.align}
                style={{ minWidth: col.minWidth }}
                className="font-semibold text-slate-700 dark:text-slate-200"
              >
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
              className={onRowClick ? 'cursor-pointer' : ''}
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

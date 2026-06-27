export function formatCurrency(amount: number | string): string {
  const value = typeof amount === 'string' ? parseFloat(amount) : amount;
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(value || 0);
}

export function formatDate(date: string): string {
  return new Intl.DateTimeFormat('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date(date));
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function parseDecimal(value: string): number {
  return parseFloat(value) || 0;
}

export function getApiErrorMessage(error: unknown, fallback = 'Something went wrong'): string {
  if (error && typeof error === 'object' && 'response' in error) {
    const axiosError = error as { response?: { data?: { detail?: string } } };
    return axiosError.response?.data?.detail ?? fallback;
  }
  return fallback;
}

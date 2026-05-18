import { useEffect, useState } from 'react';
import { mockDelay } from '@/services/mockApi';

/** Simulates async data loading for skeleton states */
export function useMockFetch<T>(data: T, delayMs = 500) {
  const [result, setResult] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    mockDelay(data, delayMs).then((d) => {
      if (!cancelled) {
        setResult(d);
        setLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [data, delayMs]);

  return { data: result ?? data, loading };
}

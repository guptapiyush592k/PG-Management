export const queryKeys = {
  me: {
    context: ['me', 'context'] as const,
  },
  flats: {
    all: ['flats'] as const,
    list: (params?: Record<string, unknown>) => ['flats', 'list', params] as const,
  },
  rooms: {
    all: ['rooms'] as const,
    list: (params?: Record<string, unknown>) => ['rooms', 'list', params] as const,
  },
  beds: {
    all: ['beds'] as const,
    list: (params?: Record<string, unknown>) => ['beds', 'list', params] as const,
  },
  residents: {
    all: ['residents'] as const,
    list: (params?: Record<string, unknown>) => ['residents', 'list', params] as const,
    detail: (id: string) => ['residents', id] as const,
  },
  payments: {
    all: ['payments'] as const,
    list: (params?: Record<string, unknown>) => ['payments', 'list', params] as const,
    summary: ['payments', 'summary'] as const,
  },
  bookings: {
    all: ['bookings'] as const,
    list: (params?: Record<string, unknown>) => ['bookings', 'list', params] as const,
  },
};

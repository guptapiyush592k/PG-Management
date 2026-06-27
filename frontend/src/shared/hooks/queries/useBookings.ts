import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { DEFAULT_PAGE_SIZE } from '@/shared/constants/api.constants';
import { queryKeys } from '@/shared/constants/queryKeys.constants';
import type { BookingStatus } from '@/shared/types/api.types';
import * as bookingsService from '@/services/bookings.service';
import type { BookingPayload, CheckoutPayload } from '@/services/bookings.service';

export function useBookingsQuery(params?: {
  search?: string;
  resident_id?: string;
  bed_id?: string;
  status?: BookingStatus;
}) {
  return useQuery({
    queryKey: queryKeys.bookings.list(params),
    queryFn: async () => {
      const { data } = await bookingsService.listBookings({
        page: 1,
        page_size: DEFAULT_PAGE_SIZE,
        ...params,
      });
      return data;
    },
  });
}

export function useCreateBookingMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: BookingPayload) =>
      bookingsService.createBooking(payload).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.bookings.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.beds.all });
    },
  });
}

export function useCheckoutBookingMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload?: CheckoutPayload }) =>
      bookingsService.checkoutBooking(id, payload).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.bookings.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.beds.all });
    },
  });
}

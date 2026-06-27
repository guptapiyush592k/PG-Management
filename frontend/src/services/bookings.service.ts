import { apiClient } from './apiClient';
import type { Booking, BookingStatus, ListParams, PaginatedResponse } from '@/shared/types/api.types';

export interface BookingPayload {
  resident_id: string;
  bed_id: string;
  start_date: string;
}

export interface CheckoutPayload {
  end_date?: string;
}

export const listBookings = (
  params?: ListParams & { resident_id?: string; bed_id?: string; status?: BookingStatus }
) => apiClient.get<PaginatedResponse<Booking>>('/api/v1/bookings', { params });

export const createBooking = (payload: BookingPayload) =>
  apiClient.post<Booking>('/api/v1/bookings', payload);

export const checkoutBooking = (id: string, payload?: CheckoutPayload) =>
  apiClient.post<Booking>(`/api/v1/bookings/${id}/checkout`, payload ?? {});

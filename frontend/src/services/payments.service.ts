import { apiClient } from './apiClient';
import type {
  ListParams,
  PaginatedResponse,
  Payment,
  PaymentStatus,
  PaymentSummary,
} from '@/shared/types/api.types';

export interface PaymentPayload {
  resident_id: string;
  booking_id?: string | null;
  amount: number;
  due_date: string;
  paid_date?: string | null;
  status?: PaymentStatus;
  payment_mode?: string | null;
  notes?: string | null;
}

export interface PaymentUpdatePayload {
  resident_id?: string;
  booking_id?: string | null;
  amount?: number;
  due_date?: string;
  paid_date?: string | null;
  status?: PaymentStatus;
  payment_mode?: string | null;
  notes?: string | null;
}

export const listPayments = (params?: ListParams & { resident_id?: string; status?: PaymentStatus }) =>
  apiClient.get<PaginatedResponse<Payment>>('/api/v1/payments', { params });

export const getPaymentSummary = () =>
  apiClient.get<PaymentSummary>('/api/v1/payments/summary');

export const createPayment = (payload: PaymentPayload) =>
  apiClient.post<Payment>('/api/v1/payments', payload);

export const updatePayment = (id: string, payload: PaymentUpdatePayload) =>
  apiClient.patch<Payment>(`/api/v1/payments/${id}`, payload);

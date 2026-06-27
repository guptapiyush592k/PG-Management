import { apiClient } from './apiClient';
import type { ListParams, PaginatedResponse, Resident } from '@/shared/types/api.types';

export interface ResidentPayload {
  name: string;
  phone: string;
  email?: string | null;
  aadhaar?: string | null;
  joining_date: string;
  deposit?: number;
  notes?: string | null;
  is_active?: boolean;
}

export interface ResidentUpdatePayload {
  name?: string;
  phone?: string;
  email?: string | null;
  aadhaar?: string | null;
  joining_date?: string;
  deposit?: number;
  notes?: string | null;
  is_active?: boolean;
}

export const listResidents = (params?: ListParams & { is_active?: boolean }) =>
  apiClient.get<PaginatedResponse<Resident>>('/api/v1/residents', { params });

export const getResident = (id: string) =>
  apiClient.get<Resident>(`/api/v1/residents/${id}`);

export const createResident = (payload: ResidentPayload) =>
  apiClient.post<Resident>('/api/v1/residents', payload);

export const updateResident = (id: string, payload: ResidentUpdatePayload) =>
  apiClient.patch<Resident>(`/api/v1/residents/${id}`, payload);

export const deleteResident = (id: string) => apiClient.delete(`/api/v1/residents/${id}`);

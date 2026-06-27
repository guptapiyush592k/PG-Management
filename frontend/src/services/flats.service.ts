import { apiClient } from './apiClient';
import type { Flat, ListParams, PaginatedResponse } from '@/shared/types/api.types';

export interface FlatPayload {
  name: string;
  address: string;
  is_active?: boolean;
}

export interface FlatUpdatePayload {
  name?: string;
  address?: string;
  is_active?: boolean;
}

export const listFlats = (params?: ListParams & { is_active?: boolean }) =>
  apiClient.get<PaginatedResponse<Flat>>('/api/v1/flats', { params });

export const getFlat = (id: string) => apiClient.get<Flat>(`/api/v1/flats/${id}`);

export const createFlat = (payload: FlatPayload) =>
  apiClient.post<Flat>('/api/v1/flats', payload);

export const updateFlat = (id: string, payload: FlatUpdatePayload) =>
  apiClient.patch<Flat>(`/api/v1/flats/${id}`, payload);

export const deleteFlat = (id: string) => apiClient.delete(`/api/v1/flats/${id}`);

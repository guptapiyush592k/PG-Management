import { apiClient } from './apiClient';
import type { Bed, BedStatus, ListParams, PaginatedResponse } from '@/shared/types/api.types';

export interface BedPayload {
  room_id: string;
  bed_label: string;
  rent_amount: number;
  status?: BedStatus;
}

export interface BedUpdatePayload {
  room_id?: string;
  bed_label?: string;
  rent_amount?: number;
  status?: BedStatus;
}

export const listBeds = (params?: ListParams & { room_id?: string; status?: BedStatus }) =>
  apiClient.get<PaginatedResponse<Bed>>('/api/v1/beds', { params });

export const createBed = (payload: BedPayload) =>
  apiClient.post<Bed>('/api/v1/beds', payload);

export const updateBed = (id: string, payload: BedUpdatePayload) =>
  apiClient.patch<Bed>(`/api/v1/beds/${id}`, payload);

export const deleteBed = (id: string) => apiClient.delete(`/api/v1/beds/${id}`);

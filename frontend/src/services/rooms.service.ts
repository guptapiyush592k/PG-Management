import { apiClient } from './apiClient';
import type { ListParams, PaginatedResponse, Room } from '@/shared/types/api.types';

export interface RoomPayload {
  flat_id: string;
  room_number: string;
}

export interface RoomUpdatePayload {
  flat_id?: string;
  room_number?: string;
}

export const listRooms = (params?: ListParams & { flat_id?: string }) =>
  apiClient.get<PaginatedResponse<Room>>('/api/v1/rooms', { params });

export const createRoom = (payload: RoomPayload) =>
  apiClient.post<Room>('/api/v1/rooms', payload);

export const updateRoom = (id: string, payload: RoomUpdatePayload) =>
  apiClient.patch<Room>(`/api/v1/rooms/${id}`, payload);

export const deleteRoom = (id: string) => apiClient.delete(`/api/v1/rooms/${id}`);

import { apiClient } from './apiClient';
import type { TokenResponse } from '@/shared/types/api.types';

export interface LoginPayload {
  email: string;
  password: string;
  tenant_id?: string;
}

export interface SignupPayload {
  full_name: string;
  email: string;
  password: string;
}

export const login = (payload: LoginPayload) =>
  apiClient.post<TokenResponse>('/auth/login', payload);

export const signup = (payload: SignupPayload) =>
  apiClient.post<TokenResponse>('/auth/signup', payload);

export const logout = (refreshToken: string) =>
  apiClient.post<{ message: string }>('/auth/logout', { refresh_token: refreshToken });

export const refresh = (refreshToken: string) =>
  apiClient.post<TokenResponse>('/auth/refresh', { refresh_token: refreshToken });

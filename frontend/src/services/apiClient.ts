import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { API_BASE_URL } from '@/shared/constants/api.constants';
import { AUTH_STORAGE_KEY } from '@/features/auth/auth.constants';
import type { TokenResponse } from '@/shared/types/api.types';

interface StoredAuth {
  accessToken: string;
  refreshToken: string;
  tenantId: string;
}

export function getStoredAuth(): StoredAuth | null {
  const raw = localStorage.getItem(AUTH_STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredAuth;
  } catch {
    return null;
  }
}

export function setStoredAuth(auth: StoredAuth): void {
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(auth));
}

export function clearStoredAuth(): void {
  localStorage.removeItem(AUTH_STORAGE_KEY);
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const auth = getStoredAuth();
  if (auth?.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`;
  }
  if (auth?.tenantId && config.url?.startsWith('/api/v1')) {
    config.headers['X-Tenant-ID'] = auth.tenantId;
  }
  return config;
});

let refreshPromise: Promise<StoredAuth | null> | null = null;

async function refreshTokens(): Promise<StoredAuth | null> {
  const auth = getStoredAuth();
  if (!auth?.refreshToken) return null;

  try {
    const { data } = await axios.post<TokenResponse>(
      `${API_BASE_URL}/auth/refresh`,
      { refresh_token: auth.refreshToken },
      { headers: { 'Content-Type': 'application/json' } }
    );
    const next: StoredAuth = {
      accessToken: data.access_token,
      refreshToken: data.refresh_token,
      tenantId: data.tenant_id,
    };
    setStoredAuth(next);
    return next;
  } catch {
    clearStoredAuth();
    return null;
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config;
    if (!original || error.response?.status !== 401) {
      return Promise.reject(error);
    }

    if (original.url?.includes('/auth/')) {
      return Promise.reject(error);
    }

    if (!refreshPromise) {
      refreshPromise = refreshTokens().finally(() => {
        refreshPromise = null;
      });
    }

    const auth = await refreshPromise;
    if (!auth) {
      window.dispatchEvent(new Event('auth:logout'));
      return Promise.reject(error);
    }

    original.headers.Authorization = `Bearer ${auth.accessToken}`;
    if (original.url?.startsWith('/api/v1')) {
      original.headers['X-Tenant-ID'] = auth.tenantId;
    }
    return apiClient(original);
  }
);

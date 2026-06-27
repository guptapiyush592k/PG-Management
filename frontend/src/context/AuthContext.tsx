import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { AUTH_STORAGE_KEY } from '@/features/auth/auth.constants';
import { queryKeys } from '@/shared/constants/queryKeys.constants';
import type { MeContext, TokenResponse } from '@/shared/types/api.types';
import { clearStoredAuth, getStoredAuth, setStoredAuth } from '@/services/apiClient';
import * as authService from '@/services/auth.service';
import * as meService from '@/services/me.service';

interface AuthContextValue {
  isAuthenticated: boolean;
  isLoading: boolean;
  context: MeContext | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (fullName: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshContext: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function persistTokens(data: TokenResponse): void {
  setStoredAuth({
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
    tenantId: data.tenant_id,
  });
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [context, setContext] = useState<MeContext | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadContext = useCallback(async () => {
    const auth = getStoredAuth();
    if (!auth?.accessToken) {
      setContext(null);
      return;
    }
    const { data } = await meService.getMeContext();
    setContext(data);
    queryClient.setQueryData(queryKeys.me.context, data);
  }, [queryClient]);

  useEffect(() => {
    const init = async () => {
      try {
        await loadContext();
      } catch {
        clearStoredAuth();
        setContext(null);
      } finally {
        setIsLoading(false);
      }
    };
    init();

    const onLogout = () => {
      clearStoredAuth();
      setContext(null);
      queryClient.clear();
    };
    window.addEventListener('auth:logout', onLogout);
    return () => window.removeEventListener('auth:logout', onLogout);
  }, [loadContext, queryClient]);

  const login = useCallback(
    async (email: string, password: string) => {
      const { data } = await authService.login({ email, password });
      persistTokens(data);
      await loadContext();
    },
    [loadContext]
  );

  const signup = useCallback(
    async (fullName: string, email: string, password: string) => {
      const { data } = await authService.signup({ full_name: fullName, email, password });
      persistTokens(data);
      await loadContext();
    },
    [loadContext]
  );

  const logout = useCallback(async () => {
    const auth = getStoredAuth();
    if (auth?.refreshToken) {
      try {
        await authService.logout(auth.refreshToken);
      } catch {
        /* ignore logout errors */
      }
    }
    clearStoredAuth();
    setContext(null);
    queryClient.clear();
  }, [queryClient]);

  const value = useMemo<AuthContextValue>(
    () => ({
      isAuthenticated: !!getStoredAuth()?.accessToken && !!context,
      isLoading,
      context,
      login,
      signup,
      logout,
      refreshContext: loadContext,
    }),
    [context, isLoading, login, signup, logout, loadContext]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export function usePermissions() {
  return useAuth().context?.permissions;
}

export { AUTH_STORAGE_KEY };

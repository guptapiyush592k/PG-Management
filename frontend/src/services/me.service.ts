import { apiClient } from './apiClient';
import type { MeContext } from '@/shared/types/api.types';

export const getMeContext = () => apiClient.get<MeContext>('/me/context');

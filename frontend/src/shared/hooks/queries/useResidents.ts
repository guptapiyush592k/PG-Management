import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { DEFAULT_PAGE_SIZE } from '@/shared/constants/api.constants';
import { queryKeys } from '@/shared/constants/queryKeys.constants';
import * as residentsService from '@/services/residents.service';
import type { ResidentPayload, ResidentUpdatePayload } from '@/services/residents.service';

export function useResidentsQuery(params?: { search?: string; is_active?: boolean }) {
  return useQuery({
    queryKey: queryKeys.residents.list(params),
    queryFn: async () => {
      const { data } = await residentsService.listResidents({
        page: 1,
        page_size: DEFAULT_PAGE_SIZE,
        ...params,
      });
      return data;
    },
  });
}

export function useResidentQuery(id: string) {
  return useQuery({
    queryKey: queryKeys.residents.detail(id),
    queryFn: async () => {
      const { data } = await residentsService.getResident(id);
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateResidentMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ResidentPayload) =>
      residentsService.createResident(payload).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.residents.all }),
  });
}

export function useUpdateResidentMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: ResidentUpdatePayload }) =>
      residentsService.updateResident(id, payload).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.residents.all }),
  });
}

export function useDeleteResidentMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => residentsService.deleteResident(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.residents.all }),
  });
}

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { DEFAULT_PAGE_SIZE } from '@/shared/constants/api.constants';
import { queryKeys } from '@/shared/constants/queryKeys.constants';
import * as flatsService from '@/services/flats.service';
import type { FlatPayload, FlatUpdatePayload } from '@/services/flats.service';

export function useFlatsQuery(params?: { search?: string; is_active?: boolean }) {
  return useQuery({
    queryKey: queryKeys.flats.list(params),
    queryFn: async () => {
      const { data } = await flatsService.listFlats({
        page: 1,
        page_size: DEFAULT_PAGE_SIZE,
        ...params,
      });
      return data;
    },
  });
}

export function useCreateFlatMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: FlatPayload) => flatsService.createFlat(payload).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.flats.all }),
  });
}

export function useUpdateFlatMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: FlatUpdatePayload }) =>
      flatsService.updateFlat(id, payload).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.flats.all }),
  });
}

export function useDeleteFlatMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => flatsService.deleteFlat(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.flats.all }),
  });
}

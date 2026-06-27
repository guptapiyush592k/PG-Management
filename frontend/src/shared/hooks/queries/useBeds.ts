import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { DEFAULT_PAGE_SIZE } from '@/shared/constants/api.constants';
import { queryKeys } from '@/shared/constants/queryKeys.constants';
import type { BedStatus } from '@/shared/types/api.types';
import * as bedsService from '@/services/beds.service';
import type { BedPayload, BedUpdatePayload } from '@/services/beds.service';

export function useBedsQuery(params?: { search?: string; room_id?: string; status?: BedStatus }) {
  return useQuery({
    queryKey: queryKeys.beds.list(params),
    queryFn: async () => {
      const { data } = await bedsService.listBeds({
        page: 1,
        page_size: DEFAULT_PAGE_SIZE,
        ...params,
      });
      return data;
    },
  });
}

export function useCreateBedMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: BedPayload) => bedsService.createBed(payload).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.beds.all }),
  });
}

export function useUpdateBedMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: BedUpdatePayload }) =>
      bedsService.updateBed(id, payload).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.beds.all }),
  });
}

export function useDeleteBedMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => bedsService.deleteBed(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.beds.all }),
  });
}

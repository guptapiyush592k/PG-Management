import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { DEFAULT_PAGE_SIZE } from '@/shared/constants/api.constants';
import { queryKeys } from '@/shared/constants/queryKeys.constants';
import * as roomsService from '@/services/rooms.service';
import type { RoomPayload, RoomUpdatePayload } from '@/services/rooms.service';

export function useRoomsQuery(params?: { search?: string; flat_id?: string }) {
  return useQuery({
    queryKey: queryKeys.rooms.list(params),
    queryFn: async () => {
      const { data } = await roomsService.listRooms({
        page: 1,
        page_size: DEFAULT_PAGE_SIZE,
        ...params,
      });
      return data;
    },
  });
}

export function useCreateRoomMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: RoomPayload) => roomsService.createRoom(payload).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.rooms.all }),
  });
}

export function useUpdateRoomMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: RoomUpdatePayload }) =>
      roomsService.updateRoom(id, payload).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.rooms.all }),
  });
}

export function useDeleteRoomMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => roomsService.deleteRoom(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.rooms.all }),
  });
}

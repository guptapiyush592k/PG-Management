import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@/shared/constants/queryKeys.constants';
import * as meService from '@/services/me.service';

export function useMeContextQuery(enabled = true) {
  return useQuery({
    queryKey: queryKeys.me.context,
    queryFn: async () => {
      const { data } = await meService.getMeContext();
      return data;
    },
    enabled,
  });
}

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { DEFAULT_PAGE_SIZE } from '@/shared/constants/api.constants';
import { queryKeys } from '@/shared/constants/queryKeys.constants';
import type { PaymentStatus } from '@/shared/types/api.types';
import * as paymentsService from '@/services/payments.service';
import type { PaymentPayload, PaymentUpdatePayload } from '@/services/payments.service';

export function usePaymentsQuery(
  params?: {
    search?: string;
    resident_id?: string;
    status?: PaymentStatus;
  },
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: queryKeys.payments.list(params),
    queryFn: async () => {
      const { data } = await paymentsService.listPayments({
        page: 1,
        page_size: DEFAULT_PAGE_SIZE,
        ...params,
      });
      return data;
    },
    enabled: options?.enabled ?? true,
  });
}

export function usePaymentSummaryQuery() {
  return useQuery({
    queryKey: queryKeys.payments.summary,
    queryFn: async () => {
      const { data } = await paymentsService.getPaymentSummary();
      return data;
    },
  });
}

export function useCreatePaymentMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: PaymentPayload) =>
      paymentsService.createPayment(payload).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.payments.all });
    },
  });
}

export function useUpdatePaymentMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: PaymentUpdatePayload }) =>
      paymentsService.updatePayment(id, payload).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.payments.all });
    },
  });
}

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { pricesApi } from '@/lib/api';
import type { Price } from '@/types';

export function useCreatePrice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ itemId, listId, data }: { itemId: number; listId: number; data: Partial<Price> }) =>
      pricesApi.create(itemId, listId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['packing-list', variables.listId] });
    },
  });
}

export function useVotePrice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ priceId, isUpvote }: { priceId: number; isUpvote: boolean }) =>
      pricesApi.vote(priceId, isUpvote),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packing-list'] });
    },
  });
}

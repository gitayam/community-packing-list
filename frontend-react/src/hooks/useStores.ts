import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { storesApi } from '@/lib/api';
import type { Store } from '@/types';

export function useStores() {
  return useQuery({
    queryKey: ['stores'],
    queryFn: async () => {
      const response = await storesApi.list();
      return response.data;
    },
  });
}

export function useStore(id: number) {
  return useQuery({
    queryKey: ['store', id],
    queryFn: async () => {
      const response = await storesApi.get(id);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreateStore() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<Store>) => storesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stores'] });
    },
  });
}

export function useUpdateStore() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Store> }) =>
      storesApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['stores'] });
      queryClient.invalidateQueries({ queryKey: ['store', variables.id] });
    },
  });
}

export function useDeleteStore() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => storesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stores'] });
    },
  });
}

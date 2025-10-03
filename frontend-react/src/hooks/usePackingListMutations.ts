import { useMutation, useQueryClient } from '@tanstack/react-query';
import { packingListsApi, itemsApi } from '@/lib/api';
import type { PackingList, PackingListItem } from '@/types';

export function useCreatePackingList() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<PackingList>) => packingListsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packing-lists'] });
    },
  });
}

export function useUpdatePackingList() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<PackingList> }) =>
      packingListsApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['packing-lists'] });
      queryClient.invalidateQueries({ queryKey: ['packing-list', variables.id] });
    },
  });
}

export function useDeletePackingList() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => packingListsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packing-lists'] });
    },
  });
}

export function useUploadPackingList() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (formData: FormData) => packingListsApi.upload(formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packing-lists'] });
    },
  });
}

export function useTogglePacked() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ listId, itemId }: { listId: number; itemId: number }) =>
      packingListsApi.togglePacked(listId, itemId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['packing-list', variables.listId] });
    },
  });
}

export function useCreateItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ listId, data }: { listId: number; data: Partial<PackingListItem> }) =>
      itemsApi.create(listId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['packing-list', variables.listId] });
    },
  });
}

export function useUpdateItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ listId, itemId, data }: { listId: number; itemId: number; data: Partial<PackingListItem> }) =>
      itemsApi.update(listId, itemId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['packing-list', variables.listId] });
    },
  });
}

export function useDeleteItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ listId, itemId }: { listId: number; itemId: number }) =>
      itemsApi.delete(listId, itemId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['packing-list', variables.listId] });
    },
  });
}

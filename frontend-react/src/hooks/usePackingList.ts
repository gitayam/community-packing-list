import { useQuery } from '@tanstack/react-query';
import { packingListsApi } from '@/lib/api';

export function usePackingList(id: number) {
  return useQuery({
    queryKey: ['packing-list', id],
    queryFn: async () => {
      const response = await packingListsApi.get(id);
      return response.data;
    },
    enabled: !!id,
  });
}

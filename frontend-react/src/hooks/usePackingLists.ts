import { useQuery } from '@tanstack/react-query';
import { packingListsApi } from '@/lib/api';

export function usePackingLists() {
  return useQuery({
    queryKey: ['packing-lists'],
    queryFn: async () => {
      const response = await packingListsApi.list();
      return response.data;
    },
  });
}

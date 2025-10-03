import axios from 'axios';
import type {
  PackingList,
  PackingListDetailResponse,
  Store,
  Price,
  PackingListItem,
} from '@/types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Packing Lists
export const packingListsApi = {
  list: () => api.get<PackingList[]>('/packing-lists/'),
  get: (id: number) => api.get<PackingListDetailResponse>(`/packing-lists/${id}/detail_view/`),
  create: (data: Partial<PackingList>) => api.post<PackingList>('/packing-lists/', data),
  update: (id: number, data: Partial<PackingList>) => api.put<PackingList>(`/packing-lists/${id}/`, data),
  delete: (id: number) => api.delete(`/packing-lists/${id}/`),
  upload: (formData: FormData) => api.post('/packing-lists/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  togglePacked: (listId: number, itemId: number) =>
    api.post(`/packing-lists/${listId}/toggle_packed/`, { toggle_packed_item_id: itemId }),
};

// Items
export const itemsApi = {
  create: (listId: number, data: Partial<PackingListItem>) =>
    api.post<PackingListItem>('/packing-list-items/', { ...data, packing_list: listId }),
  update: (listId: number, itemId: number, data: Partial<PackingListItem>) =>
    api.put<PackingListItem>(`/packing-list-items/${itemId}/`, data),
  delete: (listId: number, itemId: number) =>
    api.delete(`/packing-list-items/${itemId}/`),
};

// Prices
export const pricesApi = {
  create: (itemId: number, listId: number, data: Partial<Price>) =>
    api.post<Price>('/prices/', { ...data, item: itemId }),
  vote: (priceId: number, isUpvote: boolean) =>
    api.post('/votes/', {
      price_id: priceId,
      [isUpvote ? 'upvote_price_id' : 'downvote_price_id']: priceId,
    }),
};

// Stores
export const storesApi = {
  list: () => api.get<Store[]>('/stores/'),
  get: (id: number) => api.get<Store>(`/stores/${id}/`),
  create: (data: Partial<Store>) => api.post<Store>('/stores/', data),
  update: (id: number, data: Partial<Store>) => api.put<Store>(`/stores/${id}/`, data),
  delete: (id: number) => api.delete(`/stores/${id}/`),
};

import axios from 'axios';
import type {
  PackingList,
  PackingListDetailResponse,
  Store,
  Price,
  PackingListItem,
} from '@/types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Packing Lists
export const packingListsApi = {
  list: () => api.get<PackingList[]>('/'),
  get: (id: number) => api.get<PackingListDetailResponse>(`/list/${id}/`),
  create: (data: Partial<PackingList>) => api.post<PackingList>('/list/create/', data),
  update: (id: number, data: Partial<PackingList>) => api.put<PackingList>(`/list/${id}/update/`, data),
  delete: (id: number) => api.delete(`/list/${id}/delete/`),
  upload: (formData: FormData) => api.post('/list/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  togglePacked: (listId: number, itemId: number) =>
    api.post(`/list/${listId}/toggle_packed/`, { toggle_packed_item_id: itemId }),
};

// Items
export const itemsApi = {
  create: (listId: number, data: Partial<PackingListItem>) =>
    api.post<PackingListItem>(`/list/${listId}/add_item/`, data),
  update: (listId: number, itemId: number, data: Partial<PackingListItem>) =>
    api.put<PackingListItem>(`/list/${listId}/edit_item/${itemId}/`, data),
  delete: (listId: number, itemId: number) =>
    api.delete(`/list/${listId}/delete_item/${itemId}/`),
};

// Prices
export const pricesApi = {
  create: (itemId: number, listId: number, data: Partial<Price>) =>
    api.post<Price>(`/item/${itemId}/add_price/to_list/${listId}/`, data),
  vote: (priceId: number, isUpvote: boolean) =>
    api.post('/vote/', {
      price_id: priceId,
      [isUpvote ? 'upvote_price_id' : 'downvote_price_id']: priceId,
    }),
};

// Stores
export const storesApi = {
  list: () => api.get<Store[]>('/stores/'),
  get: (id: number) => api.get<Store>(`/stores/${id}/`),
  create: (data: Partial<Store>) => api.post<Store>('/stores/', data),
  update: (id: number, data: Partial<Store>) => api.put<Store>(`/stores/${id}/edit/`, data),
  delete: (id: number) => api.delete(`/stores/${id}/delete/`),
};

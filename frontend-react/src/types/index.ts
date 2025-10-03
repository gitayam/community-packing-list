export interface School {
  id: number;
  name: string;
  address?: string;
  latitude?: number;
  longitude?: number;
}

export interface Base {
  id: number;
  name: string;
  address?: string;
  latitude?: number;
  longitude?: number;
}

export interface Store {
  id: number;
  name: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  full_address_legacy?: string;
  url?: string;
  latitude?: number;
  longitude?: number;
  is_online: boolean;
  is_in_person: boolean;
}

export type PackingListType = 'course' | 'selection' | 'training' | 'deployment' | 'other';

export interface PackingList {
  id: number;
  name: string;
  description?: string;
  type: PackingListType;
  custom_type?: string;
  school?: School;
  base?: Base;
}

export interface Item {
  id: number;
  name: string;
  description?: string;
}

export interface PackingListItem {
  id: number;
  packing_list: number;
  item: Item;
  quantity: number;
  notes?: string;
  packed: boolean;
  section?: string;
  nsn_lin?: string;
  required: boolean;
  instructions?: string;
}

export interface Price {
  id: number;
  item: number;
  store: Store;
  price: string; // Decimal as string
  quantity: number;
  date_purchased?: string;
}

export interface Vote {
  id: number;
  price: number;
  is_correct_price: boolean;
  ip_address?: string;
  created_at: string;
}

export interface PriceWithVotes {
  price: Price;
  upvotes: number;
  downvotes: number;
  vote_confidence: number;
  price_per_unit: number;
}

export interface PackingListDetailResponse {
  packing_list: PackingList;
  items_with_prices: Array<{
    pli: PackingListItem;
    item: Item;
    prices_with_votes: PriceWithVotes[];
  }>;
}

// Core data types for the packing list application

export interface PackingList {
  id: number;
  name: string;
  description?: string;
  branch: string;
  event_type: string;
  school_type?: string;
  assessment_type?: string;
  training_type?: string;
  school?: School;
  base?: Base;
  created_at: string;
  updated_at: string;
}

export interface PackingListItem {
  id: number;
  packing_list: number;
  name: string;
  section: string;
  quantity: number;
  required: boolean;
  nsn?: string;
  lin?: string;
  instructions?: string;
  packed: boolean;
  created_at: string;
  updated_at: string;
}

export interface School {
  id: number;
  name: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  latitude?: number;
  longitude?: number;
}

export interface Base {
  id: number;
  name: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
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
  latitude?: number;
  longitude?: number;
  url?: string;
  is_online: boolean;
  is_in_person: boolean;
  google_maps_link?: string;
  apple_maps_link?: string;
  formatted_address?: string;
}

export interface Price {
  id: number;
  item: number;
  store: Store;
  price: number;
  quantity: number;
  date_purchased?: string;
  upvotes: number;
  downvotes: number;
  created_at: string;
  updated_at: string;
}

export interface Vote {
  id: number;
  price: number;
  vote_type: 'up' | 'down';
  ip_address: string;
  created_at: string;
}

// Form data types
export interface PackingListFormData {
  branch: string;
  event_type: string;
  school_type?: string;
  assessment_type?: string;
  training_type?: string;
  school?: number;
  base?: number;
  name: string;
  description?: string;
}

export interface PriceFormData {
  store: number | '__add_new__';
  price: number;
  quantity: number;
  date_purchased?: string;
  store_name?: string;
  store_address_line1?: string;
  store_address_line2?: string;
  store_city?: string;
  store_state?: string;
  store_zip_code?: string;
  store_country?: string;
  store_url?: string;
  store_is_online?: boolean;
  store_is_in_person?: boolean;
}

export interface StoreFormData {
  name: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  url?: string;
  is_online: boolean;
  is_in_person: boolean;
}

// API response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  html?: string;
  errors?: Record<string, string[]>;
}

export interface VoteResponse {
  success: boolean;
  upvotes: number;
  downvotes: number;
  message?: string;
}

// UI state types
export interface TableSortState {
  column: string;
  direction: 'asc' | 'desc';
}

export interface FilterState {
  searchTerm: string;
  baseFilter?: number;
  radius?: number;
  city?: string;
  state?: string;
  zip_code?: string;
  school_id?: number;
  user_lat?: number;
  user_lon?: number;
}

export interface ModalState {
  isOpen: boolean;
  type: 'price' | 'edit-item' | 'store';
  data?: any;
}

// Event types
export interface TableRowData {
  itemName: string;
  section: string;
  quantity: number;
  required: boolean;
  packed: boolean;
  price?: number;
  store?: string;
  nsn?: string;
}

export interface PriceDetailsData {
  itemId: number;
  prices: Price[];
  position: {
    top: number;
    left: number;
  };
}

// Branch mapping types
export interface BranchMapping {
  [key: string]: string[];
}

export const SCHOOL_BRANCHES: BranchMapping = {
  airborne: ["army", "all"],
  air_assault: ["army", "all"],
  jumpmaster: ["army", "all"],
  ranger_school: ["army", "all"],
  pathfinder: ["army", "all"],
  sniper: ["army", "marines", "all"],
  mountain: ["army", "all"],
  sapper: ["army", "all"],
  cdqc: ["army", "all"],
  sfqc: ["army", "all"],
  buds: ["navy", "all"],
  sere: ["army", "navy", "marines", "air_force", "all"],
  other: ["all", "army", "navy", "marines", "air_force"]
};

export const ASSESSMENT_BRANCHES: BranchMapping = {
  sfas: ["army", "all"],
  poas: ["army", "all"],
  caas: ["army", "all"],
  rasp: ["army", "all"],
  ocs: ["army", "navy", "marines", "air_force", "all"],
  wocs: ["army", "all"],
  seal_pst: ["navy", "all"],
  recon: ["marines", "all"],
  pj_indoc: ["air_force", "all"],
  marsoc_as: ["marines", "all"],
  cct_selection: ["air_force", "all"],
  other: ["all", "army", "navy", "marines", "air_force"]
};

export const TRAINING_BRANCHES: BranchMapping = {
  bct: ["army", "all"],
  ait: ["army", "all"],
  osut: ["army", "all"],
  pre_ranger: ["army", "all"],
  pre_sapper: ["army", "all"],
  pre_airborne: ["army", "all"],
  pre_seal: ["navy", "all"],
  tactical_fitness: ["all", "army", "navy", "marines", "air_force"],
  never_quit: ["all", "army", "navy", "marines", "air_force"],
  other: ["all", "army", "navy", "marines", "air_force"]
}; 
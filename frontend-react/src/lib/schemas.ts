import { z } from 'zod';

export const createPackingListSchema = z.object({
  name: z.string().min(1, 'Name is required').max(200, 'Name is too long'),
  description: z.string().optional(),
  type: z.enum(['course', 'selection', 'training', 'deployment', 'other']),
  custom_type: z.string().optional(),
  school_id: z.number().optional(),
  base_id: z.number().optional(),
});

export type CreatePackingListInput = z.infer<typeof createPackingListSchema>;

export const createStoreSchema = z.object({
  name: z.string().min(1, 'Store name is required').max(200),
  address_line1: z.string().optional(),
  address_line2: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  zip_code: z.string().optional(),
  country: z.string().optional(),
  url: z.string().url('Invalid URL').optional().or(z.literal('')),
  latitude: z.number().optional(),
  longitude: z.number().optional(),
  is_online: z.boolean(),
  is_in_person: z.boolean(),
});

export type CreateStoreInput = z.infer<typeof createStoreSchema>;

export const createPriceSchema = z.object({
  store_id: z.number().min(1, 'Store is required'),
  price: z.string().min(1, 'Price is required'),
  quantity: z.number().min(1, 'Quantity must be at least 1').default(1),
  date_purchased: z.string().optional(),
});

export type CreatePriceInput = z.infer<typeof createPriceSchema>;

export const createItemSchema = z.object({
  item_name: z.string().min(1, 'Item name is required'),
  item_description: z.string().optional(),
  quantity: z.number().min(1).default(1),
  notes: z.string().optional(),
  section: z.string().optional(),
  nsn_lin: z.string().optional(),
  required: z.boolean().default(false),
  instructions: z.string().optional(),
});

export type CreateItemInput = z.infer<typeof createItemSchema>;

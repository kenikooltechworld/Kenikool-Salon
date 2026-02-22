export interface Service {
  id: string;
  name: string;
  description?: string;
  duration_minutes: number;
  price: number;
  category: string;
  color?: string;
  icon?: string;
  is_active: boolean;
  is_published?: boolean;
  public_description?: string;
  public_image_url?: string;
  allow_public_booking?: boolean;
  tags?: string[];
  created_at: string;
  updated_at: string;
}

export interface CreateServiceInput {
  name: string;
  description?: string;
  duration_minutes: number;
  price: number;
  category: string;
  color?: string;
  icon?: string;
  is_active?: boolean;
  is_published?: boolean;
  public_description?: string;
  public_image_url?: string;
  allow_public_booking?: boolean;
  tags?: string[];
}

export interface UpdateServiceInput {
  name?: string;
  description?: string;
  duration_minutes?: number;
  price?: number;
  category?: string;
  color?: string;
  icon?: string;
  is_active?: boolean;
  is_published?: boolean;
  public_description?: string;
  public_image_url?: string;
  allow_public_booking?: boolean;
  tags?: string[];
}

export interface ServiceFilters {
  category?: string;
  is_active?: boolean;
  is_published?: boolean;
  search?: string;
  page?: number;
  limit?: number;
}

export type PaymentStatus = 'paid' | 'pending' | 'partial' | 'overdue';
export type BedStatus = 'occupied' | 'vacant' | 'maintenance';
export type BookingStatus = 'active' | 'completed' | 'cancelled';
export type ThemeMode = 'light' | 'dark';

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface ApiError {
  detail: string;
  error_code: string;
  errors?: unknown[];
}

export interface User {
  id: string;
  email: string;
  full_name: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
  tenant_id: string;
}

export interface Permissions {
  manage_flats: boolean;
  manage_rooms: boolean;
  manage_beds: boolean;
  manage_residents: boolean;
  manage_payments: boolean;
  manage_files: boolean;
}

export interface TenantContext {
  id: string;
  name: string;
  logo_url: string | null;
  primary_color: string;
  secondary_color: string;
  is_demo: boolean;
  subscription_status: string;
}

export interface MeContext {
  user: { id: string; name: string; email: string };
  tenant: TenantContext;
  permissions: Permissions;
}

export interface Flat {
  id: string;
  tenant_id: string;
  name: string;
  address: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Room {
  id: string;
  tenant_id: string;
  flat_id: string;
  room_number: string;
  created_at: string;
  updated_at: string;
}

export interface Bed {
  id: string;
  tenant_id: string;
  room_id: string;
  bed_label: string;
  rent_amount: string;
  status: BedStatus;
  created_at: string;
  updated_at: string;
}

export interface Resident {
  id: string;
  tenant_id: string;
  name: string;
  phone: string;
  email: string | null;
  aadhaar: string | null;
  joining_date: string;
  deposit: string;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Payment {
  id: string;
  tenant_id: string;
  resident_id: string;
  booking_id: string | null;
  amount: string;
  due_date: string;
  paid_date: string | null;
  status: PaymentStatus;
  payment_mode: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface PaymentSummary {
  total_collected: string;
  pending_amount: string;
  overdue_amount: string;
  counts: Record<PaymentStatus, number>;
}

export interface Booking {
  id: string;
  tenant_id: string;
  resident_id: string;
  bed_id: string;
  start_date: string;
  end_date: string | null;
  status: BookingStatus;
  created_at: string;
  updated_at: string;
}

export interface ListParams {
  page?: number;
  page_size?: number;
  search?: string;
}

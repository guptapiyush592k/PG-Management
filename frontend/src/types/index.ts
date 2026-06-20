export type PaymentStatus = 'paid' | 'pending' | 'partial' | 'overdue';
export type BedStatus = 'occupied' | 'vacant' | 'maintenance';
export type ThemeMode = 'light' | 'dark';

export interface Flat {
  id: string;
  name: string;
  address: string;
  totalRooms: number;
  totalBeds: number;
  occupiedBeds: number;
  vacantBeds: number;
}

export interface Room {
  id: string;
  flatId: string;
  flatName: string;
  roomNumber: string;
  totalBeds: number;
  occupiedBeds: number;
  vacantBeds: number;
}

export interface Bed {
  id: string;
  bedId: string;
  flatId: string;
  flatName: string;
  roomId: string;
  roomNumber: string;
  rentAmount: number;
  status: BedStatus;
  tenantId?: string;
  tenantName?: string;
}

export interface Tenant {
  id: string;
  name: string;
  phone: string;
  aadhaar: string;
  joiningDate: string;
  dueDate: string;
  assignedBedId: string;
  assignedBedLabel: string;
  flatName: string;
  rentAmount: number;
  deposit: number;
  paymentStatus: PaymentStatus;
  email?: string;
  notes?: string;
}

export interface Payment {
  id: string;
  tenantId: string;
  tenantName: string;
  amount: number;
  dueDate: string;
  paidDate?: string;
  status: PaymentStatus;
  paymentMode?: string;
  flatName: string;
}

export interface DashboardStats {
  totalBeds: number;
  occupiedBeds: number;
  vacantBeds: number;
  occupancyPercent: number;
  pendingAmount: number;
  monthlyCollection: number;
}

export interface ChartDataPoint {
  name: string;
  value?: number;
  [key: string]: string | number | undefined;
}

export interface NavItem {
  path: string;
  label: string;
  icon: string;
}

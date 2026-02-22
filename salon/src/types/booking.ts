export type BookingStatus =
  | "scheduled"
  | "confirmed"
  | "completed"
  | "cancelled"
  | "no_show";

export interface Booking {
  id: string;
  customerId: string;
  serviceId: string;
  staffId: string;
  startTime: string;
  endTime: string;
  status: BookingStatus;
  notes?: string;
  locationId?: string;
  price?: number;
  cancellationReason?: string;
  cancelledAt?: string;
  cancelledBy?: string;
  noShowReason?: string;
  markedNoShowAt?: string;
  confirmedAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateBookingInput {
  customerId?: string;
  customerName?: string;
  customerEmail?: string;
  customerPhone?: string;
  serviceId: string;
  staffId: string;
  startTime: string;
  endTime: string;
  notes?: string;
  paymentOption?: "now" | "later";
}

export interface UpdateBookingInput {
  notes?: string;
}

export interface BookingFilters {
  status?: BookingStatus;
  startDate?: string;
  endDate?: string;
  staffId?: string;
  serviceId?: string;
  customerId?: string;
  page?: number;
  limit?: number;
}

export interface BookingFormData {
  serviceId?: string;
  staffId?: string;
  customerId?: string;
  startTime?: string;
  endTime?: string;
  notes?: string;
}

// Common types used across the application

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, string>;
  };
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Re-export booking types
export type {
  BookingStatus,
  Booking,
  CreateBookingInput,
  UpdateBookingInput,
  BookingFilters,
  BookingFormData,
} from "./booking";

// Re-export timeSlot types
export type {
  TimeSlot,
  CreateTimeSlotInput,
  TimeSlotFilters,
  AvailableSlot,
} from "./timeSlot";

// Re-export service types
export type {
  Service,
  CreateServiceInput,
  UpdateServiceInput,
  ServiceFilters,
} from "./service";

// Re-export availability types
export type {
  Availability,
  CreateAvailabilityInput,
  UpdateAvailabilityInput,
  AvailabilityFilters,
} from "./availability";

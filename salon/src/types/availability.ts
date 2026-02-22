export interface Availability {
  id: string;
  staffId: string;
  isRecurring: boolean;
  dayOfWeek?: number;
  startTime: string;
  endTime: string;
  breakStart?: string;
  breakEnd?: string;
  startDate?: string;
  endDate?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateAvailabilityInput {
  staffId: string;
  isRecurring: boolean;
  dayOfWeek?: number;
  startTime: string;
  endTime: string;
  breakStart?: string;
  breakEnd?: string;
  startDate?: string;
  endDate?: string;
  isActive?: boolean;
}

export interface UpdateAvailabilityInput {
  startTime?: string;
  endTime?: string;
  breakStart?: string;
  breakEnd?: string;
  isActive?: boolean;
}

export interface AvailabilityFilters {
  staffId?: string;
  isRecurring?: boolean;
  isActive?: boolean;
  page?: number;
  limit?: number;
}

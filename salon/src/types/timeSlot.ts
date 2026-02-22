export interface TimeSlot {
  id: string;
  staffId: string;
  serviceId: string;
  startTime: string;
  endTime: string;
  isReserved: boolean;
  reservationExpiresAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateTimeSlotInput {
  staffId: string;
  serviceId: string;
  startTime: string;
  endTime: string;
}

export interface TimeSlotFilters {
  staffId?: string;
  serviceId?: string;
  startDate?: string;
  endDate?: string;
  isReserved?: boolean;
  page?: number;
  limit?: number;
}

export interface AvailableSlot {
  start_time: string;
  end_time: string;
  staff_id: string;
  duration_minutes: number;
  isAvailable: boolean;
}

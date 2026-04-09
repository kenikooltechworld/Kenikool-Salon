import { useQuery, useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

interface PublicService {
  id: string;
  name: string;
  description: string;
  duration_minutes: number;
  price: number;
  is_published: boolean;
  public_description?: string;
  public_image_url?: string;
  allow_public_booking: boolean;
  benefits?: string[];
}

interface PublicStaff {
  id: string;
  first_name: string;
  last_name: string;
  is_available_for_public_booking: boolean;
  bio?: string;
  profile_image_url?: string;
  specialties?: string[];
  rating?: number;
  review_count?: number;
}

interface TimeSlot {
  time: string;
  available: boolean;
}

interface AvailabilityResponse {
  date: string;
  slots: TimeSlot[];
}

interface CreatePublicBookingInput {
  service_id: string;
  staff_id: string;
  booking_date: string;
  booking_time: string;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  notes?: string;
  payment_option?: "now" | "later";
}

interface PublicBookingResponse {
  id: string;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  booking_date: string;
  booking_time: string;
  duration_minutes: number;
  status: string;
  created_at: string;
}

export function usePublicServices() {
  return useQuery({
    queryKey: ["public-services"],
    queryFn: async () => {
      const { data } = await apiClient.get<PublicService[]>("/public/services");
      return data || [];
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function usePublicStaff(serviceId?: string) {
  return useQuery({
    queryKey: ["public-staff", serviceId],
    queryFn: async () => {
      const params = serviceId ? `?service_id=${serviceId}` : "";
      const { data } = await apiClient.get<PublicStaff[]>(
        `/public/staff${params}`,
      );
      return data || [];
    },
    enabled: !!serviceId,
    staleTime: 5 * 60 * 1000,
  });
}

export function usePublicAvailability(
  serviceId: string,
  staffId: string,
  bookingDate: string,
) {
  return useQuery({
    queryKey: ["public-availability", serviceId, staffId, bookingDate],
    queryFn: async () => {
      const { data } = await apiClient.get<AvailabilityResponse>(
        "/public/availability",
        {
          params: {
            service_id: serviceId,
            staff_id: staffId,
            booking_date: bookingDate,
          },
        },
      );
      return data;
    },
    enabled: !!serviceId && !!staffId && !!bookingDate,
    staleTime: 1 * 60 * 1000,
  });
}

export function useCreatePublicBooking() {
  return useMutation({
    mutationFn: async (input: CreatePublicBookingInput) => {
      const { data } = await apiClient.post<PublicBookingResponse>(
        "/public/bookings",
        input,
      );
      return data;
    },
  });
}

export function usePublicBooking(bookingId: string) {
  return useQuery({
    queryKey: ["public-booking", bookingId],
    queryFn: async () => {
      const { data } = await apiClient.get<PublicBookingResponse>(
        `/public/bookings/${bookingId}`,
      );
      return data;
    },
    enabled: !!bookingId,
  });
}

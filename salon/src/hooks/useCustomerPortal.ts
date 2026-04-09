import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

interface BookingHistory {
  id: string;
  service_name: string;
  staff_name: string;
  booking_date: string;
  booking_time: string;
  status: string;
  payment_status?: string;
  total_price: number;
  notes?: string;
  created_at: string;
}

interface RebookData {
  service_id: string;
  staff_id: string;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
}

export function useCustomerBookingHistory(statusFilter?: string) {
  const token = localStorage.getItem("customer_token");

  return useQuery({
    queryKey: ["customer-bookings", statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (statusFilter) {
        params.append("status_filter", statusFilter);
      }

      const { data } = await apiClient.get<BookingHistory[]>(
        `/public/customer-portal/bookings?${params.toString()}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );
      return data;
    },
    enabled: !!token,
  });
}

export function useCustomerBookingDetails(bookingId: string | null) {
  const token = localStorage.getItem("customer_token");

  return useQuery({
    queryKey: ["customer-booking", bookingId],
    queryFn: async () => {
      if (!bookingId) return null;

      const { data } = await apiClient.get<BookingHistory>(
        `/public/customer-portal/bookings/${bookingId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );
      return data;
    },
    enabled: !!token && !!bookingId,
  });
}

export function useRebookAppointment() {
  const token = localStorage.getItem("customer_token");

  return useMutation({
    mutationFn: async (bookingId: string) => {
      const { data } = await apiClient.post<{
        message: string;
        booking_data: RebookData;
      }>(
        `/public/customer-portal/bookings/${bookingId}/rebook`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );
      return data;
    },
  });
}

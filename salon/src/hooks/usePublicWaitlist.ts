import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface WaitlistStatus {
  queue_length: number;
  average_wait_time_minutes: number;
  is_accepting: boolean;
  message?: string;
}

export interface WaitlistPosition {
  position: number;
  estimated_wait_time_minutes: number;
  status: string;
  check_in_time: string;
  service_name?: string;
  staff_name?: string;
}

export interface JoinWaitlistData {
  service_id: string;
  staff_id?: string;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  preferred_date?: string;
  notes?: string;
}

export interface JoinWaitlistResponse {
  message: string;
  position: number;
  estimated_wait_time_minutes: number;
  queue_entry_id: string;
}

// Get waitlist status
export function useWaitlistStatus() {
  return useQuery({
    queryKey: ["public-waitlist-status"],
    queryFn: async () => {
      const { data } = await apiClient.get<WaitlistStatus>(
        "/public/waitlist/status",
      );
      return data;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

// Join waitlist
export function useJoinWaitlist() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (waitlistData: JoinWaitlistData) => {
      const { data } = await apiClient.post<JoinWaitlistResponse>(
        "/public/waitlist/join",
        waitlistData,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["public-waitlist-status"] });
    },
  });
}

// Get customer position
export function useWaitlistPosition(email: string | null) {
  return useQuery({
    queryKey: ["public-waitlist-position", email],
    queryFn: async () => {
      if (!email) return null;
      const { data } = await apiClient.get<WaitlistPosition | null>(
        "/public/waitlist/position",
        { params: { email } },
      );
      return data;
    },
    enabled: !!email,
    refetchInterval: 15000, // Refetch every 15 seconds
  });
}

// Cancel waitlist entry
export function useCancelWaitlist() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (email: string) => {
      const { data } = await apiClient.delete("/public/waitlist/cancel", {
        params: { email },
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["public-waitlist-status"] });
      queryClient.invalidateQueries({ queryKey: ["public-waitlist-position"] });
    },
  });
}

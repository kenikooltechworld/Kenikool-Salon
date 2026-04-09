import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useAuthStore } from "@/stores/auth";

export interface AttendanceRecord {
  id: string;
  staff_id: string;
  check_in_time: string;
  check_out_time?: string;
  hours_worked?: number;
  status: "checked_in" | "checked_out";
  is_late?: boolean;
  is_early_departure?: boolean;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface AttendanceFilters {
  startDate?: string;
  endDate?: string;
  status?: string;
}

export interface ClockInData {
  notes?: string;
}

export interface ClockOutData {
  notes?: string;
}

/**
 * Fetch current staff member's attendance records with filtering
 * Automatically filters by staff_id from authenticated user
 */
export function useMyAttendance(filters?: AttendanceFilters) {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["my-attendance", filters],
    queryFn: async () => {
      const { data } = await apiClient.get<AttendanceRecord[]>("/attendance", {
        params: {
          staff_id: user?.id,
          ...filters,
        },
      });
      return Array.isArray(data) ? data : [];
    },
    enabled: !!user?.id,
  });
}

/**
 * Get current attendance status (if staff is currently clocked in)
 */
export function useCurrentAttendanceStatus() {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["current-attendance-status"],
    queryFn: async () => {
      const { data } = await apiClient.get<AttendanceRecord | null>(
        "/attendance/current",
        {
          params: {
            staff_id: user?.id,
          },
        },
      );
      return data;
    },
    enabled: !!user?.id,
    refetchInterval: 30000, // Refetch every 30 seconds to keep status current
  });
}

/**
 * Clock in for current staff member
 */
export function useClockIn() {
  const queryClient = useQueryClient();
  const user = useAuthStore((state) => state.user);

  return useMutation({
    mutationFn: async (clockInData?: ClockInData) => {
      const { data } = await apiClient.post<AttendanceRecord>(
        "/attendance/clock-in",
        {
          staff_id: user?.id,
          ...clockInData,
        },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-attendance"] });
      queryClient.invalidateQueries({
        queryKey: ["current-attendance-status"],
      });
      queryClient.invalidateQueries({ queryKey: ["staff-metrics"] });
    },
  });
}

/**
 * Clock out for current staff member
 */
export function useClockOut() {
  const queryClient = useQueryClient();
  const user = useAuthStore((state) => state.user);

  return useMutation({
    mutationFn: async (clockOutData?: ClockOutData) => {
      const { data } = await apiClient.post<AttendanceRecord>(
        "/attendance/clock-out",
        {
          staff_id: user?.id,
          ...clockOutData,
        },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-attendance"] });
      queryClient.invalidateQueries({
        queryKey: ["current-attendance-status"],
      });
      queryClient.invalidateQueries({ queryKey: ["staff-metrics"] });
    },
  });
}

/**
 * Get attendance summary for current period
 */
export function useAttendanceSummary(
  period: "week" | "month" | "year" = "month",
) {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["attendance-summary", period],
    queryFn: async () => {
      const { data } = await apiClient.get<{
        total_hours: number;
        total_days: number;
        late_arrivals: number;
        early_departures: number;
        average_hours_per_day: number;
      }>("/attendance/summary", {
        params: {
          staff_id: user?.id,
          period,
        },
      });
      return data;
    },
    enabled: !!user?.id,
  });
}

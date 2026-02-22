import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface TimeOffRequest {
  id: string;
  staff_id: string;
  start_date: string;
  end_date: string;
  reason: string;
  status: "pending" | "approved" | "denied";
  created_at: string;
  updated_at: string;
}

interface TimeOffFilters {
  staff_id?: string;
  status?: string;
}

interface CreateTimeOffData {
  staff_id: string;
  start_date: string;
  end_date: string;
  reason: string;
}

/**
 * Fetch all time-off requests with optional filters
 */
export function useTimeOffRequests(filters?: TimeOffFilters) {
  return useQuery({
    queryKey: ["time-off-requests", filters],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: TimeOffRequest[] }>(
        "/time-off-requests",
        {
          params: filters,
        },
      );
      return data.data || [];
    },
  });
}

/**
 * Fetch single time-off request by ID
 */
export function useTimeOffRequest(id: string) {
  return useQuery({
    queryKey: ["time-off-requests", id],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: TimeOffRequest }>(
        `/time-off-requests/${id}`,
      );
      return data.data || null;
    },
    enabled: !!id,
  });
}

/**
 * Create new time-off request
 */
export function useCreateTimeOffRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (requestData: CreateTimeOffData) => {
      const { data } = await apiClient.post<{ data: TimeOffRequest }>(
        "/time-off-requests",
        requestData,
      );
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["time-off-requests"] });
    },
  });
}

/**
 * Approve time-off request
 */
export function useApproveTimeOffRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.put<{ data: TimeOffRequest }>(
        `/time-off-requests/${id}/approve`,
        {},
      );
      return data.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["time-off-requests"] });
      queryClient.invalidateQueries({
        queryKey: ["time-off-requests", data.id],
      });
    },
  });
}

/**
 * Deny time-off request
 */
export function useDenyTimeOffRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.put<{ data: TimeOffRequest }>(
        `/time-off-requests/${id}/deny`,
        {},
      );
      return data.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["time-off-requests"] });
      queryClient.invalidateQueries({
        queryKey: ["time-off-requests", data.id],
      });
    },
  });
}

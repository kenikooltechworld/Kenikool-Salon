import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import type { TimeSlot, CreateTimeSlotInput, TimeSlotFilters } from "@/types";

const TIME_SLOTS_QUERY_KEY = "timeSlots";

export function useTimeSlots(filters?: TimeSlotFilters) {
  return useQuery({
    queryKey: [TIME_SLOTS_QUERY_KEY, filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.staffId) params.append("staff_id", filters.staffId);
      if (filters?.serviceId) params.append("service_id", filters.serviceId);
      if (filters?.startDate) params.append("start_date", filters.startDate);
      if (filters?.endDate) params.append("end_date", filters.endDate);
      if (filters?.isReserved !== undefined)
        params.append("is_reserved", filters.isReserved.toString());
      if (filters?.page) params.append("page", filters.page.toString());
      if (filters?.limit) params.append("limit", filters.limit.toString());

      const { data } = await apiClient.get<{ data: TimeSlot[] }>(
        `/time-slots?${params}`,
      );
      return data.data || [];
    },
    staleTime: 2 * 60 * 1000,
  });
}

export function useTimeSlot(id: string) {
  return useQuery({
    queryKey: [TIME_SLOTS_QUERY_KEY, id],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: TimeSlot }>(
        `/time-slots/${id}`,
      );
      return data.data || null;
    },
    enabled: !!id,
    staleTime: 2 * 60 * 1000,
  });
}

export function useCreateTimeSlot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: CreateTimeSlotInput) => {
      const { data } = await apiClient.post<{ data: TimeSlot }>(
        "/time-slots",
        input,
      );
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TIME_SLOTS_QUERY_KEY] });
    },
  });
}

export function useConfirmTimeSlot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post<{ data: TimeSlot }>(
        `/time-slots/${id}/confirm`,
      );
      return data.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: [TIME_SLOTS_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [TIME_SLOTS_QUERY_KEY, id] });
    },
  });
}

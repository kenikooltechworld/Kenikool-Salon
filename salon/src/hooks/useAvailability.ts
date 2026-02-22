import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import type {
  Availability,
  CreateAvailabilityInput,
  AvailabilityFilters,
} from "@/types";

const AVAILABILITY_QUERY_KEY = "availability";

export function useAvailability(filters?: AvailabilityFilters) {
  return useQuery({
    queryKey: [AVAILABILITY_QUERY_KEY, filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.staffId) params.append("staff_id", filters.staffId);
      if (filters?.isRecurring !== undefined)
        params.append("is_recurring", filters.isRecurring.toString());
      if (filters?.isActive !== undefined)
        params.append("is_active", filters.isActive.toString());
      if (filters?.page) params.append("page", filters.page.toString());
      if (filters?.limit) params.append("limit", filters.limit.toString());

      const { data } = await apiClient.get<{ data: Availability[] }>(
        `/availability?${params}`,
      );
      return data.data || [];
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useAvailabilityById(id: string) {
  return useQuery({
    queryKey: [AVAILABILITY_QUERY_KEY, id],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: Availability }>(
        `/availability/${id}`,
      );
      return data.data || null;
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateAvailability() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: CreateAvailabilityInput) => {
      const { data } = await apiClient.post<{ data: Availability }>(
        "/availability",
        input,
      );
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [AVAILABILITY_QUERY_KEY] });
    },
  });
}

export function useUpdateAvailability() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      ...input
    }: {
      id: string;
      [key: string]: any;
    }) => {
      const { data } = await apiClient.put<{ data: Availability }>(
        `/availability/${id}`,
        input,
      );
      return data.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: [AVAILABILITY_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [AVAILABILITY_QUERY_KEY, id] });
    },
  });
}

export function useDeleteAvailability() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/availability/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [AVAILABILITY_QUERY_KEY] });
    },
  });
}

export function useAvailableSlots(
  staffId: string,
  serviceId: string,
  date: string,
) {
  return useQuery({
    queryKey: ["availableSlots", staffId, serviceId, date],
    queryFn: async () => {
      const { data } = await apiClient.get(
        `/availability/slots/available?staff_id=${staffId}&service_id=${serviceId}&target_date=${date}`,
      );
      return data.slots || [];
    },
    enabled: !!staffId && !!serviceId && !!date,
    staleTime: 1 * 60 * 1000,
  });
}

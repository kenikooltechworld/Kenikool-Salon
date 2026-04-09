import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import type { Notification } from "@/types/notification";

// Message types for staff communication
const MESSAGE_TYPES = ["manager_message", "team_announcement", "custom"];

interface MessageFilters {
  status?: "read" | "unread";
  limit?: number;
  offset?: number;
  search?: string;
}

// Fetch messages (notifications with message types)
export const useMessages = (filters?: MessageFilters) => {
  return useQuery({
    queryKey: ["messages", filters],
    queryFn: async () => {
      const params = new URLSearchParams();

      // Filter by message notification types
      MESSAGE_TYPES.forEach((type) => {
        params.append("notification_type", type);
      });

      if (filters?.status === "read") params.append("status", "read");
      if (filters?.status === "unread") params.append("status", "unread");
      if (filters?.limit) params.append("limit", filters.limit.toString());
      if (filters?.offset) params.append("skip", filters.offset.toString());

      const { data } = await apiClient.get(`/notifications?${params}`);
      const messages = (
        Array.isArray(data) ? data : data.data || []
      ) as Notification[];

      // Apply search filter on client side if provided
      if (filters?.search) {
        const searchLower = filters.search.toLowerCase();
        return messages.filter(
          (msg) =>
            msg.subject?.toLowerCase().includes(searchLower) ||
            msg.content?.toLowerCase().includes(searchLower),
        );
      }

      return messages;
    },
    staleTime: 30000, // 30 seconds
  });
};

// Fetch single message
export const useMessage = (messageId: string) => {
  return useQuery({
    queryKey: ["message", messageId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/notifications/${messageId}`);
      return data as Notification;
    },
    enabled: !!messageId,
  });
};

// Mark message as read
export const useMarkMessageRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (messageId: string) => {
      const { data } = await apiClient.patch(
        `/notifications/${messageId}/mark-read`,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["messages"] });
      queryClient.invalidateQueries({ queryKey: ["messages-unread-count"] });
    },
  });
};

// Mark message as unread
export const useMarkMessageUnread = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (messageId: string) => {
      // This would need a backend endpoint to mark as unread
      // For now, we'll use a workaround by updating the notification
      const { data } = await apiClient.patch(`/notifications/${messageId}`, {
        is_read: false,
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["messages"] });
      queryClient.invalidateQueries({ queryKey: ["messages-unread-count"] });
    },
  });
};

// Get unread message count
export const useUnreadMessageCount = () => {
  return useQuery({
    queryKey: ["messages-unread-count"],
    queryFn: async () => {
      // Get unread notifications filtered by message types
      const params = new URLSearchParams();
      MESSAGE_TYPES.forEach((type) => {
        params.append("notification_type", type);
      });
      params.append("status", "unread");

      const { data } = await apiClient.get(`/notifications?${params}`);
      const messages = (
        Array.isArray(data) ? data : data.data || []
      ) as Notification[];
      return messages.length;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};

// Delete message
export const useDeleteMessage = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (messageId: string) => {
      await apiClient.delete(`/notifications/${messageId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["messages"] });
      queryClient.invalidateQueries({ queryKey: ["messages-unread-count"] });
    },
  });
};

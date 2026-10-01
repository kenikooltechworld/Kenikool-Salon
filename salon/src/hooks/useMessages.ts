import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import type { Notification } from "@/types/notification";

interface MessageFilters {
  status?: "read" | "unread" | "all";
  limit?: number;
  offset?: number;
  search?: string;
}

// Fetch messages (inter-department communication)
export const useMessages = (filters?: MessageFilters) => {
  return useQuery({
    queryKey: ["messages", filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.status && filters.status !== "all") params.append("status", filters.status);
      if (filters?.limit) params.append("limit", filters.limit.toString());
      if (filters?.offset) params.append("skip", filters.offset.toString());

      const { data } = await apiClient.get(`/notifications/messages?${params.toString()}`);
      const messages = (Array.isArray(data) ? data : data.data || []) as Notification[];

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
    staleTime: 30000,
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
      const { data } = await apiClient.patch(`/notifications/${messageId}/unread`);
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
      const { data } = await apiClient.get(`/notifications/messages?status=unread&limit=100`);
      const messages = (Array.isArray(data) ? data : data.data || []) as Notification[];
      return messages.length;
    },
    refetchInterval: 30000,
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

// Send inter-department message
export const useSendMessage = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      recipient_type: string;
      role_id?: string;
      recipient_ids?: string[];
      notification_type: string;
      content: string;
      subject?: string;
      channel?: string;
      send_email?: boolean;
    }) => {
      const { data } = await apiClient.post("/notifications/send-message", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["messages"] });
      queryClient.invalidateQueries({ queryKey: ["messages-unread-count"] });
    },
  });
};

// Staff sends message to owner/manager or other staff
export const useSendStaffMessage = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      recipient_type: string;
      recipient_ids?: string[];
      role_id?: string;
      notification_type: string;
      content: string;
      subject?: string;
      channel?: string;
      send_email?: boolean;
    }) => {
      const { data } = await apiClient.post("/notifications/staff/send-message", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["messages"] });
      queryClient.invalidateQueries({ queryKey: ["messages-unread-count"] });
    },
  });
};

// Customer sends message to staff or owner
export const useSendCustomerMessage = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      recipient_type: string;
      recipient_ids?: string[];
      notification_type: string;
      content: string;
      subject?: string;
      channel?: string;
      send_email?: boolean;
    }) => {
      const { data } = await apiClient.post("/notifications/customer/send-message", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["messages"] });
      queryClient.invalidateQueries({ queryKey: ["messages-unread-count"] });
    },
  });
};

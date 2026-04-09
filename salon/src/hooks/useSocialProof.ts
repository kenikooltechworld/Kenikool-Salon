import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface BookingActivity {
  id: string;
  customer_name: string;
  service_name: string;
  booking_type: string;
  created_at: string;
}

export interface SocialMediaPost {
  id: string;
  platform: string;
  media_url: string;
  media_type: string;
  caption?: string;
  permalink?: string;
  likes_count: number;
  comments_count: number;
  published_at: string;
}

export function useRecentBookings(limit: number = 10, hours: number = 24) {
  return useQuery({
    queryKey: ["recent-bookings", limit, hours],
    queryFn: async () => {
      const { data } = await apiClient.get<BookingActivity[]>(
        `/social-proof/recent-bookings?limit=${limit}&hours=${hours}`,
      );
      return data;
    },
    refetchInterval: 60000, // Refetch every minute
  });
}

export function useSocialFeed(platform?: string, limit: number = 12) {
  return useQuery({
    queryKey: ["social-feed", platform, limit],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (platform) params.append("platform", platform);
      params.append("limit", limit.toString());

      const { data } = await apiClient.get<SocialMediaPost[]>(
        `/social-proof/social-feed?${params.toString()}`,
      );
      return data;
    },
  });
}

export function useSyncInstagram() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (syncData: {
      access_token: string;
      user_id: string;
      limit?: number;
    }) => {
      const { data } = await apiClient.post(
        "/social-proof/sync-instagram",
        syncData,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["social-feed"] });
    },
  });
}

export function useTogglePostVisibility() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      postId,
      isActive,
    }: {
      postId: string;
      isActive: boolean;
    }) => {
      const { data } = await apiClient.patch(
        `/social-proof/social-feed/${postId}/toggle?is_active=${isActive}`,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["social-feed"] });
    },
  });
}

export function useDeleteSocialPost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (postId: string) => {
      const { data } = await apiClient.delete(
        `/social-proof/social-feed/${postId}`,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["social-feed"] });
    },
  });
}

export interface VideoTestimonial {
  id: string;
  customer_name: string;
  video_url: string;
  thumbnail_url?: string;
  testimonial_text?: string;
  rating: number;
  created_at: string;
}

export function useVideoTestimonials(limit: number = 10) {
  return useQuery({
    queryKey: ["video-testimonials", limit],
    queryFn: async () => {
      const { data } = await apiClient.get<VideoTestimonial[]>(
        `/social-proof/video-testimonials?limit=${limit}`,
      );
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

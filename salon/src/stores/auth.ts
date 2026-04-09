import { create } from "zustand";
import { persist } from "zustand/middleware";
import { apiClient } from "@/lib/utils/api";
import { queryClient } from "@/lib/react-query";

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  phone: string;
  role: string;
  roleNames: string[];
  tenantId: string;
  avatar?: string;
}

interface AuthState {
  user: User | null;
  permissions: string[];
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setPermissions: (permissions: string[]) => void;
  setIsLoading: (loading: boolean) => void;
  updateUser: (user: Partial<User>) => void;
  logout: () => Promise<void>;
  isAuthenticated: () => boolean;
  hasPermission: (permission: string) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      permissions: [],
      isLoading: false,

      setUser: (user) => set({ user }),
      setPermissions: (permissions) => set({ permissions }),
      setIsLoading: (isLoading) => set({ isLoading }),

      updateUser: (updates) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null,
        })),

      logout: async () => {
        try {
          // Call backend to clear httpOnly cookies
          await apiClient.post("/auth/logout");
        } catch (error) {
          console.error("Logout error:", error);
          // Continue with local logout even if backend call fails
        } finally {
          // Clear React Query cache to prevent stale data from previous tenant
          queryClient.clear();

          // Clear local state
          set({
            user: null,
            permissions: [],
            isLoading: false,
          });
        }
      },

      isAuthenticated: () => {
        const { user } = get();
        return !!user;
      },

      hasPermission: (permission: string) => {
        const { permissions } = get();
        return permissions.includes(permission) || permissions.includes("*");
      },
    }),
    {
      name: "auth-store",
      partialize: (state) => ({
        user: state.user,
        permissions: state.permissions,
      }),
    },
  ),
);

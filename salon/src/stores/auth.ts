import { create } from "zustand";
import type { User } from "./types";

export interface AuthState {
  user: User | null;
  permissions: string[];
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setPermissions: (permissions: string[]) => void;
  setIsLoading: (loading: boolean) => void;
  updateUser: (updates: Partial<User>) => void;
  logout: () => Promise<void>;
  isAuthenticated: () => boolean;
  hasPermission: (permission: string) => boolean;
}

export const useAuthStore = create<AuthState>()((set, get) => ({
  user: null,
  permissions: [],
  isLoading: true,

  setUser: (user) => set({ user }),
  setPermissions: (permissions) => set({ permissions }),
  setIsLoading: (isLoading) => set({ isLoading }),

  updateUser: (updates) =>
    set((state) => ({
      user: state.user ? { ...state.user, ...updates } : null,
    })),

  logout: async () => {
    set({
      user: null,
      permissions: [],
      isLoading: false,
    });
  },

  isAuthenticated: () => {
    const { user } = get();
    return !!user;
  },

  hasPermission: (permission: string) => {
    const { permissions } = get();
    return permissions.includes(permission) || permissions.includes("*");
  },
}));

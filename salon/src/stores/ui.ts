import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface Notification {
  id: string;
  type: "success" | "error" | "warning" | "info";
  message: string;
  duration?: number;
}

interface UIState {
  theme: "default" | "elegant" | "vibrant";
  isDarkMode: boolean;
  modals: Record<string, boolean>;
  notifications: Notification[];
  setTheme: (theme: "default" | "elegant" | "vibrant") => void;
  toggleDarkMode: () => void;
  setDarkMode: (isDark: boolean) => void;
  openModal: (name: string) => void;
  closeModal: (name: string) => void;
  closeAllModals: () => void;
  addNotification: (notification: Omit<Notification, "id">) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  currentTheme: () => string;
  isModalOpen: (name: string) => boolean;
}

export const useUIStore = create<UIState>()(
  persist(
    (set, get) => ({
      theme: "default",
      isDarkMode: false,
      modals: {},
      notifications: [],

      setTheme: (theme) => set({ theme }),

      toggleDarkMode: () => set((state) => ({ isDarkMode: !state.isDarkMode })),

      setDarkMode: (isDark) => set({ isDarkMode: isDark }),

      openModal: (name) =>
        set((state) => ({
          modals: { ...state.modals, [name]: true },
        })),

      closeModal: (name) =>
        set((state) => ({
          modals: { ...state.modals, [name]: false },
        })),

      closeAllModals: () => set({ modals: {} }),

      addNotification: (notification) =>
        set((state) => ({
          notifications: [
            ...state.notifications,
            {
              ...notification,
              id: `${Date.now()}-${Math.random()}`,
            },
          ],
        })),

      removeNotification: (id) =>
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        })),

      clearNotifications: () => set({ notifications: [] }),

      currentTheme: () => {
        const { theme, isDarkMode } = get();
        return isDarkMode ? `${theme}-dark` : theme;
      },

      isModalOpen: (name) => {
        const { modals } = get();
        return modals[name] || false;
      },
    }),
    {
      name: "ui-store",
      partialize: (state) => ({
        theme: state.theme,
        isDarkMode: state.isDarkMode,
      }),
    },
  ),
);

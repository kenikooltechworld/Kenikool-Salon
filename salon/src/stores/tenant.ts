import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface TenantSettings {
  brandingLogoUrl?: string;
  primaryColor?: string;
  secondaryColor?: string;
  featuresEnabled?: string[];
  customDomain?: string;
  timezone?: string;
  language?: string;
}

export interface Tenant {
  id: string;
  name: string;
  subdomain: string;
  subscriptionTier: "starter" | "professional" | "enterprise";
  status: "active" | "suspended" | "deleted";
  isPublished: boolean;
  settings?: TenantSettings;
}

interface TenantState {
  currentTenant: Tenant | null;
  settings: TenantSettings | null;
  isLoading: boolean;
  setTenant: (tenant: Tenant | null) => void;
  setSettings: (settings: TenantSettings | null) => void;
  updateSettings: (updates: Partial<TenantSettings>) => void;
  setIsLoading: (loading: boolean) => void;
  tenantId: () => string | null;
  tenantName: () => string | null;
  isFeatureEnabled: (feature: string) => boolean;
}

export const useTenantStore = create<TenantState>()(
  persist(
    (set, get) => ({
      currentTenant: null,
      settings: null,
      isLoading: false,

      setTenant: (tenant) => set({ currentTenant: tenant }),
      setSettings: (settings) => set({ settings }),

      updateSettings: (updates) =>
        set((state) => ({
          settings: state.settings
            ? { ...state.settings, ...updates }
            : updates,
        })),

      setIsLoading: (isLoading) => set({ isLoading }),

      tenantId: () => {
        const { currentTenant } = get();
        return currentTenant?.id || null;
      },

      tenantName: () => {
        const { currentTenant } = get();
        return currentTenant?.name || null;
      },

      isFeatureEnabled: (feature: string) => {
        const { settings } = get();
        return settings?.featuresEnabled?.includes(feature) || false;
      },
    }),
    {
      name: "tenant-store",
      partialize: (state) => ({
        currentTenant: state.currentTenant,
        settings: state.settings,
      }),
    },
  ),
);

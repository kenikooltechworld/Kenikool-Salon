import { create } from "zustand";
import type { BookingFormData, BookingFilters } from "@/types";

interface BookingsStore {
  // Wizard state
  wizardStep: number;
  formData: BookingFormData;
  setWizardStep: (step: number) => void;
  updateFormData: (data: Partial<BookingFormData>) => void;
  resetFormData: () => void;

  // Filters state
  filters: BookingFilters;
  setFilters: (filters: BookingFilters) => void;
  resetFilters: () => void;

  // UI state
  selectedBookingId: string | null;
  setSelectedBookingId: (id: string | null) => void;
  calendarView: "day" | "week" | "month";
  setCalendarView: (view: "day" | "week" | "month") => void;
  isCreateModalOpen: boolean;
  setIsCreateModalOpen: (open: boolean) => void;
  isDetailModalOpen: boolean;
  setIsDetailModalOpen: (open: boolean) => void;
}

const initialFormData: BookingFormData = {
  serviceId: undefined,
  staffId: undefined,
  customerId: undefined,
  startTime: undefined,
  endTime: undefined,
  notes: undefined,
};

const initialFilters: BookingFilters = {
  page: 1,
  limit: 10,
};

export const useBookingsStore = create<BookingsStore>((set) => ({
  // Wizard state
  wizardStep: 1,
  formData: initialFormData,
  setWizardStep: (step) => set({ wizardStep: step }),
  updateFormData: (data) =>
    set((state) => ({
      formData: { ...state.formData, ...data },
    })),
  resetFormData: () => set({ formData: initialFormData, wizardStep: 1 }),

  // Filters state
  filters: initialFilters,
  setFilters: (filters) => set({ filters }),
  resetFilters: () => set({ filters: initialFilters }),

  // UI state
  selectedBookingId: null,
  setSelectedBookingId: (id) => set({ selectedBookingId: id }),
  calendarView: "month",
  setCalendarView: (view) => set({ calendarView: view }),
  isCreateModalOpen: false,
  setIsCreateModalOpen: (open) => set({ isCreateModalOpen: open }),
  isDetailModalOpen: false,
  setIsDetailModalOpen: (open) => set({ isDetailModalOpen: open }),
}));

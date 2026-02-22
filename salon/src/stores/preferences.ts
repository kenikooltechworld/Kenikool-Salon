import { create } from "zustand";
import { persist } from "zustand/middleware";

interface PreferencesState {
  language: string;
  timezone: string;
  dateFormat: string;
  timeFormat: string;
  setLanguage: (language: string) => void;
  setTimezone: (timezone: string) => void;
  setDateFormat: (format: string) => void;
  setTimeFormat: (format: string) => void;
}

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set) => ({
      language: "en",
      timezone: "Africa/Lagos",
      dateFormat: "MMM DD, YYYY",
      timeFormat: "12h",

      setLanguage: (language) => set({ language }),
      setTimezone: (timezone) => set({ timezone }),
      setDateFormat: (dateFormat) => set({ dateFormat }),
      setTimeFormat: (timeFormat) => set({ timeFormat }),
    }),
    {
      name: "preferences-store",
    },
  ),
);

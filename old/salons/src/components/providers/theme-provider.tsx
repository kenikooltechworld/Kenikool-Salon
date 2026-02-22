/**
 * Theme Provider Component
 * Manages theme state and provides theme context to the application
 */

import React, { createContext, useContext, useEffect, useState } from "react";
import {
  Theme,
  ThemeName,
  ThemeMode,
  getTheme,
  applyTheme,
} from "@/lib/themes";

interface ThemeContextType {
  theme: Theme;
  themeName: ThemeName;
  themeMode: ThemeMode;
  setThemeName: (name: ThemeName) => void;
  setThemeMode: (mode: ThemeMode) => void;
  toggleThemeMode: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: ThemeName;
  defaultMode?: ThemeMode;
  storageKey?: string;
}

export function ThemeProvider({
  children,
  defaultTheme = "default",
  defaultMode = "light",
  storageKey = "kenikool-theme",
}: ThemeProviderProps) {
  const [mounted, setMounted] = useState(false);
  const [themeName, setThemeNameState] = useState<ThemeName>(defaultTheme);
  const [themeMode, setThemeModeState] = useState<ThemeMode>(defaultMode);
  const [theme, setTheme] = useState<Theme>(
    getTheme(defaultTheme, defaultMode)
  );

  // Load theme from localStorage on mount
  useEffect(() => {
    setMounted(true);

    try {
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        const { name, mode } = JSON.parse(stored);
        if (name) setThemeNameState(name);
        if (mode) setThemeModeState(mode);
      }
    } catch (error) {
      console.error("Failed to load theme from storage:", error);
    }
  }, [storageKey]);

  // Update theme when name or mode changes
  useEffect(() => {
    if (!mounted) return;

    const newTheme = getTheme(themeName, themeMode);
    setTheme(newTheme);
    applyTheme(newTheme);

    // Save to localStorage
    try {
      localStorage.setItem(
        storageKey,
        JSON.stringify({ name: themeName, mode: themeMode })
      );
    } catch (error) {
      console.error("Failed to save theme to storage:", error);
    }
  }, [themeName, themeMode, storageKey, mounted]);

  const setThemeName = (name: ThemeName) => {
    setThemeNameState(name);
  };

  const setThemeMode = (mode: ThemeMode) => {
    setThemeModeState(mode);
  };

  const toggleThemeMode = () => {
    setThemeModeState((prev) => (prev === "light" ? "dark" : "light"));
  };

  const value: ThemeContextType = {
    theme,
    themeName,
    themeMode,
    setThemeName,
    setThemeMode,
    toggleThemeMode,
  };

  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}

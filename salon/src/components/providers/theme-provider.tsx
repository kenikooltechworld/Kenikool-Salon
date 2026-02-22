import React, { createContext, useContext, useEffect, useState } from "react";

export type ThemeMode = "light" | "dark";
export type ThemeName = "default" | "elegant" | "vibrant";

interface ThemeContextType {
  themeName: ThemeName;
  themeMode: ThemeMode;
  setThemeName: (name: ThemeName) => void;
  toggleThemeMode: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [themeName, setThemeNameState] = useState<ThemeName>(() => {
    if (typeof window !== "undefined") {
      return (localStorage.getItem("themeName") || "default") as ThemeName;
    }
    return "default";
  });

  const [themeMode, setThemeModeState] = useState<ThemeMode>(() => {
    if (typeof window !== "undefined") {
      return (localStorage.getItem("themeMode") || "light") as ThemeMode;
    }
    return "light";
  });

  // Apply theme on mount and when theme changes
  useEffect(() => {
    applyThemeToDOM(themeName, themeMode);
  }, [themeName, themeMode]);

  const setThemeName = (name: ThemeName) => {
    setThemeNameState(name);
    localStorage.setItem("themeName", name);
  };

  const toggleThemeMode = () => {
    const newMode = themeMode === "light" ? "dark" : "light";
    setThemeModeState(newMode);
    localStorage.setItem("themeMode", newMode);
  };

  return (
    <ThemeContext.Provider
      value={{ themeName, themeMode, setThemeName, toggleThemeMode }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within ThemeProvider");
  }
  return context;
}

// Simple theme application function
function applyThemeToDOM(themeName: ThemeName, themeMode: ThemeMode) {
  const root = document.documentElement;

  // Set data attributes for theme and mode
  root.setAttribute("data-theme", themeName);
  root.setAttribute("data-mode", themeMode);

  // Apply basic theme colors via CSS variables
  const themes: Record<ThemeName, Record<ThemeMode, Record<string, string>>> = {
    default: {
      light: {
        "--primary": "#0ea5e9",
        "--primary-foreground": "#ffffff",
        "--secondary": "#14b8a6",
        "--secondary-foreground": "#ffffff",
        "--background": "#f0f9ff",
        "--foreground": "#0c4a6e",
        "--card": "#ffffff",
        "--border": "#bae6fd",
        "--muted": "#e0f2fe",
        "--muted-foreground": "#0369a1",
      },
      dark: {
        "--primary": "#22d3ee",
        "--primary-foreground": "#0c4a6e",
        "--secondary": "#2dd4bf",
        "--secondary-foreground": "#134e4a",
        "--background": "#0c4a6e",
        "--foreground": "#f0f9ff",
        "--card": "#075985",
        "--border": "#0369a1",
        "--muted": "#0369a1",
        "--muted-foreground": "#bae6fd",
      },
    },
    elegant: {
      light: {
        "--primary": "#7c3aed",
        "--primary-foreground": "#ffffff",
        "--secondary": "#f472b6",
        "--secondary-foreground": "#ffffff",
        "--background": "#faf5ff",
        "--foreground": "#3b0764",
        "--card": "#ffffff",
        "--border": "#e9d5ff",
        "--muted": "#f3e8ff",
        "--muted-foreground": "#6b21a8",
      },
      dark: {
        "--primary": "#a78bfa",
        "--primary-foreground": "#1e1b4b",
        "--secondary": "#f9a8d4",
        "--secondary-foreground": "#500724",
        "--background": "#1e1b4b",
        "--foreground": "#faf5ff",
        "--card": "#312e81",
        "--border": "#4c1d95",
        "--muted": "#4c1d95",
        "--muted-foreground": "#e9d5ff",
      },
    },
    vibrant: {
      light: {
        "--primary": "#d946ef",
        "--primary-foreground": "#ffffff",
        "--secondary": "#f97316",
        "--secondary-foreground": "#ffffff",
        "--background": "#fff7ed",
        "--foreground": "#7c2d12",
        "--card": "#ffffff",
        "--border": "#fed7aa",
        "--muted": "#ffedd5",
        "--muted-foreground": "#c2410c",
      },
      dark: {
        "--primary": "#e879f9",
        "--primary-foreground": "#4a044e",
        "--secondary": "#fb923c",
        "--secondary-foreground": "#431407",
        "--background": "#431407",
        "--foreground": "#fff7ed",
        "--card": "#7c2d12",
        "--border": "#9a3412",
        "--muted": "#9a3412",
        "--muted-foreground": "#fed7aa",
      },
    },
  };

  const themeColors = themes[themeName][themeMode];
  Object.entries(themeColors).forEach(([key, value]) => {
    root.style.setProperty(key, value);
  });
}

/**
 * Ocean Breeze Theme - Fresh & Professional
 * Vibrant blue-teal gradient with coral accents
 * Perfect for modern, trustworthy salon brands
 */

import type { Theme } from "./types";

export const defaultLightTheme: Theme = {
  name: "default",
  mode: "light",
  colors: {
    // Primary - Vibrant Ocean Blue
    primary: "#0ea5e9",
    primaryHover: "#0284c7",
    primaryActive: "#0369a1",
    primaryForeground: "#ffffff",

    // Secondary - Fresh Teal
    secondary: "#14b8a6",
    secondaryHover: "#0d9488",
    secondaryActive: "#0f766e",
    secondaryForeground: "#ffffff",

    // Accent - Coral Pink
    accent: "#f43f5e",
    accentHover: "#e11d48",
    accentActive: "#be123c",
    accentForeground: "#ffffff",

    // Neutral - Soft sky backgrounds
    background: "#f0f9ff",
    foreground: "#0c4a6e",
    card: "#ffffff",
    cardForeground: "#0c4a6e",
    popover: "#ffffff",
    popoverForeground: "#0c4a6e",

    // Borders - Ocean tint
    border: "#bae6fd",
    input: "#e0f2fe",
    ring: "#0ea5e9",

    // Status - Clear and vibrant
    success: "#10b981",
    successForeground: "#ffffff",
    warning: "#f59e0b",
    warningForeground: "#ffffff",
    error: "#ef4444",
    errorForeground: "#ffffff",
    info: "#06b6d4",
    infoForeground: "#ffffff",

    // Muted - Light cyan
    muted: "#e0f2fe",
    mutedForeground: "#0369a1",

    // Destructive
    destructive: "#dc2626",
    destructiveForeground: "#ffffff",
  },
  radius: {
    sm: "0.375rem",
    md: "0.5rem",
    lg: "0.75rem",
    xl: "1rem",
    full: "9999px",
  },
  shadows: {
    sm: "0 2px 4px 0 rgba(14, 165, 233, 0.1)",
    md: "0 4px 8px -1px rgba(14, 165, 233, 0.15), 0 2px 4px -2px rgba(14, 165, 233, 0.1)",
    lg: "0 10px 20px -3px rgba(14, 165, 233, 0.2), 0 4px 6px -4px rgba(14, 165, 233, 0.1)",
    xl: "0 20px 30px -5px rgba(14, 165, 233, 0.25), 0 8px 10px -6px rgba(14, 165, 233, 0.1)",
  },
  typography: {
    fontFamily: {
      sans: "var(--font-geist-sans)",
      mono: "var(--font-geist-mono)",
    },
    fontSize: {
      xs: "0.75rem",
      sm: "0.875rem",
      base: "1rem",
      lg: "1.125rem",
      xl: "1.25rem",
      "2xl": "1.5rem",
      "3xl": "1.875rem",
      "4xl": "2.25rem",
    },
    fontWeight: {
      normal: "400",
      medium: "500",
      semibold: "600",
      bold: "700",
    },
  },
};

export const defaultDarkTheme: Theme = {
  ...defaultLightTheme,
  mode: "dark",
  colors: {
    // Primary - Bright cyan
    primary: "#22d3ee",
    primaryHover: "#06b6d4",
    primaryActive: "#0891b2",
    primaryForeground: "#0c4a6e",

    // Secondary - Bright teal
    secondary: "#2dd4bf",
    secondaryHover: "#14b8a6",
    secondaryActive: "#0d9488",
    secondaryForeground: "#134e4a",

    // Accent - Bright coral
    accent: "#fb7185",
    accentHover: "#f43f5e",
    accentActive: "#e11d48",
    accentForeground: "#881337",

    // Neutral - Deep ocean
    background: "#0c4a6e",
    foreground: "#f0f9ff",
    card: "#075985",
    cardForeground: "#f0f9ff",
    popover: "#075985",
    popoverForeground: "#f0f9ff",

    // Borders
    border: "#0369a1",
    input: "#0284c7",
    ring: "#22d3ee",

    // Status
    success: "#34d399",
    successForeground: "#064e3b",
    warning: "#fbbf24",
    warningForeground: "#78350f",
    error: "#f87171",
    errorForeground: "#7f1d1d",
    info: "#22d3ee",
    infoForeground: "#0c4a6e",

    // Muted
    muted: "#0369a1",
    mutedForeground: "#bae6fd",

    // Destructive
    destructive: "#f87171",
    destructiveForeground: "#7f1d1d",
  },
};

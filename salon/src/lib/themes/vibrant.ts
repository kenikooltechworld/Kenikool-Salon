/**
 * Sunset Vibes Theme - Bold & Energetic
 * Vibrant orange, magenta, and lime green palette
 * Perfect for trendy, youthful, and creative salons
 */

import type { Theme } from "./types";

export const vibrantLightTheme: Theme = {
  name: "vibrant",
  mode: "light",
  colors: {
    // Primary - Electric Magenta
    primary: "#d946ef",
    primaryHover: "#c026d3",
    primaryActive: "#a21caf",
    primaryForeground: "#ffffff",

    // Secondary - Vibrant Orange
    secondary: "#f97316",
    secondaryHover: "#ea580c",
    secondaryActive: "#c2410c",
    secondaryForeground: "#ffffff",

    // Accent - Electric Lime
    accent: "#84cc16",
    accentHover: "#65a30d",
    accentActive: "#4d7c0f",
    accentForeground: "#1a2e05",

    // Neutral - Soft warm backgrounds
    background: "#fff7ed",
    foreground: "#7c2d12",
    card: "#ffffff",
    cardForeground: "#7c2d12",
    popover: "#ffffff",
    popoverForeground: "#7c2d12",

    // Borders - Warm orange tint
    border: "#fed7aa",
    input: "#ffedd5",
    ring: "#d946ef",

    // Status
    success: "#22c55e",
    successForeground: "#ffffff",
    warning: "#f59e0b",
    warningForeground: "#ffffff",
    error: "#ef4444",
    errorForeground: "#ffffff",
    info: "#06b6d4",
    infoForeground: "#ffffff",

    // Muted - Soft peach
    muted: "#ffedd5",
    mutedForeground: "#c2410c",

    // Destructive
    destructive: "#dc2626",
    destructiveForeground: "#ffffff",
  },
  radius: {
    sm: "0.625rem",
    md: "0.875rem",
    lg: "1.125rem",
    xl: "1.5rem",
    full: "9999px",
  },
  shadows: {
    sm: "0 3px 6px 0 rgba(217, 70, 239, 0.15)",
    md: "0 8px 16px -2px rgba(217, 70, 239, 0.22), 0 4px 8px -4px rgba(249, 115, 22, 0.15)",
    lg: "0 16px 32px -4px rgba(217, 70, 239, 0.28), 0 8px 16px -8px rgba(249, 115, 22, 0.18)",
    xl: "0 32px 48px -8px rgba(217, 70, 239, 0.35), 0 12px 20px -10px rgba(249, 115, 22, 0.22)",
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

export const vibrantDarkTheme: Theme = {
  ...vibrantLightTheme,
  mode: "dark",
  colors: {
    // Primary - Bright fuchsia
    primary: "#e879f9",
    primaryHover: "#d946ef",
    primaryActive: "#c026d3",
    primaryForeground: "#4a044e",

    // Secondary - Bright orange
    secondary: "#fb923c",
    secondaryHover: "#f97316",
    secondaryActive: "#ea580c",
    secondaryForeground: "#431407",

    // Accent - Bright lime
    accent: "#a3e635",
    accentHover: "#84cc16",
    accentActive: "#65a30d",
    accentForeground: "#1a2e05",

    // Neutral - Deep warm
    background: "#431407",
    foreground: "#fff7ed",
    card: "#7c2d12",
    cardForeground: "#fff7ed",
    popover: "#7c2d12",
    popoverForeground: "#fff7ed",

    // Borders
    border: "#9a3412",
    input: "#c2410c",
    ring: "#e879f9",

    // Status
    success: "#4ade80",
    successForeground: "#052e16",
    warning: "#fbbf24",
    warningForeground: "#451a03",
    error: "#f87171",
    errorForeground: "#450a0a",
    info: "#22d3ee",
    infoForeground: "#083344",

    // Muted
    muted: "#9a3412",
    mutedForeground: "#fed7aa",

    // Destructive
    destructive: "#f87171",
    destructiveForeground: "#450a0a",
  },
};

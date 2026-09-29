/**
 * Royal Elegance Theme - Luxurious & Sophisticated
 * Deep purple, gold, and rose gold palette
 * Perfect for high-end, premium salon experiences
 */

import type { Theme } from "./types";

export const elegantLightTheme: Theme = {
  name: "elegant",
  mode: "light",
  colors: {
    // Primary - Royal Purple
    primary: "#7c3aed",
    primaryHover: "#6d28d9",
    primaryActive: "#5b21b6",
    primaryForeground: "#ffffff",

    // Secondary - Rose Gold
    secondary: "#f472b6",
    secondaryHover: "#ec4899",
    secondaryActive: "#db2777",
    secondaryForeground: "#ffffff",

    // Accent - Luxurious Gold
    accent: "#eab308",
    accentHover: "#ca8a04",
    accentActive: "#a16207",
    accentForeground: "#422006",

    // Neutral - Warm cream backgrounds
    background: "#faf5ff",
    foreground: "#3b0764",
    card: "#ffffff",
    cardForeground: "#3b0764",
    popover: "#ffffff",
    popoverForeground: "#3b0764",

    // Borders - Purple tint
    border: "#e9d5ff",
    input: "#f3e8ff",
    ring: "#7c3aed",

    // Status
    success: "#22c55e",
    successForeground: "#ffffff",
    warning: "#f59e0b",
    warningForeground: "#ffffff",
    error: "#dc2626",
    errorForeground: "#ffffff",
    info: "#8b5cf6",
    infoForeground: "#ffffff",

    // Muted - Soft lavender
    muted: "#f3e8ff",
    mutedForeground: "#6b21a8",

    // Destructive
    destructive: "#be123c",
    destructiveForeground: "#ffffff",
  },
  radius: {
    sm: "0.5rem",
    md: "0.75rem",
    lg: "1rem",
    xl: "1.5rem",
    full: "9999px",
  },
  shadows: {
    sm: "0 2px 6px 0 rgba(124, 58, 237, 0.12)",
    md: "0 6px 12px -2px rgba(124, 58, 237, 0.18), 0 3px 6px -3px rgba(124, 58, 237, 0.12)",
    lg: "0 12px 24px -4px rgba(124, 58, 237, 0.22), 0 6px 12px -6px rgba(124, 58, 237, 0.14)",
    xl: "0 24px 40px -8px rgba(124, 58, 237, 0.28), 0 10px 16px -8px rgba(124, 58, 237, 0.16)",
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

export const elegantDarkTheme: Theme = {
  ...elegantLightTheme,
  mode: "dark",
  colors: {
    // Primary - Bright violet
    primary: "#a78bfa",
    primaryHover: "#8b5cf6",
    primaryActive: "#7c3aed",
    primaryForeground: "#1e1b4b",

    // Secondary - Bright rose
    secondary: "#f9a8d4",
    secondaryHover: "#f472b6",
    secondaryActive: "#ec4899",
    secondaryForeground: "#500724",

    // Accent - Bright gold
    accent: "#fde047",
    accentHover: "#facc15",
    accentActive: "#eab308",
    accentForeground: "#422006",

    // Neutral - Deep purple
    background: "#1e1b4b",
    foreground: "#faf5ff",
    card: "#312e81",
    cardForeground: "#faf5ff",
    popover: "#312e81",
    popoverForeground: "#faf5ff",

    // Borders
    border: "#4c1d95",
    input: "#5b21b6",
    ring: "#a78bfa",

    // Status
    success: "#4ade80",
    successForeground: "#052e16",
    warning: "#fbbf24",
    warningForeground: "#451a03",
    error: "#f87171",
    errorForeground: "#450a0a",
    info: "#a78bfa",
    infoForeground: "#1e1b4b",

    // Muted
    muted: "#4c1d95",
    mutedForeground: "#e9d5ff",

    // Destructive
    destructive: "#fb7185",
    destructiveForeground: "#450a0a",
  },
};

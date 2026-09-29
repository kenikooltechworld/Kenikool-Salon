/**
 * Theme System - Central Export
 */

import type { Theme, ThemeName, ThemeMode } from "./types";
import { defaultLightTheme, defaultDarkTheme } from "./default";
import { elegantLightTheme, elegantDarkTheme } from "./elegant";
import { vibrantLightTheme, vibrantDarkTheme } from "./vibrant";

export * from "./types";
export { defaultLightTheme, defaultDarkTheme } from "./default";
export { elegantLightTheme, elegantDarkTheme } from "./elegant";
export { vibrantLightTheme, vibrantDarkTheme } from "./vibrant";

export const themes: Record<ThemeName, Record<ThemeMode, Theme>> = {
  default: {
    light: defaultLightTheme,
    dark: defaultDarkTheme,
  },
  elegant: {
    light: elegantLightTheme,
    dark: elegantDarkTheme,
  },
  vibrant: {
    light: vibrantLightTheme,
    dark: vibrantDarkTheme,
  },
};

export function getTheme(name: ThemeName, mode: ThemeMode): Theme {
  return themes[name][mode];
}

export function applyTheme(theme: Theme): void {
  const root = document.documentElement;

  // Apply colors as CSS variables
  Object.entries(theme.colors).forEach(([key, value]) => {
    const cssVarName = `--${key.replace(/([A-Z])/g, "-$1").toLowerCase()}`;
    root.style.setProperty(cssVarName, value);
  });

  // Apply radius
  Object.entries(theme.radius).forEach(([key, value]) => {
    root.style.setProperty(`--radius-${key}`, value);
  });

  // Apply shadows
  Object.entries(theme.shadows).forEach(([key, value]) => {
    root.style.setProperty(`--shadow-${key}`, value);
  });

  // Apply typography
  Object.entries(theme.typography.fontSize).forEach(([key, value]) => {
    root.style.setProperty(`--font-size-${key}`, value);
  });

  Object.entries(theme.typography.fontWeight).forEach(([key, value]) => {
    root.style.setProperty(`--font-weight-${key}`, value);
  });

  // Set data attributes for theme and mode
  root.setAttribute("data-theme", theme.name);
  root.setAttribute("data-mode", theme.mode);
}

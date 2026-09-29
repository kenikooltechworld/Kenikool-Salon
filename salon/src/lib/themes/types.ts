export type ThemeMode = "light" | "dark";

export type ThemeName = "default" | "elegant" | "vibrant";

export interface ThemeColors {
  primary: string;
  primaryHover: string;
  primaryActive: string;
  primaryForeground: string;
  secondary: string;
  secondaryHover: string;
  secondaryActive: string;
  secondaryForeground: string;
  accent: string;
  accentHover: string;
  accentActive: string;
  accentForeground: string;
  background: string;
  foreground: string;
  card: string;
  cardForeground: string;
  popover: string;
  popoverForeground: string;
  border: string;
  input: string;
  ring: string;
  success: string;
  successForeground: string;
  warning: string;
  warningForeground: string;
  error: string;
  errorForeground: string;
  info: string;
  infoForeground: string;
  muted: string;
  mutedForeground: string;
  destructive: string;
  destructiveForeground: string;
}

export interface Theme {
  name: ThemeName;
  mode: ThemeMode;
  colors: ThemeColors;
  radius: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
    full: string;
  };
  shadows: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  typography: {
    fontFamily: {
      sans: string;
      mono: string;
    };
    fontSize: {
      xs: string;
      sm: string;
      base: string;
      lg: string;
      xl: string;
      "2xl": string;
      "3xl": string;
      "4xl": string;
    };
    fontWeight: {
      normal: string;
      medium: string;
      semibold: string;
      bold: string;
    };
  };
}

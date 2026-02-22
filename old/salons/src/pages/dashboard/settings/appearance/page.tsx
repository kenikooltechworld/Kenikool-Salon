import { Card } from "@/components/ui/card";
import { MoonIcon, SunIcon, MonitorIcon } from "@/components/icons";
import { useTheme } from "@/components/providers/theme-provider";
import { useState, useEffect } from "react";

export default function AppearanceSettingsPage() {
  const { themeMode, setThemeMode } = useTheme();
  const [useSystemTheme, setUseSystemTheme] = useState(false);

  // Initialize from localStorage using lazy initialization
  const [compactMode, setCompactMode] = useState(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("compactMode") === "true";
    }
    return false;
  });

  const [animationsEnabled, setAnimationsEnabled] = useState(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("animationsEnabled");
      return saved !== "false";
    }
    return true;
  });

  // Get system preference without causing effect issues
  const getSystemPreference = () => {
    if (typeof window === "undefined") return "light";
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  };

  // Apply preferences on mount
  useEffect(() => {
    // Apply compact mode class to body
    if (compactMode) {
      document.body.classList.add("compact-mode");
    }

    // Apply animations preference
    if (!animationsEnabled) {
      document.body.classList.add("reduce-motion");
    }
  }, [animationsEnabled, compactMode]);

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const handler = (e: MediaQueryListEvent) => {
      if (useSystemTheme) {
        setThemeMode(e.matches ? "dark" : "light");
      }
    };

    mediaQuery.addEventListener("change", handler);
    return () => mediaQuery.removeEventListener("change", handler);
  }, [useSystemTheme, setThemeMode]);

  const handleThemeChange = (mode: "light" | "dark" | "system") => {
    if (mode === "system") {
      setUseSystemTheme(true);
      const currentSystemPref = getSystemPreference();
      setThemeMode(currentSystemPref);
    } else {
      setUseSystemTheme(false);
      setThemeMode(mode);
    }
  };

  const handleCompactModeToggle = () => {
    const newValue = !compactMode;
    setCompactMode(newValue);
    localStorage.setItem("compactMode", String(newValue));

    if (newValue) {
      document.body.classList.add("compact-mode");
    } else {
      document.body.classList.remove("compact-mode");
    }
  };

  const handleAnimationsToggle = () => {
    const newValue = !animationsEnabled;
    setAnimationsEnabled(newValue);
    localStorage.setItem("animationsEnabled", String(newValue));

    if (!newValue) {
      document.body.classList.add("reduce-motion");
    } else {
      document.body.classList.remove("reduce-motion");
    }
  };

  const getCurrentTheme = () => {
    if (useSystemTheme) return "system";
    return themeMode;
  };

  const themes = [
    { value: "light" as const, label: "Light", icon: SunIcon },
    { value: "dark" as const, label: "Dark", icon: MoonIcon },
    { value: "system" as const, label: "System", icon: MonitorIcon },
  ];

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">
          Appearance Settings
        </h1>
        <p className="text-muted-foreground">
          Customize the look and feel of your dashboard
        </p>
      </div>

      {/* Theme Selection */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">
          Theme Preference
        </h2>
        <p className="text-sm text-muted-foreground mb-6">
          Choose how the dashboard appears to you
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {themes.map((themeOption) => {
            const Icon = themeOption.icon;
            const isSelected = getCurrentTheme() === themeOption.value;

            return (
              <button
                key={themeOption.value}
                onClick={() => handleThemeChange(themeOption.value)}
                className={`p-6 rounded-lg border-2 transition-all cursor-pointer ${
                  isSelected
                    ? "border-[var(--primary)] bg-[var(--primary)]/5"
                    : "border-[var(--border)] hover:border-[var(--primary)]/50"
                }`}
              >
                <Icon size={32} className="mx-auto mb-3" />
                <p className="font-medium text-foreground">
                  {themeOption.label}
                </p>
                {themeOption.value === "system" && (
                  <p className="text-xs text-muted-foreground mt-1">
                    Matches your device
                  </p>
                )}
              </button>
            );
          })}
        </div>
      </Card>

      {/* Display Preferences */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">
          Display Preferences
        </h2>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-foreground">Compact Mode</p>
              <p className="text-sm text-muted-foreground">
                Reduce spacing for more content
              </p>
            </div>
            <button
              onClick={handleCompactModeToggle}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors cursor-pointer ${
                compactMode
                  ? "bg-[var(--primary)]"
                  : "bg-gray-300 dark:bg-gray-600"
              }`}
              role="switch"
              aria-checked={compactMode}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  compactMode ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-foreground">Animations</p>
              <p className="text-sm text-muted-foreground">
                Enable smooth transitions
              </p>
            </div>
            <button
              onClick={handleAnimationsToggle}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors cursor-pointer ${
                animationsEnabled
                  ? "bg-[var(--primary)]"
                  : "bg-gray-300 dark:bg-gray-600"
              }`}
              role="switch"
              aria-checked={animationsEnabled}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  animationsEnabled ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
}

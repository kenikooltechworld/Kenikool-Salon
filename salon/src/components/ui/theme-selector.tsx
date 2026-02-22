import { useState, useRef, useEffect } from "react";
import { useTheme } from "@/components/providers/theme-provider";
import { Button } from "@/components/ui/button";
import { MoonIcon, SunIcon, CheckIcon } from "@/components/icons";
import type {
  ThemeName,
  ThemeMode,
} from "@/components/providers/theme-provider";

interface ThemeSelectorProps {
  variant?: "icon" | "full";
  showLabel?: boolean;
}

const themeOptions: { name: ThemeName; label: string; description: string }[] =
  [
    { name: "default", label: "Default", description: "Clean and modern" },
    {
      name: "elegant",
      label: "Elegant",
      description: "Sophisticated and refined",
    },
    { name: "vibrant", label: "Vibrant", description: "Bold and colorful" },
  ];

export function ThemeSelector({
  variant = "icon",
  showLabel = false,
}: ThemeSelectorProps) {
  const { themeName, themeMode, setThemeName, toggleThemeMode } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleThemeSelect = (name: ThemeName) => {
    setThemeName(name);
    setIsOpen(false);
  };

  if (variant === "icon") {
    return (
      <div className="relative" ref={dropdownRef}>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsOpen(!isOpen)}
          title="Change theme"
        >
          {themeMode === "light" ? (
            <SunIcon size={20} />
          ) : (
            <MoonIcon size={20} />
          )}
        </Button>

        {isOpen && (
          <div className="absolute right-0 mt-2 w-64 bg-[var(--card)] border border-[var(--border)] rounded-[var(--radius-md)] shadow-[var(--shadow-lg)] z-50">
            <div className="p-3 border-b border-[var(--border)]">
              <h3 className="font-semibold text-[var(--foreground)] text-sm">
                Theme Settings
              </h3>
            </div>

            {/* Mode Toggle */}
            <div className="p-3 border-b border-[var(--border)]">
              <p className="text-xs text-[var(--muted-foreground)] mb-2">
                Mode
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    if (themeMode !== "light") toggleThemeMode();
                  }}
                  className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-[var(--radius-sm)] transition-colors ${
                    themeMode === "light"
                      ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
                      : "bg-[var(--muted)] text-[var(--muted-foreground)] hover:bg-[var(--muted)]/80"
                  }`}
                >
                  <SunIcon size={16} />
                  <span className="text-sm">Light</span>
                </button>
                <button
                  onClick={() => {
                    if (themeMode !== "dark") toggleThemeMode();
                  }}
                  className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-[var(--radius-sm)] transition-colors ${
                    themeMode === "dark"
                      ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
                      : "bg-[var(--muted)] text-[var(--muted-foreground)] hover:bg-[var(--muted)]/80"
                  }`}
                >
                  <MoonIcon size={16} />
                  <span className="text-sm">Dark</span>
                </button>
              </div>
            </div>

            {/* Theme Selection */}
            <div className="p-3">
              <p className="text-xs text-[var(--muted-foreground)] mb-2">
                Theme
              </p>
              <div className="space-y-1">
                {themeOptions.map((option) => (
                  <button
                    key={option.name}
                    onClick={() => handleThemeSelect(option.name)}
                    className="w-full flex items-center justify-between px-3 py-2 rounded-[var(--radius-sm)] hover:bg-[var(--muted)] transition-colors text-left"
                  >
                    <div>
                      <p className="text-sm font-medium text-[var(--foreground)]">
                        {option.label}
                      </p>
                      <p className="text-xs text-[var(--muted-foreground)]">
                        {option.description}
                      </p>
                    </div>
                    {themeName === option.name && (
                      <CheckIcon size={16} className="text-[var(--primary)]" />
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Full variant with label
  return (
    <div className="relative" ref={dropdownRef}>
      <Button
        variant="outline"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2"
      >
        {themeMode === "light" ? <SunIcon size={18} /> : <MoonIcon size={18} />}
        {showLabel && <span className="text-sm">Theme</span>}
      </Button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-[var(--card)] border border-[var(--border)] rounded-[var(--radius-md)] shadow-[var(--shadow-lg)] z-50">
          <div className="p-3 border-b border-[var(--border)]">
            <h3 className="font-semibold text-[var(--foreground)] text-sm">
              Theme Settings
            </h3>
          </div>

          {/* Mode Toggle */}
          <div className="p-3 border-b border-[var(--border)]">
            <p className="text-xs text-[var(--muted-foreground)] mb-2">Mode</p>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  if (themeMode !== "light") toggleThemeMode();
                }}
                className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-[var(--radius-sm)] transition-colors ${
                  themeMode === "light"
                    ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
                    : "bg-[var(--muted)] text-[var(--muted-foreground)] hover:bg-[var(--muted)]/80"
                }`}
              >
                <SunIcon size={16} />
                <span className="text-sm">Light</span>
              </button>
              <button
                onClick={() => {
                  if (themeMode !== "dark") toggleThemeMode();
                }}
                className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-[var(--radius-sm)] transition-colors ${
                  themeMode === "dark"
                    ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
                    : "bg-[var(--muted)] text-[var(--muted-foreground)] hover:bg-[var(--muted)]/80"
                }`}
              >
                <MoonIcon size={16} />
                <span className="text-sm">Dark</span>
              </button>
            </div>
          </div>

          {/* Theme Selection */}
          <div className="p-3">
            <p className="text-xs text-[var(--muted-foreground)] mb-2">Theme</p>
            <div className="space-y-1">
              {themeOptions.map((option) => (
                <button
                  key={option.name}
                  onClick={() => handleThemeSelect(option.name)}
                  className="w-full flex items-center justify-between px-3 py-2 rounded-[var(--radius-sm)] hover:bg-[var(--muted)] transition-colors text-left"
                >
                  <div>
                    <p className="text-sm font-medium text-[var(--foreground)]">
                      {option.label}
                    </p>
                    <p className="text-xs text-[var(--muted-foreground)]">
                      {option.description}
                    </p>
                  </div>
                  {themeName === option.name && (
                    <CheckIcon size={16} className="text-[var(--primary)]" />
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

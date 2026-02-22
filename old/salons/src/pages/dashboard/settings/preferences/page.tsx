import { LanguageLocalizationSettings } from "@/components/settings/language-localization-settings";
import { CurrencyPreferences } from "@/components/settings/currency-preferences";
import { AccessibilitySettings } from "@/components/settings/accessibility-settings";

export default function PreferencesPage() {
  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Preferences</h1>
        <p className="text-muted-foreground">
          Customize your experience with language, timezone, and accessibility
          settings
        </p>
      </div>

      {/* Language & Localization */}
      <LanguageLocalizationSettings />

      {/* Currency */}
      <CurrencyPreferences />

      {/* Accessibility */}
      <AccessibilitySettings />
    </div>
  );
}

import { PrivacyToggles } from "@/components/settings/privacy-toggles";
import { DataRetentionSettings } from "@/components/settings/data-retention-settings";

export default function PrivacySettingsPage() {
  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Privacy Settings</h1>
        <p className="text-muted-foreground">
          Control how your data is used and shared
        </p>
      </div>

      {/* Privacy Toggles */}
      <PrivacyToggles />

      {/* Data Retention */}
      <DataRetentionSettings />
    </div>
  );
}

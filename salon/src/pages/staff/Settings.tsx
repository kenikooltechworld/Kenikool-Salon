import { useState } from "react";
import StaffProfileForm from "@/components/staff/StaffProfileForm";
import StaffPasswordForm from "@/components/staff/StaffPasswordForm";
import StaffNotificationsForm from "@/components/staff/StaffNotificationsForm";
import StaffAvailabilityForm from "@/components/staff/StaffAvailabilityForm";
import StaffPreferencesForm from "@/components/staff/StaffPreferencesForm";

type SettingsTab =
  | "profile"
  | "password"
  | "notifications"
  | "availability"
  | "preferences";

interface SettingsNavItem {
  id: SettingsTab;
  label: string;
  description: string;
}

const STAFF_SETTINGS_NAV: SettingsNavItem[] = [
  {
    id: "profile",
    label: "Profile",
    description: "Personal profile information",
  },
  {
    id: "password",
    label: "Password",
    description: "Change your password",
  },
  {
    id: "notifications",
    label: "Notifications",
    description: "Notification preferences",
  },
  {
    id: "availability",
    label: "Availability",
    description: "Working hours and days off",
  },
  {
    id: "preferences",
    label: "Work Preferences",
    description: "Service specializations and emergency contact",
  },
];

export default function StaffSettings() {
  const [activeTab, setActiveTab] = useState<SettingsTab>("profile");

  const renderContent = () => {
    switch (activeTab) {
      case "profile":
        return <StaffProfileForm />;
      case "password":
        return <StaffPasswordForm />;
      case "notifications":
        return <StaffNotificationsForm />;
      case "availability":
        return <StaffAvailabilityForm />;
      case "preferences":
        return <StaffPreferencesForm />;
      default:
        return <StaffProfileForm />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Manage your personal settings and preferences
        </p>
      </div>

      {/* Settings Navigation */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {STAFF_SETTINGS_NAV.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`p-4 rounded-lg border transition-colors text-left cursor-pointer ${
              activeTab === item.id
                ? "bg-primary border-primary text-primary-foreground"
                : "bg-card border-border hover:border-primary"
            }`}
          >
            <h3 className="font-semibold mb-1">{item.label}</h3>
            <p className="text-xs opacity-75">{item.description}</p>
          </button>
        ))}
      </div>

      {/* Settings Content */}
      <div>{renderContent()}</div>
    </div>
  );
}

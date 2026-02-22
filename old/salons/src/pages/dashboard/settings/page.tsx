import { Card } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import {
  BellIcon,
  UserIcon,
  BuildingIcon,
  SettingsIcon,
  LockIcon,
  CreditCardIcon,
  TagIcon,
  EyeIcon,
} from "@/components/icons";

export default function SettingsPage() {
  const navigate = useNavigate();

  const settingsSections = [
    {
      title: "Notifications",
      description: "Manage notification preferences and alerts",
      icon: BellIcon,
      href: "/dashboard/settings/notifications",
      color: "text-[var(--primary)]",
    },
    {
      title: "Profile",
      description: "Update your personal information",
      icon: UserIcon,
      href: "/dashboard/settings/profile",
      color: "text-[var(--success)]",
    },
    {
      title: "Security",
      description: "Password, 2FA, and session management",
      icon: LockIcon,
      href: "/dashboard/settings/security",
      color: "text-[var(--error)]",
    },
    {
      title: "API Keys",
      description: "Manage API keys for integrations",
      icon: CreditCardIcon,
      href: "/dashboard/settings/api-keys",
      color: "text-orange-500",
    },
    {
      title: "Privacy",
      description: "Control data sharing and retention",
      icon: LockIcon,
      href: "/dashboard/settings/privacy",
      color: "text-cyan-500",
    },
    {
      title: "Preferences",
      description: "Language, timezone, and accessibility",
      icon: SettingsIcon,
      href: "/dashboard/settings/preferences",
      color: "text-[var(--info)]",
    },
    {
      title: "Salon Details",
      description: "Manage salon information and branding",
      icon: BuildingIcon,
      href: "/dashboard/settings/salon",
      color: "text-[var(--warning)]",
    },
    {
      title: "Appearance",
      description: "Customize theme and display preferences",
      icon: EyeIcon,
      href: "/dashboard/settings/appearance",
      color: "text-pink-500",
    },
    {
      title: "Billing",
      description: "Subscription and payment methods",
      icon: CreditCardIcon,
      href: "/dashboard/settings/billing",
      color: "text-purple-500",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="text-muted-foreground">
          Manage your account and application preferences
        </p>
      </div>

      {/* Settings Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {settingsSections.map((section) => {
          const Icon = section.icon;
          return (
            <Card
              key={section.href}
              className="p-6 cursor-pointer hover:shadow-lg transition-all hover:border-[var(--primary)]"
              onClick={() => navigate(section.href)}
            >
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-lg bg-muted ${section.color}`}>
                  <Icon size={24} />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-foreground mb-1">
                    {section.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {section.description}
                  </p>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

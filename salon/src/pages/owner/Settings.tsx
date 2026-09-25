import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/auth";
import {
  SettingsIcon,
  CreditCardIcon,
  DollarSignIcon,
  TrendingUpIcon,
  PackageIcon,
  BellIcon,
  MailIcon,
} from "@/components/icons";

interface SettingsNavItem {
  id: string;
  title: string;
  description: string;
  icon: any;
  path: string;
  allowedRoles: string[];
  color: string;
}

const SETTINGS_NAV_ITEMS: SettingsNavItem[] = [
  {
    id: "general",
    title: "General Settings",
    description: "Basic business information, hours, and branding",
    icon: SettingsIcon,
    path: "/settings/general",
    allowedRoles: ["Owner", "Manager"],
    color: "text-blue-500",
  },
  {
    id: "commission",
    title: "Commission Settings",
    description: "Staff commission rules and financial settings",
    icon: DollarSignIcon,
    path: "/settings/commission",
    allowedRoles: ["Owner"],
    color: "text-green-500",
  },
  {
    id: "financial",
    title: "Financial Settings",
    description: "Balance enforcement, refunds, and payment policies",
    icon: TrendingUpIcon,
    path: "/settings/financial",
    allowedRoles: ["Owner"],
    color: "text-emerald-500",
  },
  {
    id: "operational",
    title: "Operational Settings",
    description: "Resources, inventory, and operational management",
    icon: PackageIcon,
    path: "/settings/operational",
    allowedRoles: ["Owner", "Manager"],
    color: "text-orange-500",
  },
  {
    id: "billing",
    title: "Billing & Subscription",
    description: "Plans, subscriptions, and billing management",
    icon: CreditCardIcon,
    path: "/settings/billing",
    allowedRoles: ["Owner", "Manager"],
    color: "text-pink-500",
  },
  {
    id: "notifications",
    title: "Notification Preferences",
    description: "Email, SMS, and push notification settings",
    icon: BellIcon,
    path: "/settings/notifications",
    allowedRoles: ["Owner", "Manager"],
    color: "text-indigo-500",
  },
  {
    id: "email-templates",
    title: "Email Templates",
    description: "Customize customer welcome and notification emails",
    icon: MailIcon,
    path: "/settings/email-templates",
    allowedRoles: ["Owner", "Manager"],
    color: "text-violet-500",
  },
];

function getSettingsNavForRole(roleNames: string[]): SettingsNavItem[] {
  return SETTINGS_NAV_ITEMS.filter((item) =>
    item.allowedRoles.some((role) => roleNames.includes(role)),
  );
}

export default function Settings() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 600);
    return () => clearTimeout(timer);
  }, []);

  const filteredSettingsNav = user?.roleNames
    ? getSettingsNavForRole(user.roleNames)
    : [];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-8 w-40" />
          <Skeleton className="h-5 w-72" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="p-6 space-y-4">
              <div className="flex items-start gap-4">
                <Skeleton className="h-12 w-12 rounded-lg" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-5 w-32" />
                  <Skeleton className="h-4 w-48" />
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="text-muted-foreground">
          Manage your salon settings and preferences
        </p>
      </div>

      {/* Settings Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredSettingsNav.map((section) => {
          const Icon = section.icon;
          return (
            <Card
              key={section.id}
              className="p-6 cursor-pointer hover:shadow-lg transition-all hover:border-primary"
              onClick={() => navigate(section.path)}
            >
              <div className="flex items-start gap-4">
                <div
                  className={`p-3 rounded-lg bg-muted ${section.color}`}
                  style={{
                    backgroundColor: "var(--muted)",
                  }}
                >
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

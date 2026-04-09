import { Card } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/auth";
import {
  SettingsIcon,
  LockIcon,
  CreditCardIcon,
  MonitorIcon,
  DollarSignIcon,
  TrendingUpIcon,
  PackageIcon,
  ZapIcon,
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
    id: "system",
    title: "System Configuration",
    description: "Middleware, security, and system settings",
    icon: MonitorIcon,
    path: "/settings/system",
    allowedRoles: ["Owner"],
    color: "text-purple-500",
  },
  {
    id: "security",
    title: "Security Policies",
    description: "Access control, authentication, and security rules",
    icon: LockIcon,
    path: "/settings/security",
    allowedRoles: ["Owner"],
    color: "text-red-500",
  },
  {
    id: "integrations",
    title: "Integrations",
    description: "SMS, payment gateways, and third-party services",
    icon: ZapIcon,
    path: "/settings/integrations",
    allowedRoles: ["Owner"],
    color: "text-yellow-500",
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
    id: "cache",
    title: "Cache & Performance",
    description: "Performance optimization and caching settings",
    icon: ZapIcon,
    path: "/settings/cache",
    allowedRoles: ["Owner"],
    color: "text-cyan-500",
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

  const filteredSettingsNav = user?.roleNames
    ? getSettingsNavForRole(user.roleNames)
    : [];

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

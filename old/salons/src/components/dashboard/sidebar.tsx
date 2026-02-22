import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils/cn";
import { useTenant } from "@/lib/api/hooks/useTenant";
import {
  HomeIcon,
  ScissorsIcon,
  UsersIcon,
  CalendarIcon,
  PackageIcon,
  UserIcon,
  ChartIcon,
  CreditCardIcon,
  DollarSignIcon,
  ClockIcon,
  SettingsIcon,
  SparklesIcon,
  MicIcon,
  GiftIcon,
  TagIcon,
  MapPinIcon,
  GlobeIcon,
  StarIcon,
} from "@/components/icons";

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  subItems?: NavItem[];
}

const navItems: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: HomeIcon },
  { label: "Services", href: "/dashboard/services", icon: ScissorsIcon },
  { label: "Clients", href: "/dashboard/clients", icon: UsersIcon },
  { label: "Bookings", href: "/dashboard/bookings", icon: CalendarIcon },
  { label: "Inventory", href: "/dashboard/inventory", icon: PackageIcon },
  { label: "Staff", href: "/dashboard/staff", icon: UserIcon },
  { label: "Analytics", href: "/dashboard/analytics", icon: ChartIcon },
  {
    label: "Voice Assistant",
    href: "/dashboard/voice-assistant",
    icon: MicIcon,
  },
  { label: "AI Insights", href: "/dashboard/ai-insights", icon: SparklesIcon },
  { label: "Payments", href: "/dashboard/payments", icon: CreditCardIcon },
  {
    label: "POS",
    href: "/dashboard/pos",
    icon: CreditCardIcon,
    subItems: [
      { label: "Checkout", href: "/dashboard/pos", icon: CreditCardIcon },
      {
        label: "Transactions",
        href: "/dashboard/pos/transactions",
        icon: ChartIcon,
      },
      { label: "Reports", href: "/dashboard/pos/reports", icon: ChartIcon },
    ],
  },
  { label: "Gift Cards", href: "/dashboard/gift-cards", icon: GiftIcon },
  { label: "Memberships", href: "/dashboard/memberships", icon: StarIcon },
  { label: "Packages", href: "/dashboard/packages", icon: TagIcon },
  { label: "Promo Codes", href: "/dashboard/promo-codes", icon: TagIcon },
  { label: "Expenses", href: "/dashboard/expenses", icon: DollarSignIcon },
  { label: "Accounting", href: "/dashboard/accounting", icon: DollarSignIcon },
  { label: "Reviews", href: "/dashboard/reviews", icon: StarIcon },
  { label: "Waitlist", href: "/dashboard/waitlist", icon: ClockIcon },
  { label: "Campaigns", href: "/dashboard/campaigns", icon: TagIcon },
  { label: "Locations", href: "/dashboard/locations", icon: MapPinIcon },
  { label: "Referrals", href: "/dashboard/referrals", icon: UsersIcon },
  { label: "Domains", href: "/dashboard/domains", icon: GlobeIcon },
  { label: "Integrations", href: "/dashboard/integrations", icon: PackageIcon },
  { label: "White Label", href: "/dashboard/white-label", icon: SparklesIcon },
  { label: "Settings", href: "/dashboard/settings", icon: SettingsIcon },
];

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const location = useLocation();
  const pathname = location.pathname;
  const { data: tenant } = useTenant();

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed top-0 left-0 h-full w-64 bg-[var(--card)] border-r border-[var(--border)] z-50 transition-transform duration-300 lg:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex flex-col h-full">
          {/* Salon Logo/Name */}
          <div className="h-16 flex items-center px-6 border-b border-[var(--border)]">
            <Link
              to="/dashboard"
              prefetch={true}
              className="flex items-center gap-3"
            >
              {tenant?.logo_url ? (
                <img
                  src={tenant.logo_url}
                  alt={tenant.salon_name}
                  className="h-8 w-8 rounded-lg object-cover"
                />
              ) : (
                <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                  <ScissorsIcon size={18} className="text-primary" />
                </div>
              )}
              <span className="font-bold text-lg text-foreground">
                {tenant?.salon_name || "Salon"}
              </span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto py-4">
            <ul className="space-y-1 px-3">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                const hasSubItems = item.subItems && item.subItems.length > 0;
                const isParentActive =
                  hasSubItems &&
                  item.subItems.some((sub) => pathname === sub.href);

                return (
                  <li key={item.href}>
                    <Link
                      to={item.href}
                      prefetch={true}
                      onClick={() => onClose()}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2.5 rounded-[var(--radius-md)] transition-colors",
                        isActive || isParentActive
                          ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
                          : "text-[var(--muted-foreground)] hover:bg-[var(--muted)] hover:text-[var(--foreground)]"
                      )}
                    >
                      <Icon size={20} />
                      <span className="font-medium">{item.label}</span>
                    </Link>
                    {hasSubItems && (
                      <ul className="ml-8 mt-1 space-y-1">
                        {item.subItems.map((subItem) => {
                          const SubIcon = subItem.icon;
                          const isSubActive = pathname === subItem.href;
                          return (
                            <li key={subItem.href}>
                              <Link
                                to={subItem.href}
                                prefetch={true}
                                onClick={() => onClose()}
                                className={cn(
                                  "flex items-center gap-2 px-3 py-2 rounded-[var(--radius-md)] transition-colors text-sm",
                                  isSubActive
                                    ? "bg-[var(--primary)]/10 text-[var(--primary)]"
                                    : "text-[var(--muted-foreground)] hover:bg-[var(--muted)] hover:text-[var(--foreground)]"
                                )}
                              >
                                <SubIcon size={16} />
                                <span>{subItem.label}</span>
                              </Link>
                            </li>
                          );
                        })}
                      </ul>
                    )}
                  </li>
                );
              })}
            </ul>
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-[var(--border)]">
            <div className="bg-[var(--muted)] rounded-[var(--radius-md)] p-3">
              <p className="text-xs font-semibold text-[var(--foreground)] mb-1">
                Need Help?
              </p>
              <p className="text-xs text-[var(--muted-foreground)]">
                Contact support for assistance
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

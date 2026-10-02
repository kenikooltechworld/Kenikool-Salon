import { useState, useEffect, useCallback } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/auth";
import { useTenantStore } from "@/stores/tenant";
import { ThemeSelector } from "@/components/ui/theme-selector";
import NotificationBadge from "@/components/notifications/NotificationBadge";
import NotificationCenter from "@/components/notifications/NotificationCenter";
import { RefreshButton } from "@/components/ui/refresh-button";
import { usePageRefresh } from "@/contexts/PageRefreshContext";
import { useOperationalSettings } from "@/hooks/useOperationalSettings";
import {
  MenuIcon,
  XIcon,
  HomeIcon,
  CalendarIcon,
  UsersIcon,
  ScissorsIcon,
  FileTextIcon,
  SettingsIcon,
  LogOutIcon,
  UserIcon,
  ShoppingCartIcon,
  ClockIcon,
  PackageIcon,
  MessageSquareIcon,
} from "@/components/icons";

const menuItems = [
  { icon: HomeIcon, label: "Dashboard", path: "/dashboard" },
  { icon: CalendarIcon, label: "Bookings", path: "/bookings" },
  { icon: UsersIcon, label: "Customers", path: "/customers" },
  { icon: ScissorsIcon, label: "Services", path: "/services" },
  { icon: UsersIcon, label: "Staff", path: "/staff" },
  { icon: FileTextIcon, label: "Invoices", path: "/invoices" },
  { icon: ShoppingCartIcon, label: "POS", path: "/pos" },
  { icon: PackageIcon, label: "Inventory", path: "/inventory" },
  { icon: UsersIcon, label: "Group Bookings", path: "/owner/group-bookings" },
  { icon: MessageSquareIcon, label: "Messages", path: "/owner/messages" },
  { icon: ScissorsIcon, label: "Social Proof", path: "/owner/social-proof" },
  { icon: UserIcon, label: "My Profile", path: "/owner/profile" },
  { icon: UserIcon, label: "My Account", path: "/my-account" },
  { icon: SettingsIcon, label: "Settings", path: "/settings" },
  { icon: UsersIcon, label: "Waiting Room", path: "/waiting-room" },
  { icon: ScissorsIcon, label: "Resources", path: "/resources" },
];

// Role-based menu filtering
function getMenuItemsForRole(roleNames: string[], waitingRoomEnabled: boolean): typeof menuItems {
  // Owner: Full access except My Account
  if (roleNames.includes("Owner")) {
    let items = menuItems.filter((item) => item.path !== "/my-account");
    if (!waitingRoomEnabled) {
      items = items.filter((item) => item.path !== "/waiting-room");
    }
    return items;
  }

  // Manager: Access to bookings, customers, services, staff, invoices, reports, settings
  if (roleNames.includes("Manager")) {
    let items = menuItems.filter((item) =>
      [
        "/dashboard",
        "/bookings",
        "/customers",
        "/services",
        "/staff",
        "/invoices",
        "/inventory",
        "/settings",
        "/owner/profile",
      ].includes(item.path),
    );
    if (!waitingRoomEnabled) {
      items = items.filter((item) => item.path !== "/waiting-room");
    }
    return items;
  }

  // Staff: Access to staff dashboard
  if (roleNames.includes("Staff")) {
    return [
      { icon: HomeIcon, label: "Dashboard", path: "/staff/dashboard" },
      {
        icon: CalendarIcon,
        label: "Appointments",
        path: "/staff/appointments",
      },
      { icon: ClockIcon, label: "Shifts", path: "/staff/shifts" },
      { icon: CalendarIcon, label: "Time Off", path: "/staff/time-off" },
      { icon: SettingsIcon, label: "Settings", path: "/staff/settings" },
    ];
  }

  // Customer: Only access to their account
  if (roleNames.includes("Customer")) {
    return [{ icon: UserIcon, label: "My Account", path: "/my-account" }];
  }

  // Default: minimal access
  return [{ icon: HomeIcon, label: "Dashboard", path: "/dashboard" }];
}

export function DashboardLayout() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const tenantName = useTenantStore((state) => state.tenantName());
  const logout = useAuthStore((state) => state.logout);
  const { data: operationalSettings } = useOperationalSettings();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notificationCenterOpen, setNotificationCenterOpen] = useState(false);
  const [currentPath, setCurrentPath] = useState(window.location.pathname);
  const [isMobile, setIsMobile] = useState<boolean>(() => window.innerWidth < 768);

  // Get filtered menu items based on user role
  const waitingRoomEnabled = operationalSettings?.waiting_room_enabled ?? true;
  const filteredMenuItems = user?.roleNames
    ? getMenuItemsForRole(user.roleNames, waitingRoomEnabled)
    : getMenuItemsForRole([], waitingRoomEnabled);

  const { refreshHandler } = usePageRefresh();

  // Close mobile menu on escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape" && mobileMenuOpen) {
        setMobileMenuOpen(false);
      }
    };

    if (mobileMenuOpen) {
      document.addEventListener("keydown", handleEscape);
      // Prevent body scroll when mobile menu is open
      document.body.style.overflow = "hidden";
    }

    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.body.style.overflow = "";
    };
  }, [mobileMenuOpen]);

  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      if (mobile) {
        setSidebarCollapsed(false);
        setMobileMenuOpen(false);
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleLogout = async () => {
    await logout();
    localStorage.removeItem("csrfToken");
    localStorage.removeItem("sessionId");
    navigate("/");
  };

  const handleNavigation = (path: string) => {
    setCurrentPath(path);
    navigate(path);
    setMobileMenuOpen(false);
  };

  const getUserProfilePath = () => {
    if (user?.roleNames?.includes("Owner") || user?.roleNames?.includes("Manager")) {
      return "/owner/profile";
    }
    if (user?.roleNames?.includes("Staff")) {
      return "/staff/settings";
    }
    return "/my-account";
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Mobile Overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 md:hidden"
          onClick={() => setMobileMenuOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={[
          "bg-card border-r border-border transition-all duration-300 ease-in-out flex flex-col",
          // Base mobile: fixed full-height sidebar that slides in from left
          "fixed inset-y-0 left-0 z-40",
          "h-full",
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full",
          // Desktop: relative positioning
          "md:relative md:translate-x-0",
          sidebarCollapsed ? "md:w-20" : "md:w-64",
          "w-[280px]",
          "safe-area-inset-left",
        ].join(" ")}
      >
        {/* Sidebar Header */}
        <div className="h-16 border-b border-border flex items-center justify-between px-4">
          {(sidebarCollapsed === false || mobileMenuOpen) && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">K</span>
              </div>
              <span className="font-bold text-lg text-foreground">
                {tenantName || "Kenikool"}
              </span>
            </div>
          )}
          <button
            onClick={() => {
              if (isMobile) {
                setMobileMenuOpen(false);
              } else {
                setSidebarCollapsed((prev) => !prev);
              }
            }}
            className="p-2 -mr-2 hover:bg-muted rounded-lg transition cursor-pointer min-w-[44px] min-h-[44px] flex items-center justify-center"
            aria-label={isMobile ? "Close menu" : "Toggle sidebar"}
          >
            {isMobile && mobileMenuOpen ? (
              <XIcon size={24} />
            ) : sidebarCollapsed ? (
              <MenuIcon size={20} />
            ) : (
              <XIcon size={20} />
            )}
          </button>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-1">
          {filteredMenuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPath === item.path;
            return (
              <button
                key={item.path}
                onClick={() => handleNavigation(item.path)}
                className={[
                  "w-full flex items-center gap-3 px-4 py-3 rounded-xl transition cursor-pointer min-h-[44px]",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground",
                ].join(" ")}
                title={!sidebarCollapsed ? "" : item.label}
              >
                <Icon size={22} className="flex-shrink-0" />
                {(sidebarCollapsed === false || mobileMenuOpen) && (
                  <span className="text-sm font-medium truncate">{item.label}</span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="border-t border-border p-2">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-destructive hover:bg-destructive/10 transition cursor-pointer min-h-[44px]"
            title={!sidebarCollapsed ? "" : "Logout"}
          >
            <LogOutIcon size={22} className="flex-shrink-0" />
            {(sidebarCollapsed === false || mobileMenuOpen) && (
              <span className="text-sm font-medium">Logout</span>
            )}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden w-full">
        {/* Top Navbar */}
        <header className="h-16 bg-card border-b border-border flex items-center justify-between px-3 md:px-6 safe-area-inset-top">
          <div className="flex items-center gap-3">
            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 -ml-2 hover:bg-muted rounded-xl transition cursor-pointer min-w-[44px] min-h-[44px] flex items-center justify-center"
              aria-label="Toggle mobile menu"
              aria-expanded={mobileMenuOpen}
            >
              <MenuIcon size={22} className="text-foreground" />
            </button>

            <h1 className="text-base font-semibold text-foreground truncate md:text-lg">
              {filteredMenuItems.find((item) => item.path === currentPath)
                ?.label || "Dashboard"}
            </h1>
          </div>

          <div className="flex items-center gap-1 md:gap-3">
            {/* Notifications */}
            <NotificationBadge
              onClick={() => setNotificationCenterOpen(true)}
            />

            {refreshHandler && (
              <RefreshButton onClick={refreshHandler} />
            )}

            {/* Theme Selector */}
            <ThemeSelector variant="icon" />

            {/* User Menu - Hidden on mobile */}
            <button
              onClick={() => handleNavigation(getUserProfilePath())}
              className="hidden sm:flex items-center gap-3 pl-3 md:pl-4 border-l border-border cursor-pointer bg-transparent hover:bg-muted/50 rounded-xl transition p-2 -mr-2"
              title="My Account"
            >
              <div className="w-9 h-9 md:w-10 md:h-10 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center flex-shrink-0">
                <UserIcon size={18} className="text-white md:hidden" />
                <UserIcon size={20} className="text-white hidden md:block" />
              </div>
              <div className="hidden md:block text-left">
                <p className="text-sm font-medium text-foreground truncate">
                  {user?.firstName}
                </p>
                <p className="text-xs text-muted-foreground truncate">
                  {user?.email}
                </p>
              </div>
            </button>
          </div>
        </header>

        {/* Notification Center Modal */}
        <NotificationCenter
          isOpen={notificationCenterOpen}
          onClose={() => setNotificationCenterOpen(false)}
        />

        {/* Page Content */}
        <main className="flex-1 overflow-auto">
          <div className="p-3 md:p-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

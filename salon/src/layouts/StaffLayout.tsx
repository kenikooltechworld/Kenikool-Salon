import { useState, useEffect } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { useAuthUser } from "@/hooks/useAuthUser";
import { queryClient } from "@/lib/react-query";
import { useTenantStore } from "@/stores/tenant";
import { ThemeSelector } from "@/components/ui/theme-selector";
import NotificationBadge from "@/components/notifications/NotificationBadge";
import StaffNotificationCenter from "@/components/staff/StaffNotificationCenter";
import { RefreshButton } from "@/components/ui/refresh-button";
import { usePageRefresh } from "@/contexts/PageRefreshContext";
import {
  MenuIcon,
  XIcon,
  HomeIcon,
  CalendarIcon,
  ClockIcon,
  SettingsIcon,
  LogOutIcon,
  UserIcon,
  DollarSignIcon,
  StarIcon,
  FileIcon,
  TargetIcon,
  MessageSquareIcon,
} from "@/components/icons";
import { useUnreadMessageCount } from "@/hooks/useMessages";

const staffMenuItems = [
  { icon: HomeIcon, label: "Dashboard", path: "/staff/dashboard" },
  { icon: CalendarIcon, label: "Appointments", path: "/staff/appointments" },
  { icon: ClockIcon, label: "Shifts", path: "/staff/shifts" },
  { icon: CalendarIcon, label: "Time Off", path: "/staff/time-off" },
  { icon: DollarSignIcon, label: "Earnings", path: "/staff/earnings" },
  { icon: StarIcon, label: "Performance", path: "/staff/performance" },
  { icon: ClockIcon, label: "Attendance", path: "/staff/attendance" },
  { icon: FileIcon, label: "Documents", path: "/staff/documents" },
  { icon: TargetIcon, label: "Goals", path: "/staff/goals" },
  {
    icon: MessageSquareIcon,
    label: "Messages",
    path: "/staff/messages",
    showBadge: true,
  },
  { icon: SettingsIcon, label: "Settings", path: "/staff/settings" },
];

export function StaffLayout() {
  const navigate = useNavigate();
  const { data: user } = useAuthUser();
  const tenantName = useTenantStore((state) => state.tenantName());
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notificationCenterOpen, setNotificationCenterOpen] = useState(false);
  const [currentPath, setCurrentPath] = useState(window.location.pathname);
  const [isMobile, setIsMobile] = useState<boolean>(() => window.innerWidth < 768);

  // Get unread message count
  const { data: unreadCount = 0 } = useUnreadMessageCount();

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
    queryClient.removeQueries({ queryKey: ["auth", "me"] });
    localStorage.removeItem("csrfToken");
    localStorage.removeItem("sessionId");
    navigate("/");
  };

  const handleNavigation = (path: string) => {
    setCurrentPath(path);
    navigate(path);
    setMobileMenuOpen(false);
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
          "fixed inset-y-0 left-0 z-40",
          "h-full",
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full",
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
          {staffMenuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPath === item.path;
            const showBadge = item.showBadge && unreadCount > 0;

            return (
              <button
                key={item.path}
                onClick={() => handleNavigation(item.path)}
                className={[
                  "w-full flex items-center gap-3 px-4 py-3 rounded-xl transition cursor-pointer min-h-[44px] relative",
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
                {showBadge && (
                  <span
                    className={[
                      sidebarCollapsed && !mobileMenuOpen
                        ? "absolute -top-1 -right-1"
                        : "ml-auto",
                      "flex items-center justify-center min-w-[20px] h-5 px-1.5 text-xs font-bold text-white bg-red-600 rounded-full",
                    ].join(" ")}
                  >
                    {unreadCount > 99 ? "99+" : unreadCount}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="border-t border-border p-2">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-muted-foreground hover:text-foreground hover:bg-muted/50 transition cursor-pointer min-h-[44px]"
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
              {staffMenuItems.find((item) => item.path === currentPath)
                ?.label || "Staff Dashboard"}
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
            <div className="hidden sm:flex items-center gap-3 pl-3 md:pl-4 border-l border-border">
              <div className="w-9 h-9 md:w-10 md:h-10 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center flex-shrink-0">
                <UserIcon size={18} className="text-white md:hidden" />
                <UserIcon size={20} className="text-white hidden md:block" />
              </div>
              <div className="hidden md:block">
                <p className="text-sm font-medium text-foreground truncate">
                  {user?.firstName}
                </p>
                <p className="text-xs text-muted-foreground truncate">
                  {user?.email}
                </p>
              </div>
            </div>
          </div>
        </header>

        {/* Notification Center Modal */}
        <StaffNotificationCenter
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

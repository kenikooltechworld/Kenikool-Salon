import { useState, useEffect } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/auth";
import { ThemeSelector } from "@/components/ui/theme-selector";
import NotificationBadge from "@/components/notifications/NotificationBadge";
import NotificationCenter from "@/components/notifications/NotificationCenter";
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
} from "@/components/icons";

const menuItems = [
  { icon: HomeIcon, label: "Dashboard", path: "/dashboard" },
  { icon: CalendarIcon, label: "Bookings", path: "/bookings" },
  { icon: UsersIcon, label: "Customers", path: "/customers" },
  { icon: ScissorsIcon, label: "Services", path: "/services" },
  { icon: UsersIcon, label: "Staff", path: "/staff" },
  { icon: FileTextIcon, label: "Invoices", path: "/invoices" },
  { icon: ShoppingCartIcon, label: "POS", path: "/pos" },
  { icon: SettingsIcon, label: "Settings", path: "/settings" },
  { icon: UsersIcon, label: "Waiting Room", path: "/waiting-room" },
  { icon: ScissorsIcon, label: "Resources", path: "/resources" },
];

export function DashboardLayout() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notificationCenterOpen, setNotificationCenterOpen] = useState(false);
  const [currentPath, setCurrentPath] = useState(window.location.pathname);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      if (mobile) {
        setSidebarOpen(false);
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleLogout = () => {
    logout();
    localStorage.removeItem("tenantId");
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
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-20"
        } bg-card border-r border-border transition-all duration-300 flex flex-col fixed md:relative h-full z-40 md:z-0 ${
          !mobileMenuOpen && isMobile ? "-translate-x-full" : "translate-x-0"
        } md:translate-x-0`}
      >
        {/* Sidebar Header */}
        <div className="h-16 border-b border-border flex items-center justify-between px-4">
          {sidebarOpen && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">K</span>
              </div>
              <span className="font-bold text-lg text-foreground">
                Kenikool
              </span>
            </div>
          )}
          <button
            onClick={() => {
              if (isMobile) {
                setMobileMenuOpen(false);
              } else {
                setSidebarOpen(!sidebarOpen);
              }
            }}
            className="p-2 hover:bg-muted rounded-md transition cursor-pointer"
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? <XIcon size={20} /> : <MenuIcon size={20} />}
          </button>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 overflow-y-auto px-2 py-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPath === item.path;
            return (
              <button
                key={item.path}
                onClick={() => handleNavigation(item.path)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition cursor-pointer ${
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
                title={!sidebarOpen ? item.label : ""}
              >
                <Icon size={20} className="flex-shrink-0" />
                {sidebarOpen && (
                  <span className="text-sm font-medium">{item.label}</span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="border-t border-border p-2 space-y-2">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-destructive hover:bg-destructive/10 transition cursor-pointer"
            title={!sidebarOpen ? "Logout" : ""}
          >
            <LogOutIcon size={20} className="flex-shrink-0" />
            {sidebarOpen && <span className="text-sm font-medium">Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden w-full">
        {/* Top Navbar */}
        <header className="h-16 bg-card border-b border-border flex items-center justify-between px-4 md:px-6">
          <div className="flex items-center gap-4">
            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 hover:bg-muted rounded-lg transition cursor-pointer"
              aria-label="Toggle mobile menu"
            >
              <MenuIcon size={20} className="text-muted-foreground" />
            </button>

            <h1 className="text-lg font-semibold text-foreground truncate">
              {menuItems.find((item) => item.path === currentPath)?.label ||
                "Dashboard"}
            </h1>
          </div>

          <div className="flex items-center gap-2 md:gap-4">
            {/* Notifications */}
            <NotificationBadge
              onClick={() => setNotificationCenterOpen(true)}
            />

            {/* Theme Selector */}
            <ThemeSelector variant="icon" />

            {/* User Menu - Hidden on mobile */}
            <div className="hidden sm:flex items-center gap-3 pl-4 border-l border-border">
              <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center flex-shrink-0">
                <UserIcon size={20} className="text-white" />
              </div>
              <div className="hidden sm:block">
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
        <NotificationCenter
          isOpen={notificationCenterOpen}
          onClose={() => setNotificationCenterOpen(false)}
        />

        {/* Page Content */}
        <main className="flex-1 overflow-auto">
          <div className="p-4 md:p-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

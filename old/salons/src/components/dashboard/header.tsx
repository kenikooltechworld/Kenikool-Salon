import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/lib/hooks/useAuth";
import { useTenant } from "@/lib/api/hooks/useTenant";
import {
  useNotifications,
  useUpdateNotification,
  useMarkAllNotificationsRead,
} from "@/lib/api/hooks/useNotifications";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { ThemeSelector } from "@/components/ui/theme-selector";
import { Clock } from "@/components/dashboard/clock";
import {
  MenuIcon,
  SearchIcon,
  BellIcon,
  UserIcon,
  LogOutIcon,
  SettingsIcon,
  ScissorsIcon,
} from "@/components/icons";
import { formatDistanceToNow } from "date-fns";

interface HeaderProps {
  onMenuClick: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { data: tenant } = useTenant();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  // Fetch notifications
  const { data: notificationsData, isLoading: notificationsLoading } =
    useNotifications({
      limit: 5,
      is_read: false,
    });

  const updateNotification = useUpdateNotification();
  const markAllRead = useMarkAllNotificationsRead();

  const notifications = notificationsData?.notifications || [];
  const unreadCount = notificationsData?.unread_count || 0;

  // Refs for click outside detection
  const userMenuRef = useRef<HTMLDivElement>(null);
  const notificationsRef = useRef<HTMLDivElement>(null);

  // Close dropdowns when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        userMenuRef.current &&
        !userMenuRef.current.contains(event.target as Node)
      ) {
        setShowUserMenu(false);
      }
      if (
        notificationsRef.current &&
        !notificationsRef.current.contains(event.target as Node)
      ) {
        setShowNotifications(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const handleNotificationClick = async (
    notificationId: string,
    link?: string,
  ) => {
    // Mark as read
    await updateNotification.mutateAsync({
      id: notificationId,
      is_read: true,
    });

    // Navigate if there's a link
    if (link) {
      navigate(link);
    }

    setShowNotifications(false);
  };

  const handleMarkAllRead = async () => {
    await markAllRead.mutateAsync();
  };

  return (
    <header className="h-16 bg-[var(--card)] border-b border-[var(--border)] sticky top-0 z-30">
      <div className="h-full flex items-center justify-between px-4 lg:px-6">
        {/* Left section */}
        <div className="flex items-center gap-4">
          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="icon"
            onClick={onMenuClick}
            className="lg:hidden"
          >
            <MenuIcon size={24} />
          </Button>

          {/* Salon Logo & Name */}
          <div className="flex items-center gap-3">
            {tenant?.logo_url ? (
              <img
                src={tenant.logo_url}
                alt={tenant.salon_name}
                className="h-10 w-10 rounded-lg object-cover"
              />
            ) : (
              <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <ScissorsIcon size={20} className="text-primary" />
              </div>
            )}
            <div className="hidden sm:block">
              <h1 className="text-sm font-semibold text-foreground">
                {tenant?.salon_name || "Salon"}
              </h1>
              <p className="text-xs text-muted-foreground">
                {tenant?.subscription_plan === "trial"
                  ? "Trial"
                  : tenant?.subscription_plan
                    ? tenant.subscription_plan.charAt(0).toUpperCase() +
                      tenant.subscription_plan.slice(1)
                    : ""}
              </p>
            </div>
          </div>

          {/* Search */}
          <div className="hidden md:flex items-center relative ml-4">
            <SearchIcon
              size={18}
              className="absolute left-3 text-muted-foreground"
            />
            <Input
              type="search"
              placeholder="Search..."
              className="pl-10 w-64"
            />
          </div>
        </div>

        {/* Right section */}
        <div className="flex items-center gap-3">
          {/* Clock */}
          <Clock />

          {/* Theme selector */}
          <ThemeSelector variant="icon" />

          {/* Notifications */}
          <div className="relative" ref={notificationsRef}>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => {
                setShowNotifications(!showNotifications);
                setShowUserMenu(false);
              }}
            >
              <BellIcon size={20} />
              {unreadCount > 0 && (
                <Badge
                  variant="error"
                  className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
                >
                  {unreadCount > 9 ? "9+" : unreadCount}
                </Badge>
              )}
            </Button>

            {/* Notifications dropdown */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-[var(--card)] border border-[var(--border)] rounded-[var(--radius-md)] shadow-[var(--shadow-lg)] z-50">
                <div className="p-4 border-b border-[var(--border)] flex items-center justify-between">
                  <h3 className="font-semibold text-[var(--foreground)]">
                    Notifications
                  </h3>
                  {unreadCount > 0 && (
                    <button
                      onClick={handleMarkAllRead}
                      className="text-xs text-[var(--primary)] hover:underline"
                    >
                      Mark all read
                    </button>
                  )}
                </div>
                <div className="max-h-96 overflow-y-auto">
                  {notificationsLoading ? (
                    <div className="flex justify-center py-8">
                      <Spinner />
                    </div>
                  ) : notifications.length === 0 ? (
                    <div className="p-8 text-center">
                      <BellIcon
                        size={48}
                        className="mx-auto text-[var(--muted-foreground)] mb-2"
                      />
                      <p className="text-sm text-[var(--muted-foreground)]">
                        No new notifications
                      </p>
                    </div>
                  ) : (
                    notifications.map((notification) => (
                      <div
                        key={notification.id}
                        className="p-4 hover:bg-[var(--muted)] cursor-pointer border-b border-[var(--border)] transition-colors"
                        onClick={() =>
                          handleNotificationClick(
                            notification.id,
                            notification.link,
                          )
                        }
                      >
                        <p className="text-sm font-medium text-[var(--foreground)]">
                          {notification.title}
                        </p>
                        <p className="text-xs text-[var(--muted-foreground)] mt-1">
                          {notification.message}
                        </p>
                        <p className="text-xs text-[var(--muted-foreground)] mt-1">
                          {formatDistanceToNow(
                            new Date(notification.created_at),
                            { addSuffix: true },
                          )}
                        </p>
                      </div>
                    ))
                  )}
                </div>
                <div className="p-3 border-t border-[var(--border)] text-center">
                  <button
                    className="text-sm text-[var(--primary)] hover:underline"
                    onClick={() => {
                      navigate("/dashboard/notifications");
                      setShowNotifications(false);
                    }}
                  >
                    View all notifications
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* User menu */}
          <div className="relative" ref={userMenuRef}>
            <button
              onClick={() => {
                setShowUserMenu(!showUserMenu);
                setShowNotifications(false); // Close notifications when opening user menu
              }}
              className="flex items-center gap-2 hover:bg-[var(--muted)] rounded-[var(--radius-md)] p-2 transition-colors cursor-pointer"
            >
              <Avatar size="sm">
                <UserIcon size={16} />
              </Avatar>
              <div className="hidden md:block text-left">
                <p className="text-sm font-medium text-[var(--foreground)]">
                  {user?.full_name || "User"}
                </p>
                <p className="text-xs text-[var(--muted-foreground)]">
                  {user?.role || "Owner"}
                </p>
              </div>
            </button>

            {/* User dropdown */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-56 bg-[var(--card)] border border-[var(--border)] rounded-[var(--radius-md)] shadow-[var(--shadow-lg)]">
                <div className="p-3 border-b border-[var(--border)]">
                  <p className="font-medium text-[var(--foreground)]">
                    {user?.full_name || "User"}
                  </p>
                  <p className="text-xs text-[var(--muted-foreground)]">
                    {user?.email}
                  </p>
                </div>
                <div className="py-2">
                  <button
                    onClick={() => {
                      navigate("/dashboard/settings");
                      setShowUserMenu(false);
                    }}
                    className="w-full flex items-center gap-3 px-4 py-2 hover:bg-[var(--muted)] transition-colors text-[var(--foreground)] cursor-pointer"
                  >
                    <SettingsIcon size={18} />
                    <span className="text-sm">Settings</span>
                  </button>
                  <button
                    onClick={() => {
                      handleLogout();
                      setShowUserMenu(false);
                    }}
                    className="w-full flex items-center gap-3 px-4 py-2 hover:bg-[var(--muted)] transition-colors text-[var(--destructive)] cursor-pointer"
                  >
                    <LogOutIcon size={18} />
                    <span className="text-sm">Logout</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

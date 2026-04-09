import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/auth";
import { MenuIcon, XIcon } from "@/components/icons";
import { ThemeSelector } from "@/components/ui/theme-selector";
import NotificationBadge from "@/components/notifications/NotificationBadge";
import NotificationCenter from "@/components/notifications/NotificationCenter";

export function Navbar() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [notificationCenterOpen, setNotificationCenterOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    // Clear session-related items (tenant context comes from httpOnly cookie)
    localStorage.removeItem("csrfToken");
    localStorage.removeItem("sessionId");
    navigate("/");
    setIsMenuOpen(false);
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background border-b border-border shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 shrink-0">
            <div className="w-8 h-8 bg-linear-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">K</span>
            </div>
            <span className="font-bold text-lg text-foreground hidden sm:inline">
              Kenikool
            </span>
          </Link>

          {/* Center Links - Desktop */}
          {!user && (
            <div className="hidden md:flex gap-8">
              <a
                href="#features"
                className="text-sm text-muted-foreground hover:text-foreground transition"
              >
                Features
              </a>
              <a
                href="#pricing"
                className="text-sm text-muted-foreground hover:text-foreground transition"
              >
                Pricing
              </a>
              <a
                href="#"
                className="text-sm text-muted-foreground hover:text-foreground transition"
              >
                About
              </a>
            </div>
          )}

          {/* Right Side - Desktop */}
          <div className="hidden md:flex items-center gap-4">
            <ThemeSelector variant="icon" />
            {user && (
              <div
                className="cursor-pointer"
                onClick={() => setNotificationCenterOpen(true)}
              >
                <NotificationBadge />
              </div>
            )}
            {user ? (
              <>
                <Link to="/dashboard">
                  <Button
                    variant="outline"
                    size="sm"
                    className="cursor-pointer"
                  >
                    Dashboard
                  </Button>
                </Link>
                <Button
                  onClick={handleLogout}
                  size="sm"
                  className="cursor-pointer"
                >
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link to="/auth/login">
                  <Button
                    variant="outline"
                    size="sm"
                    className="cursor-pointer"
                  >
                    Sign In
                  </Button>
                </Link>
                <Link to="/auth/register">
                  <Button size="sm" className="cursor-pointer">
                    Get Started
                  </Button>
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center gap-2">
            <ThemeSelector variant="icon" />
            {user && (
              <div
                className="cursor-pointer"
                onClick={() => setNotificationCenterOpen(true)}
              >
                <NotificationBadge />
              </div>
            )}
            <button
              onClick={toggleMenu}
              className="p-2 rounded-md text-foreground hover:bg-muted transition cursor-pointer"
              aria-label="Toggle menu"
            >
              {isMenuOpen ? <XIcon size={24} /> : <MenuIcon size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-border bg-card">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {!user && (
                <>
                  <a
                    href="#features"
                    onClick={() => setIsMenuOpen(false)}
                    className="block px-3 py-2 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-muted transition"
                  >
                    Features
                  </a>
                  <a
                    href="#pricing"
                    onClick={() => setIsMenuOpen(false)}
                    className="block px-3 py-2 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-muted transition"
                  >
                    Pricing
                  </a>
                  <a
                    href="#"
                    onClick={() => setIsMenuOpen(false)}
                    className="block px-3 py-2 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-muted transition"
                  >
                    About
                  </a>
                  <div className="border-t border-border my-2"></div>
                </>
              )}

              {user ? (
                <>
                  <Link
                    to="/dashboard"
                    onClick={() => setIsMenuOpen(false)}
                    className="block"
                  >
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start cursor-pointer"
                    >
                      Dashboard
                    </Button>
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-3 py-2 rounded-md text-sm text-destructive hover:bg-destructive/10 transition cursor-pointer"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/auth/login"
                    onClick={() => setIsMenuOpen(false)}
                    className="block"
                  >
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start cursor-pointer"
                    >
                      Sign In
                    </Button>
                  </Link>
                  <Link
                    to="/auth/register"
                    onClick={() => setIsMenuOpen(false)}
                    className="block"
                  >
                    <Button
                      size="sm"
                      className="w-full justify-start cursor-pointer"
                    >
                      Get Started
                    </Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Notification Center */}
      {notificationCenterOpen && (
        <NotificationCenter
          isOpen={notificationCenterOpen}
          onClose={() => setNotificationCenterOpen(false)}
        />
      )}
    </nav>
  );
}

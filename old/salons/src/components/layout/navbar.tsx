import { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ThemeSelector } from "@/components/ui/theme-selector";
import { Clock } from "@/components/dashboard/clock";
import { ScissorsIcon } from "@/components/icons";
import { Menu, X } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import type { User } from "@/lib/api/types";

export function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const pathname = location.pathname;
  const [user, setUser] = useState<User | null>(null);
  const [mounted, setMounted] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await apiClient.get("/api/auth/me");
        setUser(response.data);
      } catch (error) {
        // User not authenticated
        setUser(null);
      } finally {
        setMounted(true);
      }
    };

    fetchUser();
  }, []);

  const handleLogout = async () => {
    try {
      await apiClient.post("/api/auth/logout", {});
    } catch (error) {
      console.error("Logout error:", error);
    }
    setUser(null);
    setMobileMenuOpen(false);
    navigate("/login");
  };

  // Don't render until mounted to avoid hydration mismatch
  if (!mounted) {
    return null;
  }

  // Don't show navbar on dashboard pages (dashboard has its own header)
  if (pathname.startsWith("/dashboard")) {
    return null;
  }

  // Don't show navbar on auth pages
  if (
    pathname.startsWith("/login") ||
    pathname.startsWith("/register") ||
    pathname.startsWith("/verify") ||
    pathname.startsWith("/forgot-password") ||
    pathname.startsWith("/resend-verification")
  ) {
    return null;
  }

  return (
    <header className="h-16 bg-[var(--card)] border-b border-[var(--border)] sticky top-0 z-50">
      <div className="h-full flex items-center justify-between px-4 lg:px-6">
        {/* Left section */}
        <div className="flex items-center gap-4">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 shrink-0">
            <ScissorsIcon size={28} className="text-primary" />
            <span className="text-lg font-bold hidden sm:inline">Kenikool</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-2 lg:gap-6 ml-6">
            {/* Public Navigation Links */}
            {!user && (
              <div className="flex items-center gap-2 lg:gap-4">
                <Link to="/marketplace">
                  <Button variant="ghost" size="sm">
                    Browse
                  </Button>
                </Link>
                <Link to="/about">
                  <Button variant="ghost" size="sm">
                    About
                  </Button>
                </Link>
                <Link to="/contact">
                  <Button variant="ghost" size="sm">
                    Contact
                  </Button>
                </Link>
              </div>
            )}
          </nav>
        </div>

        {/* Right section */}
        <div className="flex items-center gap-3">
          {/* Clock - always visible */}
          <Clock />

          {/* Theme selector - always visible */}
          <ThemeSelector variant="icon" />

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <>
                <Link to="/dashboard">
                  <Button
                    variant={pathname === "/dashboard" ? "primary" : "ghost"}
                    size="sm"
                  >
                    Dashboard
                  </Button>
                </Link>
                <div className="flex items-center gap-2 pl-3 border-l border-[var(--border)]">
                  <span className="text-xs text-[var(--muted-foreground)] truncate max-w-[120px]">
                    {user.email}
                  </span>
                  <Button variant="outline" size="sm" onClick={handleLogout}>
                    Logout
                  </Button>
                </div>
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" size="sm">
                    Login
                  </Button>
                </Link>
                <Link to="/register">
                  <Button variant="primary" size="sm">
                    Get Started
                  </Button>
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 hover:bg-[var(--muted)] rounded-md transition-colors cursor-pointer"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <nav className="md:hidden border-t border-[var(--border)] bg-[var(--card)]">
          <div className="px-4 py-4 space-y-2">
            {!user && (
              <>
                <Link
                  to="/marketplace"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block"
                >
                  <Button variant="ghost" className="w-full justify-start">
                    Browse Salons
                  </Button>
                </Link>
                <Link
                  to="/about"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block"
                >
                  <Button variant="ghost" className="w-full justify-start">
                    About
                  </Button>
                </Link>
                <Link
                  to="/contact"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block"
                >
                  <Button variant="ghost" className="w-full justify-start">
                    Contact
                  </Button>
                </Link>
              </>
            )}

            {user ? (
              <>
                <Link
                  to="/dashboard"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block"
                >
                  <Button
                    variant={pathname === "/dashboard" ? "primary" : "ghost"}
                    className="w-full justify-start"
                  >
                    Dashboard
                  </Button>
                </Link>
                <div className="px-2 py-2 text-sm text-[var(--muted-foreground)] break-all">
                  {user.email}
                </div>
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={handleLogout}
                >
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block"
                >
                  <Button variant="ghost" className="w-full justify-start">
                    Login
                  </Button>
                </Link>
                <Link
                  to="/register"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block"
                >
                  <Button variant="primary" className="w-full justify-start">
                    Get Started
                  </Button>
                </Link>
              </>
            )}
          </div>
        </nav>
      )}
    </header>
  );
}

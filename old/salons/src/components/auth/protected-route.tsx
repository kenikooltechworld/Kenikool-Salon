import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Spinner } from "@/components/ui/spinner";
import { apiClient } from "@/lib/api/client";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const pathname = location.pathname;
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check authentication by making a test request
    // If cookies are valid, the request will succeed
    // If cookies are invalid/expired, we'll get a 401
    const checkAuth = async () => {
      try {
        // Try to fetch user data - this will use cookies automatically
        const response = await apiClient.get("/api/auth/me");

        if (response.status === 200) {
          setIsAuthenticated(true);
        } else {
          setIsAuthenticated(false);
          localStorage.setItem("redirectAfterLogin", pathname);
          navigate("/login");
        }
      } catch (error: any) {
        // 401 or network error means not authenticated
        if (error.response?.status === 401 || error.code === "ERR_NETWORK") {
          setIsAuthenticated(false);
          localStorage.setItem("redirectAfterLogin", pathname);
          navigate("/login");
        } else {
          // Other errors - assume authenticated to avoid blocking
          setIsAuthenticated(true);
        }
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [navigate, pathname]);

  // Show loading spinner while checking authentication
  if (isLoading || isAuthenticated === null) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  // If not authenticated, show loading while redirecting
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  return <>{children}</>;
}

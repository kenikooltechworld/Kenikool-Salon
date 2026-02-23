import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { useAuthStore } from "@/stores/auth";
import { useToast } from "@/components/ui/toast";
import { apiClient } from "@/lib/utils/api";

export default function Login() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const setUser = useAuthStore((state) => state.setUser);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const response = await apiClient.post("/auth/login", {
        email,
        password,
      });

      if (response.data) {
        // Fetch current user data
        const userResponse = await apiClient.get("/auth/me");
        if (userResponse.data) {
          // Handle wrapped response format { data: { ... } }
          const user = userResponse.data.data || userResponse.data;
          const roleIds = user.role_ids || [];

          setUser({
            id: user.id,
            email: user.email,
            firstName: user.first_name,
            lastName: user.last_name,
            phone: user.phone,
            role: roleIds[0] || "user",
            tenantId: user.tenant_id,
          });

          // Show success toast
          showToast({
            title: "Welcome Back!",
            description: `Logged in as ${user.email}`,
            variant: "success",
            duration: 3000,
          });

          // Determine redirect path based on role
          // Fetch roles to check user's role and route accordingly
          try {
            const rolesResponse = await apiClient.get("/roles");
            const roles = rolesResponse.data?.roles || [];

            // Create a map of role IDs to role names
            const roleIdToName: { [key: string]: string } = {};
            roles.forEach((role: any) => {
              roleIdToName[role.id] = role.name;
            });

            // Get user's role names
            const userRoleNames = roleIds
              .map((id: string) => roleIdToName[id])
              .filter(Boolean);

            // Route based on role priority (Owner > Manager > Staff > Customer)
            let redirectPath = "/dashboard"; // default

            if (userRoleNames.includes("Owner")) {
              redirectPath = "/dashboard"; // Owner Dashboard
            } else if (userRoleNames.includes("Manager")) {
              redirectPath = "/manager"; // Manager Dashboard
            } else if (userRoleNames.includes("Staff")) {
              redirectPath = "/appointments"; // Staff Dashboard - view their appointments
            } else if (userRoleNames.includes("Customer")) {
              redirectPath = "/my-account"; // Customer Dashboard
            }

            navigate(redirectPath);
          } catch (roleError) {
            // If role fetching fails, default to dashboard
            console.warn(
              "Failed to fetch roles, defaulting to dashboard",
              roleError,
            );
            navigate("/dashboard");
          }
        }
      }
    } catch (err: any) {
      if (
        err.response?.status === 403 &&
        err.response?.headers["x-mfa-required"]
      ) {
        // MFA required - redirect to MFA verification
        showToast({
          title: "MFA Required",
          description: "Please verify your identity with your MFA method.",
          variant: "info",
          duration: 3000,
        });
        navigate("/auth/mfa-verify", { state: { email } });
      } else {
        const errorMessage =
          err.response?.data?.detail ||
          err.message ||
          "Failed to login. Please check your credentials.";
        setError(errorMessage);
        showToast({
          title: "Login Failed",
          description: errorMessage,
          variant: "error",
          duration: 5000,
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 to-secondary/10 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">Sign In</h1>
            <p className="text-muted-foreground">Welcome back to Kenikool</p>
          </div>

          {error && (
            <Alert variant="error" className="mb-6">
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  disabled={isLoading}
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <Link
                to="/auth/forgot-password"
                className="text-sm text-primary hover:underline"
              >
                Forgot password?
              </Link>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              disabled={isLoading || !email || !password}
              className="w-full"
            >
              {isLoading ? (
                <>
                  <Spinner className="mr-2 h-4 w-4" />
                  Signing in...
                </>
              ) : (
                "Sign In"
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              Don't have an account?{" "}
              <Link
                to="/auth/register"
                className="text-primary hover:underline font-medium"
              >
                Create one
              </Link>
            </p>
          </div>

          <div className="mt-6 pt-6 border-t border-border">
            <p className="text-xs text-muted-foreground text-center">
              By signing in, you agree to our{" "}
              <a href="#" className="text-primary hover:underline">
                Terms of Service
              </a>{" "}
              and{" "}
              <a href="#" className="text-primary hover:underline">
                Privacy Policy
              </a>
            </p>
          </div>
        </Card>

        <div className="mt-6 text-center text-sm text-muted-foreground">
          <p>
            Need help?{" "}
            <a href="#" className="text-primary hover:underline">
              Contact Support
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

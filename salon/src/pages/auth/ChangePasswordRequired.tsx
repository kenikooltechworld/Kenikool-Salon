import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";
import { apiClient } from "@/lib/utils/api";
import { useAuthStore } from "@/stores/auth";
import { useTenantStore } from "@/stores/tenant";

export default function ChangePasswordRequired() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const setUser = useAuthStore((state) => state.setUser);
  const setTenant = useTenantStore((state) => state.setTenant);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validate passwords match
    if (newPassword !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    // Validate password length
    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    setIsLoading(true);

    try {
      await apiClient.post("/auth/change-password-required", {
        new_password: newPassword,
      });

      showToast({
        title: "Success",
        description: "Password changed successfully. Logging you in...",
        variant: "success",
        duration: 3000,
      });

      // Fetch user data and redirect to appropriate dashboard
      try {
        const userResponse = await apiClient.get("/auth/me");
        if (userResponse.data) {
          const userData = userResponse.data.user || userResponse.data;
          const roleNames = userData.roleNames || [];

          // Set user in auth store
          setUser({
            id: userData.id,
            email: userData.email,
            firstName: userData.firstName,
            lastName: userData.lastName,
            phone: userData.phone,
            role: roleNames[0] || "user",
            roleNames: roleNames,
            tenantId: userData.tenantId,
          });

          // Set tenant in store
          setTenant({
            id: userData.tenantId,
            name: "",
            subdomain: "",
            subscriptionTier: "starter",
            status: "active",
            isPublished: false,
          });

          // Determine redirect path based on role
          let redirectPath = "/dashboard";
          if (roleNames.includes("Owner")) {
            redirectPath = "/dashboard";
          } else if (roleNames.includes("Manager")) {
            redirectPath = "/manager";
          } else if (roleNames.includes("Staff")) {
            redirectPath = "/staff/dashboard";
          } else if (roleNames.includes("Customer")) {
            redirectPath = "/my-account";
          }

          // Redirect after a short delay
          setTimeout(() => {
            navigate(redirectPath);
          }, 1500);
        }
      } catch (userErr) {
        // If we can't fetch user data, just redirect to dashboard
        setTimeout(() => {
          navigate("/dashboard");
        }, 1500);
      }
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail ||
        err.message ||
        "Failed to change password";
      setError(errorMessage);
      showToast({
        title: "Error",
        description: errorMessage,
        variant: "error",
        duration: 5000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 to-secondary/10 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">
              Change Password
            </h1>
            <p className="text-muted-foreground">
              You must change your password before continuing
            </p>
          </div>

          <Alert variant="warning" className="mb-6">
            <AlertTitle>Required Action</AlertTitle>
            <AlertDescription>
              For security reasons, you must set a new password on your first
              login. This password will be used for all future logins.
            </AlertDescription>
          </Alert>

          {error && (
            <Alert variant="error" className="mb-6">
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="newPassword">New Password</Label>
              <div className="relative">
                <Input
                  id="newPassword"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
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
              <p className="text-xs text-muted-foreground">
                Minimum 8 characters
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <div className="relative">
                <Input
                  id="confirmPassword"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  disabled={isLoading}
                  required
                />
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              disabled={
                isLoading ||
                !newPassword ||
                !confirmPassword ||
                newPassword.length < 8
              }
              className="w-full"
            >
              {isLoading ? (
                <>
                  <Spinner className="mr-2 h-4 w-4" />
                  Changing Password...
                </>
              ) : (
                "Change Password"
              )}
            </Button>
          </form>

          <div className="mt-6 pt-6 border-t border-border">
            <p className="text-xs text-muted-foreground text-center">
              This is a required security step. You cannot proceed without
              changing your password.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}

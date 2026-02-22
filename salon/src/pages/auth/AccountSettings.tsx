import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { Switch } from "@/components/ui/switch";
import { useAuthStore } from "@/stores/auth";
import { apiClient } from "@/lib/utils/api";

export default function AccountSettings() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const setUser = useAuthStore((state) => state.setUser);
  const logout = useAuthStore((state) => state.logout);

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [mfaEnabled, setMfaEnabled] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingUser, setIsLoadingUser] = useState(true);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate("/auth/login");
      return;
    }

    const fetchUserData = async () => {
      try {
        const response = await apiClient.get("/auth/me");
        setFirstName(response.data.first_name || "");
        setLastName(response.data.last_name || "");
        setEmail(response.data.email || "");
        setPhone(response.data.phone || "");
        setMfaEnabled(response.data.mfa_enabled || false);
      } catch (err: any) {
        setError("Failed to load user data");
      } finally {
        setIsLoadingUser(false);
      }
    };

    fetchUserData();
  }, [user, navigate]);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsLoading(true);

    try {
      await apiClient.put("/auth/me", {
        first_name: firstName,
        last_name: lastName,
        phone,
      });

      setUser({
        ...user!,
        firstName,
        lastName,
        phone,
      });

      setSuccess("Profile updated successfully");
    } catch (err: any) {
      setError(
        err.response?.data?.detail || err.message || "Failed to update profile",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleChangeEmail = async () => {
    if (!email || email === user?.email) {
      setError("Please enter a different email address");
      return;
    }

    setError("");
    setSuccess("");
    setIsLoading(true);

    try {
      await apiClient.post("/auth/change-email", {
        new_email: email,
      });

      setSuccess(
        "Verification link sent to your new email. Please verify to complete the change.",
      );
    } catch (err: any) {
      setError(
        err.response?.data?.detail || err.message || "Failed to change email",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleMFA = async () => {
    setError("");
    setSuccess("");
    setIsLoading(true);

    try {
      if (mfaEnabled) {
        await apiClient.post("/auth/mfa/disable", {});
        setMfaEnabled(false);
        setSuccess("Two-factor authentication disabled");
      } else {
        navigate("/auth/mfa-setup");
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Failed to update MFA settings",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    setError("");
    setSuccess("");
    setIsLoading(true);

    try {
      await apiClient.post("/auth/delete-account", {});
      logout();
      navigate("/auth/login");
    } catch (err: any) {
      setError(
        err.response?.data?.detail || err.message || "Failed to delete account",
      );
    } finally {
      setIsLoading(false);
      setShowDeleteConfirm(false);
    }
  };

  const handleLogout = () => {
    logout();
    localStorage.removeItem("tenantId");
    localStorage.removeItem("csrfToken");
    localStorage.removeItem("sessionId");
    navigate("/auth/login");
  };

  if (isLoadingUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary/10 to-secondary/10 flex items-center justify-center">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 to-secondary/10 p-4">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">
            Account Settings
          </h1>
          <p className="text-muted-foreground">
            Manage your account and security preferences
          </p>
        </div>

        {error && (
          <Alert variant="error" className="mb-6">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert variant="success" className="mb-6">
            <AlertTitle>Success</AlertTitle>
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        {/* Profile Section */}
        <Card className="p-6 mb-6">
          <h2 className="text-2xl font-bold text-foreground mb-6">
            Profile Information
          </h2>

          <form onSubmit={handleUpdateProfile} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName">First Name</Label>
                <Input
                  id="firstName"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  disabled={isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="lastName">Last Name</Label>
                <Input
                  id="lastName"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  disabled={isLoading}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">Phone Number</Label>
              <Input
                id="phone"
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                disabled={isLoading}
              />
            </div>

            <Button type="submit" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Spinner className="mr-2 h-4 w-4" />
                  Saving...
                </>
              ) : (
                "Save Changes"
              )}
            </Button>
          </form>
        </Card>

        {/* Email Section */}
        <Card className="p-6 mb-6">
          <h2 className="text-2xl font-bold text-foreground mb-6">
            Email Address
          </h2>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
              />
            </div>

            <Button
              onClick={handleChangeEmail}
              disabled={isLoading || email === user?.email}
              variant="outline"
            >
              {isLoading ? (
                <>
                  <Spinner className="mr-2 h-4 w-4" />
                  Updating...
                </>
              ) : (
                "Change Email"
              )}
            </Button>
          </div>
        </Card>

        {/* Security Section */}
        <Card className="p-6 mb-6">
          <h2 className="text-2xl font-bold text-foreground mb-6">Security</h2>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-base">Two-Factor Authentication</Label>
                <p className="text-sm text-muted-foreground">
                  {mfaEnabled
                    ? "Enabled - Your account is protected"
                    : "Disabled - Add an extra layer of security"}
                </p>
              </div>
              <Switch
                checked={mfaEnabled}
                onCheckedChange={handleToggleMFA}
                disabled={isLoading}
              />
            </div>

            <div className="pt-4 border-t border-border">
              <Button
                onClick={() => navigate("/auth/change-password")}
                variant="outline"
                className="w-full"
              >
                Change Password
              </Button>
            </div>
          </div>
        </Card>

        {/* Danger Zone */}
        <Card className="p-6 border-destructive/50 bg-destructive/5">
          <h2 className="text-2xl font-bold text-destructive mb-6">
            Danger Zone
          </h2>

          <div className="space-y-4">
            <Button onClick={handleLogout} variant="outline" className="w-full">
              Logout
            </Button>

            {!showDeleteConfirm ? (
              <Button
                onClick={() => setShowDeleteConfirm(true)}
                variant="destructive"
                className="w-full"
              >
                Delete Account
              </Button>
            ) : (
              <div className="space-y-4 p-4 bg-destructive/10 rounded-lg border border-destructive/20">
                <p className="text-sm text-foreground">
                  Are you sure you want to delete your account? This action
                  cannot be undone. All your data will be permanently deleted.
                </p>
                <div className="flex gap-2">
                  <Button
                    onClick={() => setShowDeleteConfirm(false)}
                    variant="outline"
                    className="flex-1"
                    disabled={isLoading}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleDeleteAccount}
                    variant="destructive"
                    className="flex-1"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <Spinner className="mr-2 h-4 w-4" />
                        Deleting...
                      </>
                    ) : (
                      "Delete Account"
                    )}
                  </Button>
                </div>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}

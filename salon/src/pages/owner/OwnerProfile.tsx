import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/components/ui/toast";
import { useAuthStore } from "@/stores/auth";
import { apiClient } from "@/lib/utils/api";
import {
  UserIcon,
  BuildingIcon,
  TrendingUpIcon,
  BellIcon,
  LockIcon,
  CheckCircleIcon,
  AlertCircleIcon,
} from "@/components/icons";

interface OwnerProfile {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  phone: string;
  role: string;
  roleNames: string[];
  tenantId: string;
}

interface BusinessProfile {
  salon_name: string;
  email: string;
  phone: string;
  address: string;
  subdomain?: string;
  subdomain_url?: string;
  subscription_tier?: string;
  status?: string;
}

interface ActivityStats {
  totalAppointments: number;
  totalRevenue: number;
  totalCustomers: number;
  pendingActions: number;
}

export default function OwnerProfile() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const setUser = useAuthStore((state) => state.setUser);
  const { showToast } = useToast();

  const [profile, setProfile] = useState<OwnerProfile>({
    id: "",
    email: "",
    firstName: "",
    lastName: "",
    phone: "",
    role: "",
    roleNames: [],
    tenantId: "",
  });
  const [business, setBusiness] = useState<BusinessProfile>({
    salon_name: "",
    email: "",
    phone: "",
    address: "",
  });
  const [activity, setActivity] = useState<ActivityStats>({
    totalAppointments: 0,
    totalRevenue: 0,
    totalCustomers: 0,
    pendingActions: 0,
  });
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);
  const [isLoadingBusiness, setIsLoadingBusiness] = useState(true);
  const [isLoadingActivity, setIsLoadingActivity] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [activeTab, setActiveTab] = useState<"profile" | "business" | "activity" | "notifications" | "security">("profile");

  useEffect(() => {
    fetchProfile();
    fetchBusiness();
    fetchActivity();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await apiClient.get("/auth/me");
      const userData = response.data.user || response.data;
      setProfile(userData);
    } catch (err: any) {
      setError("Failed to load profile");
    } finally {
      setIsLoadingProfile(false);
    }
  };

  const fetchBusiness = async () => {
    try {
      const response = await apiClient.get("/settings");
      const settings = response.data.data || response.data;
      setBusiness({
        salon_name: settings.salon_name || "",
        email: settings.email || "",
        phone: settings.phone || "",
        address: settings.address || "",
        subdomain: settings.subdomain,
        subdomain_url: settings.subdomain_url,
        subscription_tier: settings.subscription_tier,
        status: settings.status,
      });
    } catch (err: any) {
      console.error("Failed to load business settings:", err);
    } finally {
      setIsLoadingBusiness(false);
    }
  };

  const fetchActivity = async () => {
    try {
      const [metricsRes, pendingRes] = await Promise.all([
        apiClient.get("/owner/dashboard/metrics"),
        apiClient.get("/owner/dashboard/pending-actions"),
      ]);

      const metrics = metricsRes.data.data || metricsRes.data;
      const pending = pendingRes.data.data || pendingRes.data;

      setActivity({
        totalAppointments: metrics.appointments?.thisMonth || 0,
        totalRevenue: metrics.revenue?.current || 0,
        totalCustomers: 0,
        pendingActions: pending.total || 0,
      });
    } catch (err: any) {
      console.error("Failed to load activity stats:", err);
    } finally {
      setIsLoadingActivity(false);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setError("");
    setSuccess("");

    try {
      await apiClient.put("/auth/me", {
        first_name: profile.firstName,
        last_name: profile.lastName,
        phone: profile.phone,
      });

      setUser({
        ...user!,
        firstName: profile.firstName,
        lastName: profile.lastName,
        phone: profile.phone,
      });

      setSuccess("Profile updated successfully");
      showToast({
        title: "Success",
        description: "Profile updated successfully",
        variant: "success",
      });
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || "Failed to update profile";
      setError(message);
      showToast({
        title: "Error",
        description: message,
        variant: "error",
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleUpdateBusiness = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setError("");
    setSuccess("");

    try {
      await apiClient.put("/settings", {
        salon_name: business.salon_name,
        email: business.email,
        phone: business.phone,
        address: business.address,
      });
      setSuccess("Business profile updated successfully");
      showToast({
        title: "Success",
        description: "Business profile updated successfully",
        variant: "success",
      });
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || "Failed to update business profile";
      setError(message);
      showToast({
        title: "Error",
        description: message,
        variant: "error",
      });
    } finally {
      setIsSaving(false);
    }
  };

  const getSubscriptionBadge = () => {
    const tier = business.subscription_tier || "starter";
    const colors: Record<string, string> = {
      starter: "bg-gray-100 text-gray-800",
      professional: "bg-blue-100 text-blue-800",
      enterprise: "bg-purple-100 text-purple-800",
    };
    return colors[tier] || colors.starter;
  };

  const getStatusBadge = () => {
    const status = business.status || "active";
    const colors: Record<string, string> = {
      active: "bg-green-100 text-green-800",
      inactive: "bg-red-100 text-red-800",
      trial: "bg-yellow-100 text-yellow-800",
    };
    return colors[status] || colors.active;
  };

  if (isLoadingProfile || isLoadingBusiness || isLoadingActivity) {
    return (
      <div className="space-y-6">
        <div className="mb-8">
          <Skeleton className="h-9 w-48 mb-2" />
          <Skeleton className="h-5 w-64" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="p-6">
              <Skeleton className="h-5 w-24 mb-2" />
              <Skeleton className="h-8 w-16" />
            </Card>
          ))}
        </div>

        <Card className="p-6">
          <Skeleton className="h-7 w-40 mb-6" />
          <div className="space-y-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-10 w-full" />
              </div>
            ))}
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">My Profile</h1>
        <p className="text-muted-foreground mt-1">
          Manage your personal and business profile
        </p>
      </div>

      {error && (
        <Alert variant="error">
          <AlertCircleIcon size={20} />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert variant="success">
          <CheckCircleIcon size={20} />
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {/* Activity Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <TrendingUpIcon size={24} className="text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Revenue (This Month)</p>
              <p className="text-2xl font-bold text-foreground">
                ₦{activity.totalRevenue.toLocaleString()}
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <UserIcon size={24} className="text-green-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Appointments</p>
              <p className="text-2xl font-bold text-foreground">
                {activity.totalAppointments}
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
              <BellIcon size={24} className="text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Pending Actions</p>
              <p className="text-2xl font-bold text-foreground">
                {activity.pendingActions}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border">
        {[
          { id: "profile", label: "Personal Profile", icon: UserIcon },
          { id: "business", label: "Business Profile", icon: BuildingIcon },
          { id: "activity", label: "Activity", icon: TrendingUpIcon },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2 font-medium text-sm transition flex items-center gap-2 ${
                activeTab === tab.id
                  ? "text-primary border-b-2 border-primary"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Personal Profile Tab */}
      {activeTab === "profile" && (
        <Card className="p-6">
          <form onSubmit={handleUpdateProfile} className="space-y-6">
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-foreground">
                Personal Information
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="firstName">First Name</Label>
                  <Input
                    id="firstName"
                    value={profile.firstName}
                    onChange={(e) =>
                      setProfile({ ...profile, firstName: e.target.value })
                    }
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input
                    id="lastName"
                    value={profile.lastName}
                    onChange={(e) =>
                      setProfile({ ...profile, lastName: e.target.value })
                    }
                    disabled={isSaving}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  value={profile.email}
                  disabled
                  className="bg-muted opacity-60"
                />
                <p className="text-xs text-muted-foreground">
                  Email cannot be changed here. Use Account Settings to change email.
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Phone Number</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={profile.phone}
                  onChange={(e) =>
                    setProfile({ ...profile, phone: e.target.value })
                  }
                  disabled={isSaving}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="role">Role</Label>
                <Input
                  id="role"
                  value={profile.roleNames?.join(", ") || profile.role}
                  disabled
                  className="bg-muted opacity-60"
                />
              </div>
            </div>

            <div className="flex justify-end">
              <Button type="submit" disabled={isSaving}>
                {isSaving ? "Saving..." : "Save Changes"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* Business Profile Tab */}
      {activeTab === "business" && (
        <Card className="p-6">
          <form onSubmit={handleUpdateBusiness} className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-foreground">
                  Business Information
                </h3>
                <div className="flex gap-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getSubscriptionBadge()}`}>
                    {business.subscription_tier || "Starter"}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge()}`}>
                    {business.status || "Active"}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="salonName">Salon/Business Name</Label>
                  <Input
                    id="salonName"
                    value={business.salon_name}
                    onChange={(e) =>
                      setBusiness({ ...business, salon_name: e.target.value })
                    }
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="businessEmail">Business Email</Label>
                  <Input
                    id="businessEmail"
                    type="email"
                    value={business.email}
                    onChange={(e) =>
                      setBusiness({ ...business, email: e.target.value })
                    }
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="businessPhone">Business Phone</Label>
                  <Input
                    id="businessPhone"
                    type="tel"
                    value={business.phone}
                    onChange={(e) =>
                      setBusiness({ ...business, phone: e.target.value })
                    }
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="address">Address</Label>
                  <Input
                    id="address"
                    value={business.address}
                    onChange={(e) =>
                      setBusiness({ ...business, address: e.target.value })
                    }
                    disabled={isSaving}
                  />
                </div>
              </div>

              {business.subdomain_url && (
                <div className="space-y-2">
                  <Label>Subdomain URL</Label>
                  <div className="flex gap-2">
                    <Input
                      value={business.subdomain_url}
                      disabled
                      className="bg-muted opacity-60"
                    />
                    <Button
                      type="button"
                      variant="outline"
                      onClick={async () => {
                        try {
                          await navigator.clipboard.writeText(business.subdomain_url || "");
                          showToast({
                            title: "Copied",
                            description: "URL copied to clipboard",
                            variant: "success",
                          });
                        } catch {
                          showToast({
                            title: "Error",
                            description: "Failed to copy URL",
                            variant: "error",
                          });
                        }
                      }}
                    >
                      Copy
                    </Button>
                  </div>
                </div>
              )}
            </div>

            <div className="flex justify-end">
              <Button type="submit" disabled={isSaving}>
                {isSaving ? "Saving..." : "Save Changes"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* Activity Tab */}
      {activeTab === "activity" && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">
            Recent Activity
          </h3>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Total Appointments (This Month)</p>
                <p className="text-2xl font-bold text-foreground">
                  {activity.totalAppointments}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Revenue (This Month)</p>
                <p className="text-2xl font-bold text-foreground">
                  ₦{activity.totalRevenue.toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Pending Actions</p>
                <p className="text-2xl font-bold text-foreground">
                  {activity.pendingActions}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Account Status</p>
                <p className="text-sm font-medium text-foreground capitalize">
                  {business.status || "Active"}
                </p>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert } from "@/components/ui/alert";
import { useAppointments } from "@/hooks/useAppointments";
import { useAuthStore } from "@/stores/auth";
import { useTenantSettings } from "@/hooks/owner/useTenantSettings";
import { useCustomerProfile, useUpdateCustomerProfile } from "@/hooks/useCustomerAuth";
import { CalendarIcon, UserIcon, SettingsIcon, BuildingIcon } from "@/components/icons";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useToast } from "@/components/ui/toast";
import { usePageRefresh } from "@/contexts/PageRefreshContext";

export default function MyAccountPage() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const setUser = useAuthStore((state) => state.setUser);
  const { showToast } = useToast();
  const { data: appointments = [], isLoading: appointmentsLoading, refetch: refetchAppointments } = useAppointments();
  const { data: tenantSettings, isLoading: settingsLoading } = useTenantSettings();
  const { data: customerProfile, isLoading: customerLoading, refetch: refetchCustomerProfile } = useCustomerProfile();
  const updateCustomerProfile = useUpdateCustomerProfile();
  const [activeTab, setActiveTab] = useState<"bookings" | "profile">(
    "bookings",
  );
  const { setRefreshHandler } = usePageRefresh();

  const { data: authData, isLoading: authLoading, refetch: refetchAuth } = useQuery({
    queryKey: ["current-user"],
    queryFn: async () => {
      const { data } = await apiClient.get("/auth/me");
      const payload = data.user || data;
      return payload;
    },
  });

  useEffect(() => {
    if (authData) {
      setUser({
        id: authData.id,
        email: authData.email,
        firstName: authData.firstName,
        lastName: authData.lastName,
        phone: authData.phone,
        role: authData.role,
        roleNames: authData.roleNames,
        tenantId: authData.tenantId,
      });
    }
  }, [authData, setUser]);

  useEffect(() => {
    setRefreshHandler(() => {
      refetchAppointments();
      refetchCustomerProfile();
      refetchAuth();
    });
  }, [refetchAppointments, refetchCustomerProfile, refetchAuth, setRefreshHandler]);

  const currentUser = authData || user;
  const isCustomer = !!customerProfile && !currentUser?.roleNames?.some((r: string) => ["Owner", "Manager", "Staff"].includes(r));

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "confirmed":
        return "default";
      case "pending":
        return "secondary";
      case "completed":
        return "outline";
      case "cancelled":
        return "destructive";
      default:
        return "secondary";
    }
  };

  const getStatusLabel = (status: string) => {
    return status
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const upcomingAppointments = appointments.filter(
    (a: any) => a.status === "confirmed" || a.status === "pending",
  );
  const pastAppointments = appointments.filter(
    (a: any) => a.status === "completed",
  );

  const handleUpdateCustomerProfile = async (data: { first_name?: string; last_name?: string; phone?: string; address?: string; notification_preferences?: Record<string, boolean> }) => {
    try {
      await updateCustomerProfile.mutateAsync(data);
      showToast({
        title: "Success",
        description: "Profile updated successfully",
        variant: "success",
      });
    } catch (error: any) {
      showToast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to update profile",
        variant: "error",
      });
    }
  };

  if (authLoading || customerLoading) {
    return (
      <div className="w-full space-y-6 px-0 sm:px-0">
        <div className="space-y-2">
          <Skeleton className="h-8 w-40" />
          <Skeleton className="h-4 w-64" />
        </div>
        <div className="flex gap-2 border-b border-border">
          <Skeleton className="h-10 w-32" />
          <Skeleton className="h-10 w-32" />
        </div>
        <Card className="p-6">
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <Skeleton className="w-16 h-16 rounded-full" />
              <div className="space-y-2">
                <Skeleton className="h-5 w-40" />
                <Skeleton className="h-4 w-56" />
              </div>
            </div>
            <div className="border-t border-border pt-4 space-y-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="space-y-2">
                  <Skeleton className="h-3 w-16" />
                  <Skeleton className="h-4 w-full" />
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>
    );
  }

  if (!currentUser && !customerProfile) {
    return (
      <Alert variant="error">
        Failed to load profile. Please refresh the page.
      </Alert>
    );
  }

  const displayUser = isCustomer ? customerProfile : currentUser;

  return (
    <div className="w-full space-y-6 px-0 sm:px-0">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-foreground">My Account</h2>
            <p className="text-sm text-muted-foreground">
              Manage your bookings and profile
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border">
        <button
          onClick={() => setActiveTab("bookings")}
          className={`px-4 py-2 font-medium text-sm transition ${
            activeTab === "bookings"
              ? "text-primary border-b-2 border-primary"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <CalendarIcon size={16} className="inline mr-2" />
          My Bookings
        </button>
        <button
          onClick={() => setActiveTab("profile")}
          className={`px-4 py-2 font-medium text-sm transition ${
            activeTab === "profile"
              ? "text-primary border-b-2 border-primary"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <UserIcon size={16} className="inline mr-2" />
          Profile
        </button>
      </div>

      {/* Bookings Tab */}
      {activeTab === "bookings" && (
        <div className="space-y-6">
          {/* Upcoming Bookings */}
          <div className="space-y-4">
            <div className="flex flex-col gap-2">
              <h3 className="text-lg font-semibold text-foreground">
                Upcoming Bookings
              </h3>
              <p className="text-sm text-muted-foreground">
                {upcomingAppointments.length} upcoming appointment
                {upcomingAppointments.length !== 1 ? "s" : ""}
              </p>
            </div>

            {appointmentsLoading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <Card key={i} className="p-4">
                    <div className="space-y-3">
                      <div className="flex items-start justify-between">
                        <div className="space-y-2">
                          <Skeleton className="h-5 w-32" />
                          <Skeleton className="h-4 w-24" />
                        </div>
                        <Skeleton className="h-6 w-20" />
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="space-y-2">
                          <Skeleton className="h-3 w-16" />
                          <Skeleton className="h-4 w-full" />
                        </div>
                        <div className="space-y-2">
                          <Skeleton className="h-3 w-16" />
                          <Skeleton className="h-4 w-full" />
                        </div>
                      </div>
                      <div className="flex gap-2 pt-2">
                        <Skeleton className="h-9 flex-1" />
                        <Skeleton className="h-9 flex-1" />
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : upcomingAppointments.length > 0 ? (
              <div className="space-y-3">
                {upcomingAppointments.map((appointment: any) => (
                  <Card key={appointment.id} className="p-4">
                    <div className="space-y-3">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-semibold text-foreground">
                            {appointment.service_name || "Service"}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            with {appointment.staff_name || "Staff Member"}
                          </p>
                        </div>
                        <Badge
                          variant={getStatusBadgeVariant(appointment.status)}
                        >
                          {getStatusLabel(appointment.status)}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-xs text-muted-foreground">
                            Date & Time
                          </p>
                          <p className="text-foreground font-medium">
                            {appointment.startTime
                              ? new Date(appointment.startTime).toLocaleString()
                              : "N/A"}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">
                            Duration
                          </p>
                          <p className="text-foreground font-medium">
                            {appointment.duration_minutes || "N/A"} minutes
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-2 pt-2">
                        <Button
                          variant="outline"
                          size="sm"
                          className="flex-1 cursor-pointer"
                        >
                          View Details
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          className="flex-1 cursor-pointer text-destructive hover:text-destructive"
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No upcoming bookings
              </div>
            )}
          </div>

          {/* Past Bookings */}
          <div className="space-y-4">
            <div className="flex flex-col gap-2">
              <h3 className="text-lg font-semibold text-foreground">
                Past Bookings
              </h3>
              <p className="text-sm text-muted-foreground">
                {pastAppointments.length} completed appointment
                {pastAppointments.length !== 1 ? "s" : ""}
              </p>
            </div>

            {pastAppointments.length > 0 ? (
              <div className="space-y-3">
                {pastAppointments.slice(0, 5).map((appointment: any) => (
                  <Card key={appointment.id} className="p-4 opacity-75">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-semibold text-foreground">
                          {appointment.service_name || "Service"}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {appointment.startTime
                            ? new Date(
                                appointment.startTime,
                              ).toLocaleDateString()
                            : "N/A"}
                        </p>
                      </div>
                      <Badge variant="outline">Completed</Badge>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No past bookings
              </div>
            )}
          </div>
        </div>
      )}

      {/* Profile Tab */}
      {activeTab === "profile" && (
        <div className="space-y-6">
          {settingsLoading ? (
            <div className="space-y-6">
              <Card className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <Skeleton className="w-16 h-16 rounded-full" />
                    <div className="space-y-2">
                      <Skeleton className="h-5 w-40" />
                      <Skeleton className="h-4 w-56" />
                    </div>
                  </div>
                  <div className="border-t border-border pt-4 space-y-4">
                    {[...Array(3)].map((_, i) => (
                      <div key={i} className="space-y-2">
                        <Skeleton className="h-3 w-16" />
                        <Skeleton className="h-4 w-full" />
                      </div>
                    ))}
                  </div>
                </div>
              </Card>
              <Card className="p-6">
                <div className="space-y-4">
                  <Skeleton className="h-5 w-24" />
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="flex items-center justify-between">
                      <Skeleton className="h-4 w-40" />
                      <Skeleton className="h-4 w-12" />
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          ) : (
            <>
              <Card className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
                      <UserIcon size={32} className="text-primary" />
                    </div>
                    <div>
                      <p className="text-lg font-semibold text-foreground">
                        {displayUser?.firstName} {displayUser?.lastName}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {displayUser?.email}
                      </p>
                    </div>
                  </div>

                  <div className="border-t border-border pt-4 space-y-4">
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Email</p>
                      <p className="text-foreground">{displayUser?.email}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Phone</p>
                      <p className="text-foreground">
                        {displayUser?.phone || "Not provided"}
                      </p>
                    </div>
                    {isCustomer && customerProfile && (
                      <>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Address</p>
                          <p className="text-foreground">
                            {customerProfile.address || "Not provided"}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Outstanding Balance</p>
                          <p className="text-foreground">
                            ₦{customerProfile.outstanding_balance?.toLocaleString() || "0"}
                          </p>
                        </div>
                      </>
                    )}
                    {!isCustomer && (
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Role</p>
                        <p className="text-foreground">
                          {currentUser?.roleNames?.[0] || currentUser?.role || "User"}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </Card>

              {tenantSettings && (
                <Card className="p-6">
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <BuildingIcon size={16} className="text-muted-foreground" />
                      <p className="text-xs text-muted-foreground uppercase tracking-wider">
                        Business Profile
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">
                        Business Name
                      </p>
                      <p className="text-foreground">
                        {tenantSettings.tenant_name || tenantSettings.salon_name || "Not set"}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">
                        Subdomain
                      </p>
                      <p className="text-foreground">
                        {tenantSettings.subdomain || "Not set"}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">
                        Subscription
                      </p>
                      <p className="text-foreground capitalize">
                        {(tenantSettings as any).subscription_tier || "starter"}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Status</p>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 capitalize">
                        {(tenantSettings as any).status || "active"}
                      </span>
                    </div>
                  </div>
                </Card>
              )}

              <Card className="p-6">
                <div className="space-y-4">
                  <h3 className="font-semibold text-foreground">Preferences</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-foreground">Email Notifications</p>
                      <input
                        type="checkbox"
                        defaultChecked
                        className="w-4 h-4 cursor-pointer"
                        onChange={(e) => {
                          if (isCustomer && customerProfile) {
                            handleUpdateCustomerProfile({
                              notification_preferences: {
                                ...customerProfile.notification_preferences,
                                email: e.target.checked,
                              },
                            });
                          }
                        }}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-foreground">SMS Reminders</p>
                      <input
                        type="checkbox"
                        defaultChecked
                        className="w-4 h-4 cursor-pointer"
                        onChange={(e) => {
                          if (isCustomer && customerProfile) {
                            handleUpdateCustomerProfile({
                              notification_preferences: {
                                ...customerProfile.notification_preferences,
                                sms: e.target.checked,
                              },
                            });
                          }
                        }}
                      />
                    </div>
                  </div>
                </div>
              </Card>
            </>
          )}
        </div>
      )}
    </div>
  );
}

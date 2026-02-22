import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAppointments } from "@/hooks/useAppointments";
import { useAuthStore } from "@/stores/auth";
import { CalendarIcon, UserIcon, SettingsIcon } from "@/components/icons";

export default function MyAccountPage() {
  const user = useAuthStore((state) => state.user);
  const { data: appointments = [], isLoading } = useAppointments();
  const [activeTab, setActiveTab] = useState<"bookings" | "profile">(
    "bookings",
  );

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

  return (
    <div className="w-full space-y-6 px-0 sm:px-0">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <h2 className="text-2xl font-bold text-foreground">My Account</h2>
        <p className="text-sm text-muted-foreground">
          Manage your bookings and profile
        </p>
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

            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">
                Loading bookings...
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
                            {appointment.start_time
                              ? new Date(
                                  appointment.start_time,
                                ).toLocaleString()
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
                          {appointment.start_time
                            ? new Date(
                                appointment.start_time,
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
          <Card className="p-6">
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
                  <UserIcon size={32} className="text-primary" />
                </div>
                <div>
                  <p className="text-lg font-semibold text-foreground">
                    {user?.firstName} {user?.lastName}
                  </p>
                  <p className="text-sm text-muted-foreground">{user?.email}</p>
                </div>
              </div>

              <div className="border-t border-border pt-4 space-y-4">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Email</p>
                  <p className="text-foreground">{user?.email}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Phone</p>
                  <p className="text-foreground">
                    {user?.phone || "Not provided"}
                  </p>
                </div>
              </div>

              <div className="border-t border-border pt-4">
                <Button
                  variant="outline"
                  className="w-full cursor-pointer gap-2"
                >
                  <SettingsIcon size={16} />
                  Edit Profile
                </Button>
              </div>
            </div>
          </Card>

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
                  />
                </div>
                <div className="flex items-center justify-between">
                  <p className="text-sm text-foreground">SMS Reminders</p>
                  <input
                    type="checkbox"
                    defaultChecked
                    className="w-4 h-4 cursor-pointer"
                  />
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}

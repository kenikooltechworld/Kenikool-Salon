import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAppointments } from "@/hooks/useAppointments";
import { useStaff } from "@/hooks/useStaff";

export default function ManagerPage() {
  const { data: appointments = [], isLoading: appointmentsLoading } =
    useAppointments();
  const { data: staffList = [], isLoading: staffLoading } = useStaff();
  const [dateFilter, setDateFilter] = useState<string>("today");

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

  const activeStaff = staffList.filter(
    (s: any) => s.status === "active",
  ).length;
  const totalAppointments = appointments.length;
  const completedAppointments = appointments.filter(
    (a: any) => a.status === "completed",
  ).length;

  return (
    <div className="w-full space-y-6 px-0 sm:px-0">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <h2 className="text-2xl font-bold text-foreground">
          Manager Dashboard
        </h2>
        <p className="text-sm text-muted-foreground">
          Manage operations and monitor team performance
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-6">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Active Staff</p>
            <p className="text-3xl font-bold text-foreground">{activeStaff}</p>
            <p className="text-xs text-muted-foreground">
              {staffList.length} total staff members
            </p>
          </div>
        </Card>

        <Card className="p-6">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Total Appointments</p>
            <p className="text-3xl font-bold text-foreground">
              {totalAppointments}
            </p>
            <p className="text-xs text-muted-foreground">
              {completedAppointments} completed
            </p>
          </div>
        </Card>

        <Card className="p-6">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Completion Rate</p>
            <p className="text-3xl font-bold text-foreground">
              {totalAppointments > 0
                ? Math.round((completedAppointments / totalAppointments) * 100)
                : 0}
              %
            </p>
            <p className="text-xs text-muted-foreground">
              Based on all appointments
            </p>
          </div>
        </Card>
      </div>

      {/* Appointments Section */}
      <div className="space-y-4">
        <div className="flex flex-col gap-2">
          <h3 className="text-lg font-semibold text-foreground">
            Recent Appointments
          </h3>
          <p className="text-sm text-muted-foreground">
            Overview of upcoming and recent appointments
          </p>
        </div>

        {appointmentsLoading ? (
          <div className="text-center py-8 text-muted-foreground">
            Loading appointments...
          </div>
        ) : appointments.length > 0 ? (
          <div className="bg-card border border-border rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-muted border-b border-border">
                  <tr>
                    <th className="px-4 lg:px-6 py-3 text-left text-sm font-semibold text-foreground">
                      Customer
                    </th>
                    <th className="hidden lg:table-cell px-4 lg:px-6 py-3 text-left text-sm font-semibold text-foreground">
                      Staff
                    </th>
                    <th className="hidden lg:table-cell px-4 lg:px-6 py-3 text-left text-sm font-semibold text-foreground">
                      Service
                    </th>
                    <th className="px-4 lg:px-6 py-3 text-left text-sm font-semibold text-foreground">
                      Date & Time
                    </th>
                    <th className="px-4 lg:px-6 py-3 text-left text-sm font-semibold text-foreground">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {appointments.slice(0, 10).map((appointment: any) => (
                    <tr
                      key={appointment.id}
                      className="hover:bg-muted/50 transition"
                    >
                      <td className="px-4 lg:px-6 py-4 text-sm text-foreground">
                        <p className="font-medium">
                          {appointment.customer_name || "N/A"}
                        </p>
                      </td>
                      <td className="hidden lg:table-cell px-4 lg:px-6 py-4 text-sm text-muted-foreground">
                        {appointment.staff_name || "N/A"}
                      </td>
                      <td className="hidden lg:table-cell px-4 lg:px-6 py-4 text-sm text-muted-foreground">
                        {appointment.service_name || "N/A"}
                      </td>
                      <td className="px-4 lg:px-6 py-4 text-sm text-muted-foreground">
                        {appointment.start_time
                          ? new Date(appointment.start_time).toLocaleString()
                          : "N/A"}
                      </td>
                      <td className="px-4 lg:px-6 py-4 text-sm">
                        <Badge
                          variant={getStatusBadgeVariant(appointment.status)}
                        >
                          {getStatusLabel(appointment.status)}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            No appointments found
          </div>
        )}
      </div>

      {/* Staff Section */}
      <div className="space-y-4">
        <div className="flex flex-col gap-2">
          <h3 className="text-lg font-semibold text-foreground">
            Team Members
          </h3>
          <p className="text-sm text-muted-foreground">
            Your assigned staff members
          </p>
        </div>

        {staffLoading ? (
          <div className="text-center py-8 text-muted-foreground">
            Loading staff...
          </div>
        ) : staffList.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {staffList.map((staff: any) => (
              <Card key={staff.id} className="p-4">
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-semibold text-foreground">
                        {staff.firstName} {staff.lastName}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {staff.email}
                      </p>
                    </div>
                    <Badge
                      variant={
                        staff.status === "active" ? "default" : "secondary"
                      }
                    >
                      {getStatusLabel(staff.status)}
                    </Badge>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    <p>{staff.phone || "N/A"}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            No staff members found
          </div>
        )}
      </div>
    </div>
  );
}

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMyAppointments } from "@/hooks/useMyAppointments";
import { StaffAppointmentsList } from "@/components/staff/StaffAppointmentsList";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/components/ui/toast";
import type { StaffAppointment } from "@/hooks/useMyAppointments";

type ViewMode = "list" | "calendar";
type StatusFilter =
  | "all"
  | "scheduled"
  | "confirmed"
  | "in_progress"
  | "completed"
  | "cancelled";

export default function StaffAppointments() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [viewMode, setViewMode] = useState<ViewMode>("list");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");

  const {
    data: appointments = [],
    isLoading,
    error,
    refetch,
  } = useMyAppointments({
    status: statusFilter === "all" ? undefined : statusFilter,
  });

  const handleViewDetails = (appointment: StaffAppointment) => {
    navigate(`/staff/appointments/${appointment.id}`, {
      state: { appointment },
    });
  };

  const handleRefresh = () => {
    refetch();
    showToast({
      title: "Refreshed",
      description: "Appointments list updated",
    });
  };

  // Sort appointments by date ascending
  const sortedAppointments = [...appointments].sort(
    (a, b) => new Date(a.startTime).getTime() - new Date(b.startTime).getTime(),
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            My Appointments
          </h1>
          <p className="text-muted-foreground mt-2">
            Manage your appointments and schedule
          </p>
        </div>
        <Button onClick={handleRefresh} variant="outline" size="sm">
          Refresh
        </Button>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">View:</span>
          <div className="flex gap-2">
            <Button
              variant={viewMode === "list" ? "primary" : "outline"}
              size="sm"
              onClick={() => setViewMode("list")}
            >
              List
            </Button>
            <Button
              variant={viewMode === "calendar" ? "primary" : "outline"}
              size="sm"
              onClick={() => setViewMode("calendar")}
              disabled
            >
              Calendar (Coming Soon)
            </Button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Status:</span>
          <Select
            value={statusFilter}
            onValueChange={(value) => setStatusFilter(value as StatusFilter)}
          >
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="scheduled">Scheduled</SelectItem>
              <SelectItem value="confirmed">Confirmed</SelectItem>
              <SelectItem value="in_progress">In Progress</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="cancelled">Cancelled</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Appointments List */}
      <StaffAppointmentsList
        appointments={sortedAppointments}
        isLoading={isLoading}
        error={error?.message}
        onViewDetails={handleViewDetails}
        onRetry={handleRefresh}
      />
    </div>
  );
}

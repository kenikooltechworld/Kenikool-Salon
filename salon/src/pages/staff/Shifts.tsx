import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMyShifts } from "@/hooks/useMyShifts";
import { StaffShiftsList } from "@/components/staff/StaffShiftsList";
import { BookingCalendar } from "@/components/bookings/BookingCalendar";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import type { Shift } from "@/hooks/useShifts";

type ViewMode = "list" | "calendar";

export default function StaffShifts() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [viewMode, setViewMode] = useState<ViewMode>("list");

  const { data: shifts = [], isLoading, error, refetch } = useMyShifts();

  const handleViewDetails = (shift: Shift) => {
    navigate(`/staff/shifts/${shift.id}`, {
      state: { shift },
    });
  };

  const handleRefresh = () => {
    refetch();
    showToast({
      title: "Refreshed",
      description: "Shifts list updated",
    });
  };

  // Sort shifts by date ascending
  const sortedShifts = [...shifts].sort(
    (a, b) =>
      new Date(a.start_time).getTime() - new Date(b.start_time).getTime(),
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">My Shifts</h1>
          <p className="text-muted-foreground mt-2">
            View your assigned shifts and work schedule
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
      </div>

      {/* Shifts List */}
      {viewMode === "list" && (
        <StaffShiftsList
          shifts={sortedShifts}
          isLoading={isLoading}
          error={error?.message}
          onViewDetails={handleViewDetails}
          onRetry={handleRefresh}
        />
      )}

      {/* Calendar View - Coming Soon */}
      {viewMode === "calendar" && (
        <div className="rounded-lg border border-border bg-muted/50 p-8 text-center">
          <p className="text-muted-foreground">Calendar view coming soon</p>
        </div>
      )}
    </div>
  );
}

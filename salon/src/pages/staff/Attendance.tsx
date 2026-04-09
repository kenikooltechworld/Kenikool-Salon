import { StaffAttendanceTracker } from "@/components/staff/StaffAttendanceTracker";
import { AttendanceHistory } from "@/components/staff/AttendanceHistory";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { useQueryClient } from "@tanstack/react-query";

export default function StaffAttendance() {
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ["my-attendance"] });
    queryClient.invalidateQueries({ queryKey: ["current-attendance-status"] });
    queryClient.invalidateQueries({ queryKey: ["attendance-summary"] });
    showToast({
      title: "Refreshed",
      description: "Attendance data updated",
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Attendance</h1>
          <p className="text-muted-foreground mt-2">
            Track your work hours and attendance history
          </p>
        </div>
        <Button onClick={handleRefresh} variant="outline" size="sm">
          Refresh
        </Button>
      </div>

      {/* Clock In/Out Tracker */}
      <StaffAttendanceTracker />

      {/* Attendance History */}
      <AttendanceHistory />
    </div>
  );
}

import { StaffAttendanceTracker } from "@/components/staff/StaffAttendanceTracker";
import { AttendanceHistory } from "@/components/staff/AttendanceHistory";
import { useQueryClient } from "@tanstack/react-query";
import { usePageRefresh } from "@/contexts/PageRefreshContext";
import { useEffect } from "react";

export default function StaffAttendance() {
  const queryClient = useQueryClient();
  const { setRefreshHandler } = usePageRefresh();

  useEffect(() => {
    setRefreshHandler(() => {
      queryClient.invalidateQueries({ queryKey: ["my-attendance"] });
      queryClient.invalidateQueries({ queryKey: ["current-attendance-status"] });
      queryClient.invalidateQueries({ queryKey: ["attendance-summary"] });
    });
  }, [queryClient, setRefreshHandler]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Attendance</h1>
          <p className="text-muted-foreground mt-2">
            Track your work hours and attendance history
          </p>
        </div>
      </div>

      {/* Clock In/Out Tracker */}
      <StaffAttendanceTracker />

      {/* Attendance History */}
      <AttendanceHistory />
    </div>
  );
}

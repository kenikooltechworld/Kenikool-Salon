import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { apiClient } from "@/lib/api/client";

interface AttendanceRecord {
  id: string;
  date: string;
  clock_in_time?: string;
  clock_out_time?: string;
  hours_worked: number;
  status: string;
}

interface AttendanceTabProps {
  stylistId: string;
  attendanceRecords: AttendanceRecord[];
  isLoading: boolean;
  attendanceStatus: "not_clocked_in" | "clocked_in" | "clocked_out";
  currentHoursWorked: number;
  currentTime: Date;
  attendancePage: number;
  onPageChange: (page: number) => void;
  onStatusChange: (
    status: "not_clocked_in" | "clocked_in" | "clocked_out",
  ) => void;
  onHoursChange: (hours: number) => void;
  onRefetch: () => void;
}

export function AttendanceTab({
  stylistId,
  attendanceRecords,
  isLoading,
  attendanceStatus,
  currentHoursWorked,
  currentTime,
  attendancePage,
  onPageChange,
  onStatusChange,
  onHoursChange,
  onRefetch,
}: AttendanceTabProps) {
  const handleClockIn = async () => {
    try {
      const response = await apiClient.post(
        `/api/stylists/${stylistId}/clock-in`,
      );
      onStatusChange("clocked_in");
      onHoursChange(0);

      // Save to localStorage immediately for persistence
      const sessionData = {
        status: "clocked_in",
        attendanceId: response.data?.id,
        stylistId: stylistId,
        date: new Date().toISOString(),
        hoursWorked: 0,
      };
      localStorage.setItem(
        `attendance_session_${stylistId}`,
        JSON.stringify(sessionData),
      );

      // Refetch attendance data
      onRefetch();
    } catch (err) {
      console.error("Clock in error:", err);
    }
  };

  const handleClockOut = async () => {
    try {
      // Get current attendance record to find the attendance_id
      const currentMonth = new Date().toISOString().slice(0, 7);
      const attendanceResponse = await apiClient.get(
        `/api/stylists/${stylistId}/attendance?month=${currentMonth}`,
      );
      const records = attendanceResponse.data || [];

      // Find today's record that hasn't been clocked out yet
      const today = new Date().toDateString();
      const todayRecord = records.find((r: any) => {
        const recordDate = new Date(r.date).toDateString();
        return recordDate === today && !r.clock_out_time;
      });

      if (!todayRecord) {
        console.error("No active clock-in record found for today");
        return;
      }

      // Clock out with the attendance_id
      const clockOutResponse = await apiClient.post(
        `/api/stylists/${stylistId}/clock-out`,
        {
          attendance_id: todayRecord.id,
        },
      );

      onStatusChange("clocked_out");

      // Update localStorage with clocked out status
      const sessionData = {
        status: "clocked_out",
        attendanceId: todayRecord.id,
        stylistId: stylistId,
        date: new Date().toISOString(),
        hoursWorked: clockOutResponse.data?.hours_worked || 0,
      };
      localStorage.setItem(
        `attendance_session_${stylistId}`,
        JSON.stringify(sessionData),
      );

      // Refetch attendance data
      onRefetch();
    } catch (err) {
      console.error("Clock out error:", err);
    }
  };

  // Sort records by date ascending (oldest first) - NO SORT, backend already sorts descending
  const sortedRecords = attendanceRecords;

  const totalPages = Math.ceil(sortedRecords.length / 10);
  const startIndex = (attendancePage - 1) * 10;
  const endIndex = Math.min(attendancePage * 10, sortedRecords.length);
  const paginatedRecords = sortedRecords.slice(startIndex, endIndex);

  return (
    <Card className="p-4 sm:p-6">
      <h2 className="text-lg sm:text-xl font-bold text-foreground mb-6">
        Attendance & Time Clock
      </h2>

      {/* Clock In/Out Section */}
      <div className="mb-8 p-4 border border-border rounded-lg bg-muted/30">
        <div className="text-center mb-6">
          <p className="text-sm text-muted-foreground mb-2">Current Time</p>
          <p className="text-4xl font-bold font-mono">
            {currentTime.toLocaleTimeString()}
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            {currentTime.toLocaleDateString("en-US", {
              weekday: "long",
              month: "long",
              day: "numeric",
            })}
          </p>

          {/* Status and Hours Worked */}
          <div className="mt-6 grid grid-cols-2 gap-4">
            <div className="p-3 bg-background rounded-lg border border-border">
              <p className="text-xs text-muted-foreground mb-1">Status</p>
              <p className="text-lg font-bold capitalize">
                {attendanceStatus === "clocked_in" ? (
                  <span className="text-green-600">Clocked In</span>
                ) : attendanceStatus === "clocked_out" ? (
                  <span className="text-red-600">Clocked Out</span>
                ) : (
                  <span className="text-gray-600">Not Clocked In</span>
                )}
              </p>
            </div>
            <div className="p-3 bg-background rounded-lg border border-border">
              <p className="text-xs text-muted-foreground mb-1">Hours Worked</p>
              <p className="text-lg font-bold">
                {(() => {
                  const totalSeconds = Math.floor(currentHoursWorked * 3600);
                  const hours = Math.floor(totalSeconds / 3600);
                  const minutes = Math.floor((totalSeconds % 3600) / 60);
                  const seconds = totalSeconds % 60;
                  return `${hours}h ${minutes}m ${seconds}s`;
                })()}
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <Button
            className="w-full cursor-pointer"
            disabled={attendanceStatus === "clocked_in"}
            onClick={handleClockIn}
          >
            Clock In
          </Button>
          <Button
            variant="outline"
            className="w-full cursor-pointer"
            disabled={attendanceStatus !== "clocked_in"}
            onClick={handleClockOut}
          >
            Clock Out
          </Button>
        </div>
      </div>

      {/* Attendance Records */}
      <div>
        <h3 className="font-semibold mb-4">Attendance Records</h3>
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : attendanceRecords.length > 0 ? (
          <>
            <div className="overflow-x-auto mb-4">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-2 px-3">Date</th>
                    <th className="text-left py-2 px-3">Clock In</th>
                    <th className="text-left py-2 px-3">Clock Out</th>
                    <th className="text-left py-2 px-3">Hours Worked</th>
                    <th className="text-left py-2 px-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedRecords.map((record: AttendanceRecord) => (
                    <tr
                      key={record.id}
                      className="border-b border-border hover:bg-muted/50"
                    >
                      <td className="py-2 px-3">
                        {record.date
                          ? new Date(record.date).toLocaleDateString()
                          : "-"}
                      </td>
                      <td className="py-2 px-3">
                        {record.clock_in_time
                          ? new Date(record.clock_in_time).toLocaleTimeString()
                          : "-"}
                      </td>
                      <td className="py-2 px-3">
                        {record.clock_out_time
                          ? new Date(record.clock_out_time).toLocaleTimeString()
                          : "-"}
                      </td>
                      <td className="py-2 px-3">
                        {(() => {
                          const totalSeconds = Math.floor(
                            (record.hours_worked || 0) * 3600,
                          );
                          const hours = Math.floor(totalSeconds / 3600);
                          const minutes = Math.floor(
                            (totalSeconds % 3600) / 60,
                          );
                          const seconds = totalSeconds % 60;
                          return `${hours}h ${minutes}m ${seconds}s`;
                        })()}
                      </td>
                      <td className="py-2 px-3">
                        <Badge variant="secondary">{record.status}</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pt-4 border-t border-border">
              <p className="text-xs sm:text-sm text-muted-foreground">
                Showing {startIndex + 1} to {endIndex} of {sortedRecords.length}{" "}
                records
              </p>
              <div className="flex flex-wrap items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={attendancePage === 1}
                  onClick={() => onPageChange(Math.max(1, attendancePage - 1))}
                >
                  Previous
                </Button>
                <div className="flex items-center gap-1">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                    (page) => (
                      <Button
                        key={page}
                        variant={
                          attendancePage === page ? "primary" : "outline"
                        }
                        size="sm"
                        className="w-8 h-8 p-0 text-xs"
                        onClick={() => onPageChange(page)}
                      >
                        {page}
                      </Button>
                    ),
                  )}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={attendancePage === totalPages}
                  onClick={() =>
                    onPageChange(Math.min(totalPages, attendancePage + 1))
                  }
                >
                  Next
                </Button>
              </div>
            </div>
          </>
        ) : (
          <p className="text-muted-foreground">
            No attendance records for this month
          </p>
        )}
      </div>
    </Card>
  );
}

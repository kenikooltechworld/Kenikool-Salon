import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  ClockIcon,
  CheckCircleIcon,
  AlertCircleIcon,
  LogInIcon,
  LogOutIcon,
} from "@/components/icons";
import {
  useCurrentAttendanceStatus,
  useClockIn,
  useClockOut,
  useAttendanceSummary,
} from "@/hooks/useAttendance";
import { formatTime } from "@/lib/utils/format";

export function StaffAttendanceTracker() {
  const [notes, setNotes] = useState("");
  const [showNotesInput, setShowNotesInput] = useState(false);

  const { data: currentStatus, isLoading: statusLoading } =
    useCurrentAttendanceStatus();
  const { data: summary } = useAttendanceSummary("month");
  const clockIn = useClockIn();
  const clockOut = useClockOut();

  const isCheckedIn = currentStatus?.status === "checked_in";
  const isLoading = statusLoading || clockIn.isPending || clockOut.isPending;

  const handleClockIn = async () => {
    try {
      await clockIn.mutateAsync(notes ? { notes } : undefined);
      setNotes("");
      setShowNotesInput(false);
    } catch (error) {
      console.error("Clock in failed:", error);
    }
  };

  const handleClockOut = async () => {
    try {
      await clockOut.mutateAsync(notes ? { notes } : undefined);
      setNotes("");
      setShowNotesInput(false);
    } catch (error) {
      console.error("Clock out failed:", error);
    }
  };

  const calculateCurrentHours = () => {
    if (!currentStatus?.check_in_time) return 0;
    const checkInTime = new Date(currentStatus.check_in_time);
    const now = new Date();
    const diffMs = now.getTime() - checkInTime.getTime();
    return Math.floor((diffMs / (1000 * 60 * 60)) * 10) / 10; // Round to 1 decimal
  };

  return (
    <div className="space-y-6">
      {/* Clock In/Out Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ClockIcon size={20} />
            Clock In/Out
          </CardTitle>
          <CardDescription>
            {isCheckedIn
              ? "You are currently clocked in"
              : "Clock in to start tracking your work hours"}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Current Status */}
          {isCheckedIn && currentStatus && (
            <Alert variant="success">
              <AlertDescription className="space-y-2">
                <div className="flex items-center gap-2 font-medium">
                  <CheckCircleIcon size={16} />
                  Currently Clocked In
                </div>
                <div className="text-sm space-y-1">
                  <p>
                    <span className="text-muted-foreground">
                      Check-in time:
                    </span>{" "}
                    <span className="font-medium">
                      {formatTime(currentStatus.check_in_time)}
                    </span>
                  </p>
                  <p>
                    <span className="text-muted-foreground">
                      Hours worked today:
                    </span>{" "}
                    <span className="font-medium">
                      {calculateCurrentHours()}h
                    </span>
                  </p>
                  {currentStatus.is_late && (
                    <p className="flex items-center gap-1">
                      <AlertCircleIcon size={14} />
                      Late arrival
                    </p>
                  )}
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* Error Messages */}
          {clockIn.isError && (
            <Alert variant="error">
              <AlertDescription>
                Failed to clock in. Please try again.
              </AlertDescription>
            </Alert>
          )}

          {clockOut.isError && (
            <Alert variant="error">
              <AlertDescription>
                Failed to clock out. Please try again.
              </AlertDescription>
            </Alert>
          )}

          {/* Success Messages */}
          {clockIn.isSuccess && (
            <Alert variant="success">
              <AlertDescription>Successfully clocked in!</AlertDescription>
            </Alert>
          )}

          {clockOut.isSuccess && (
            <Alert variant="success">
              <AlertDescription>Successfully clocked out!</AlertDescription>
            </Alert>
          )}

          {/* Notes Input (Optional) */}
          {showNotesInput && (
            <div className="space-y-2">
              <Label htmlFor="notes">Notes (Optional)</Label>
              <Textarea
                id="notes"
                placeholder="Add any notes about your shift..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
              />
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2">
            {!isCheckedIn ? (
              <>
                <Button
                  onClick={handleClockIn}
                  disabled={isLoading}
                  className="flex-1"
                  size="lg"
                >
                  <LogInIcon size={18} className="mr-2" />
                  {clockIn.isPending ? "Clocking In..." : "Clock In"}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setShowNotesInput(!showNotesInput)}
                  disabled={isLoading}
                >
                  {showNotesInput ? "Hide Notes" : "Add Notes"}
                </Button>
              </>
            ) : (
              <>
                <Button
                  onClick={handleClockOut}
                  disabled={isLoading}
                  variant="destructive"
                  className="flex-1"
                  size="lg"
                >
                  <LogOutIcon size={18} className="mr-2" />
                  {clockOut.isPending ? "Clocking Out..." : "Clock Out"}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setShowNotesInput(!showNotesInput)}
                  disabled={isLoading}
                >
                  {showNotesInput ? "Hide Notes" : "Add Notes"}
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Monthly Summary Card */}
      {summary && (
        <Card>
          <CardHeader>
            <CardTitle>This Month's Summary</CardTitle>
            <CardDescription>
              Your attendance statistics for the current month
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Total Hours</p>
                <p className="text-2xl font-bold">
                  {summary.total_hours.toFixed(1)}h
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Total Days</p>
                <p className="text-2xl font-bold">{summary.total_days}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Late Arrivals</p>
                <p className="text-2xl font-bold text-warning">
                  {summary.late_arrivals}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Avg Hours/Day</p>
                <p className="text-2xl font-bold">
                  {summary.average_hours_per_day.toFixed(1)}h
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

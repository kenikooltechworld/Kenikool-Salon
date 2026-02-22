import { Modal } from "@/components/ui/modal";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  CalendarIcon,
  ClockIcon,
  AlertTriangleIcon,
  CheckIcon,
} from "@/components/icons";
import {
  useStylistAttendance,
  useClockIn,
  useClockOut,
} from "@/lib/api/hooks/useStylists";
import { Stylist } from "@/lib/api/types";
import { useState } from "react";

interface AttendanceModalProps {
  isOpen: boolean;
  onClose: () => void;
  stylist: Stylist;
}

export function AttendanceModal({
  isOpen,
  onClose,
  stylist,
}: AttendanceModalProps) {
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7)); // YYYY-MM

  const {
    data: attendance,
    isLoading,
    error,
    refetch,
  } = useStylistAttendance(stylist.id, month);

  const clockInMutation = useClockIn();
  const clockOutMutation = useClockOut();

  const todayAttendance = attendance?.find(
    (a: any) =>
      new Date(a.date).toDateString() === new Date().toDateString() &&
      !a.clock_out_time
  );

  const handleClockIn = async () => {
    try {
      await clockInMutation.mutateAsync(stylist.id);
      refetch();
    } catch (error) {
      console.error("Error clocking in:", error);
    }
  };

  const handleClockOut = async () => {
    if (!todayAttendance) return;
    try {
      await clockOutMutation.mutateAsync({
        stylistId: stylist.id,
        attendanceId: todayAttendance.id,
      });
      refetch();
    } catch (error) {
      console.error("Error clocking out:", error);
    }
  };

  const calculateHours = (clockIn: string, clockOut: string | null) => {
    if (!clockOut) return "In Progress";
    const start = new Date(clockIn);
    const end = new Date(clockOut);
    const hours = (end.getTime() - start.getTime()) / (1000 * 60 * 60);
    return `${hours.toFixed(1)} hrs`;
  };

  const totalHours =
    attendance?.reduce((sum: number, a: any) => {
      if (a.clock_out_time) {
        const start = new Date(a.clock_in_time);
        const end = new Date(a.clock_out_time);
        return sum + (end.getTime() - start.getTime()) / (1000 * 60 * 60);
      }
      return sum;
    }, 0) || 0;

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <div className="p-6">
        <h2 className="text-2xl font-bold text-foreground mb-6">
          Attendance - {stylist.name}
        </h2>

        {/* Clock In/Out Controls */}
        <Card className="p-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">
                Current Status
              </p>
              <div className="flex items-center gap-2">
                {todayAttendance ? (
                  <>
                    <Badge variant="success">Clocked In</Badge>
                    <span className="text-sm text-muted-foreground">
                      Since{" "}
                      {new Date(
                        todayAttendance.clock_in_time
                      ).toLocaleTimeString()}
                    </span>
                  </>
                ) : (
                  <Badge variant="secondary">Not Clocked In</Badge>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {!todayAttendance ? (
                <Button
                  variant="primary"
                  onClick={handleClockIn}
                  disabled={clockInMutation.isPending}
                >
                  {clockInMutation.isPending ? (
                    <>
                      <Spinner size="sm" />
                      Clocking In...
                    </>
                  ) : (
                    <>
                      <ClockIcon size={16} />
                      Clock In
                    </>
                  )}
                </Button>
              ) : (
                <Button
                  variant="outline"
                  onClick={handleClockOut}
                  disabled={clockOutMutation.isPending}
                >
                  {clockOutMutation.isPending ? (
                    <>
                      <Spinner size="sm" />
                      Clocking Out...
                    </>
                  ) : (
                    <>
                      <CheckIcon size={16} />
                      Clock Out
                    </>
                  )}
                </Button>
              )}
            </div>
          </div>
        </Card>

        {/* Month Selector */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-foreground mb-1">
            Select Month
          </label>
          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="px-3 py-2 border border-[var(--border)] rounded-lg bg-background text-foreground"
          />
        </div>

        {/* Summary */}
        <Card className="p-4 mb-6 bg-[var(--info)]/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CalendarIcon size={20} className="text-[var(--info)]" />
              <div>
                <p className="text-sm text-muted-foreground">Total Hours</p>
                <p className="text-xl font-bold text-foreground">
                  {totalHours.toFixed(1)} hrs
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Days Worked</p>
              <p className="text-xl font-bold text-foreground">
                {attendance?.filter((a: any) => a.clock_out_time).length || 0}
              </p>
            </div>
          </div>
        </Card>

        {/* Attendance Log */}
        {isLoading ? (
          <div className="flex justify-center py-12">
            <Spinner />
          </div>
        ) : error ? (
          <Alert variant="error">
            <AlertTriangleIcon size={20} />
            <div>
              <h3 className="font-semibold">Error loading attendance</h3>
              <p className="text-sm">{error.message}</p>
            </div>
          </Alert>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {attendance && attendance.length > 0 ? (
              attendance.map((record: any) => (
                <Card key={record.id} className="p-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <CalendarIcon
                        size={16}
                        className="text-muted-foreground"
                      />
                      <div>
                        <p className="font-medium text-foreground">
                          {new Date(record.date).toLocaleDateString("en-US", {
                            weekday: "short",
                            month: "short",
                            day: "numeric",
                          })}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(record.clock_in_time).toLocaleTimeString()}{" "}
                          -{" "}
                          {record.clock_out_time
                            ? new Date(
                                record.clock_out_time
                              ).toLocaleTimeString()
                            : "In Progress"}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge
                        variant={record.clock_out_time ? "success" : "warning"}
                        size="sm"
                      >
                        {calculateHours(
                          record.clock_in_time,
                          record.clock_out_time
                        )}
                      </Badge>
                    </div>
                  </div>
                </Card>
              ))
            ) : (
              <div className="text-center py-12">
                <ClockIcon
                  size={48}
                  className="mx-auto text-muted-foreground mb-3"
                />
                <p className="text-muted-foreground">
                  No attendance records for this month
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </Modal>
  );
}

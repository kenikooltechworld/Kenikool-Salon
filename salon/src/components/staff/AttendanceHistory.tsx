import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ClockIcon,
  CalendarIcon,
  AlertCircleIcon,
  CheckCircleIcon,
  FilterIcon,
} from "@/components/icons";
import { useMyAttendance, type AttendanceRecord } from "@/hooks/useAttendance";
import { formatDate, formatTime } from "@/lib/utils/format";

export function AttendanceHistory() {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const filters = {
    ...(startDate && { startDate }),
    ...(endDate && { endDate }),
    ...(statusFilter !== "all" && { status: statusFilter }),
  };

  const {
    data: attendanceRecords,
    isLoading,
    isError,
  } = useMyAttendance(filters);

  const handleClearFilters = () => {
    setStartDate("");
    setEndDate("");
    setStatusFilter("all");
  };

  const calculateHoursWorked = (record: AttendanceRecord) => {
    if (!record.check_out_time) return null;

    if (record.hours_worked !== undefined) {
      return record.hours_worked;
    }

    const checkIn = new Date(record.check_in_time);
    const checkOut = new Date(record.check_out_time);
    const diffMs = checkOut.getTime() - checkIn.getTime();
    return Math.floor((diffMs / (1000 * 60 * 60)) * 10) / 10; // Round to 1 decimal
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CalendarIcon size={20} />
          Attendance History
        </CardTitle>
        <CardDescription>View your past clock in/out records</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Filters */}
        <div className="bg-muted/50 rounded-lg p-4 space-y-4">
          <div className="flex items-center gap-2 text-sm font-medium">
            <FilterIcon size={16} />
            Filters
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="start-date">Start Date</Label>
              <Input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="end-date">End Date</Label>
              <Input
                id="end-date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="status-filter">Status</Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger id="status-filter">
                  <SelectValue placeholder="All statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="checked_in">Checked In</SelectItem>
                  <SelectItem value="checked_out">Checked Out</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          {(startDate || endDate || statusFilter !== "all") && (
            <Button variant="outline" size="sm" onClick={handleClearFilters}>
              Clear Filters
            </Button>
          )}
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        )}

        {/* Error State */}
        {isError && (
          <div className="text-center py-8 text-muted-foreground">
            <AlertCircleIcon
              size={48}
              className="mx-auto mb-2 text-destructive"
            />
            <p>Failed to load attendance history</p>
            <Button variant="outline" size="sm" className="mt-2">
              Retry
            </Button>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !isError && attendanceRecords?.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <ClockIcon size={48} className="mx-auto mb-2 opacity-50" />
            <p>No attendance records found</p>
            <p className="text-sm">Your attendance history will appear here</p>
          </div>
        )}

        {/* Attendance Records List */}
        {!isLoading &&
          !isError &&
          attendanceRecords &&
          attendanceRecords.length > 0 && (
            <div className="space-y-3">
              {attendanceRecords.map((record) => {
                const hoursWorked = calculateHoursWorked(record);

                return (
                  <div
                    key={record.id}
                    className="border rounded-lg p-4 hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 space-y-2">
                        {/* Date */}
                        <div className="flex items-center gap-2">
                          <CalendarIcon
                            size={16}
                            className="text-muted-foreground"
                          />
                          <span className="font-medium">
                            {formatDate(record.check_in_time)}
                          </span>
                          {record.status === "checked_in" ? (
                            <Badge variant="default" className="bg-success">
                              <CheckCircleIcon size={12} className="mr-1" />
                              Checked In
                            </Badge>
                          ) : (
                            <Badge variant="secondary">Checked Out</Badge>
                          )}
                        </div>

                        {/* Times */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm">
                          <div>
                            <span className="text-muted-foreground">
                              Check In:{" "}
                            </span>
                            <span className="font-medium">
                              {formatTime(record.check_in_time)}
                            </span>
                          </div>
                          {record.check_out_time && (
                            <>
                              <div>
                                <span className="text-muted-foreground">
                                  Check Out:{" "}
                                </span>
                                <span className="font-medium">
                                  {formatTime(record.check_out_time)}
                                </span>
                              </div>
                              <div>
                                <span className="text-muted-foreground">
                                  Hours:{" "}
                                </span>
                                <span className="font-medium">
                                  {hoursWorked !== null
                                    ? `${hoursWorked}h`
                                    : "N/A"}
                                </span>
                              </div>
                            </>
                          )}
                        </div>

                        {/* Flags */}
                        {(record.is_late || record.is_early_departure) && (
                          <div className="flex gap-2 text-sm">
                            {record.is_late && (
                              <Badge
                                variant="outline"
                                className="text-warning border-warning"
                              >
                                <AlertCircleIcon size={12} className="mr-1" />
                                Late Arrival
                              </Badge>
                            )}
                            {record.is_early_departure && (
                              <Badge
                                variant="outline"
                                className="text-warning border-warning"
                              >
                                <AlertCircleIcon size={12} className="mr-1" />
                                Early Departure
                              </Badge>
                            )}
                          </div>
                        )}

                        {/* Notes */}
                        {record.notes && (
                          <div className="text-sm text-muted-foreground bg-muted/50 rounded p-2">
                            <span className="font-medium">Notes: </span>
                            {record.notes}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
      </CardContent>
    </Card>
  );
}

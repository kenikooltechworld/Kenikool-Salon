"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";

interface AttendanceReportProps {
  staffId?: string;
  startDate?: Date;
  endDate?: Date;
}

export function AttendanceReport({
  staffId,
  startDate,
  endDate,
}: AttendanceReportProps) {
  const { data: response, isLoading } = useQuery({
    queryKey: ["attendance-report", staffId, startDate, endDate],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (startDate) params.append("start_date", startDate.toISOString());
      if (endDate) params.append("end_date", endDate.toISOString());
      if (staffId) params.append("staff_id", staffId);

      const res = await fetch(`/api/staff/attendance/reports?${params}`);
      if (!res.ok) throw new Error("Failed to fetch report");
      return res.json();
    },
  });

  const report = response?.data;

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
    );
  }

  if (!report) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground text-center">
            No attendance data available
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Days</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{report.total_days || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {report.period_start && report.period_end
                ? `${new Date(report.period_start).toLocaleDateString()} - ${new Date(report.period_end).toLocaleDateString()}`
                : ""}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Present</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {report.present_days || 0}
            </div>
            <Badge className="mt-2 bg-green-100 text-green-800">
              {report.punctuality_rate?.toFixed(1) || 0}%
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Late</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {report.late_days || 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">days</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Absent</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {report.absent_days || 0}
            </div>
            <Badge className="mt-2 bg-red-100 text-red-800">
              {report.absence_rate?.toFixed(1) || 0}%
            </Badge>
          </CardContent>
        </Card>
      </div>

      {/* Hours Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Hours Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Total Hours</p>
              <p className="text-2xl font-bold">
                {report.total_hours?.toFixed(2) || "0.00"}h
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Average per Day</p>
              <p className="text-2xl font-bold">
                {report.total_days > 0
                  ? (report.total_hours / report.total_days).toFixed(2)
                  : "0.00"}
                h
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Overtime Hours</p>
              <p className="text-2xl font-bold text-orange-600">
                {report.total_overtime?.toFixed(2) || "0.00"}h
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* By Staff Breakdown */}
      {report.by_staff && Object.keys(report.by_staff).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Attendance by Staff</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(report.by_staff).map(
                ([id, staff]: [string, any]) => (
                  <div key={id} className="border rounded p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{staff.staff_name}</h4>
                      <Badge variant="secondary">{staff.total_days} days</Badge>
                    </div>
                    <div className="grid grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Present</p>
                        <p className="font-semibold text-green-600">
                          {staff.present_days}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Late</p>
                        <p className="font-semibold text-yellow-600">
                          {staff.late_days}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Absent</p>
                        <p className="font-semibold text-red-600">
                          {staff.absent_days}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Total Hours</p>
                        <p className="font-semibold">
                          {staff.total_hours?.toFixed(2) || "0.00"}h
                        </p>
                      </div>
                    </div>
                  </div>
                ),
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

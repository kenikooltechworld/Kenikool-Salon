"use client";

import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface AttendanceRecord {
  _id: string;
  staff_name: string;
  date: string;
  clock_in: string;
  clock_out?: string;
  total_hours: number;
  regular_hours: number;
  overtime_hours: number;
  status: "present" | "late" | "absent";
  late_minutes: number;
}

interface AttendanceListProps {
  staffId?: string;
  title?: string;
}

const STATUS_COLORS = {
  present: "bg-green-100 text-green-800",
  late: "bg-yellow-100 text-yellow-800",
  absent: "bg-red-100 text-red-800",
};

export function AttendanceList({
  staffId,
  title = "Attendance Records",
}: AttendanceListProps) {
  const { data: response, isLoading } = useQuery({
    queryKey: ["attendance-records", staffId],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (staffId) params.append("staff_id", staffId);

      const res = await fetch(`/api/staff/attendance?${params}`);
      if (!res.ok) throw new Error("Failed to fetch records");
      return res.json();
    },
  });

  const records: AttendanceRecord[] = response?.data || [];

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!records || records.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No attendance records found
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Clock In</TableHead>
                <TableHead>Clock Out</TableHead>
                <TableHead className="text-right">Total Hours</TableHead>
                <TableHead className="text-right">Regular</TableHead>
                <TableHead className="text-right">Overtime</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {records.map((record) => (
                <TableRow key={record._id}>
                  <TableCell>
                    {format(new Date(record.date), "MMM dd, yyyy")}
                  </TableCell>
                  <TableCell>
                    {format(new Date(record.clock_in), "HH:mm:ss")}
                  </TableCell>
                  <TableCell>
                    {record.clock_out
                      ? format(new Date(record.clock_out), "HH:mm:ss")
                      : "-"}
                  </TableCell>
                  <TableCell className="text-right font-semibold">
                    {record.total_hours.toFixed(2)}h
                  </TableCell>
                  <TableCell className="text-right">
                    {record.regular_hours.toFixed(2)}h
                  </TableCell>
                  <TableCell className="text-right">
                    {record.overtime_hours.toFixed(2)}h
                  </TableCell>
                  <TableCell>
                    <Badge
                      className={
                        STATUS_COLORS[
                          record.status as keyof typeof STATUS_COLORS
                        ]
                      }
                    >
                      {record.status === "late"
                        ? `Late (${record.late_minutes}m)`
                        : record.status.charAt(0).toUpperCase() +
                          record.status.slice(1)}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

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

interface TimeOffRequest {
  _id: string;
  staff_name: string;
  request_type: string;
  start_date: string;
  end_date: string;
  total_days: number;
  reason: string;
  status: "pending" | "approved" | "denied";
  reviewed_at?: string;
}

interface TimeOffListProps {
  staffId?: string;
  status?: "pending" | "approved" | "denied";
  title?: string;
}

const STATUS_COLORS = {
  pending: "bg-yellow-100 text-yellow-800",
  approved: "bg-green-100 text-green-800",
  denied: "bg-red-100 text-red-800",
};

const TYPE_LABELS = {
  vacation: "Vacation",
  sick: "Sick Leave",
  personal: "Personal",
  unpaid: "Unpaid Leave",
};

export function TimeOffList({
  staffId,
  status,
  title = "Time-Off Requests",
}: TimeOffListProps) {
  const { data: requests, isLoading } = useQuery({
    queryKey: ["time-off-requests", staffId, status],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (staffId) params.append("staff_id", staffId);
      if (status) params.append("status", status);

      const res = await fetch(`/api/staff/time-off?${params}`);
      if (!res.ok) throw new Error("Failed to fetch requests");
      return res.json();
    },
  });

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

  if (!requests || requests.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No time-off requests found
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
                <TableHead>Staff</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Start Date</TableHead>
                <TableHead>End Date</TableHead>
                <TableHead>Days</TableHead>
                <TableHead>Reason</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {requests.map((request: TimeOffRequest) => (
                <TableRow key={request._id}>
                  <TableCell className="font-medium">
                    {request.staff_name}
                  </TableCell>
                  <TableCell>
                    {TYPE_LABELS[
                      request.request_type as keyof typeof TYPE_LABELS
                    ] || request.request_type}
                  </TableCell>
                  <TableCell>
                    {format(new Date(request.start_date), "MMM dd, yyyy")}
                  </TableCell>
                  <TableCell>
                    {format(new Date(request.end_date), "MMM dd, yyyy")}
                  </TableCell>
                  <TableCell>{request.total_days}</TableCell>
                  <TableCell className="max-w-xs truncate">
                    {request.reason}
                  </TableCell>
                  <TableCell>
                    <Badge
                      className={
                        STATUS_COLORS[
                          request.status as keyof typeof STATUS_COLORS
                        ]
                      }
                    >
                      {request.status.charAt(0).toUpperCase() +
                        request.status.slice(1)}
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

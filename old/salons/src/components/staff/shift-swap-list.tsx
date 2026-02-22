"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import { toast } from "sonner";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface ShiftSwap {
  _id: string;
  requesting_staff_name: string;
  target_staff_name: string;
  shift_date: string;
  shift_start: string;
  shift_end: string;
  reason: string;
  status: "pending" | "accepted" | "declined" | "approved" | "cancelled";
  created_at: string;
}

interface ShiftSwapListProps {
  staffId?: string;
  status?: string;
  title?: string;
  showActions?: boolean;
  onSwapUpdated?: () => void;
}

const STATUS_COLORS = {
  pending: "bg-yellow-100 text-yellow-800",
  accepted: "bg-blue-100 text-blue-800",
  declined: "bg-red-100 text-red-800",
  approved: "bg-green-100 text-green-800",
  cancelled: "bg-gray-100 text-gray-800",
};

export function ShiftSwapList({
  staffId,
  status,
  title = "Shift Swap Requests",
  showActions = false,
  onSwapUpdated,
}: ShiftSwapListProps) {
  const {
    data: swaps,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["shift-swaps", staffId, status],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (staffId) params.append("staff_id", staffId);
      if (status) params.append("status", status);

      const res = await fetch(`/api/staff/shift-swaps?${params}`);
      if (!res.ok) throw new Error("Failed to fetch swaps");
      return res.json();
    },
  });

  const respondMutation = useMutation({
    mutationFn: async ({
      swapId,
      swapStatus,
    }: {
      swapId: string;
      swapStatus: string;
    }) => {
      const res = await fetch(`/api/staff/shift-swaps/${swapId}/respond`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: swapStatus }),
      });

      if (!res.ok) throw new Error("Failed to respond to swap");
      return res.json();
    },
    onSuccess: () => {
      toast.success("Response submitted");
      refetch();
      onSwapUpdated?.();
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to respond");
    },
  });

  const approveMutation = useMutation({
    mutationFn: async (swapId: string) => {
      const res = await fetch(`/api/staff/shift-swaps/${swapId}/approve`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
      });

      if (!res.ok) throw new Error("Failed to approve swap");
      return res.json();
    },
    onSuccess: () => {
      toast.success("Shift swap approved");
      refetch();
      onSwapUpdated?.();
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to approve");
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

  if (!swaps || swaps.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No shift swap requests found
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
                <TableHead>From</TableHead>
                <TableHead>To</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Time</TableHead>
                <TableHead>Reason</TableHead>
                <TableHead>Status</TableHead>
                {showActions && <TableHead>Actions</TableHead>}
              </TableRow>
            </TableHeader>
            <TableBody>
              {swaps.map((swap: ShiftSwap) => (
                <TableRow key={swap._id}>
                  <TableCell className="font-medium">
                    {swap.requesting_staff_name}
                  </TableCell>
                  <TableCell>{swap.target_staff_name}</TableCell>
                  <TableCell>
                    {format(new Date(swap.shift_date), "MMM dd")}
                  </TableCell>
                  <TableCell>
                    {swap.shift_start} - {swap.shift_end}
                  </TableCell>
                  <TableCell className="max-w-xs truncate">
                    {swap.reason}
                  </TableCell>
                  <TableCell>
                    <Badge
                      className={
                        STATUS_COLORS[swap.status as keyof typeof STATUS_COLORS]
                      }
                    >
                      {swap.status.charAt(0).toUpperCase() +
                        swap.status.slice(1)}
                    </Badge>
                  </TableCell>
                  {showActions && (
                    <TableCell>
                      {swap.status === "pending" && (
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              respondMutation.mutate({
                                swapId: swap._id,
                                swapStatus: "accepted",
                              })
                            }
                            disabled={respondMutation.isPending}
                          >
                            Accept
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              respondMutation.mutate({
                                swapId: swap._id,
                                swapStatus: "declined",
                              })
                            }
                            disabled={respondMutation.isPending}
                          >
                            Decline
                          </Button>
                        </div>
                      )}
                      {swap.status === "accepted" && (
                        <Button
                          size="sm"
                          onClick={() => approveMutation.mutate(swap._id)}
                          disabled={approveMutation.isPending}
                        >
                          Approve
                        </Button>
                      )}
                    </TableCell>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface ShiftSwapModalProps {
  staffId: string;
  staffName: string;
  isOpen: boolean;
  onClose: () => void;
  onSwapCreated?: () => void;
}

interface StaffMember {
  _id: string;
  name: string;
}

export function ShiftSwapModal({
  staffId,
  staffName,
  isOpen,
  onClose,
  onSwapCreated,
}: ShiftSwapModalProps) {
  const [targetStaffId, setTargetStaffId] = useState("");
  const [shiftDate, setShiftDate] = useState("");
  const [shiftStart, setShiftStart] = useState("09:00");
  const [shiftEnd, setShiftEnd] = useState("17:00");
  const [reason, setReason] = useState("");

  // Fetch available staff members
  const { data: staffList, isLoading: staffLoading } = useQuery({
    queryKey: ["staff-list"],
    queryFn: async () => {
      const res = await fetch(`/api/stylists?is_active=true`);
      if (!res.ok) throw new Error("Failed to fetch staff");
      return res.json();
    },
  });

  const createSwapMutation = useMutation({
    mutationFn: async () => {
      if (!targetStaffId || !shiftDate || !reason.trim()) {
        throw new Error("Please fill in all required fields");
      }

      const res = await fetch(`/api/staff/shift-swaps`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target_staff_id: targetStaffId,
          shift_date: new Date(shiftDate).toISOString(),
          shift_start: shiftStart,
          shift_end: shiftEnd,
          reason,
        }),
      });

      if (!res.ok) throw new Error("Failed to create shift swap request");
      return res.json();
    },
    onSuccess: () => {
      toast.success("Shift swap request created");
      onSwapCreated?.();
      onClose();
      setTargetStaffId("");
      setShiftDate("");
      setShiftStart("09:00");
      setShiftEnd("17:00");
      setReason("");
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to create request");
    },
  });

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Request Shift Swap - {staffName}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Target Staff */}
          <div>
            <Label htmlFor="target-staff">Swap With</Label>
            {staffLoading ? (
              <Skeleton className="h-10 w-full mt-1" />
            ) : (
              <Select value={targetStaffId} onValueChange={setTargetStaffId}>
                <SelectTrigger id="target-staff" className="mt-1">
                  <SelectValue placeholder="Select staff member" />
                </SelectTrigger>
                <SelectContent>
                  {staffList?.map((staff: StaffMember) => (
                    <SelectItem key={staff._id} value={staff._id}>
                      {staff.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>

          {/* Shift Date */}
          <div>
            <Label htmlFor="shift-date">Shift Date</Label>
            <Input
              id="shift-date"
              type="date"
              value={shiftDate}
              onChange={(e) => setShiftDate(e.target.value)}
              className="mt-1"
            />
          </div>

          {/* Shift Times */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label htmlFor="shift-start">Start Time</Label>
              <Input
                id="shift-start"
                type="time"
                value={shiftStart}
                onChange={(e) => setShiftStart(e.target.value)}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="shift-end">End Time</Label>
              <Input
                id="shift-end"
                type="time"
                value={shiftEnd}
                onChange={(e) => setShiftEnd(e.target.value)}
                className="mt-1"
              />
            </div>
          </div>

          {/* Reason */}
          <div>
            <Label htmlFor="reason">Reason for Swap</Label>
            <Textarea
              id="reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Explain why you need to swap this shift..."
              className="mt-1 resize-none"
              rows={3}
            />
          </div>

          {/* Info */}
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="pt-4 text-sm text-blue-900">
              <p>
                ℹ️ The target staff member will be notified and can accept or
                decline. A manager must then approve the swap.
              </p>
            </CardContent>
          </Card>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={() => createSwapMutation.mutate()}
            disabled={
              !targetStaffId ||
              !shiftDate ||
              !reason.trim() ||
              createSwapMutation.isPending
            }
          >
            {createSwapMutation.isPending ? "Creating..." : "Request Swap"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

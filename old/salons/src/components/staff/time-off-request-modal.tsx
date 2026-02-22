"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
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
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface TimeOffRequestModalProps {
  staffId: string;
  staffName: string;
  isOpen: boolean;
  onClose: () => void;
  onRequestCreated?: () => void;
}

const TIME_OFF_TYPES = [
  { value: "vacation", label: "Vacation" },
  { value: "sick", label: "Sick Leave" },
  { value: "personal", label: "Personal" },
  { value: "unpaid", label: "Unpaid Leave" },
];

export function TimeOffRequestModal({
  staffId,
  staffName,
  isOpen,
  onClose,
  onRequestCreated,
}: TimeOffRequestModalProps) {
  const [requestType, setRequestType] = useState("vacation");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [reason, setReason] = useState("");
  const [notes, setNotes] = useState("");

  const createRequestMutation = useMutation({
    mutationFn: async () => {
      if (!startDate || !endDate || !reason.trim()) {
        throw new Error("Please fill in all required fields");
      }

      if (new Date(startDate) > new Date(endDate)) {
        throw new Error("Start date must be before end date");
      }

      const res = await fetch(`/api/staff/time-off`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          request_type: requestType,
          start_date: new Date(startDate).toISOString(),
          end_date: new Date(endDate).toISOString(),
          reason,
          notes: notes || undefined,
        }),
      });

      if (!res.ok) throw new Error("Failed to create time-off request");
      return res.json();
    },
    onSuccess: () => {
      toast.success("Time-off request submitted");
      onRequestCreated?.();
      onClose();
      setRequestType("vacation");
      setStartDate("");
      setEndDate("");
      setReason("");
      setNotes("");
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to create request");
    },
  });

  const calculateDays = () => {
    if (!startDate || !endDate) return 0;
    const start = new Date(startDate);
    const end = new Date(endDate);
    return (
      Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Request Time Off - {staffName}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Type */}
          <div>
            <Label htmlFor="type">Type of Leave</Label>
            <Select value={requestType} onValueChange={setRequestType}>
              <SelectTrigger id="type" className="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TIME_OFF_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Dates */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label htmlFor="start-date">Start Date</Label>
              <Input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="end-date">End Date</Label>
              <Input
                id="end-date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="mt-1"
              />
            </div>
          </div>

          {/* Days Summary */}
          {startDate && endDate && (
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="pt-4">
                <p className="text-sm text-blue-900">
                  <strong>Total Days:</strong> {calculateDays()} day(s)
                </p>
              </CardContent>
            </Card>
          )}

          {/* Reason */}
          <div>
            <Label htmlFor="reason">Reason</Label>
            <Input
              id="reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g., Family vacation, Medical appointment"
              className="mt-1"
            />
          </div>

          {/* Notes */}
          <div>
            <Label htmlFor="notes">Additional Notes (Optional)</Label>
            <Textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Any additional information..."
              className="mt-1 resize-none"
              rows={3}
            />
          </div>

          {/* Info */}
          <div className="bg-amber-50 border border-amber-200 rounded p-3 text-sm text-amber-800">
            ℹ️ Your request will be reviewed by management. You'll be notified
            once it's approved or denied.
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={() => createRequestMutation.mutate()}
            disabled={
              !startDate ||
              !endDate ||
              !reason.trim() ||
              createRequestMutation.isPending
            }
          >
            {createRequestMutation.isPending
              ? "Submitting..."
              : "Submit Request"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

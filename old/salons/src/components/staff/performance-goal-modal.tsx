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
import { Card, CardContent } from "@/components/ui/card";

interface PerformanceGoalModalProps {
  staffId: string;
  staffName: string;
  isOpen: boolean;
  onClose: () => void;
  onGoalCreated?: () => void;
}

const GOAL_TYPES = [
  { value: "revenue", label: "Revenue Target" },
  { value: "bookings", label: "Booking Target" },
  { value: "rating", label: "Rating Target" },
  { value: "rebooking_rate", label: "Rebooking Rate Target" },
];

export function PerformanceGoalModal({
  staffId,
  staffName,
  isOpen,
  onClose,
  onGoalCreated,
}: PerformanceGoalModalProps) {
  const [goalType, setGoalType] = useState("revenue");
  const [targetValue, setTargetValue] = useState("");
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [notes, setNotes] = useState("");

  const createGoalMutation = useMutation({
    mutationFn: async () => {
      if (!targetValue || !periodStart || !periodEnd) {
        throw new Error("Please fill in all required fields");
      }

      if (new Date(periodStart) >= new Date(periodEnd)) {
        throw new Error("Start date must be before end date");
      }

      const res = await fetch(`/api/staff/performance/goals`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          staff_id: staffId,
          goal_type: goalType,
          target_value: parseFloat(targetValue),
          period_start: new Date(periodStart).toISOString(),
          period_end: new Date(periodEnd).toISOString(),
          notes: notes || undefined,
        }),
      });

      if (!res.ok) throw new Error("Failed to create goal");
      return res.json();
    },
    onSuccess: () => {
      toast.success("Performance goal created");
      onGoalCreated?.();
      onClose();
      setGoalType("revenue");
      setTargetValue("");
      setPeriodStart("");
      setPeriodEnd("");
      setNotes("");
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to create goal");
    },
  });

  const getPlaceholder = () => {
    switch (goalType) {
      case "revenue":
        return "e.g., 5000";
      case "bookings":
        return "e.g., 50";
      case "rating":
        return "e.g., 4.5";
      case "rebooking_rate":
        return "e.g., 75";
      default:
        return "";
    }
  };

  const getUnit = () => {
    switch (goalType) {
      case "revenue":
        return "$";
      case "bookings":
        return "bookings";
      case "rating":
        return "/5";
      case "rebooking_rate":
        return "%";
      default:
        return "";
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Set Performance Goal - {staffName}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Goal Type */}
          <div>
            <Label htmlFor="goal-type">Goal Type</Label>
            <Select value={goalType} onValueChange={setGoalType}>
              <SelectTrigger id="goal-type" className="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {GOAL_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Target Value */}
          <div>
            <Label htmlFor="target-value">Target Value</Label>
            <div className="flex gap-2 mt-1">
              <Input
                id="target-value"
                type="number"
                value={targetValue}
                onChange={(e) => setTargetValue(e.target.value)}
                placeholder={getPlaceholder()}
                step="0.01"
              />
              <div className="flex items-center px-3 bg-muted rounded border">
                <span className="text-sm font-medium">{getUnit()}</span>
              </div>
            </div>
          </div>

          {/* Period */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label htmlFor="period-start">Start Date</Label>
              <Input
                id="period-start"
                type="date"
                value={periodStart}
                onChange={(e) => setPeriodStart(e.target.value)}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="period-end">End Date</Label>
              <Input
                id="period-end"
                type="date"
                value={periodEnd}
                onChange={(e) => setPeriodEnd(e.target.value)}
                className="mt-1"
              />
            </div>
          </div>

          {/* Notes */}
          <div>
            <Label htmlFor="notes">Notes (Optional)</Label>
            <Textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add any additional notes about this goal..."
              className="mt-1 resize-none"
              rows={3}
            />
          </div>

          {/* Info */}
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="pt-4 text-sm text-blue-900">
              <p>
                ℹ️ Performance goals help track staff progress. Goals are
                monitored throughout the period and marked as achieved when
                targets are met.
              </p>
            </CardContent>
          </Card>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={() => createGoalMutation.mutate()}
            disabled={
              !targetValue ||
              !periodStart ||
              !periodEnd ||
              createGoalMutation.isPending
            }
          >
            {createGoalMutation.isPending ? "Creating..." : "Create Goal"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

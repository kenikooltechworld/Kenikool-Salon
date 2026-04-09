import { useParams, useNavigate } from "react-router-dom";
import { useMyShift } from "@/hooks/useMyShifts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDate, formatTime } from "@/lib/utils/format";
import { ArrowLeftIcon } from "@/components/icons";
import type { Shift } from "@/hooks/useShifts";
import type { BadgeProps } from "@/components/ui/badge";

const statusVariants: Record<
  Shift["status"],
  NonNullable<BadgeProps["variant"]>
> = {
  scheduled: "default",
  in_progress: "accent",
  completed: "outline",
  cancelled: "destructive",
};

const statusLabels: Record<Shift["status"], string> = {
  scheduled: "Scheduled",
  in_progress: "In Progress",
  completed: "Completed",
  cancelled: "Cancelled",
};

export default function ShiftDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: shift, isLoading, error } = useMyShift(id || "");

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/staff/shifts")}
          className="mb-4"
        >
          <ArrowLeftIcon size={16} className="mr-2" />
          Back
        </Button>
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (error && !shift) {
    return (
      <div className="space-y-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/staff/shifts")}
          className="mb-4"
        >
          <ArrowLeftIcon size={16} className="mr-2" />
          Back
        </Button>
        <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-6">
          <p className="text-sm text-destructive font-medium">
            Failed to load shift
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            {error?.message || "An error occurred while loading the shift"}
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate("/staff/shifts")}
            className="mt-4"
          >
            Back to Shifts
          </Button>
        </div>
      </div>
    );
  }

  if (!shift) {
    return (
      <div className="space-y-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/staff/shifts")}
          className="mb-4"
        >
          <ArrowLeftIcon size={16} className="mr-2" />
          Back
        </Button>
        <div className="rounded-lg border border-border bg-muted/50 p-6 text-center">
          <p className="text-muted-foreground">Shift not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => navigate("/staff/shifts")}
        className="mb-4"
      >
        <ArrowLeftIcon size={16} className="mr-2" />
        Back to Shifts
      </Button>

      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-2xl">Shift Details</CardTitle>
              <p className="text-muted-foreground mt-2">ID: {shift.id}</p>
            </div>
            <Badge variant={statusVariants[shift.status]}>
              {statusLabels[shift.status]}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Date */}
          <div>
            <p className="text-sm text-muted-foreground font-medium">Date</p>
            <p className="text-lg font-semibold mt-1">
              {formatDate(new Date(shift.start_time))}
            </p>
          </div>

          {/* Start Time */}
          <div className="border-t border-border pt-4">
            <p className="text-sm text-muted-foreground font-medium">
              Start Time
            </p>
            <p className="text-lg font-semibold mt-1">
              {formatTime(new Date(shift.start_time))}
            </p>
          </div>

          {/* End Time */}
          <div className="border-t border-border pt-4">
            <p className="text-sm text-muted-foreground font-medium">
              End Time
            </p>
            <p className="text-lg font-semibold mt-1">
              {formatTime(new Date(shift.end_time))}
            </p>
          </div>

          {/* Labor Cost */}
          {shift.labor_cost !== null && shift.labor_cost !== undefined && (
            <div className="border-t border-border pt-4">
              <p className="text-sm text-muted-foreground font-medium">
                Labor Cost
              </p>
              <p className="text-lg font-semibold mt-1">
                ${shift.labor_cost.toFixed(2)}
              </p>
            </div>
          )}

          {/* Created At */}
          <div className="border-t border-border pt-4">
            <p className="text-xs text-muted-foreground">
              Created on {formatDate(new Date(shift.created_at))}
            </p>
          </div>

          {/* Actions */}
          <div className="border-t border-border pt-4 flex gap-2">
            <Button variant="outline" onClick={() => navigate("/staff/shifts")}>
              Back
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatDate, formatTime } from "@/lib/utils/format";
import type { Shift } from "@/hooks/useShifts";
import type { BadgeProps } from "@/components/ui/badge";

interface StaffShiftCardProps {
  shift: Shift;
  onViewDetails?: (shift: Shift) => void;
}

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

export function StaffShiftCard({ shift, onViewDetails }: StaffShiftCardProps) {
  const startDate = new Date(shift.start_time);
  const endDate = new Date(shift.end_time);

  return (
    <Card hover>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-base">{formatDate(startDate)}</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">Shift Schedule</p>
          </div>
          <Badge variant={statusVariants[shift.status]}>
            {statusLabels[shift.status]}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <p className="text-muted-foreground">Start Time</p>
            <p className="font-medium">{formatTime(startDate)}</p>
          </div>
          <div>
            <p className="text-muted-foreground">End Time</p>
            <p className="font-medium">{formatTime(endDate)}</p>
          </div>
        </div>

        {shift.labor_cost > 0 && (
          <div className="pt-2 border-t border-border">
            <p className="text-sm text-muted-foreground mb-1">Labor Cost</p>
            <p className="text-sm font-medium">
              ${shift.labor_cost.toFixed(2)}
            </p>
          </div>
        )}

        <div className="pt-2 border-t border-border flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onViewDetails?.(shift)}
            className="flex-1"
          >
            View Details
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

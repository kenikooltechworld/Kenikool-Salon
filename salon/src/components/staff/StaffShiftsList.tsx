import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { StaffShiftCard } from "./StaffShiftCard";
import type { Shift } from "@/hooks/useShifts";

interface StaffShiftsListProps {
  shifts: Shift[];
  isLoading?: boolean;
  error?: string;
  onViewDetails?: (shift: Shift) => void;
  onRetry?: () => void;
}

export function StaffShiftsList({
  shifts,
  isLoading = false,
  error,
  onViewDetails,
  onRetry,
}: StaffShiftsListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className="h-48 w-full" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-4">
        <p className="text-sm text-destructive font-medium">
          Failed to load shifts
        </p>
        <p className="text-sm text-muted-foreground mt-1">
          {error || "Network error. Please try again."}
        </p>
        {onRetry && (
          <Button
            variant="outline"
            size="sm"
            onClick={onRetry}
            className="mt-3"
          >
            Retry
          </Button>
        )}
      </div>
    );
  }

  if (shifts.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-muted/50 p-8 text-center">
        <p className="text-muted-foreground">No shifts found</p>
        <p className="text-sm text-muted-foreground mt-1">
          Your shifts will appear here
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {shifts.map((shift) => (
        <StaffShiftCard
          key={shift.id}
          shift={shift}
          onViewDetails={onViewDetails}
        />
      ))}
    </div>
  );
}

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { StaffTimeOffCard } from "./StaffTimeOffCard";
import type { TimeOffRequest } from "@/hooks/useTimeOffRequests";

interface StaffTimeOffListProps {
  requests: TimeOffRequest[];
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
}

export function StaffTimeOffList({
  requests,
  isLoading = false,
  error,
  onRetry,
}: StaffTimeOffListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className="h-40 w-full" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-4">
        <p className="text-sm text-destructive font-medium">
          Failed to load time off requests
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

  if (requests.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-muted/50 p-8 text-center">
        <p className="text-muted-foreground">No time off requests found</p>
        <p className="text-sm text-muted-foreground mt-1">
          Your time off requests will appear here
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {requests.map((request) => (
        <StaffTimeOffCard key={request.id} request={request} />
      ))}
    </div>
  );
}

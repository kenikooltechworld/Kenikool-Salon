import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { TimeOffRequest } from "@/hooks/useTimeOffRequests";
import { formatDate } from "@/lib/utils/format";

interface TimeOffCardProps {
  request: TimeOffRequest;
  staffName: string;
  onApprove?: (requestId: string) => void;
  onDeny?: (requestId: string) => void;
  canApprove?: boolean;
}

const statusColors: Record<string, string> = {
  pending: "bg-warning/10 text-warning",
  approved: "bg-success/10 text-success",
  denied: "bg-destructive/10 text-destructive",
};

export function TimeOffCard({
  request,
  staffName,
  onApprove,
  onDeny,
  canApprove = false,
}: TimeOffCardProps) {
  const startDate = new Date(request.start_date);
  const endDate = new Date(request.end_date);
  const daysDuration = Math.ceil(
    (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24),
  );

  return (
    <Card className="p-4">
      <div className="space-y-3">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold text-lg">{staffName}</h3>
            <p className="text-sm text-muted-foreground">
              {formatDate(startDate)} to {formatDate(endDate)} ({daysDuration}{" "}
              days)
            </p>
          </div>
          <Badge className={statusColors[request.status]}>
            {request.status}
          </Badge>
        </div>

        <div className="bg-muted p-3 rounded">
          <p className="text-sm font-medium text-foreground">Reason</p>
          <p className="text-sm text-muted-foreground">{request.reason}</p>
        </div>

        {canApprove && request.status === "pending" && (
          <div className="flex gap-2 border-t pt-3">
            {onApprove && (
              <Button
                variant="primary"
                size="sm"
                onClick={() => onApprove(request.id)}
                className="flex-1"
              >
                Approve
              </Button>
            )}
            {onDeny && (
              <Button
                variant="destructive"
                size="sm"
                onClick={() => onDeny(request.id)}
                className="flex-1"
              >
                Deny
              </Button>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils/format";
import type { TimeOffRequest } from "@/hooks/useTimeOffRequests";
import type { BadgeProps } from "@/components/ui/badge";

interface StaffTimeOffCardProps {
  request: TimeOffRequest;
}

const statusVariants: Record<
  TimeOffRequest["status"],
  NonNullable<BadgeProps["variant"]>
> = {
  pending: "default",
  approved: "outline",
  denied: "destructive",
};

const statusLabels: Record<TimeOffRequest["status"], string> = {
  pending: "Pending",
  approved: "Approved",
  denied: "Denied",
};

export function StaffTimeOffCard({ request }: StaffTimeOffCardProps) {
  const startDate = new Date(request.start_date);
  const endDate = new Date(request.end_date);
  const daysDuration = Math.ceil(
    (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24),
  );
  const createdDate = new Date(request.created_at);

  return (
    <Card hover>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-base">
              {formatDate(startDate)} to {formatDate(endDate)}
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              {daysDuration} day{daysDuration !== 1 ? "s" : ""}
            </p>
          </div>
          <Badge variant={statusVariants[request.status]}>
            {statusLabels[request.status]}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {request.reason && (
          <div>
            <p className="text-sm text-muted-foreground mb-1">Reason</p>
            <p className="text-sm text-foreground">{request.reason}</p>
          </div>
        )}

        {request.status === "denied" && (
          <div className="pt-2 border-t border-border">
            <p className="text-sm text-muted-foreground mb-1">Status</p>
            <p className="text-sm text-destructive">Request was denied</p>
          </div>
        )}

        <div className="pt-2 border-t border-border">
          <p className="text-xs text-muted-foreground">
            Submitted on {formatDate(createdDate)}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircleIcon, CheckIcon, XIcon } from "@/components/icons";
import type { PendingAction } from "@/hooks/owner";
import { formatDate } from "@/lib/utils/date";

interface PendingActionsProps {
  actions: PendingAction[];
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
  onMarkComplete?: (actionId: string) => void;
  onDismiss?: (actionId: string) => void;
  isMarkingComplete?: boolean;
  isDismissing?: boolean;
}

const getPriorityStyle = (priority: string): React.CSSProperties => {
  const styles: Record<string, React.CSSProperties> = {
    high: {
      backgroundColor: "var(--destructive-bg, #fee2e2)",
      color: "var(--destructive)",
    },
    medium: {
      backgroundColor: "var(--warning-bg, #fef3c7)",
      color: "var(--warning, #f59e0b)",
    },
    low: {
      backgroundColor: "var(--info-bg, #dbeafe)",
      color: "var(--info, #3b82f6)",
    },
  };
  return styles[priority] || {};
};

const typeIcons: Record<string, string> = {
  payment: "💳",
  staff: "👤",
  inventory: "📦",
  customer: "👥",
  system: "⚙️",
};

export function PendingActions({
  actions,
  isLoading = false,
  error,
  onRetry,
  onMarkComplete,
  onDismiss,
  isMarkingComplete = false,
  isDismissing = false,
}: PendingActionsProps) {
  // Ensure actions is always an array
  const safeActions = Array.isArray(actions) ? actions : [];

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircleIcon size={20} />
            Pending Actions
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-destructive/50 bg-destructive/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircleIcon size={20} />
            Pending Actions
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-destructive font-medium">
            Unable to load pending actions
          </p>
          <p className="text-sm text-muted-foreground">{error}</p>
          {onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              className="w-full"
            >
              Retry
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  if (safeActions.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircleIcon size={20} />
            Pending Actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No pending actions
          </p>
        </CardContent>
      </Card>
    );
  }

  const displayedActions = safeActions.slice(0, 10);
  const hasMore = safeActions.length > 10;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertCircleIcon size={20} />
          Pending Actions
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {displayedActions.map((action) => (
            <div
              key={action.id}
              className="flex items-start justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
            >
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-lg">
                    {typeIcons[action.type] || "📌"}
                  </span>
                  <p className="font-medium text-sm">{action.description}</p>
                  <Badge style={getPriorityStyle(action.priority)}>
                    {action.priority}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">
                  Due: {formatDate(action.dueDate)}
                </p>
              </div>
              <div className="flex gap-2 ml-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onMarkComplete?.(action.id)}
                  disabled={isMarkingComplete}
                  title="Mark as complete"
                >
                  <CheckIcon size={16} />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onDismiss?.(action.id)}
                  disabled={isDismissing}
                  title="Dismiss"
                >
                  <XIcon size={16} />
                </Button>
              </div>
            </div>
          ))}
          {hasMore && (
            <Button variant="outline" className="w-full" size="sm">
              View All ({safeActions.length} total)
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

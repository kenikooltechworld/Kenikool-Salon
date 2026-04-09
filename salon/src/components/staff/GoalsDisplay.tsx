import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Button } from "@/components/ui/button";
import {
  RefreshCwIcon,
  TrendingUpIcon,
  TargetIcon,
  CheckCircleIcon,
  AlertCircleIcon,
  CalendarIcon,
} from "@/components/icons";
import type { GoalProgress } from "@/hooks/useGoals";

interface GoalsDisplayProps {
  goals: GoalProgress[];
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
}

/**
 * Goals display component showing personal sales and commission targets
 * Displays goals with progress bars and status indicators
 *
 * Features:
 * - Display personal sales targets
 * - Display commission targets
 * - Display progress toward targets (percentage complete)
 * - Display days remaining for each goal
 * - Visual progress bars
 * - Status badges (active, completed, expired)
 * - On-track indicators
 *
 * Requirements: 17.1, 17.2, 17.3
 */
export function GoalsDisplay({
  goals,
  isLoading = false,
  error,
  onRetry,
}: GoalsDisplayProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TargetIcon size={20} />
            My Goals & Targets
          </CardTitle>
        </CardHeader>
        <CardContent className="flex justify-center py-8">
          <Spinner />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card
        variant="outlined"
        className="border-destructive/50 bg-destructive/5"
      >
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TargetIcon size={20} />
            My Goals & Targets
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-destructive font-medium">
            Unable to load goals
          </p>
          <p className="text-xs text-muted-foreground">{error}</p>
          {onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              className="w-full"
            >
              <RefreshCwIcon size={14} className="mr-1" />
              Retry
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  const getGoalTypeLabel = (type: string) => {
    switch (type) {
      case "sales":
        return "Sales Target";
      case "commission":
        return "Commission Target";
      case "appointments":
        return "Appointments Target";
      case "customer_satisfaction":
        return "Customer Satisfaction";
      default:
        return type;
    }
  };

  const getGoalTypeIcon = (type: string) => {
    switch (type) {
      case "sales":
      case "commission":
        return <TrendingUpIcon size={16} />;
      case "appointments":
        return <CalendarIcon size={16} />;
      case "customer_satisfaction":
        return <CheckCircleIcon size={16} />;
      default:
        return <TargetIcon size={16} />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return (
          <Badge variant="default" className="bg-green-500">
            Completed
          </Badge>
        );
      case "active":
        return <Badge variant="secondary">Active</Badge>;
      case "expired":
        return <Badge variant="outline">Expired</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const formatValue = (type: string, value: number) => {
    if (type === "sales" || type === "commission") {
      return `₦${value.toLocaleString("en-NG", { maximumFractionDigits: 2 })}`;
    }
    if (type === "customer_satisfaction") {
      return `${value.toFixed(1)}%`;
    }
    return value.toString();
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <TargetIcon size={20} />
            My Goals & Targets
          </CardTitle>
          {onRetry && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onRetry}
              title="Refresh goals"
              className="px-2"
            >
              <RefreshCwIcon size={14} />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {goals.length === 0 ? (
          <div className="text-center py-8">
            <TargetIcon
              size={48}
              className="mx-auto text-muted-foreground mb-3"
            />
            <p className="text-muted-foreground">
              No active goals. Your targets will appear here once set by
              management.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {goals.map((goalProgress) => {
              const {
                goal,
                progress_percentage,
                remaining_value,
                days_remaining,
                on_track,
              } = goalProgress;

              return (
                <div
                  key={goal.id}
                  className="p-4 border rounded-lg space-y-3 hover:bg-muted/50 transition-colors"
                >
                  {/* Goal Header */}
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      {getGoalTypeIcon(goal.goal_type)}
                      <div>
                        <h4 className="font-medium text-foreground">
                          {getGoalTypeLabel(goal.goal_type)}
                        </h4>
                        <p className="text-xs text-muted-foreground">
                          {new Date(goal.period_start).toLocaleDateString()} -{" "}
                          {new Date(goal.period_end).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {getStatusBadge(goal.status)}
                      {on_track ? (
                        <CheckCircleIcon
                          size={16}
                          className="text-green-500"
                          title="On track"
                        />
                      ) : (
                        <AlertCircleIcon
                          size={16}
                          className="text-yellow-500"
                          title="Behind target"
                        />
                      )}
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Progress</span>
                      <span className="font-medium">
                        {progress_percentage.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-3 overflow-hidden">
                      <div
                        className={`h-full transition-all ${
                          progress_percentage >= 100
                            ? "bg-green-500"
                            : on_track
                              ? "bg-primary"
                              : "bg-yellow-500"
                        }`}
                        style={{
                          width: `${Math.min(progress_percentage, 100)}%`,
                        }}
                      />
                    </div>
                  </div>

                  {/* Goal Details */}
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Target</p>
                      <p className="font-medium">
                        {formatValue(goal.goal_type, goal.target_value)}
                      </p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Current</p>
                      <p className="font-medium">
                        {formatValue(goal.goal_type, goal.current_value)}
                      </p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Remaining</p>
                      <p className="font-medium">
                        {formatValue(goal.goal_type, remaining_value)}
                      </p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-muted-foreground">Days Left</p>
                      <p className="font-medium">
                        {days_remaining > 0
                          ? `${days_remaining} days`
                          : "Expired"}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

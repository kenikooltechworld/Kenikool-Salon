import {
  useWaitingRoomQueue,
  useQueueStats,
  useCallNextCustomer,
  useMarkInService,
  useMarkCompleted,
  useMarkNoShow,
} from "@/hooks/useWaitingRoom";
import { Users, Clock, CheckCircle, AlertCircle } from "@/components/icons";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

export default function WaitingRoomQueue() {
  const { data: queue = [], isLoading: queueLoading } = useWaitingRoomQueue();
  const { data: stats } = useQueueStats();
  const callNext = useCallNextCustomer();
  const markInService = useMarkInService();
  const markCompleted = useMarkCompleted();
  const markNoShow = useMarkNoShow();

  const handleCallNext = () => {
    callNext.mutate();
  };

  const handleMarkInService = (queueEntryId: string) => {
    markInService.mutate(queueEntryId);
  };

  const handleMarkCompleted = (queueEntryId: string) => {
    markCompleted.mutate(queueEntryId);
  };

  const handleMarkNoShow = (queueEntryId: string) => {
    if (window.confirm("Mark this customer as no-show?")) {
      markNoShow.mutate({ queueEntryId });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "waiting":
        return "bg-warning text-warning-foreground";
      case "called":
        return "bg-info text-info-foreground";
      case "in_service":
        return "bg-success text-success-foreground";
      case "completed":
        return "bg-muted text-muted-foreground";
      case "no_show":
        return "bg-destructive text-destructive-foreground";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  if (queueLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className="h-20 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-background rounded-lg border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-5 h-5 text-info" />
              <span className="text-sm font-medium text-muted-foreground">
                Waiting
              </span>
            </div>
            <p className="text-2xl font-bold text-foreground">
              {stats.total_waiting}
            </p>
          </div>

          <div className="p-4 bg-background rounded-lg border border-border">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-5 h-5 text-warning" />
              <span className="text-sm font-medium text-muted-foreground">
                Avg Wait
              </span>
            </div>
            <p className="text-2xl font-bold text-foreground">
              {stats.average_wait_time_minutes}m
            </p>
          </div>

          <div className="p-4 bg-background rounded-lg border border-border">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-5 h-5 text-success" />
              <span className="text-sm font-medium text-muted-foreground">
                Completed
              </span>
            </div>
            <p className="text-2xl font-bold text-foreground">
              {stats.total_completed_today}
            </p>
          </div>

          <div className="p-4 bg-background rounded-lg border border-border">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-5 h-5 text-destructive" />
              <span className="text-sm font-medium text-muted-foreground">
                No-show
              </span>
            </div>
            <p className="text-2xl font-bold text-foreground">
              {stats.total_no_shows_today}
            </p>
          </div>
        </div>
      )}

      {/* Call Next Button */}
      <button
        onClick={handleCallNext}
        disabled={queue.length === 0 || callNext.isPending}
        className={cn(
          "w-full px-6 py-3 rounded-lg font-semibold transition-colors",
          queue.length === 0 || callNext.isPending
            ? "bg-muted text-muted-foreground cursor-not-allowed"
            : "bg-success text-success-foreground hover:bg-success/90",
        )}
      >
        {callNext.isPending ? "Calling..." : "Call Next Customer"}
      </button>

      {/* Queue List */}
      {queue.length === 0 ? (
        <div className="p-8 text-center text-muted-foreground">
          <p>No customers in queue</p>
        </div>
      ) : (
        <div className="space-y-3">
          {queue.map((entry) => (
            <div
              key={entry.id}
              className="p-4 bg-background rounded-lg border border-border"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg font-bold text-foreground">
                      #{entry.position}
                    </span>
                    <span
                      className={cn(
                        "px-2 py-1 rounded-full text-xs font-medium",
                        getStatusColor(entry.status),
                      )}
                    >
                      {entry.status.replace(/_/g, " ")}
                    </span>
                  </div>
                  <p className="font-semibold text-foreground">
                    {entry.customer_name}
                  </p>
                  {entry.service_name && (
                    <p className="text-sm text-muted-foreground">
                      {entry.service_name}
                    </p>
                  )}
                  {entry.estimated_wait_time_minutes && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Est. wait: {entry.estimated_wait_time_minutes}m
                    </p>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                {entry.status === "waiting" && (
                  <button
                    onClick={() => handleMarkInService(entry.id)}
                    disabled={markInService.isPending}
                    className="flex-1 px-3 py-2 bg-info text-info-foreground rounded hover:bg-info/90 disabled:bg-muted text-sm font-medium"
                  >
                    In Service
                  </button>
                )}
                {entry.status === "in_service" && (
                  <button
                    onClick={() => handleMarkCompleted(entry.id)}
                    disabled={markCompleted.isPending}
                    className="flex-1 px-3 py-2 bg-success text-success-foreground rounded hover:bg-success/90 disabled:bg-muted text-sm font-medium"
                  >
                    Completed
                  </button>
                )}
                {(entry.status === "waiting" || entry.status === "called") && (
                  <button
                    onClick={() => handleMarkNoShow(entry.id)}
                    disabled={markNoShow.isPending}
                    className="flex-1 px-3 py-2 bg-destructive text-destructive-foreground rounded hover:bg-destructive/90 disabled:bg-muted text-sm font-medium"
                  >
                    No-show
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

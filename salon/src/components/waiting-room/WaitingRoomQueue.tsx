import {
  useWaitingRoomQueue,
  useQueueStats,
  useCallNextCustomer,
  useMarkInService,
  useMarkCompleted,
  useMarkNoShow,
} from "@/hooks/useWaitingRoom";
import {
  UsersIcon,
  ClockIcon,
  CheckCircleIcon,
  AlertCircleIcon,
} from "@/components/icons";
import { cn } from "@/lib/utils/cn";

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
        return "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200";
      case "called":
        return "bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200";
      case "in_service":
        return "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200";
      case "completed":
        return "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200";
      case "no_show":
        return "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200";
      default:
        return "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200";
    }
  };

  if (queueLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="h-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"
          />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Waiting
              </span>
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {stats.total_waiting}
            </p>
          </div>

          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-5 h-5 text-orange-600" />
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Avg Wait
              </span>
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {stats.average_wait_time_minutes}m
            </p>
          </div>

          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Completed
              </span>
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {stats.total_completed_today}
            </p>
          </div>

          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                No-show
              </span>
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
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
            ? "bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed"
            : "bg-green-600 text-white hover:bg-green-700",
        )}
      >
        {callNext.isPending ? "Calling..." : "Call Next Customer"}
      </button>

      {/* Queue List */}
      {queue.length === 0 ? (
        <div className="p-8 text-center text-gray-500 dark:text-gray-400">
          <p>No customers in queue</p>
        </div>
      ) : (
        <div className="space-y-3">
          {queue.map((entry) => (
            <div
              key={entry.id}
              className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg font-bold text-gray-900 dark:text-white">
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
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {entry.customer_name}
                  </p>
                  {entry.service_name && (
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {entry.service_name}
                    </p>
                  )}
                  {entry.estimated_wait_time_minutes && (
                    <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
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
                    className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 text-sm font-medium"
                  >
                    In Service
                  </button>
                )}
                {entry.status === "in_service" && (
                  <button
                    onClick={() => handleMarkCompleted(entry.id)}
                    disabled={markCompleted.isPending}
                    className="flex-1 px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400 text-sm font-medium"
                  >
                    Completed
                  </button>
                )}
                {(entry.status === "waiting" || entry.status === "called") && (
                  <button
                    onClick={() => handleMarkNoShow(entry.id)}
                    disabled={markNoShow.isPending}
                    className="flex-1 px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:bg-gray-400 text-sm font-medium"
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

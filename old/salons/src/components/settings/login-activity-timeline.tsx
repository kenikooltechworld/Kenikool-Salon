import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import {
  CheckIcon,
  AlertTriangleIcon,
  MonitorIcon,
  MapPinIcon,
  ClockIcon,
  AlertIcon,
} from "@/components/icons";
import {
  useLoginActivity,
  useMarkLoginAsNotMe,
} from "@/lib/api/hooks/useSettings";
import { useQueryClient } from "@tanstack/react-query";

export function LoginActivityTimeline() {
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const queryClient = useQueryClient();

  const { data: activities = [], isLoading } = useLoginActivity();

  const markNotMeMutation = useMarkLoginAsNotMe({
    onSuccess: () => {
      setSuccessMessage("Login marked as suspicious. We'll review it.");
      queryClient.invalidateQueries({ queryKey: ["login-activity"] });
      setTimeout(() => setSuccessMessage(""), 3000);
    },
    onError: (error: any) => {
      setErrorMessage(error.response?.data?.detail || "Failed to mark login");
    },
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (seconds < 60) return "Just now";
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return `${Math.floor(seconds / 604800)}w ago`;
  };

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-foreground mb-6">
        Login Activity
      </h2>

      {successMessage && (
        <Alert variant="success" className="mb-4">
          <CheckIcon size={20} />
          <p>{successMessage}</p>
        </Alert>
      )}

      {errorMessage && (
        <Alert variant="error" className="mb-4">
          <AlertTriangleIcon size={20} />
          <p>{errorMessage}</p>
        </Alert>
      )}

      {isLoading ? (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      ) : activities.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-muted-foreground">No login activity</p>
        </div>
      ) : (
        <div className="space-y-3">
          {activities.map((activity, index) => (
            <div
              key={activity.id}
              className={`relative p-4 rounded-lg border ${
                activity.flagged
                  ? "bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800"
                  : activity.success
                    ? "bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800"
                    : "bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800"
              }`}
            >
              {/* Timeline Connector */}
              {index < activities.length - 1 && (
                <div className="absolute left-8 top-full w-0.5 h-3 bg-border" />
              )}

              <div className="flex items-start gap-4">
                {/* Status Icon */}
                <div className="flex-shrink-0 mt-1">
                  {activity.flagged ? (
                    <div className="w-6 h-6 rounded-full bg-red-600 flex items-center justify-center">
                      <AlertIcon size={16} className="text-white" />
                    </div>
                  ) : activity.success ? (
                    <div className="w-6 h-6 rounded-full bg-green-600 flex items-center justify-center">
                      <CheckIcon size={16} className="text-white" />
                    </div>
                  ) : (
                    <div className="w-6 h-6 rounded-full bg-yellow-600 flex items-center justify-center">
                      <AlertTriangleIcon size={16} className="text-white" />
                    </div>
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <div>
                      <p className="font-medium text-foreground">
                        {activity.success ? "Successful Login" : "Failed Login"}
                        {activity.flagged && " (Suspicious)"}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {getTimeAgo(activity.timestamp)}
                      </p>
                    </div>
                  </div>

                  <div className="space-y-1 text-xs text-muted-foreground mb-3">
                    <div className="flex items-center gap-2">
                      <MonitorIcon size={14} />
                      <span>{activity.device || "Unknown device"}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPinIcon size={14} />
                      <span>{activity.location || "Unknown location"}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span>IP: {activity.ip_address}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <ClockIcon size={14} />
                      <span>{formatDate(activity.timestamp)}</span>
                    </div>
                  </div>

                  {activity.flagged && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => markNotMeMutation.mutate(activity.id)}
                      disabled={markNotMeMutation.isPending}
                    >
                      {markNotMeMutation.isPending ? (
                        <>
                          <Spinner size="sm" />
                          Reporting...
                        </>
                      ) : (
                        "This Wasn't Me"
                      )}
                    </Button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {activities.length > 0 && (
        <p className="text-xs text-muted-foreground mt-4">
          Showing last 50 login attempts
        </p>
      )}
    </Card>
  );
}

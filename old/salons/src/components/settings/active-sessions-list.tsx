import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import {
  CheckIcon,
  AlertTriangleIcon,
  TrashIcon,
  MonitorIcon,
  MapPinIcon,
  ClockIcon,
} from "@/components/icons";
import {
  useSessions,
  useRevokeSession,
  useRevokeAllOtherSessions,
} from "@/lib/api/hooks/useSettings";
import { useQueryClient } from "@tanstack/react-query";

export function ActiveSessionsList() {
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const queryClient = useQueryClient();

  const { data: sessions = [], isLoading } = useSessions();

  const revokeSessionMutation = useRevokeSession({
    onSuccess: () => {
      setSuccessMessage("Session revoked successfully");
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      setTimeout(() => setSuccessMessage(""), 3000);
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to revoke session",
      );
    },
  });

  const revokeAllOtherMutation = useRevokeAllOtherSessions({
    onSuccess: (data) => {
      setSuccessMessage(
        `Logged out ${data.revoked_count} other session(s) successfully`,
      );
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      setTimeout(() => setSuccessMessage(""), 3000);
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to revoke sessions",
      );
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
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-foreground">
            Active Sessions
          </h2>
          <p className="text-sm text-muted-foreground">
            Manage devices where you're currently logged in
          </p>
        </div>
        {sessions.length > 1 && (
          <Button
            variant="outline"
            onClick={() => revokeAllOtherMutation.mutate()}
            disabled={revokeAllOtherMutation.isPending}
          >
            {revokeAllOtherMutation.isPending ? (
              <>
                <Spinner size="sm" />
                Logging out...
              </>
            ) : (
              "Logout All Other Devices"
            )}
          </Button>
        )}
      </div>

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
      ) : sessions.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-muted-foreground">No active sessions</p>
        </div>
      ) : (
        <div className="space-y-3">
          {sessions.map((session) => (
            <div
              key={session.id}
              className="flex items-start justify-between p-4 bg-muted rounded-lg border border-border"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <MonitorIcon size={18} className="text-muted-foreground" />
                  <div>
                    <p className="font-medium text-foreground">
                      {session.device}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {session.browser}
                    </p>
                  </div>
                  {session.is_current && (
                    <span className="ml-auto px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-100 text-xs rounded-full font-medium">
                      Current
                    </span>
                  )}
                </div>

                <div className="space-y-1 text-xs text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <MapPinIcon size={14} />
                    <span>{session.location || "Unknown location"}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>IP: {session.ip_address}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <ClockIcon size={14} />
                    <span>Last active: {getTimeAgo(session.last_active)}</span>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Created: {formatDate(session.created_at)}
                  </div>
                </div>
              </div>

              {!session.is_current && (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => revokeSessionMutation.mutate(session.id)}
                  disabled={revokeSessionMutation.isPending}
                  className="ml-4"
                >
                  {revokeSessionMutation.isPending ? (
                    <Spinner size="sm" />
                  ) : (
                    <TrashIcon size={18} className="text-destructive" />
                  )}
                </Button>
              )}
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

import { useOffline } from "@/lib/offline/use-offline";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  WifiIcon,
  WifiOffIcon,
  RefreshIcon,
  CheckIcon,
  AlertTriangleIcon,
} from "@/components/icons";
import { formatDistanceToNow } from "date-fns";
import { useState, useEffect } from "react";
import { syncEngine } from "@/lib/offline/sync-engine";

export function OfflineIndicator() {
  const { isOnline, syncProgress, pendingCount, manualSync, dbError } =
    useOffline();
  const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    const updateLastSync = async () => {
      try {
        const time = await syncEngine.getLastSyncTime();
        setLastSyncTime(time);
      } catch (error) {
        console.error("Failed to get last sync time:", error);
      }
    };

    updateLastSync();
    const interval = setInterval(updateLastSync, 10000);

    return () => clearInterval(interval);
  }, [syncProgress]);

  if (isOnline && pendingCount === 0 && syncProgress.status === "idle") {
    return null; // Don't show anything when everything is normal
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div
        className={`bg-card border border-border rounded-lg shadow-lg transition-all ${
          isExpanded ? "w-80" : "w-auto"
        }`}
      >
        {/* Compact View */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 p-3 w-full hover:bg-muted transition-colors"
        >
          {isOnline ? (
            <WifiIcon size={20} className="text-success" />
          ) : (
            <WifiOffIcon size={20} className="text-error" />
          )}

          <div className="flex-1 text-left">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-foreground">
                {isOnline ? "Online" : "Offline Mode"}
              </span>
              {pendingCount > 0 && (
                <Badge variant="warning" className="text-xs">
                  {pendingCount} pending
                </Badge>
              )}
            </div>

            {syncProgress.status === "syncing" && (
              <div className="text-xs text-muted-foreground">
                Syncing... {syncProgress.completed}/{syncProgress.total}
              </div>
            )}
          </div>

          {syncProgress.status === "syncing" && <Spinner size="sm" />}
          {syncProgress.status === "success" && (
            <CheckIcon size={16} className="text-success" />
          )}
          {syncProgress.status === "error" && (
            <AlertTriangleIcon size={16} className="text-error" />
          )}
        </button>

        {/* Expanded View */}
        {isExpanded && (
          <div className="border-t border-border p-4 space-y-3">
            {/* Status */}
            <div>
              <div className="text-xs font-medium text-muted-foreground mb-1">
                Connection Status
              </div>
              <div className="flex items-center gap-2">
                {isOnline ? (
                  <>
                    <div className="w-2 h-2 rounded-full bg-success" />
                    <span className="text-sm text-foreground">
                      Connected to server
                    </span>
                  </>
                ) : (
                  <>
                    <div className="w-2 h-2 rounded-full bg-error" />
                    <span className="text-sm text-foreground">
                      Working offline
                    </span>
                  </>
                )}
              </div>
            </div>

            {/* Pending Transactions */}
            {pendingCount > 0 && (
              <div>
                <div className="text-xs font-medium text-muted-foreground mb-1">
                  Pending Changes
                </div>
                <div className="text-sm text-foreground">
                  {pendingCount} transaction{pendingCount !== 1 ? "s" : ""}{" "}
                  waiting to sync
                </div>
              </div>
            )}

            {/* Sync Progress */}
            {syncProgress.status === "syncing" && (
              <div>
                <div className="text-xs font-medium text-muted-foreground mb-1">
                  Sync Progress
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-foreground">
                      {syncProgress.completed} / {syncProgress.total}
                    </span>
                    <span className="text-muted-foreground">
                      {Math.round(
                        (syncProgress.completed / syncProgress.total) * 100
                      )}
                      %
                    </span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full transition-all"
                      style={{
                        width: `${
                          (syncProgress.completed / syncProgress.total) * 100
                        }%`,
                      }}
                    />
                  </div>
                  {syncProgress.failed > 0 && (
                    <div className="text-xs text-error">
                      {syncProgress.failed} failed
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Last Sync */}
            {lastSyncTime && (
              <div>
                <div className="text-xs font-medium text-muted-foreground mb-1">
                  Last Sync
                </div>
                <div className="text-sm text-foreground">
                  {formatDistanceToNow(lastSyncTime, { addSuffix: true })}
                </div>
              </div>
            )}

            {/* Error Message */}
            {dbError && (
              <div className="p-2 bg-error/10 border border-error/20 rounded text-xs text-error">
                <div className="font-medium mb-1">Database Error</div>
                {dbError}
              </div>
            )}

            {syncProgress.status === "error" && syncProgress.error && (
              <div className="p-2 bg-error/10 border border-error/20 rounded text-xs text-error">
                {syncProgress.error}
              </div>
            )}

            {/* Manual Sync Button */}
            {isOnline && pendingCount > 0 && (
              <Button
                size="sm"
                fullWidth
                onClick={manualSync}
                disabled={syncProgress.status === "syncing"}
              >
                {syncProgress.status === "syncing" ? (
                  <>
                    <Spinner size="sm" />
                    Syncing...
                  </>
                ) : (
                  <>
                    <RefreshIcon size={16} />
                    Sync Now
                  </>
                )}
              </Button>
            )}

            {/* Offline Info */}
            {!isOnline && (
              <div className="p-2 bg-warning/10 border border-warning/20 rounded text-xs text-foreground">
                <div className="font-medium mb-1">Limited Functionality</div>
                <div className="text-muted-foreground">
                  You can continue working. Changes will sync when you&apos;re
                  back online.
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  WifiOffIcon,
  CheckCircleIcon,
  AlertCircleIcon,
  RefreshCwIcon,
} from "@/components/icons";

interface QueuedTransaction {
  id: string;
  customerName: string;
  amount: number;
  timestamp: number;
  status: "pending" | "synced" | "failed";
  itemCount: number;
  error?: string;
}

interface OfflineQueueProps {
  onRetrySync?: () => void;
}

export default function OfflineQueue({ onRetrySync }: OfflineQueueProps) {
  const [transactions, setTransactions] = useState<QueuedTransaction[]>([]);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    // Load queued transactions from localStorage
    const loadQueuedTransactions = () => {
      try {
        const stored = localStorage.getItem("pos_offline_queue");
        if (stored) {
          const parsed = JSON.parse(stored);
          setTransactions(parsed as QueuedTransaction[]);
        }
      } catch (err) {
        console.error("Failed to load offline queue:", err);
      }
    };

    loadQueuedTransactions();

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  const handleRetrySync = async () => {
    setIsSyncing(true);
    try {
      // Call the parent's retry sync function if provided
      if (onRetrySync) {
        onRetrySync();
      }

      // Simulate sync delay
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Update transactions status
      const updated = transactions.map((t) =>
        t.status === "failed" ? { ...t, status: "pending" as const } : t,
      );
      setTransactions(updated);
      localStorage.setItem("pos_offline_queue", JSON.stringify(updated));
    } catch (err) {
      console.error("Sync failed:", err);
    } finally {
      setIsSyncing(false);
    }
  };

  const handleRemoveTransaction = (id: string) => {
    const updated = transactions.filter((t) => t.id !== id);
    setTransactions(updated);
    localStorage.setItem("pos_offline_queue", JSON.stringify(updated));
  };

  const pendingCount = transactions.filter(
    (t) => t.status === "pending",
  ).length;
  const failedCount = transactions.filter((t) => t.status === "failed").length;
  const syncedCount = transactions.filter((t) => t.status === "synced").length;

  if (transactions.length === 0) {
    return null;
  }

  return (
    <Card className="p-4 md:p-6 border-2 border-amber-500">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <WifiOffIcon
              size={20}
              className={isOnline ? "text-green-600" : "text-amber-600"}
            />
            <h3 className="text-base md:text-lg font-semibold text-foreground">
              Offline Queue
            </h3>
          </div>
          <div className="text-xs md:text-sm text-muted-foreground">
            {isOnline ? "Online" : "Offline"}
          </div>
        </div>

        {/* Status Summary */}
        <div className="grid grid-cols-3 gap-2">
          <div className="bg-amber-50 dark:bg-amber-950 p-2 rounded-lg text-center">
            <p className="text-xs text-muted-foreground">Pending</p>
            <p className="text-lg font-bold text-amber-600">{pendingCount}</p>
          </div>
          <div className="bg-red-50 dark:bg-red-950 p-2 rounded-lg text-center">
            <p className="text-xs text-muted-foreground">Failed</p>
            <p className="text-lg font-bold text-red-600">{failedCount}</p>
          </div>
          <div className="bg-green-50 dark:bg-green-950 p-2 rounded-lg text-center">
            <p className="text-xs text-muted-foreground">Synced</p>
            <p className="text-lg font-bold text-green-600">{syncedCount}</p>
          </div>
        </div>

        {/* Transactions List */}
        <div className="max-h-64 overflow-y-auto space-y-2">
          {transactions.map((transaction) => (
            <div
              key={transaction.id}
              className={`p-3 rounded-lg border ${
                transaction.status === "synced"
                  ? "bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800"
                  : transaction.status === "failed"
                    ? "bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800"
                    : "bg-amber-50 dark:bg-amber-950 border-amber-200 dark:border-amber-800"
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    {transaction.status === "synced" && (
                      <CheckCircleIcon
                        size={16}
                        className="text-green-600 flex-shrink-0"
                      />
                    )}
                    {transaction.status === "failed" && (
                      <AlertCircleIcon
                        size={16}
                        className="text-red-600 flex-shrink-0"
                      />
                    )}
                    <p className="font-medium text-sm text-foreground truncate">
                      {transaction.customerName}
                    </p>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {transaction.itemCount} item
                    {transaction.itemCount !== 1 ? "s" : ""} •{" "}
                    {new Date(transaction.timestamp).toLocaleTimeString()}
                  </p>
                  {transaction.error && (
                    <p className="text-xs text-red-600 mt-1">
                      {transaction.error}
                    </p>
                  )}
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="font-semibold text-sm text-foreground">
                    ₦
                    {transaction.amount.toLocaleString("en-NG", {
                      maximumFractionDigits: 2,
                    })}
                  </p>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveTransaction(transaction.id)}
                    className="text-xs text-muted-foreground hover:text-destructive mt-1"
                  >
                    Remove
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Actions */}
        {failedCount > 0 && (
          <Alert variant="warning">
            <p className="text-sm">
              {failedCount} transaction{failedCount !== 1 ? "s" : ""} failed to
              sync. Retry when online.
            </p>
          </Alert>
        )}

        <Button
          onClick={handleRetrySync}
          disabled={
            isSyncing || !isOnline || (pendingCount === 0 && failedCount === 0)
          }
          className="w-full"
        >
          {isSyncing ? (
            <>
              <Spinner className="w-4 h-4 mr-2" />
              Syncing...
            </>
          ) : (
            <>
              <RefreshCwIcon size={16} className="mr-2" />
              Retry Sync
            </>
          )}
        </Button>
      </div>
    </Card>
  );
}

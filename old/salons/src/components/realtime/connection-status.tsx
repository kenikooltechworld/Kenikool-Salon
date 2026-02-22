import { useRealtime } from "@/lib/realtime/notifications-provider";
import { CheckCircleIcon, AlertTriangleIcon } from "@/components/icons";

export function ConnectionStatus() {
  const { isConnected, lastUpdate } = useRealtime();

  if (isConnected) {
    return null; // Don't show anything when connected
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className="bg-[var(--card)] border border-[var(--border)] rounded-lg shadow-lg p-4 flex items-center gap-3">
        <AlertTriangleIcon size={20} className="text-[var(--warning)]" />
        <div>
          <p className="font-medium text-foreground text-sm">Connection Lost</p>
          <p className="text-xs text-muted-foreground">
            Trying to reconnect...
          </p>
        </div>
      </div>
    </div>
  );
}

export function RealtimeIndicator() {
  const { isConnected, lastUpdate } = useRealtime();

  return (
    <div className="flex items-center gap-2 text-xs text-muted-foreground">
      <div
        className={`w-2 h-2 rounded-full ${
          isConnected ? "bg-[var(--success)]" : "bg-[var(--error)]"
        } animate-pulse`}
      />
      <span>{isConnected ? "Live" : "Offline"}</span>
      {lastUpdate && (
        <span className="text-xs">
          • Updated {lastUpdate.toLocaleTimeString()}
        </span>
      )}
    </div>
  );
}

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { WifiOffIcon, WifiIcon } from "@/components/icons";

interface OfflineStatusBannerProps {
  isOnline: boolean;
  pendingSync: number;
  onSyncNow: () => void;
}

export function OfflineStatusBanner({
  isOnline,
  pendingSync,
  onSyncNow,
}: OfflineStatusBannerProps) {
  if (isOnline && pendingSync === 0) return null;

  if (!isOnline) {
    return (
      <Card className="bg-yellow-50 border-yellow-200">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <WifiOffIcon className="h-6 w-6 text-[var(--accent)]" />
              <div>
                <p className="font-medium text-[var(--foreground)]">Offline Mode</p>
                <p className="text-sm text-[var(--muted-foreground)]">
                  Transactions will be saved and synced when connection is
                  restored
                </p>
              </div>
            </div>
            {pendingSync > 0 && (
              <div className="text-right">
                <p className="text-sm font-medium text-[var(--foreground)]">
                  {pendingSync} pending
                </p>
                <p className="text-xs text-[var(--muted-foreground)]">transactions to sync</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isOnline && pendingSync > 0) {
    return (
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <WifiIcon className="h-6 w-6 text-[var(--primary)]" />
              <div>
                <p className="font-medium text-[var(--foreground)]">
                  Online - Pending Sync
                </p>
                <p className="text-sm text-[var(--muted-foreground)]">
                  {pendingSync} offline transactions waiting to sync
                </p>
              </div>
            </div>
            <Button onClick={onSyncNow} variant="outline" size="sm">
              Sync Now
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return null;
}

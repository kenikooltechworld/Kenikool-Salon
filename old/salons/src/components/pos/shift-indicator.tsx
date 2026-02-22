import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ClockIcon } from "@/components/icons";
import { type Shift } from "@/lib/api/hooks/usePOS";
import { formatCurrency } from "@/lib/utils/currency";

interface ShiftIndicatorProps {
  currentShift: Shift | null;
  onStartShift: () => void;
  onEndShift: () => void;
}

export function ShiftIndicator({
  currentShift,
  onStartShift,
  onEndShift,
}: ShiftIndicatorProps) {
  if (!currentShift) {
    return (
      <div className="flex items-center gap-2 bg-[var(--muted)] border border-[var(--border)] rounded-lg p-3">
        <ClockIcon className="h-5 w-5 text-[var(--accent)]" />
        <div className="flex-1">
          <p className="text-sm font-medium text-[var(--foreground)]">No Active Shift</p>
          <p className="text-xs text-[var(--muted-foreground)]">
            Start a shift to begin processing transactions
          </p>
        </div>
        <Button size="sm" onClick={onStartShift}>
          Start Shift
        </Button>
      </div>
    );
  }

  const duration = Math.max(
    0,
    Math.floor(
      (new Date().getTime() - new Date(currentShift.start_time).getTime()) /
        1000 /
        60
    )
  );
  const hours = Math.floor(duration / 60);
  const minutes = duration % 60;

  return (
    <div className="flex items-center gap-2 bg-[var(--muted)] border border-[var(--border)] rounded-lg p-3">
      <ClockIcon className="h-5 w-5 text-[var(--primary)]" />
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium text-[var(--foreground)]">Shift Active</p>
          <Badge variant="outline" className="text-xs">
            {hours}h {minutes}m
          </Badge>
        </div>
        <div className="flex gap-4 text-xs text-[var(--muted-foreground)] mt-1">
          <span>Sales: {formatCurrency(currentShift.total_sales || 0)}</span>
          <span>Cash: {formatCurrency(currentShift.total_cash || 0)}</span>
          <span>Card: {formatCurrency(currentShift.total_card || 0)}</span>
        </div>
      </div>
      <Button size="sm" variant="outline" onClick={onEndShift}>
        End Shift
      </Button>
    </div>
  );
}

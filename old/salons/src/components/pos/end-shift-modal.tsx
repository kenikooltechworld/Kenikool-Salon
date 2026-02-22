import { useState } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useEndShift, type Shift } from "@/lib/api/hooks/usePOS";
import { toast } from "sonner";
import { formatCurrency } from "@/lib/utils/currency";

interface EndShiftModalProps {
  open: boolean;
  onClose: () => void;
  currentShift: Shift | null;
}

export function EndShiftModal({
  open,
  onClose,
  currentShift,
}: EndShiftModalProps) {
  const [closingCash, setClosingCash] = useState<string>("");
  const [notes, setNotes] = useState<string>("");

  const endShift = useEndShift();

  const handleSubmit = async () => {
    const cash = parseFloat(closingCash);
    if (isNaN(cash) || cash < 0) {
      toast.error("Please enter a valid closing cash amount");
      return;
    }

    try {
      const result = await endShift.mutateAsync({
        closing_cash: cash,
        notes: notes || undefined,
      });
      toast.success(result.message || "Shift ended successfully");
      setClosingCash("");
      setNotes("");
      onClose();
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Failed to end shift");
    }
  };

  const variance = currentShift
    ? parseFloat(closingCash || "0") - currentShift.expected_cash
    : 0;

  return (
    <Modal open={open} onClose={onClose} size="lg">
      <div className="p-6">
        <h2 className="text-xl font-bold text-[var(--foreground)] mb-4">
          End Shift
        </h2>

        <div className="space-y-4">
          {currentShift && (
            <div className="bg-[var(--muted)] p-4 rounded-[var(--radius-md)] space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-[var(--muted-foreground)]">
                  Opening Cash:
                </span>
                <span className="font-medium">
                  {formatCurrency(currentShift.opening_cash)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-[var(--muted-foreground)]">
                  Expected Cash:
                </span>
                <span className="font-medium">
                  {formatCurrency(currentShift.expected_cash)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-[var(--muted-foreground)]">
                  Total Sales:
                </span>
                <span className="font-medium">
                  {formatCurrency(currentShift.total_sales)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-[var(--muted-foreground)]">
                  Cash Sales:
                </span>
                <span className="font-medium">
                  {formatCurrency(currentShift.total_cash)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-[var(--muted-foreground)]">
                  Card Sales:
                </span>
                <span className="font-medium">
                  {formatCurrency(currentShift.total_card)}
                </span>
              </div>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="closing-cash">Actual Closing Cash</Label>
            <Input
              id="closing-cash"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              value={closingCash}
              onChange={(e) => setClosingCash(e.target.value)}
            />
          </div>

          {closingCash && (
            <div
              className={`p-3 rounded-[var(--radius-md)] ${
                variance === 0
                  ? "bg-[var(--muted)] text-[var(--foreground)]"
                  : variance > 0
                  ? "bg-[var(--muted)] text-[var(--primary)]"
                  : "bg-[var(--muted)] text-[var(--destructive)]"
              }`}
            >
              <div className="flex justify-between items-center">
                <span className="font-medium">Variance:</span>
                <span className="text-lg font-bold">
                  {variance >= 0 ? "+" : ""}
                  {formatCurrency(Math.abs(variance))}
                </span>
              </div>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="notes">Notes (Optional)</Label>
            <Textarea
              id="notes"
              placeholder="Any notes about this shift..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
            />
          </div>
        </div>

        <div className="flex gap-3 pt-6">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={endShift.isPending}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={endShift.isPending}
            className="flex-1"
          >
            {endShift.isPending ? "Ending..." : "End Shift"}
          </Button>
        </div>
      </div>
    </Modal>
  );
}

import { useState } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useStartShift } from "@/lib/api/hooks/usePOS";
import { toast } from "sonner";

interface StartShiftModalProps {
  open: boolean;
  onClose: () => void;
}

export function StartShiftModal({ open, onClose }: StartShiftModalProps) {
  const [openingCash, setOpeningCash] = useState<string>("");
  const [notes, setNotes] = useState<string>("");

  const startShift = useStartShift();

  const handleSubmit = async () => {
    const cash = parseFloat(openingCash);
    if (isNaN(cash) || cash < 0) {
      toast.error("Please enter a valid opening cash amount");
      return;
    }

    try {
      const result = await startShift.mutateAsync({
        opening_cash: cash,
        notes: notes || undefined,
      });
      toast.success(result.message || "Shift started successfully");
      setOpeningCash("");
      setNotes("");
      onClose();
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Failed to start shift");
    }
  };

  return (
    <Modal open={open} onClose={onClose} size="md">
      <div className="p-6">
        <h2 className="text-xl font-bold text-[var(--foreground)] mb-4">
          Start Shift
        </h2>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="opening-cash">Opening Cash Amount</Label>
            <Input
              id="opening-cash"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              value={openingCash}
              onChange={(e) => setOpeningCash(e.target.value)}
            />
          </div>

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
            disabled={startShift.isPending}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={startShift.isPending}
            className="flex-1"
          >
            {startShift.isPending ? "Starting..." : "Start Shift"}
          </Button>
        </div>
      </div>
    </Modal>
  );
}

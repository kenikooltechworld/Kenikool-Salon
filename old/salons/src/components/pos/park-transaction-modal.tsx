import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useParkTransaction, POSCartItem } from "@/lib/api/hooks/usePOS";
import { toast } from "sonner";
import { XIcon } from "@/components/icons";
import { formatCurrency } from "@/lib/utils/currency";

interface ParkTransactionModalProps {
  open: boolean;
  onClose: () => void;
  items: POSCartItem[];
  clientId?: string;
  stylistId?: string;
  discountTotal: number;
  tax: number;
  tip: number;
  notes?: string;
}

export function ParkTransactionModal({
  open,
  onClose,
  items,
  clientId,
  stylistId,
  discountTotal,
  tax,
  tip,
  notes,
}: ParkTransactionModalProps) {
  const [customerName, setCustomerName] = useState("");
  const [customerPhone, setCustomerPhone] = useState("");
  const [parkNotes, setParkNotes] = useState(notes || "");

  const parkTransaction = useParkTransaction();

  const handlePark = async () => {
    if (!customerName && !customerPhone) {
      toast.error("Please provide customer name or phone for identification");
      return;
    }

    try {
      const result = await parkTransaction.mutateAsync({
        transaction: {
          items,
          client_id: clientId,
          stylist_id: stylistId,
          discount_total: discountTotal,
          tax,
          tip,
          notes: parkNotes,
        },
        customer_name: customerName,
        customer_phone: customerPhone,
      });

      toast.success(`Transaction parked: ${result.hold_number}`);
      onClose();
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Failed to park transaction");
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Park Transaction</span>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <XIcon className="h-4 w-4" />
            </Button>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Park this transaction to complete later. Provide customer
            information for easy identification.
          </p>

          <div className="space-y-2">
            <Label>Customer Name</Label>
            <Input
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              placeholder="Enter customer name"
            />
          </div>

          <div className="space-y-2">
            <Label>Customer Phone</Label>
            <Input
              value={customerPhone}
              onChange={(e) => setCustomerPhone(e.target.value)}
              placeholder="Enter customer phone"
            />
          </div>

          <div className="space-y-2">
            <Label>Notes (Optional)</Label>
            <Textarea
              value={parkNotes}
              onChange={(e) => setParkNotes(e.target.value)}
              placeholder="Add any notes about this hold..."
              className="min-h-[80px]"
              maxLength={500}
            />
            <p className="text-xs text-muted-foreground">
              {parkNotes.length}/500
            </p>
          </div>

          <div className="p-3 bg-muted rounded-lg">
            <div className="flex justify-between text-sm">
              <span>Items:</span>
              <span className="font-medium">{items.length}</span>
            </div>
            <div className="flex justify-between text-sm mt-1">
              <span>Total:</span>
              <span className="font-medium">
                {formatCurrency(
                  items.reduce(
                    (sum, item) => sum + item.price * item.quantity,
                    0
                  ) -
                    discountTotal +
                    tax +
                    tip
                )}
              </span>
            </div>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" className="flex-1" onClick={onClose}>
              Cancel
            </Button>
            <Button
              className="flex-1"
              onClick={handlePark}
              disabled={parkTransaction.isPending}
            >
              {parkTransaction.isPending ? "Parking..." : "Park Transaction"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

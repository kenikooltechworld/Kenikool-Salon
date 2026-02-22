import { useState } from "react";
import {
  Invoice,
  Payment,
  useRecordPayment,
} from "@/lib/api/hooks/useAccounting";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { showToast } from "@/lib/utils/toast";

interface PaymentFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  invoice: Invoice | null;
}

export function PaymentFormModal({
  isOpen,
  onClose,
  invoice,
}: PaymentFormModalProps) {
  const recordPaymentMutation = useRecordPayment();
  const [formData, setFormData] = useState<Payment>({
    amount: 0,
    payment_date: new Date().toISOString().split("T")[0],
    payment_method: "cash",
    reference: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!invoice) return;

    if (formData.amount <= 0) {
      showToast("Payment amount must be greater than 0", "error");
      return;
    }

    if (formData.amount > invoice.balance) {
      showToast("Payment amount cannot exceed balance", "error");
      return;
    }

    try {
      await recordPaymentMutation.mutateAsync({
        id: invoice._id,
        payment: formData,
      });
      showToast("Payment recorded successfully", "success");
      setFormData({
        amount: 0,
        payment_date: new Date().toISOString().split("T")[0],
        payment_method: "cash",
        reference: "",
      });
      onClose();
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to record payment",
        "error"
      );
    }
  };

  if (!invoice) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Record Payment">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="p-4 bg-[var(--muted)] rounded-[var(--radius-md)]">
          <div className="flex justify-between mb-2">
            <span className="text-[var(--muted-foreground)]">Invoice:</span>
            <span className="font-semibold">{invoice.invoice_number}</span>
          </div>
          <div className="flex justify-between mb-2">
            <span className="text-[var(--muted-foreground)]">Total:</span>
            <span className="font-semibold">₦{invoice.total.toFixed(2)}</span>
          </div>
          <div className="flex justify-between mb-2">
            <span className="text-[var(--muted-foreground)]">Paid:</span>
            <span className="font-semibold">
              ₦{invoice.amount_paid.toFixed(2)}
            </span>
          </div>
          <div className="flex justify-between pt-2 border-t">
            <span className="font-semibold">Balance Due:</span>
            <span className="font-bold text-lg text-[var(--primary)]">
              ₦{invoice.balance.toFixed(2)}
            </span>
          </div>
        </div>

        <div>
          <Label htmlFor="amount">Payment Amount</Label>
          <Input
            id="amount"
            type="number"
            step="0.01"
            value={formData.amount || ""}
            onChange={(e) =>
              setFormData({
                ...formData,
                amount: parseFloat(e.target.value) || 0,
              })
            }
            placeholder="0.00"
            max={invoice.balance}
            required
          />
          <p className="text-sm text-[var(--muted-foreground)] mt-1">
            Maximum: ₦{invoice.balance.toFixed(2)}
          </p>
        </div>

        <div>
          <Label htmlFor="payment_date">Payment Date</Label>
          <Input
            id="payment_date"
            type="date"
            value={formData.payment_date}
            onChange={(e) =>
              setFormData({ ...formData, payment_date: e.target.value })
            }
            required
          />
        </div>

        <div>
          <Label htmlFor="payment_method">Payment Method</Label>
          <Select
            id="payment_method"
            value={formData.payment_method}
            onChange={(e) =>
              setFormData({ ...formData, payment_method: e.target.value })
            }
            required
          >
            <option value="cash">Cash</option>
            <option value="card">Card</option>
            <option value="bank_transfer">Bank Transfer</option>
            <option value="check">Check</option>
            <option value="other">Other</option>
          </Select>
        </div>

        <div>
          <Label htmlFor="reference">Reference (Optional)</Label>
          <Input
            id="reference"
            value={formData.reference || ""}
            onChange={(e) =>
              setFormData({ ...formData, reference: e.target.value })
            }
            placeholder="Transaction reference"
          />
        </div>

        <div className="flex gap-3 pt-4">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            className="flex-1"
            disabled={recordPaymentMutation.isPending}
          >
            Record Payment
          </Button>
        </div>
      </form>
    </Modal>
  );
}

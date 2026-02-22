import { useState } from "react";
import { useUpdateGroupBooking } from "@/lib/api/hooks/useGroupBookings";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { Select } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { AlertTriangleIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";
import type { GroupBooking } from "@/lib/api/types";

interface PaymentRecordModalProps {
  isOpen: boolean;
  onClose: () => void;
  booking: GroupBooking;
}

export function PaymentRecordModal({
  isOpen,
  onClose,
  booking,
}: PaymentRecordModalProps) {
  const updateGroupBooking = useUpdateGroupBooking();

  const [paymentStatus, setPaymentStatus] = useState(
    booking.payment_status || "unpaid"
  );
  const [paymentMethod, setPaymentMethod] = useState(
    booking.payment_method || ""
  );
  const [amountPaid, setAmountPaid] = useState(
    booking.total_price?.toString() || "0"
  );
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!paymentStatus) {
      newErrors.paymentStatus = "Payment status is required";
    }

    if (paymentStatus === "paid" && !paymentMethod) {
      newErrors.paymentMethod = "Payment method is required for paid bookings";
    }

    const amount = parseFloat(amountPaid);
    if (isNaN(amount) || amount < 0) {
      newErrors.amountPaid = "Invalid amount";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    const updateData = {
      payment_status: paymentStatus,
      payment_method: paymentMethod || undefined,
      amount_paid: parseFloat(amountPaid),
    };

    try {
      await updateGroupBooking.mutateAsync({
        bookingId: booking._id,
        data: updateData,
      });
      showToast("Payment recorded successfully!", "success");
      onClose();
    } catch (error: unknown) {
      const err = error as {
        response?: { data?: { message?: string } };
        message?: string;
      };
      const errorMessage =
        err.response?.data?.message ||
        err.message ||
        "Failed to record payment";
      setErrors({ submit: errorMessage });
      showToast(errorMessage, "error");
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="md">
      <div className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">
          Record Payment
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {errors.submit && (
            <Alert variant="error">
              <AlertTriangleIcon size={20} />
              <div>
                <p className="text-sm">{errors.submit}</p>
              </div>
            </Alert>
          )}

          {/* Booking Summary */}
          <div className="p-4 bg-muted rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-muted-foreground">Organizer:</span>
              <span className="font-medium">{booking.organizer_name}</span>
            </div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-muted-foreground">
                Total Members:
              </span>
              <span className="font-medium">{booking.total_members}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">
                Total Amount:
              </span>
              <span className="text-lg font-bold text-primary">
                ₦{booking.total_price?.toLocaleString() || 0}
              </span>
            </div>
          </div>

          {/* Payment Status */}
          <div>
            <Label htmlFor="payment_status">Payment Status *</Label>
            <Select
              id="payment_status"
              value={paymentStatus}
              onChange={(e) => setPaymentStatus(e.target.value)}
              error={!!errors.paymentStatus}
            >
              <option value="unpaid">Unpaid</option>
              <option value="partial">Partially Paid</option>
              <option value="paid">Paid</option>
            </Select>
            {errors.paymentStatus && (
              <p className="text-sm text-error mt-1">{errors.paymentStatus}</p>
            )}
          </div>

          {/* Payment Method */}
          {paymentStatus !== "unpaid" && (
            <div>
              <Label htmlFor="payment_method">Payment Method *</Label>
              <Select
                id="payment_method"
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
                error={!!errors.paymentMethod}
              >
                <option value="">Select payment method</option>
                <option value="cash">Cash</option>
                <option value="card">Card</option>
                <option value="transfer">Bank Transfer</option>
                <option value="pos">POS</option>
                <option value="mobile_money">Mobile Money</option>
              </Select>
              {errors.paymentMethod && (
                <p className="text-sm text-error mt-1">
                  {errors.paymentMethod}
                </p>
              )}
            </div>
          )}

          {/* Amount Paid */}
          {paymentStatus !== "unpaid" && (
            <div>
              <Label htmlFor="amount_paid">Amount Paid *</Label>
              <Input
                id="amount_paid"
                type="number"
                step="0.01"
                value={amountPaid}
                onChange={(e) => setAmountPaid(e.target.value)}
                placeholder="Enter amount paid"
                error={!!errors.amountPaid}
              />
              {errors.amountPaid && (
                <p className="text-sm text-error mt-1">{errors.amountPaid}</p>
              )}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={updateGroupBooking.isPending}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={updateGroupBooking.isPending}
              className="flex-1"
            >
              {updateGroupBooking.isPending ? (
                <>
                  <Spinner size="sm" />
                  Recording...
                </>
              ) : (
                "Record Payment"
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
}

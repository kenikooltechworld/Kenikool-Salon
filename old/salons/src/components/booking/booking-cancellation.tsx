import { useState } from "react";
import { useCancelBooking } from "@/lib/api/hooks/useBookings";
import { useToast } from "@/hooks/use-toast";
import {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalBody,
  ModalFooter,
} from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { AlertCircle } from "lucide-react";

interface BookingCancellationProps {
  isOpen: boolean;
  onClose: () => void;
  bookingId: string;
  bookingDetails: {
    serviceName: string;
    stylistName: string;
    date: string;
    time: string;
    price: number;
  };
  cancellationPolicy?: string;
}

export function BookingCancellation({
  isOpen,
  onClose,
  bookingId,
  bookingDetails,
  cancellationPolicy,
}: BookingCancellationProps) {
  const { toast } = useToast();
  const [cancellationReason, setCancellationReason] = useState("");
  const [confirmed, setConfirmed] = useState(false);

  const cancellationMutation = useCancelBooking();

  const handleCancel = async () => {
    if (!cancellationReason.trim()) {
      toast("Please provide a cancellation reason", "error");
      return;
    }

    if (!confirmed) {
      toast("Please confirm the cancellation", "error");
      return;
    }

    cancellationMutation.mutate(
      { id: bookingId, reason: cancellationReason },
      {
        onSuccess: (data) => {
          toast("Booking cancelled successfully", "success");
          if (data.refund_amount && data.refund_amount > 0) {
            toast(
              `Refund of ₦${data.refund_amount.toLocaleString()} will be processed`,
              "success",
            );
          }
          onClose();
        },
        onError: (error: any) => {
          toast(
            error.response?.data?.detail || "Failed to cancel booking",
            "error",
          );
        },
      },
    );
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="md">
      <ModalHeader>
        <ModalTitle>Cancel Booking</ModalTitle>
      </ModalHeader>

      <ModalBody className="space-y-6">
        {/* Warning */}
        <div className="flex gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
          <div>
            <p className="font-semibold text-red-900 text-sm">
              This action cannot be undone
            </p>
            <p className="text-sm text-red-800 mt-1">
              Cancelling this booking will free up the time slot for other
              customers.
            </p>
          </div>
        </div>

        {/* Booking Details */}
        <Card>
          <CardContent className="pt-4 space-y-3">
            <div>
              <p className="text-sm text-[var(--muted-foreground)]">Service</p>
              <p className="font-semibold text-[var(--foreground)]">
                {bookingDetails.serviceName}
              </p>
            </div>
            <div>
              <p className="text-sm text-[var(--muted-foreground)]">Stylist</p>
              <p className="font-semibold text-[var(--foreground)]">
                {bookingDetails.stylistName}
              </p>
            </div>
            <div>
              <p className="text-sm text-[var(--muted-foreground)]">
                Date & Time
              </p>
              <p className="font-semibold text-[var(--foreground)]">
                {new Date(bookingDetails.date).toLocaleDateString("en-US", {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </p>
              <p className="text-sm text-[var(--foreground)]">
                {bookingDetails.time}
              </p>
            </div>
            <div className="pt-3 border-t border-[var(--border)]">
              <p className="text-sm text-[var(--muted-foreground)]">Amount</p>
              <p className="font-bold text-[var(--primary)] text-lg">
                ₦{bookingDetails.price.toLocaleString()}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Cancellation Policy */}
        {cancellationPolicy && (
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm font-semibold text-blue-900 mb-2">
              Cancellation Policy
            </p>
            <p className="text-sm text-blue-800">{cancellationPolicy}</p>
          </div>
        )}

        {/* Cancellation Reason */}
        <div>
          <Label required>Reason for Cancellation</Label>
          <Input
            value={cancellationReason}
            onChange={(e) => setCancellationReason(e.target.value)}
            placeholder="Please tell us why you're cancelling..."
            className="mt-2"
            maxLength={500}
          />
          <p className="text-xs text-[var(--muted-foreground)] mt-1">
            {cancellationReason.length}/500 characters
          </p>
        </div>

        {/* Confirmation Checkbox */}
        <div className="flex items-start gap-3">
          <input
            type="checkbox"
            id="confirm"
            checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
            className="mt-1"
          />
          <label htmlFor="confirm" className="text-sm text-[var(--foreground)]">
            I understand that this booking will be cancelled and the time slot
            will be available for other customers.
          </label>
        </div>
      </ModalBody>

      <ModalFooter>
        <Button variant="outline" onClick={onClose}>
          Keep Booking
        </Button>
        <Button
          variant="destructive"
          onClick={handleCancel}
          disabled={
            cancellationMutation.isPending ||
            !cancellationReason.trim() ||
            !confirmed
          }
        >
          {cancellationMutation.isPending ? "Cancelling..." : "Cancel Booking"}
        </Button>
      </ModalFooter>
    </Modal>
  );
}

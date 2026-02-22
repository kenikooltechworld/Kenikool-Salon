import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { AlertTriangleIcon, CheckCircleIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";
import { apiClient } from "@/lib/api/client";
import type { GroupBooking } from "@/lib/api/types";

interface SendReminderModalProps {
  isOpen: boolean;
  onClose: () => void;
  booking: GroupBooking;
}

export function SendReminderModal({
  isOpen,
  onClose,
  booking,
}: SendReminderModalProps) {
  const [message, setMessage] = useState(
    `Hi ${
      booking.organizer_name
    }, this is a reminder about your group booking on ${new Date(
      booking.booking_date
    ).toLocaleDateString()} for ${
      booking.total_members
    } members. Total: ₦${booking.total_price?.toLocaleString()}. See you soon!`
  );
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const handleSendSMS = async () => {
    setSending(true);
    setError("");

    try {
      await apiClient.post(
        `/api/group-bookings/${booking._id}/send-reminder`,
        null,
        {
          params: {
            message: message,
            method: "sms",
          },
        }
      );

      showToast("SMS reminder sent successfully!", "success");
      onClose();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const errorMessage =
        error.response?.data?.detail || "Failed to send SMS reminder";
      setError(errorMessage);
      showToast(errorMessage, "error");
    } finally {
      setSending(false);
    }
  };

  const handleSendWhatsApp = async () => {
    setSending(true);
    setError("");

    try {
      await apiClient.post(
        `/api/group-bookings/${booking._id}/send-reminder`,
        null,
        {
          params: {
            message: message,
            method: "whatsapp",
          },
        }
      );

      showToast("WhatsApp reminder sent successfully!", "success");
      onClose();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const errorMessage =
        error.response?.data?.detail || "Failed to send WhatsApp reminder";
      setError(errorMessage);
      showToast(errorMessage, "error");
    } finally {
      setSending(false);
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="md">
      <div className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">
          Send Reminder
        </h2>

        <div className="space-y-4">
          {error && (
            <Alert variant="error">
              <AlertTriangleIcon size={20} />
              <div>
                <p className="text-sm">{error}</p>
              </div>
            </Alert>
          )}

          {/* Booking Summary */}
          <div className="p-4 bg-muted rounded-lg space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Organizer:</span>
              <span className="font-medium">{booking.organizer_name}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Phone:</span>
              <span className="font-medium">{booking.organizer_phone}</span>
            </div>
            {booking.organizer_email && (
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Email:</span>
                <span className="font-medium">{booking.organizer_email}</span>
              </div>
            )}
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Date:</span>
              <span className="font-medium">
                {new Date(booking.booking_date).toLocaleDateString()}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Members:</span>
              <span className="font-medium">{booking.total_members}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Total:</span>
              <span className="text-lg font-bold text-primary">
                ₦{booking.total_price?.toLocaleString() || 0}
              </span>
            </div>
          </div>

          {/* Message */}
          <div>
            <Label htmlFor="message">Message</Label>
            <Textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Enter reminder message..."
              rows={5}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Customize the message before sending
            </p>
          </div>

          {/* Send Options */}
          <div className="space-y-2">
            <Button
              onClick={handleSendWhatsApp}
              disabled={sending || !message.trim()}
              className="w-full"
              variant="primary"
            >
              {sending ? (
                <>
                  <Spinner size="sm" />
                  Sending via WhatsApp...
                </>
              ) : (
                <>
                  <CheckCircleIcon className="w-4 h-4 mr-2" />
                  Send via WhatsApp
                </>
              )}
            </Button>

            <Button
              onClick={handleSendSMS}
              disabled={sending || !message.trim()}
              className="w-full"
              variant="outline"
            >
              {sending ? (
                <>
                  <Spinner size="sm" />
                  Sending SMS...
                </>
              ) : (
                <>
                  <CheckCircleIcon className="w-4 h-4 mr-2" />
                  Send via SMS
                </>
              )}
            </Button>
          </div>

          <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <p className="text-xs text-blue-800 dark:text-blue-200">
              <strong>Note:</strong> Messages will be sent via Termii API.
              WhatsApp messages may fallback to SMS if WhatsApp delivery fails.
              Ensure your Termii account has sufficient credits.
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={sending}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
}

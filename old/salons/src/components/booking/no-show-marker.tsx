import React, { useState } from "react";
import { AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface NoShowMarkerProps {
  bookingId: string;
  onMarkNoShow: (bookingId: string) => Promise<void>;
  onCancel?: () => void;
  loading?: boolean;
}

export const NoShowMarker: React.FC<NoShowMarkerProps> = ({
  bookingId,
  onMarkNoShow,
  onCancel,
  loading = false,
}) => {
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleConfirm = async () => {
    setSubmitting(true);
    setError(null);

    try {
      await onMarkNoShow(bookingId);
      setConfirming(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to mark no-show");
    } finally {
      setSubmitting(false);
    }
  };

  if (!confirming) {
    return (
      <Button
        variant="outline"
        onClick={() => setConfirming(true)}
        disabled={loading}
        className="w-full"
      >
        Mark as No-Show
      </Button>
    );
  }

  return (
    <div className="space-y-3 rounded-lg border border-red-200 bg-red-50 p-4">
      <div className="flex items-start gap-2">
        <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="font-medium text-red-900">Mark as No-Show?</h3>
          <p className="text-sm text-red-800 mt-1">
            This will record that the customer did not arrive for their
            appointment.
          </p>
        </div>
      </div>

      {error && (
        <div className="text-sm text-red-900 bg-red-100 rounded p-2">
          {error}
        </div>
      )}

      <div className="flex gap-2">
        <Button
          variant="destructive"
          onClick={handleConfirm}
          disabled={submitting || loading}
          className="flex-1"
        >
          {submitting ? "Marking..." : "Confirm No-Show"}
        </Button>
        <Button
          variant="outline"
          onClick={() => setConfirming(false)}
          disabled={submitting || loading}
          className="flex-1"
        >
          Cancel
        </Button>
      </div>
    </div>
  );
};

import { useState } from "react";
import { Dialog } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { CheckCircleIcon, AlertTriangleIcon } from "@/components/icons";
import { useRequestReview } from "@/lib/api/hooks/useClients";

interface ReviewRequestModalProps {
  isOpen: boolean;
  clientId: string;
  onClose: () => void;
}

export function ReviewRequestModal({
  isOpen,
  clientId,
  onClose,
}: ReviewRequestModalProps) {
  const requestReview = useRequestReview(clientId);
  const [channel, setChannel] = useState<"sms" | "email" | "whatsapp">("sms");

  const handleSubmit = async () => {
    try {
      await requestReview.mutateAsync({ channel });
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (error) {
      console.error("Failed to request review:", error);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center">
        <div className="bg-background rounded-lg shadow-lg max-w-md w-full mx-4">
          {/* Header */}
          <div className="border-b border-border p-6 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-foreground">
              Request Review
            </h2>
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground"
            >
              ✕
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-4">
            {/* Success Message */}
            {requestReview.isSuccess && (
              <Alert variant="success">
                <CheckCircleIcon size={20} />
                <div>
                  <h3 className="font-semibold">Review Request Sent</h3>
                  <p className="text-sm">
                    Review request has been sent via {channel.toUpperCase()}
                  </p>
                </div>
              </Alert>
            )}

            {/* Error Message */}
            {requestReview.isError && (
              <Alert variant="error">
                <AlertTriangleIcon size={20} />
                <div>
                  <h3 className="font-semibold">Error Sending Request</h3>
                  <p className="text-sm">
                    {requestReview.error?.message || "Failed to send review request"}
                  </p>
                </div>
              </Alert>
            )}

            {/* Channel Selection */}
            {!requestReview.isSuccess && (
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Communication Channel
                </label>
                <Select
                  value={channel}
                  onChange={(e) => setChannel(e.target.value as any)}
                  disabled={requestReview.isPending}
                >
                  <option value="sms">SMS</option>
                  <option value="email">Email</option>
                  <option value="whatsapp">WhatsApp</option>
                </Select>
                <p className="text-xs text-muted-foreground mt-2">
                  The review request will be sent to the client via their preferred{" "}
                  {channel.toUpperCase()} contact information.
                </p>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-border p-6 flex gap-3 justify-end">
            <Button
              variant="outline"
              onClick={onClose}
              disabled={requestReview.isPending}
            >
              {requestReview.isSuccess ? "Close" : "Cancel"}
            </Button>
            {!requestReview.isSuccess && (
              <Button
                onClick={handleSubmit}
                disabled={requestReview.isPending}
              >
                {requestReview.isPending ? (
                  <>
                    <Spinner size="sm" className="mr-2" />
                    Sending...
                  </>
                ) : (
                  "Send Request"
                )}
              </Button>
            )}
          </div>
        </div>
      </div>
    </Dialog>
  );
}

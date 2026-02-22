import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { AlertTriangleIcon } from "@/components/icons";
import { apiClient } from "@/lib/api/client";

export interface BulkMessageModalProps {
  isOpen: boolean;
  selectedClientIds: string[];
  onClose: () => void;
  onSuccess?: () => void;
}

/**
 * Modal for sending bulk messages to selected clients
 * Supports SMS, Email, and WhatsApp channels
 * 
 * Requirements: REQ-CM-011 (Task 27.3)
 */
export function BulkMessageModal({
  isOpen,
  selectedClientIds,
  onClose,
  onSuccess,
}: BulkMessageModalProps) {
  const [channel, setChannel] = useState<"sms" | "email" | "whatsapp">("sms");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState<string | null>(null);

  const sendBulkMessage = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post("/clients/bulk/send-message", {
        client_ids: selectedClientIds,
        channel,
        content: message,
        subject: channel === "email" ? subject : undefined,
      });
      return response.data;
    },
    onSuccess: () => {
      setMessage("");
      setSubject("");
      setChannel("sms");
      onSuccess?.();
      onClose();
    },
    onError: (err: any) => {
      setError(err.response?.data?.error?.message || "Failed to send messages");
    },
  });

  const handleSend = () => {
    if (!message.trim()) {
      setError("Message cannot be empty");
      return;
    }

    if (channel === "email" && !subject.trim()) {
      setError("Subject is required for email");
      return;
    }

    setError(null);
    sendBulkMessage.mutate();
  };

  const characterCount = message.length;
  const smsLimit = 160;
  const isOverLimit = channel === "sms" && characterCount > smsLimit;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Send Bulk Message</DialogTitle>
          <DialogDescription>
            Send a message to {selectedClientIds.length} client
            {selectedClientIds.length !== 1 ? "s" : ""}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Channel Selection */}
          <div className="space-y-2">
            <Label htmlFor="channel">Channel</Label>
            <Select value={channel} onValueChange={(v: any) => setChannel(v)}>
              <SelectTrigger id="channel">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="sms">SMS</SelectItem>
                <SelectItem value="email">Email</SelectItem>
                <SelectItem value="whatsapp">WhatsApp</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Email Subject (only for email) */}
          {channel === "email" && (
            <div className="space-y-2">
              <Label htmlFor="subject">Subject</Label>
              <Input
                id="subject"
                placeholder="Email subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
              />
            </div>
          )}

          {/* Message Content */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="message">Message</Label>
              {channel === "sms" && (
                <span
                  className={`text-xs ${
                    isOverLimit ? "text-red-500 font-medium" : "text-muted-foreground"
                  }`}
                >
                  {characterCount}/{smsLimit}
                </span>
              )}
            </div>
            <Textarea
              id="message"
              placeholder="Enter your message..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={5}
              className={isOverLimit ? "border-red-500" : ""}
            />
            {channel === "sms" && isOverLimit && (
              <p className="text-xs text-red-500">
                Message exceeds SMS limit. It will be split into multiple messages.
              </p>
            )}
          </div>

          {/* Error Alert */}
          {error && (
            <Alert variant="error">
              <AlertTriangleIcon size={16} />
              <div>{error}</div>
            </Alert>
          )}

          {/* Loading State */}
          {sendBulkMessage.isPending && (
            <div className="flex items-center justify-center gap-2 py-4">
              <Spinner size="sm" />
              <span className="text-sm text-muted-foreground">
                Sending messages...
              </span>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={sendBulkMessage.isPending}>
            Cancel
          </Button>
          <Button
            onClick={handleSend}
            disabled={sendBulkMessage.isPending || !message.trim()}
          >
            {sendBulkMessage.isPending ? (
              <>
                <Spinner size="sm" className="mr-2" />
                Sending...
              </>
            ) : (
              "Send"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

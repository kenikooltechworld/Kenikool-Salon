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
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";
import { useSendReceipt } from "@/lib/api/hooks/usePOS";
import { toast } from "sonner";
import { Loader2, Mail, MessageSquare, Printer } from "@/components/icons";

interface ReceiptOptionsModalProps {
  open: boolean;
  onClose: () => void;
  transactionId: string;
}

export function ReceiptOptionsModal({
  open,
  onClose,
  transactionId,
}: ReceiptOptionsModalProps) {
  const [method, setMethod] = useState<"email" | "sms" | "print">("email");
  const [recipient, setRecipient] = useState("");
  const [savePreference, setSavePreference] = useState(false);

  const sendReceipt = useSendReceipt();

  const handleSend = async () => {
    if ((method === "email" || method === "sms") && !recipient) {
      toast.error(
        `Please enter ${method === "email" ? "email address" : "phone number"}`
      );
      return;
    }

    try {
      const result = await sendReceipt.mutateAsync({
        transaction_id: transactionId,
        method,
        recipient: method === "print" ? undefined : recipient,
        save_preference: savePreference,
      });

      toast.success(result.message);
      handleClose();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to send receipt");
    }
  };

  const handleClose = () => {
    setMethod("email");
    setRecipient("");
    setSavePreference(false);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Send Receipt</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <Label>Delivery Method</Label>
            <RadioGroup value={method} onValueChange={(v: any) => setMethod(v)}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="email" id="email" />
                <Label
                  htmlFor="email"
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <Mail className="h-4 w-4" />
                  Email
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="sms" id="sms" />
                <Label
                  htmlFor="sms"
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <MessageSquare className="h-4 w-4" />
                  SMS
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="print" id="print" />
                <Label
                  htmlFor="print"
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <Printer className="h-4 w-4" />
                  Print
                </Label>
              </div>
            </RadioGroup>
          </div>

          {method !== "print" && (
            <div>
              <Label htmlFor="recipient">
                {method === "email" ? "Email Address" : "Phone Number"}
              </Label>
              <Input
                id="recipient"
                type={method === "email" ? "email" : "tel"}
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
                placeholder={
                  method === "email" ? "customer@example.com" : "+1234567890"
                }
              />
            </div>
          )}

          {method !== "print" && (
            <div className="flex items-center space-x-2">
              <Checkbox
                id="savePreference"
                checked={savePreference}
                onCheckedChange={(checked) =>
                  setSavePreference(checked as boolean)
                }
              />
              <Label
                htmlFor="savePreference"
                className="text-sm font-normal cursor-pointer"
              >
                Save as customer preference
              </Label>
            </div>
          )}

          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button onClick={handleSend} disabled={sendReceipt.isPending}>
              {sendReceipt.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Sending...
                </>
              ) : (
                "Send Receipt"
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

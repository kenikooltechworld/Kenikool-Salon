import { useState } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  DownloadIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
} from "@/components/icons";
import {
  generateReceiptPDF,
  printReceipt,
  type ReceiptData,
} from "@/lib/utils/receipt";

interface ReceiptModalProps {
  open: boolean;
  onClose: () => void;
  receiptData: ReceiptData;
}

export function ReceiptModal({
  open,
  onClose,
  receiptData,
}: ReceiptModalProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDownloadPDF = async () => {
    setIsGenerating(true);
    setError(null);

    try {
      await generateReceiptPDF(receiptData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate PDF");
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePrint = () => {
    try {
      printReceipt(receiptData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to print receipt");
    }
  };

  const handleSendWhatsApp = () => {
    const message = `Receipt for ${
      receiptData.service_name
    }\nAmount: ₦${receiptData.amount_paid.toLocaleString()}\nReceipt No: ${
      receiptData.receipt_number
    }`;
    const whatsappUrl = `https://wa.me/${receiptData.client_phone.replace(
      /\D/g,
      ""
    )}?text=${encodeURIComponent(message)}`;
    window.open(whatsappUrl, "_blank");
  };

  const handleSendSMS = () => {
    const message = `Receipt for ${
      receiptData.service_name
    }. Amount: ₦${receiptData.amount_paid.toLocaleString()}. Receipt No: ${
      receiptData.receipt_number
    }. Thank you!`;
    const smsUrl = `sms:${receiptData.client_phone}?body=${encodeURIComponent(
      message
    )}`;
    window.location.href = smsUrl;
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Receipt Generated"
      description="Choose how to deliver the receipt"
      size="md"
    >
      <div className="space-y-4">
        {/* Receipt Preview */}
        <div className="p-4 bg-muted rounded-lg">
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Receipt No:</span>
              <span className="font-medium text-foreground">
                {receiptData.receipt_number}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Client:</span>
              <span className="font-medium text-foreground">
                {receiptData.client_name}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Service:</span>
              <span className="font-medium text-foreground">
                {receiptData.service_name}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Amount Paid:</span>
              <span className="font-bold text-foreground text-lg">
                ₦{receiptData.amount_paid.toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        {/* Success Message */}
        <Alert variant="success">
          <CheckCircleIcon size={20} />
          <div>
            <h3 className="font-semibold">Payment Successful</h3>
            <p className="text-sm">Receipt has been generated</p>
          </div>
        </Alert>

        {/* Error Message */}
        {error && (
          <Alert variant="error">
            <AlertTriangleIcon size={20} />
            <div>
              <h3 className="font-semibold">Error</h3>
              <p className="text-sm">{error}</p>
            </div>
          </Alert>
        )}

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-3">
          <Button
            variant="outline"
            onClick={handleDownloadPDF}
            disabled={isGenerating}
          >
            {isGenerating ? (
              <>
                <Spinner size="sm" />
                Generating...
              </>
            ) : (
              <>
                <DownloadIcon size={20} />
                Download PDF
              </>
            )}
          </Button>

          <Button variant="outline" onClick={handlePrint}>
            🖨️ Print
          </Button>

          <Button variant="outline" onClick={handleSendWhatsApp}>
            💬 WhatsApp
          </Button>

          <Button variant="outline" onClick={handleSendSMS}>
            📱 SMS
          </Button>
        </div>

        {/* Close Button */}
        <Button fullWidth onClick={onClose}>
          Close
        </Button>
      </div>
    </Modal>
  );
}

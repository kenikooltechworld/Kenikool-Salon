import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PrinterIcon, MailIcon, CheckCircleIcon } from "@/components/icons";
import type { POSTransaction } from "@/lib/api/hooks/usePOS";
import { useGenerateReceipt } from "@/lib/api/hooks/usePOS";
import { useState } from "react";
import { toast } from "sonner";
import { formatCurrency } from "@/lib/utils/currency";

interface POSReceiptProps {
  transaction: POSTransaction | null;
  open: boolean;
  onClose: () => void;
}

export function POSReceipt({ transaction, open, onClose }: POSReceiptProps) {
  const [email, setEmail] = useState("");
  const [emailSent, setEmailSent] = useState(false);
  const generateReceipt = useGenerateReceipt();

  if (!transaction) return null;

  const handlePrint = () => {
    // Create a print-specific window
    const printWindow = window.open("", "_blank");
    if (!printWindow) {
      toast.error("Please allow popups to print receipts");
      return;
    }

    const receiptHTML = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Receipt - ${transaction.transaction_number}</title>
          <style>
            @media print {
              @page {
                size: 80mm auto;
                margin: 0;
              }
              body {
                margin: 0;
                padding: 10mm;
              }
            }
            body {
              font-family: 'Courier New', monospace;
              font-size: 12px;
              line-height: 1.4;
              max-width: 80mm;
              margin: 0 auto;
              padding: 10mm;
            }
            .header {
              text-align: center;
              margin-bottom: 10px;
              border-bottom: 2px dashed #000;
              padding-bottom: 10px;
            }
            .header h1 {
              margin: 0;
              font-size: 18px;
            }
            .header p {
              margin: 2px 0;
              font-size: 10px;
            }
            .item {
              display: flex;
              justify-content: space-between;
              margin: 5px 0;
            }
            .totals {
              border-top: 2px dashed #000;
              margin-top: 10px;
              padding-top: 10px;
            }
            .total-line {
              display: flex;
              justify-content: space-between;
              margin: 3px 0;
            }
            .total-line.grand {
              font-weight: bold;
              font-size: 14px;
              border-top: 2px solid #000;
              padding-top: 5px;
              margin-top: 5px;
            }
            .footer {
              text-align: center;
              margin-top: 15px;
              padding-top: 10px;
              border-top: 2px dashed #000;
              font-size: 10px;
            }
            .footer p {
              margin: 3px 0;
            }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>RECEIPT</h1>
            <p>${transaction.transaction_number}</p>
            <p>${new Date(transaction.created_at).toLocaleString()}</p>
          </div>

          <div class="items">
            ${transaction.items
              .map(
                (item) => `
              <div class="item">
                <span>${item.item_name} x${item.quantity}</span>
                <span>${formatCurrency(item.price * item.quantity)}</span>
              </div>
            `
              )
              .join("")}
          </div>

          <div class="totals">
            <div class="total-line">
              <span>Subtotal:</span>
              <span>${formatCurrency(transaction.subtotal)}</span>
            </div>
            ${
              transaction.discount_total > 0
                ? `
            <div class="total-line">
              <span>Discount:</span>
              <span>-${formatCurrency(transaction.discount_total)}</span>
            </div>
            `
                : ""
            }
            ${
              transaction.tax > 0
                ? `
            <div class="total-line">
              <span>Tax:</span>
              <span>${formatCurrency(transaction.tax)}</span>
            </div>
            `
                : ""
            }
            ${
              transaction.tip > 0
                ? `
            <div class="total-line">
              <span>Tip:</span>
              <span>${formatCurrency(transaction.tip)}</span>
            </div>
            `
                : ""
            }
            <div class="total-line grand">
              <span>TOTAL:</span>
              <span>${formatCurrency(transaction.total)}</span>
            </div>
          </div>

          <div class="payments">
            <p style="margin: 10px 0 5px 0; font-weight: bold;">Payment Methods:</p>
            ${transaction.payments
              .map(
                (payment) => `
              <div class="total-line">
                <span style="text-transform: capitalize;">${
                  payment.method === "gift_card" ? "Gift Card" : payment.method
                }${payment.method === "gift_card" && payment.reference ? ` (${payment.reference.substring(0, 15)}...)` : ""}</span>
                <span>${formatCurrency(payment.amount)}</span>
              </div>
            `
              )
              .join("")}
            ${
              transaction.gift_card_redemptions && transaction.gift_card_redemptions.length > 0
                ? `
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px dashed #000;">
              <p style="margin: 5px 0; font-weight: bold; font-size: 11px;">Gift Card Balances:</p>
              ${transaction.gift_card_redemptions.map(redemption => `
              <div class="total-line" style="font-size: 10px;">
                <span>${redemption.card_number.substring(0, 15)}...</span>
                <span>Remaining: ${formatCurrency(redemption.remaining_balance)}</span>
              </div>
              `).join("")}
            </div>
            `
                : ""
            }
            ${
              transaction.payments.reduce((sum, p) => sum + p.amount, 0) >
              transaction.total
                ? `
            <div class="total-line" style="margin-top: 5px; color: #0066cc;">
              <span>Change:</span>
              <span>${formatCurrency(
                transaction.payments.reduce((sum, p) => sum + p.amount, 0) -
                  transaction.total
              )}</span>
            </div>
            `
                : ""
            }
          </div>

          <div class="footer">
            <p>Thank you for your business!</p>
            <p style="margin-top: 10px; font-weight: bold;">Powered by Kenikool Salon</p>
          </div>
        </body>
      </html>
    `;

    printWindow.document.write(receiptHTML);
    printWindow.document.close();
    printWindow.focus();

    // Wait for content to load then print
    setTimeout(() => {
      printWindow.print();
      printWindow.close();
    }, 250);
  };

  const handleEmailReceipt = async () => {
    if (!email) {
      toast.error("Please enter an email address");
      return;
    }

    try {
      await generateReceipt.mutateAsync({
        transaction_id: transaction.id,
        email,
      });
      setEmailSent(true);
      toast.success("Receipt sent successfully!");
      setTimeout(() => {
        setEmailSent(false);
        setEmail("");
      }, 3000);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to send receipt");
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CheckCircleIcon className="h-5 w-5 text-[var(--primary)]" />
            Payment Successful
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Receipt Preview */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-center text-lg">Receipt</CardTitle>
              <p className="text-center text-sm text-muted-foreground">
                {transaction.transaction_number}
              </p>
              <p className="text-center text-xs text-muted-foreground">
                {formatDate(transaction.created_at)}
              </p>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Items */}
              <div className="space-y-2">
                {transaction.items.map((item, index) => (
                  <div key={index} className="flex justify-between text-sm">
                    <div>
                      <span>{item.item_name}</span>
                      <span className="text-muted-foreground">
                        {" "}
                        x{item.quantity}
                      </span>
                    </div>
                    <span>{formatCurrency(item.price * item.quantity)}</span>
                  </div>
                ))}
              </div>

              {/* Totals */}
              <div className="space-y-1 pt-2 border-t">
                <div className="flex justify-between text-sm">
                  <span>Subtotal:</span>
                  <span>{formatCurrency(transaction.subtotal)}</span>
                </div>
                {transaction.discount_total > 0 && (
                  <div className="flex justify-between text-sm text-[var(--primary)]">
                    <span>Discount:</span>
                    <span>-{formatCurrency(transaction.discount_total)}</span>
                  </div>
                )}
                {transaction.tax > 0 && (
                  <div className="flex justify-between text-sm">
                    <span>Tax:</span>
                    <span>{formatCurrency(transaction.tax)}</span>
                  </div>
                )}
                {transaction.tip > 0 && (
                  <div className="flex justify-between text-sm">
                    <span>Tip:</span>
                    <span>{formatCurrency(transaction.tip)}</span>
                  </div>
                )}
                <div className="flex justify-between font-bold pt-2 border-t">
                  <span>Total:</span>
                  <span>{formatCurrency(transaction.total)}</span>
                </div>
              </div>

              {/* Payments */}
              <div className="space-y-1 pt-2 border-t">
                <p className="text-sm font-medium">Payment Methods:</p>
                {transaction.payments.map((payment, index) => (
                  <div key={index} className="flex justify-between text-sm">
                    <span className="capitalize">
                      {payment.method === "gift_card" ? "Gift Card" : payment.method}
                      {payment.method === "gift_card" && payment.reference && (
                        <span className="text-xs text-muted-foreground ml-1">
                          ({payment.reference.substring(0, 15)}...)
                        </span>
                      )}
                    </span>
                    <span>{formatCurrency(payment.amount)}</span>
                  </div>
                ))}
              </div>

              {/* Gift Card Remaining Balances */}
              {transaction.gift_card_redemptions && transaction.gift_card_redemptions.length > 0 && (
                <div className="space-y-1 pt-2 border-t">
                  <p className="text-sm font-medium">Gift Card Balances:</p>
                  {transaction.gift_card_redemptions.map((redemption, index) => (
                    <div key={index} className="flex justify-between text-xs">
                      <span className="text-muted-foreground">
                        {redemption.card_number.substring(0, 15)}...
                      </span>
                      <span className="font-medium">
                        Remaining: {formatCurrency(redemption.remaining_balance)}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* Change */}
              {transaction.payments.reduce((sum, p) => sum + p.amount, 0) >
                transaction.total && (
                <div className="flex justify-between text-sm font-medium text-[var(--primary)] pt-2 border-t">
                  <span>Change:</span>
                  <span>
                    {formatCurrency(
                      transaction.payments.reduce(
                        (sum, p) => sum + p.amount,
                        0
                      ) - transaction.total
                    )}
                  </span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Email Receipt */}
          <div className="space-y-2">
            <Label htmlFor="email-receipt">Email Receipt (Optional)</Label>
            <div className="flex gap-2">
              <Input
                id="email-receipt"
                type="email"
                placeholder="customer@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={emailSent}
              />
              <Button
                onClick={handleEmailReceipt}
                disabled={!email || emailSent || generateReceipt.isPending}
                variant="outline"
              >
                {generateReceipt.isPending ? (
                  "Sending..."
                ) : emailSent ? (
                  <CheckCircleIcon className="h-4 w-4" />
                ) : (
                  <MailIcon className="h-4 w-4" />
                )}
              </Button>
            </div>
            {emailSent && (
              <p className="text-sm text-[var(--primary)]">
                Receipt sent successfully!
              </p>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <Button onClick={handlePrint} variant="outline" className="flex-1">
              <PrinterIcon className="h-4 w-4 mr-2" />
              Print
            </Button>
            <Button onClick={onClose} className="flex-1">
              New Transaction
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

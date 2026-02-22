import {
  useReceipt,
  usePrintReceipt,
  useEmailReceipt,
} from "@/hooks/useReceipt";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";
import { useState } from "react";

interface ReceiptDisplayProps {
  transactionId: string;
}

export default function ReceiptDisplay({ transactionId }: ReceiptDisplayProps) {
  const [email, setEmail] = useState("");
  const { data: receipt, isLoading } = useReceipt(transactionId);
  const { mutate: printReceipt, isPending: isPrinting } = usePrintReceipt();
  const { mutate: emailReceipt, isPending: isEmailing } = useEmailReceipt();
  const { showToast } = useToast();

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <Spinner />
      </div>
    );
  }

  if (!receipt) {
    return (
      <Card className="p-6 text-center">
        <p className="text-muted-foreground">Receipt not found</p>
      </Card>
    );
  }

  const handlePrint = () => {
    printReceipt(
      {
        receiptId: receipt.id,
        printerName: "default",
      },
      {
        onSuccess: () => {
          showToast({
            title: "Success",
            description: "Receipt sent to printer",
            variant: "success",
          });
        },
        onError: () => {
          showToast({
            title: "Error",
            description: "Failed to print receipt",
            variant: "error",
          });
        },
      },
    );
  };

  const handleEmail = () => {
    if (!email) {
      showToast({
        title: "Email Required",
        description: "Please enter an email address",
        variant: "error",
      });
      return;
    }
    emailReceipt(
      {
        receiptId: receipt.id,
        email,
      },
      {
        onSuccess: () => {
          showToast({
            title: "Success",
            description: `Receipt sent to ${email}`,
            variant: "success",
          });
          setEmail("");
        },
        onError: () => {
          showToast({
            title: "Error",
            description: "Failed to email receipt",
            variant: "error",
          });
        },
      },
    );
  };

  return (
    <Card className="p-4 md:p-6 w-full max-w-full md:max-w-2xl mx-auto">
      <div className="space-y-4 md:space-y-6">
        {/* Receipt Header */}
        <div className="text-center border-b border-border pb-3 md:pb-4">
          <p className="text-xs md:text-sm text-muted-foreground">
            Receipt #{receipt.receiptNumber}
          </p>
          <p className="text-xs text-muted-foreground">
            {new Date(receipt.receiptDate).toLocaleString("en-NG", {
              year: "numeric",
              month: "short",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </p>
        </div>

        {/* Customer Info */}
        <div className="space-y-1 md:space-y-2">
          <p className="font-medium text-sm md:text-base text-foreground">
            {receipt.customerName}
          </p>
          {receipt.customerEmail && (
            <p className="text-xs md:text-sm text-muted-foreground">
              {receipt.customerEmail}
            </p>
          )}
          {receipt.customerPhone && (
            <p className="text-xs md:text-sm text-muted-foreground">
              {receipt.customerPhone}
            </p>
          )}
        </div>

        {/* Items */}
        <div className="border-t border-b border-border py-3 md:py-4">
          <div className="space-y-2">
            {receipt.items.map((item, idx) => (
              <div
                key={idx}
                className="flex justify-between text-xs md:text-sm gap-2"
              >
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-foreground truncate">
                    {item.itemName}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {item.quantity} × ₦
                    {item.unitPrice.toLocaleString("en-NG", {
                      maximumFractionDigits: 2,
                    })}
                  </p>
                </div>
                <p className="font-medium text-foreground flex-shrink-0">
                  ₦
                  {item.lineTotal.toLocaleString("en-NG", {
                    maximumFractionDigits: 2,
                  })}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Totals */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs md:text-sm">
            <span className="text-muted-foreground">Subtotal</span>
            <span className="font-medium text-foreground">
              ₦
              {receipt.subtotal.toLocaleString("en-NG", {
                maximumFractionDigits: 2,
              })}
            </span>
          </div>
          <div className="flex justify-between text-xs md:text-sm">
            <span className="text-muted-foreground">Tax</span>
            <span className="font-medium text-foreground">
              ₦
              {receipt.taxAmount.toLocaleString("en-NG", {
                maximumFractionDigits: 2,
              })}
            </span>
          </div>
          {receipt.discountAmount > 0 && (
            <div className="flex justify-between text-xs md:text-sm">
              <span className="text-muted-foreground">Discount</span>
              <span className="font-medium text-destructive">
                -₦
                {receipt.discountAmount.toLocaleString("en-NG", {
                  maximumFractionDigits: 2,
                })}
              </span>
            </div>
          )}
          <div className="border-t border-border pt-2 flex justify-between">
            <span className="font-semibold text-foreground text-sm md:text-base">
              Total
            </span>
            <span className="text-lg md:text-xl font-bold text-primary">
              ₦
              {receipt.total.toLocaleString("en-NG", {
                maximumFractionDigits: 2,
              })}
            </span>
          </div>
        </div>

        {/* Payment Info */}
        <div className="bg-muted p-2 md:p-3 rounded-lg">
          <p className="text-xs md:text-sm text-muted-foreground">
            Payment Method
          </p>
          <p className="font-medium text-foreground capitalize text-sm md:text-base">
            {receipt.paymentMethod}
          </p>
        </div>

        {/* Actions */}
        <div className="space-y-2 md:space-y-3">
          <div className="flex gap-2 flex-col sm:flex-row">
            <Button
              variant="outline"
              onClick={handlePrint}
              disabled={isPrinting}
              className="flex-1 text-sm md:text-base"
            >
              {isPrinting ? <Spinner className="w-4 h-4" /> : "Print"}
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                const element = document.createElement("a");
                element.href = `/receipts/${receipt.id}/pdf`;
                element.download = `receipt-${receipt.receiptNumber}.pdf`;
                element.click();
                showToast({
                  title: "Download Started",
                  description: "Receipt PDF is downloading",
                  variant: "default",
                });
              }}
              className="flex-1 text-sm md:text-base"
            >
              Download PDF
            </Button>
          </div>

          <div className="flex gap-2 flex-col sm:flex-row">
            <Input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="text-sm"
            />
            <Button
              onClick={handleEmail}
              disabled={isEmailing}
              className="flex-1 text-sm md:text-base"
            >
              {isEmailing ? <Spinner className="w-4 h-4" /> : "Email"}
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
}

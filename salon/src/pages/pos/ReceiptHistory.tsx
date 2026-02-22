import { useState } from "react";
import {
  useReceipts,
  usePrintReceipt,
  useEmailReceipt,
  useDownloadReceiptPDF,
} from "@/hooks/useReceipt";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";

export default function ReceiptHistory() {
  const [page, setPage] = useState(1);
  const [customerId, setCustomerId] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("");
  const [selectedReceiptId, setSelectedReceiptId] = useState<string | null>(
    null,
  );
  const [emailAddress, setEmailAddress] = useState("");

  const { data: receiptsData, isLoading } = useReceipts({
    customerId: customerId || undefined,
    page,
    pageSize: 20,
  });
  const printReceipt = usePrintReceipt();
  const emailReceipt = useEmailReceipt();
  const downloadPDF = useDownloadReceiptPDF();
  const { showToast } = useToast();

  const receipts = receiptsData?.receipts || [];
  const total = receiptsData?.total || 0;

  const handlePrint = async (receiptId: string) => {
    try {
      await printReceipt.mutateAsync({
        receiptId,
      });
      showToast({
        title: "Success",
        description: "Receipt sent to printer",
        variant: "success",
      });
    } catch (error) {
      showToast({
        title: "Error",
        description: "Failed to print receipt",
        variant: "error",
      });
    }
  };

  const handleEmail = async (receiptId: string) => {
    if (!emailAddress) {
      showToast({
        title: "Error",
        description: "Please enter an email address",
        variant: "error",
      });
      return;
    }

    try {
      await emailReceipt.mutateAsync({
        receiptId,
        email: emailAddress,
      });
      showToast({
        title: "Success",
        description: "Receipt sent to email",
        variant: "success",
      });
      setEmailAddress("");
    } catch (error) {
      showToast({
        title: "Error",
        description: "Failed to email receipt",
        variant: "error",
      });
    }
  };

  const handleDownloadPDF = async (receiptId: string) => {
    try {
      const blob = await downloadPDF.mutateAsync(receiptId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `receipt-${receiptId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      showToast({
        title: "Success",
        description: "Receipt downloaded",
        variant: "success",
      });
    } catch (error) {
      showToast({
        title: "Error",
        description: "Failed to download receipt",
        variant: "error",
      });
    }
  };

  const filteredReceipts = receipts.filter((receipt) => {
    if (startDate && new Date(receipt.receiptDate) < new Date(startDate))
      return false;
    if (endDate && new Date(receipt.receiptDate) > new Date(endDate))
      return false;
    if (paymentMethod && receipt.paymentMethod !== paymentMethod) return false;
    return true;
  });

  const selectedReceipt = receipts.find((r) => r.id === selectedReceiptId);

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Filters */}
      <Card className="p-4 md:p-6">
        <h3 className="text-base md:text-lg font-semibold text-foreground mb-4">
          Filters
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
          <div>
            <label className="block text-xs md:text-sm font-medium text-foreground mb-2">
              Customer ID
            </label>
            <Input
              type="text"
              value={customerId}
              onChange={(e) => {
                setCustomerId(e.target.value);
                setPage(1);
              }}
              placeholder="Filter by customer"
              className="text-sm"
            />
          </div>
          <div>
            <label className="block text-xs md:text-sm font-medium text-foreground mb-2">
              Start Date
            </label>
            <Input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="text-sm"
            />
          </div>
          <div>
            <label className="block text-xs md:text-sm font-medium text-foreground mb-2">
              End Date
            </label>
            <Input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="text-sm"
            />
          </div>
          <div>
            <label className="block text-xs md:text-sm font-medium text-foreground mb-2">
              Payment Method
            </label>
            <select
              value={paymentMethod}
              onChange={(e) => setPaymentMethod(e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm"
            >
              <option value="">All Methods</option>
              <option value="cash">Cash</option>
              <option value="card">Card</option>
              <option value="transfer">Transfer</option>
              <option value="mobile_money">Mobile Money</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Receipts List */}
      <Card className="p-4 md:p-6">
        <h3 className="text-base md:text-lg font-semibold text-foreground mb-4">
          Receipts
        </h3>
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : filteredReceipts.length === 0 ? (
          <p className="text-muted-foreground text-center py-8">
            No receipts found
          </p>
        ) : (
          <div className="space-y-2 md:space-y-3">
            {filteredReceipts.map((receipt) => (
              <div
                key={receipt.id}
                className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-2 p-3 md:p-4 bg-muted rounded-lg cursor-pointer hover:bg-muted/80 transition"
                onClick={() => setSelectedReceiptId(receipt.id)}
              >
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm md:text-base text-foreground truncate">
                    Receipt #{receipt.receiptNumber}
                  </p>
                  <p className="text-xs md:text-sm text-muted-foreground truncate">
                    {receipt.customerName} •{" "}
                    {new Date(receipt.receiptDate).toLocaleString("en-NG", {
                      year: "numeric",
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                  <div className="flex gap-2 mt-2 flex-wrap">
                    <Badge variant="secondary" className="capitalize text-xs">
                      {receipt.paymentMethod}
                    </Badge>
                    {receipt.printedAt && (
                      <Badge variant="outline" className="text-xs">
                        Printed
                      </Badge>
                    )}
                    {receipt.emailedAt && (
                      <Badge variant="outline" className="text-xs">
                        Emailed
                      </Badge>
                    )}
                  </div>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="font-bold text-sm md:text-base text-foreground">
                    ₦
                    {receipt.total.toLocaleString("en-NG", {
                      maximumFractionDigits: 2,
                    })}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {total > 20 && (
          <div className="flex justify-between items-center mt-6 pt-6 border-t border-border gap-2 flex-wrap">
            <Button
              variant="outline"
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="text-sm"
            >
              Previous
            </Button>
            <span className="text-xs md:text-sm text-muted-foreground">
              Page {page} of {Math.ceil(total / 20)}
            </span>
            <Button
              variant="outline"
              onClick={() => setPage(page + 1)}
              disabled={page >= Math.ceil(total / 20)}
              className="text-sm"
            >
              Next
            </Button>
          </div>
        )}
      </Card>

      {/* Receipt Details */}
      {selectedReceipt && (
        <Card className="p-4 md:p-6">
          <div className="flex justify-between items-start mb-4 md:mb-6 gap-2">
            <div className="flex-1 min-w-0">
              <h3 className="text-base md:text-lg font-semibold text-foreground truncate">
                Receipt #{selectedReceipt.receiptNumber}
              </h3>
              <p className="text-xs md:text-sm text-muted-foreground">
                {new Date(selectedReceipt.receiptDate).toLocaleString()}
              </p>
            </div>
            <Button
              variant="ghost"
              onClick={() => setSelectedReceiptId(null)}
              className="flex-shrink-0"
            >
              ✕
            </Button>
          </div>

          {/* Customer Info */}
          <div className="mb-4 md:mb-6 pb-4 md:pb-6 border-b border-border">
            <p className="font-medium text-sm md:text-base text-foreground">
              {selectedReceipt.customerName}
            </p>
            {selectedReceipt.customerEmail && (
              <p className="text-xs md:text-sm text-muted-foreground">
                {selectedReceipt.customerEmail}
              </p>
            )}
            {selectedReceipt.customerPhone && (
              <p className="text-xs md:text-sm text-muted-foreground">
                {selectedReceipt.customerPhone}
              </p>
            )}
          </div>

          {/* Items */}
          <div className="mb-4 md:mb-6">
            <h4 className="font-medium text-sm md:text-base text-foreground mb-3">
              Items
            </h4>
            <div className="space-y-2">
              {selectedReceipt.items.map((item, idx) => (
                <div
                  key={idx}
                  className="flex justify-between text-xs md:text-sm gap-2"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-foreground truncate">{item.itemName}</p>
                    <p className="text-muted-foreground">
                      {item.quantity} × ₦
                      {item.unitPrice.toLocaleString("en-NG", {
                        maximumFractionDigits: 2,
                      })}
                    </p>
                  </div>
                  <p className="text-foreground font-medium flex-shrink-0">
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
          <div className="mb-4 md:mb-6 pb-4 md:pb-6 border-b border-border space-y-2">
            <div className="flex justify-between text-xs md:text-sm">
              <span className="text-muted-foreground">Subtotal</span>
              <span className="text-foreground">
                ₦
                {selectedReceipt.subtotal.toLocaleString("en-NG", {
                  maximumFractionDigits: 2,
                })}
              </span>
            </div>
            {selectedReceipt.discountAmount > 0 && (
              <div className="flex justify-between text-xs md:text-sm">
                <span className="text-muted-foreground">Discount</span>
                <span className="text-foreground">
                  -₦
                  {selectedReceipt.discountAmount.toLocaleString("en-NG", {
                    maximumFractionDigits: 2,
                  })}
                </span>
              </div>
            )}
            {selectedReceipt.taxAmount > 0 && (
              <div className="flex justify-between text-xs md:text-sm">
                <span className="text-muted-foreground">Tax</span>
                <span className="text-foreground">
                  ₦
                  {selectedReceipt.taxAmount.toLocaleString("en-NG", {
                    maximumFractionDigits: 2,
                  })}
                </span>
              </div>
            )}
            <div className="flex justify-between font-bold text-sm md:text-base">
              <span className="text-foreground">Total</span>
              <span className="text-foreground">
                ₦
                {selectedReceipt.total.toLocaleString("en-NG", {
                  maximumFractionDigits: 2,
                })}
              </span>
            </div>
          </div>

          {/* Actions */}
          <div className="space-y-2 md:space-y-3">
            <div className="flex gap-2 flex-col sm:flex-row">
              <Button
                onClick={() => handlePrint(selectedReceipt.id)}
                disabled={printReceipt.isPending}
                className="flex-1 text-sm md:text-base"
              >
                {printReceipt.isPending ? "Printing..." : "Print Receipt"}
              </Button>
              <Button
                onClick={() => handleDownloadPDF(selectedReceipt.id)}
                disabled={downloadPDF.isPending}
                variant="outline"
                className="flex-1 text-sm md:text-base"
              >
                {downloadPDF.isPending ? "Downloading..." : "Download PDF"}
              </Button>
            </div>
            <div className="flex gap-2 flex-col sm:flex-row">
              <Input
                type="email"
                value={emailAddress}
                onChange={(e) => setEmailAddress(e.target.value)}
                placeholder="Email address"
                className="flex-1 text-sm"
              />
              <Button
                onClick={() => handleEmail(selectedReceipt.id)}
                disabled={emailReceipt.isPending}
                className="flex-1 text-sm md:text-base"
              >
                {emailReceipt.isPending ? "Sending..." : "Email"}
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}

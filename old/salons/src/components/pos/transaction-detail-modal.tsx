import {
  useGetTransaction,
  useGenerateReceipt,
  useUpdateTransactionNotes,
  POSCartItem,
  POSPaymentMethod,
} from "@/lib/api/hooks/usePOS";
import { useStylists } from "@/lib/api/hooks/useStylists";
import { useClients } from "@/lib/api/hooks/useClients";
import { Client, Stylist } from "@/lib/api/types";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { RefundModal } from "./refund-modal";
import { VoidModal } from "./void-modal";
import { ReturnModal } from "./return-modal";
import {
  PrinterIcon,
  MailIcon,
  RefreshCcwIcon,
  XIcon,
  XCircleIcon,
  EditIcon,
  CheckIcon,
} from "@/components/icons";
import { format } from "date-fns";
import { useState } from "react";
import { toast } from "sonner";

interface TransactionDetailModalProps {
  transactionId: string | null;
  open: boolean;
  onClose: () => void;
}

export function TransactionDetailModal({
  transactionId,
  open,
  onClose,
}: TransactionDetailModalProps) {
  const [email, setEmail] = useState("");
  const [showEmailInput, setShowEmailInput] = useState(false);
  const [showRefundModal, setShowRefundModal] = useState(false);
  const [showVoidModal, setShowVoidModal] = useState(false);
  const [showReturnModal, setShowReturnModal] = useState(false);
  const [isEditingNotes, setIsEditingNotes] = useState(false);
  const [editedNotes, setEditedNotes] = useState("");

  const { data: transaction, isLoading } = useGetTransaction(transactionId);
  const { data: stylistsData } = useStylists();
  const stylists = Array.isArray(stylistsData) ? stylistsData : [];
  const { data: clientsData } = useClients();
  const clients = clientsData?.items || [];
  const generateReceipt = useGenerateReceipt();
  const updateNotes = useUpdateTransactionNotes();

  if (!transaction) return null;

  const client = transaction.client_id
    ? clients.find((c: Client) => c.id === transaction.client_id)
    : null;
  const stylist = transaction.stylist_id
    ? stylists.find((s: Stylist) => s.id === transaction.stylist_id)
    : null;

  const getStatusBadge = (status: string) => {
    const variants: Record<
      string,
      "default" | "secondary" | "destructive" | "outline"
    > = {
      pending: "secondary",
      completed: "default",
      refunded: "destructive",
      partially_refunded: "outline",
      voided: "destructive",
    };
    const labels: Record<string, string> = {
      pending: "PENDING",
      completed: "COMPLETED",
      refunded: "REFUNDED",
      partially_refunded: "PARTIALLY REFUNDED",
      voided: "VOIDED",
    };
    return (
      <Badge variant={variants[status] || "default"}>
        {labels[status] || status.toUpperCase()}
      </Badge>
    );
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
      toast.success(`Receipt sent to ${email}`);
      setEmail("");
      setShowEmailInput(false);
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Failed to send receipt");
    }
  };

  const handlePrintReceipt = () => {
    // TODO: Implement print functionality
    toast.info("Print functionality coming soon");
  };

  const handleEditNotes = () => {
    setEditedNotes(transaction?.notes || "");
    setIsEditingNotes(true);
  };

  const handleSaveNotes = async () => {
    if (!transaction) return;

    try {
      await updateNotes.mutateAsync({
        transaction_id: transaction.id,
        notes: editedNotes,
      });
      toast.success("Notes updated successfully");
      setIsEditingNotes(false);
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Failed to update notes");
    }
  };

  const handleCancelEditNotes = () => {
    setIsEditingNotes(false);
    setEditedNotes("");
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Transaction Details</span>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <XIcon className="h-4 w-4" />
            </Button>
          </DialogTitle>
        </DialogHeader>

        {isLoading ? (
          <div className="text-center py-8">Loading...</div>
        ) : (
          <div className="space-y-6">
            {/* Transaction Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Transaction #</p>
                <p className="font-medium">{transaction.transaction_number}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Date</p>
                <p className="font-medium">
                  {format(
                    new Date(transaction.created_at),
                    "MMM dd, yyyy HH:mm"
                  )}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Client</p>
                <p className="font-medium">
                  {client?.name || "Walk-in Customer"}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Stylist</p>
                <p className="font-medium">{stylist?.name || "None"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Status</p>
                <div className="mt-1">{getStatusBadge(transaction.status)}</div>
              </div>
            </div>

            <Separator />

            {/* Items */}
            <div>
              <h3 className="font-semibold mb-3">Items</h3>
              <div className="space-y-2">
                {transaction.items.map((item: POSCartItem, index: number) => (
                  <div
                    key={index}
                    className="flex justify-between items-center p-3 bg-muted rounded-lg"
                  >
                    <div>
                      <p className="font-medium">{item.item_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {item.type === "service" ? "Service" : "Product"} • Qty:{" "}
                        {item.quantity}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">
                        {formatCurrency(item.price * item.quantity)}
                      </p>
                      {item.discount && item.discount > 0 && (
                        <p className="text-sm text-destructive">
                          -{formatCurrency(item.discount)}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <Separator />

            {/* Totals */}
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Subtotal</span>
                <span>{formatCurrency(transaction.subtotal)}</span>
              </div>
              {transaction.discount_total > 0 && (
                <div className="flex justify-between text-destructive">
                  <span>Discount</span>
                  <span>-{formatCurrency(transaction.discount_total)}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-muted-foreground">Tax</span>
                <span>{formatCurrency(transaction.tax)}</span>
              </div>
              {transaction.tip > 0 && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Tip</span>
                  <span>{formatCurrency(transaction.tip)}</span>
                </div>
              )}
              <Separator />
              <div className="flex justify-between text-lg font-bold">
                <span>Total</span>
                <span>{formatCurrency(transaction.total)}</span>
              </div>
            </div>

            {/* Payments */}
            {transaction.payments && transaction.payments.length > 0 && (
              <>
                <Separator />
                <div>
                  <h3 className="font-semibold mb-3">Payments</h3>
                  <div className="space-y-2">
                    {transaction.payments.map(
                      (payment: POSPaymentMethod, index: number) => (
                        <div
                          key={index}
                          className="flex justify-between items-center p-3 bg-muted rounded-lg"
                        >
                          <div>
                            <p className="font-medium capitalize">
                              {payment.method}
                            </p>
                            {payment.reference && (
                              <p className="text-sm text-muted-foreground">
                                Ref: {payment.reference}
                              </p>
                            )}
                          </div>
                          <p className="font-medium">
                            {formatCurrency(payment.amount)}
                          </p>
                        </div>
                      )
                    )}
                  </div>
                </div>
              </>
            )}

            {/* Notes */}
            {(transaction.notes || isEditingNotes) && (
              <>
                <Separator />
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold">Notes</h3>
                    {!isEditingNotes && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleEditNotes}
                      >
                        <EditIcon className="h-4 w-4 mr-1" />
                        Edit
                      </Button>
                    )}
                  </div>
                  {isEditingNotes ? (
                    <div className="space-y-2">
                      <Textarea
                        value={editedNotes}
                        onChange={(e) => setEditedNotes(e.target.value)}
                        placeholder="Add notes about this transaction..."
                        className="min-h-[80px]"
                        maxLength={500}
                      />
                      <div className="flex justify-between items-center">
                        <p className="text-xs text-muted-foreground">
                          {editedNotes.length}/500
                        </p>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={handleCancelEditNotes}
                          >
                            Cancel
                          </Button>
                          <Button
                            size="sm"
                            onClick={handleSaveNotes}
                            disabled={updateNotes.isPending}
                          >
                            <CheckIcon className="h-4 w-4 mr-1" />
                            {updateNotes.isPending ? "Saving..." : "Save"}
                          </Button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      {transaction.notes}
                    </p>
                  )}
                </div>
              </>
            )}

            {/* Add Notes Button if no notes exist */}
            {!transaction.notes && !isEditingNotes && (
              <>
                <Separator />
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={handleEditNotes}
                >
                  <EditIcon className="h-4 w-4 mr-2" />
                  Add Notes
                </Button>
              </>
            )}

            {/* Refund Info */}
            {(transaction.status === "refunded" ||
              transaction.status === "partially_refunded") &&
              transaction.refund_amount && (
                <>
                  <Separator />
                  <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                    <h3 className="font-semibold mb-2 text-destructive">
                      Refund Information
                    </h3>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">
                          Refund Amount:
                        </span>
                        <span className="font-medium">
                          {formatCurrency(transaction.refund_amount)}
                        </span>
                      </div>
                      {transaction.refund_reason && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Reason:</span>
                          <span className="font-medium">
                            {transaction.refund_reason}
                          </span>
                        </div>
                      )}
                      {transaction.refunded_at && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">
                            Refunded At:
                          </span>
                          <span className="font-medium">
                            {format(
                              new Date(transaction.refunded_at),
                              "MMM dd, yyyy HH:mm"
                            )}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </>
              )}

            {/* Void Info */}
            {transaction.status === "voided" && transaction.void_reason && (
              <>
                <Separator />
                <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                  <h3 className="font-semibold mb-2 text-destructive">
                    Void Information
                  </h3>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Reason:</span>
                      <span className="font-medium">
                        {transaction.void_reason}
                      </span>
                    </div>
                    {transaction.voided_at && (
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">
                          Voided At:
                        </span>
                        <span className="font-medium">
                          {format(
                            new Date(transaction.voided_at),
                            "MMM dd, yyyy HH:mm"
                          )}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </>
            )}

            <Separator />

            {/* Actions */}
            <div className="space-y-3">
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={handlePrintReceipt}
                >
                  <PrinterIcon className="h-4 w-4 mr-2" />
                  Print Receipt
                </Button>
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowEmailInput(!showEmailInput)}
                >
                  <MailIcon className="h-4 w-4 mr-2" />
                  Email Receipt
                </Button>
              </div>

              {showEmailInput && (
                <div className="space-y-2">
                  <Label>Email Address</Label>
                  <div className="flex gap-2">
                    <Input
                      type="email"
                      placeholder="customer@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                    <Button
                      onClick={handleEmailReceipt}
                      disabled={generateReceipt.isPending}
                    >
                      {generateReceipt.isPending ? "Sending..." : "Send"}
                    </Button>
                  </div>
                </div>
              )}

              {transaction.status === "pending" && (
                <Button
                  variant="destructive"
                  className="w-full"
                  onClick={() => setShowVoidModal(true)}
                >
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  Void Transaction
                </Button>
              )}

              {transaction.status === "completed" && (
                <div className="flex gap-2">
                  <Button
                    variant="destructive"
                    className="flex-1"
                    onClick={() => setShowRefundModal(true)}
                  >
                    <RefreshCcwIcon className="h-4 w-4 mr-2" />
                    Refund
                  </Button>
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => setShowReturnModal(true)}
                  >
                    <RefreshCcwIcon className="h-4 w-4 mr-2" />
                    Return/Exchange
                  </Button>
                </div>
              )}

              {transaction.status === "partially_refunded" && (
                <div className="p-3 bg-muted rounded-lg text-sm text-center">
                  <p className="text-muted-foreground">
                    This transaction has been partially refunded
                  </p>
                </div>
              )}

              {transaction.status === "refunded" && (
                <div className="p-3 bg-destructive/10 rounded-lg text-sm text-center">
                  <p className="text-destructive font-medium">
                    This transaction has been fully refunded
                  </p>
                </div>
              )}

              {transaction.status === "voided" && (
                <div className="p-3 bg-destructive/10 rounded-lg text-sm text-center">
                  <p className="text-destructive font-medium">
                    This transaction has been voided
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Refund Modal */}
        <RefundModal
          transaction={transaction}
          open={showRefundModal}
          onClose={() => setShowRefundModal(false)}
        />

        {/* Void Modal */}
        <VoidModal
          transaction={transaction}
          open={showVoidModal}
          onClose={() => setShowVoidModal(false)}
        />

        {/* Return Modal */}
        <ReturnModal
          transaction={transaction}
          open={showReturnModal}
          onClose={() => setShowReturnModal(false)}
        />
      </DialogContent>
    </Dialog>
  );
}

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { CreditCardIcon, DollarSignIcon, Trash2Icon } from "@/components/icons";
import { PromoCodeInput } from "@/components/promo-codes";
import type { POSPaymentMethod } from "@/lib/api/hooks/usePOS";
import type { PromoCodeValidation } from "@/lib/api/hooks/usePromoCodes";
import { formatCurrency, CURRENCY_SYMBOL } from "@/lib/utils/currency";
import { useToast } from "@/hooks/use-toast";

interface POSPaymentProps {
  total: number;
  clientId?: string;
  serviceIds?: string[];
  onProcessPayment: (
    payments: POSPaymentMethod[],
    promoCodeId?: string,
  ) => void;
  isProcessing?: boolean;
  membershipDiscount?: number;
  membershipPlanName?: string;
}

export function POSPayment({
  total,
  clientId,
  serviceIds = [],
  onProcessPayment,
  isProcessing,
  membershipDiscount = 0,
  membershipPlanName,
}: POSPaymentProps) {
  const [payments, setPayments] = useState<POSPaymentMethod[]>([]);
  const [currentMethod, setCurrentMethod] = useState<
    "cash" | "card" | "transfer" | "gift_card"
  >("cash");
  const [currentAmount, setCurrentAmount] = useState<string>("");
  const [currentReference, setCurrentReference] = useState<string>("");
  const [appliedPromoCode, setAppliedPromoCode] =
    useState<PromoCodeValidation | null>(null);
  const [discountAmount, setDiscountAmount] = useState(0);
  const [giftCardNumber, setGiftCardNumber] = useState<string>("");
  const [giftCardBalance, setGiftCardBalance] = useState<number | null>(null);
  const [checkingGiftCard, setCheckingGiftCard] = useState(false);

  const totalPaid = payments.reduce((sum, p) => sum + p.amount, 0);
  const remaining = total - totalPaid - membershipDiscount - discountAmount;
  const change =
    totalPaid > total - membershipDiscount - discountAmount
      ? totalPaid - (total - membershipDiscount - discountAmount)
      : 0;

  const checkGiftCardBalance = async () => {
    if (!giftCardNumber) return;

    setCheckingGiftCard(true);
    try {
      const response = await fetch(
        `/api/public/gift-cards/balance?card_number=${giftCardNumber}`,
      );
      if (!response.ok) {
        showToast({
          title: "Error",
          description: "Gift card not found or invalid",
          variant: "destructive",
        });
        setGiftCardBalance(null);
        return;
      }
      const data = await response.json();
      if (data.status !== "active") {
        showToast({
          title: "Error",
          description: `Gift card is ${data.status}`,
          variant: "destructive",
        });
        setGiftCardBalance(null);
        return;
      }
      setGiftCardBalance(data.balance);
    } catch (error) {
      showToast({
        title: "Error",
        description: "Failed to check gift card balance",
        variant: "destructive",
      });
      setGiftCardBalance(null);
    } finally {
      setCheckingGiftCard(false);
    }
  };

  const addPayment = () => {
    const amount = parseFloat(currentAmount);
    if (isNaN(amount) || amount <= 0) return;

    // Validate gift card payment
    if (currentMethod === "gift_card") {
      if (!giftCardNumber) {
        showToast({
          title: "Validation Error",
          description: "Please enter gift card number",
          variant: "destructive",
        });
        return;
      }
      if (giftCardBalance === null) {
        showToast({
          title: "Validation Error",
          description: "Please check gift card balance first",
          variant: "destructive",
        });
        return;
      }
      if (amount > giftCardBalance) {
        showToast({
          title: "Validation Error",
          description: `Insufficient gift card balance. Available: ${formatCurrency(giftCardBalance)}`,
          variant: "destructive",
        });
        return;
      }
    }

    const newPayment: POSPaymentMethod = {
      method: currentMethod,
      amount,
      reference:
        currentMethod === "gift_card"
          ? giftCardNumber
          : currentReference || undefined,
    };

    setPayments([...payments, newPayment]);
    setCurrentAmount("");
    setCurrentReference("");

    // Reset gift card fields
    if (currentMethod === "gift_card") {
      setGiftCardNumber("");
      setGiftCardBalance(null);
    }
  };

  const removePayment = (index: number) => {
    setPayments(payments.filter((_, i) => i !== index));
  };

  const handleQuickAmount = (amount: number) => {
    setCurrentAmount(amount.toString());
  };

  const handleExactAmount = () => {
    setCurrentAmount(remaining.toFixed(2));
  };

  const handleProcessPayment = () => {
    if (totalPaid < total - discountAmount - membershipDiscount) {
      showToast({
        title: "Validation Error",
        description: "Insufficient payment amount",
        variant: "destructive",
      });
      return;
    }
    onProcessPayment(payments, appliedPromoCode?.promo_code_id);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Payment</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4 max-h-[70vh] overflow-y-auto overflow-x-hidden">
        {/* Promo Code Section */}
        {clientId && (
          <div className="space-y-3 p-4 bg-[var(--muted)] rounded-lg border border-[var(--border)]">
            <h3 className="text-sm font-semibold text-[var(--foreground)]">
              Apply Promo Code
            </h3>
            <PromoCodeInput
              clientId={clientId}
              serviceIds={serviceIds}
              totalAmount={total}
              onApply={(validation) => {
                setAppliedPromoCode(validation);
                setDiscountAmount(validation.discount_amount || 0);
              }}
              onClear={() => {
                setAppliedPromoCode(null);
                setDiscountAmount(0);
              }}
              appliedCode={appliedPromoCode}
            />
          </div>
        )}

        {/* Payment Summary */}
        <div className="space-y-2 p-4 bg-[var(--muted)] rounded-lg">
          <div className="flex justify-between text-sm">
            <span>Total Due:</span>
            <span className="font-bold break-all">{formatCurrency(total)}</span>
          </div>
          {membershipDiscount > 0 && (
            <div className="flex justify-between text-sm text-[var(--primary)]">
              <span>Member Discount:</span>
              <span className="font-bold break-all">
                -{formatCurrency(membershipDiscount)}
              </span>
            </div>
          )}
          {discountAmount > 0 && (
            <div className="flex justify-between text-sm text-[var(--primary)]">
              <span>Promo Discount:</span>
              <span className="font-bold break-all">
                -{formatCurrency(discountAmount)}
              </span>
            </div>
          )}
          <div className="flex justify-between text-sm border-t pt-2">
            <span>Amount Due:</span>
            <span className="font-bold break-all">
              {formatCurrency(total - discountAmount - membershipDiscount)}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span>Total Paid:</span>
            <span className="font-bold text-[var(--success)] break-all">
              {formatCurrency(totalPaid)}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span>Remaining:</span>
            <span
              className={`font-bold break-all ${
                remaining - discountAmount > 0
                  ? "text-[var(--destructive)]"
                  : "text-[var(--success)]"
              }`}
            >
              {formatCurrency(Math.max(0, remaining - discountAmount))}
            </span>
          </div>
          {change > 0 && (
            <div className="flex justify-between text-sm pt-2 border-t">
              <span>Change:</span>
              <span className="font-bold text-[var(--accent)] break-all">
                {formatCurrency(change)}
              </span>
            </div>
          )}
        </div>

        {/* Add Payment */}
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label htmlFor="payment-method">Payment Method</Label>
              <Select
                value={currentMethod}
                onValueChange={(value) =>
                  setCurrentMethod(value as "cash" | "card" | "transfer")
                }
              >
                <SelectTrigger id="payment-method">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cash">
                    <div className="flex items-center gap-2">
                      <DollarSignIcon className="h-4 w-4" />
                      Cash
                    </div>
                  </SelectItem>
                  <SelectItem value="card">
                    <div className="flex items-center gap-2">
                      <CreditCardIcon className="h-4 w-4" />
                      Card
                    </div>
                  </SelectItem>
                  <SelectItem value="transfer">
                    <div className="flex items-center gap-2">
                      <CreditCardIcon className="h-4 w-4" />
                      Transfer
                    </div>
                  </SelectItem>
                  <SelectItem value="gift_card">
                    <div className="flex items-center gap-2">
                      <CreditCardIcon className="h-4 w-4" />
                      Gift Card
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="payment-amount">Amount</Label>
              <Input
                id="payment-amount"
                type="number"
                min="0"
                step="0.01"
                value={currentAmount}
                onChange={(e) => setCurrentAmount(e.target.value)}
                placeholder="0.00"
              />
            </div>
          </div>

          {(currentMethod === "card" || currentMethod === "transfer") && (
            <div>
              <Label htmlFor="payment-reference">Reference (Optional)</Label>
              <Input
                id="payment-reference"
                value={currentReference}
                onChange={(e) => setCurrentReference(e.target.value)}
                placeholder="Transaction ID or reference"
              />
            </div>
          )}

          {currentMethod === "gift_card" && (
            <div className="space-y-3">
              <div>
                <Label htmlFor="gift-card-number">Gift Card Number</Label>
                <div className="flex gap-2">
                  <Input
                    id="gift-card-number"
                    value={giftCardNumber}
                    onChange={(e) => {
                      setGiftCardNumber(e.target.value);
                      setGiftCardBalance(null);
                    }}
                    placeholder="GC-XXXXXXXXXXXX"
                  />
                  <Button
                    type="button"
                    onClick={checkGiftCardBalance}
                    disabled={!giftCardNumber || checkingGiftCard}
                    variant="outline"
                  >
                    {checkingGiftCard ? "Checking..." : "Check"}
                  </Button>
                </div>
              </div>
              {giftCardBalance !== null && (
                <div className="p-3 bg-muted rounded-lg">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">
                      Available Balance:
                    </span>
                    <span className="text-lg font-bold text-primary">
                      {formatCurrency(giftCardBalance)}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Quick Amount Buttons */}
          <div className="flex gap-2 flex-wrap">
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="whitespace-nowrap"
              onClick={() => handleQuickAmount(1000)}
            >
              {CURRENCY_SYMBOL}1,000
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="whitespace-nowrap"
              onClick={() => handleQuickAmount(2000)}
            >
              {CURRENCY_SYMBOL}2,000
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="whitespace-nowrap"
              onClick={() => handleQuickAmount(5000)}
            >
              {CURRENCY_SYMBOL}5,000
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="whitespace-nowrap"
              onClick={() => handleQuickAmount(10000)}
            >
              {CURRENCY_SYMBOL}10,000
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="whitespace-nowrap"
              onClick={handleExactAmount}
            >
              Exact
            </Button>
          </div>

          <Button
            type="button"
            onClick={addPayment}
            className="w-full"
            disabled={!currentAmount || parseFloat(currentAmount) <= 0}
          >
            Add Payment
          </Button>
        </div>

        {/* Payment List */}
        {payments.length > 0 && (
          <div className="space-y-2">
            <Label>Payments Added:</Label>
            {payments.map((payment, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 border rounded"
              >
                <div className="flex items-center gap-2">
                  {payment.method === "cash" ? (
                    <DollarSignIcon className="h-4 w-4" />
                  ) : (
                    <CreditCardIcon className="h-4 w-4" />
                  )}
                  <span className="capitalize">
                    {payment.method === "gift_card"
                      ? "Gift Card"
                      : payment.method}
                  </span>
                  {payment.reference && (
                    <span className="text-xs text-muted-foreground">
                      (
                      {payment.method === "gift_card"
                        ? payment.reference.substring(0, 15) + "..."
                        : payment.reference}
                      )
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-medium">
                    {formatCurrency(payment.amount)}
                  </span>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6"
                    onClick={() => removePayment(index)}
                  >
                    <Trash2Icon className="h-3 w-3 text-destructive" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
      <CardFooter>
        <Button
          onClick={handleProcessPayment}
          disabled={
            totalPaid < total - discountAmount ||
            payments.length === 0 ||
            isProcessing
          }
          className="w-full"
          size="lg"
        >
          {isProcessing
            ? "Processing..."
            : `Complete Payment (${formatCurrency(total - discountAmount)})`}
        </Button>
      </CardFooter>
    </Card>
  );
}

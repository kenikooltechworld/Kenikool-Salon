import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  DollarIcon,
  CheckCircleIcon,
  AlertTriangleIcon,
  ArrowLeftIcon,
  CreditCardIcon,
} from "@/components/icons";
import { useCheckout } from "@/lib/api/hooks/usePayments";
import { useBookings } from "@/lib/api/hooks/useBookings";
import { apiClient } from "@/lib/api/client";
import type { PaymentMethod } from "@/lib/api/types";

type PaymentMethodType = "cash" | "card" | "transfer" | "gift_card";

export default function CheckoutPage() {
  const params = useParams();
  const navigate = useNavigate();
  const bookingId = params.bookingId as string;

  const { data: bookings, isLoading: loadingBooking } = useBookings({
    booking_id: bookingId,
  });
  const booking = bookings?.[0];

  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([
    { method: "cash", amount: 0 },
  ]);
  const [selectedGateway, setSelectedGateway] = useState<
    "paystack" | "flutterwave"
  >("paystack");
  const [giftCardNumber, setGiftCardNumber] = useState<string>("");
  const [giftCardBalance, setGiftCardBalance] = useState<number | null>(null);
  const [checkingGiftCard, setCheckingGiftCard] = useState(false);

  const checkoutMutation = useCheckout({
    onSuccess: () => {
      navigate(`/dashboard/bookings`);
    },
  });

  const totalAmount = booking?.service?.price || 0;
  const depositPaid = booking?.deposit_amount || 0;
  const remainingBalance = totalAmount - depositPaid;

  const totalPaymentAmount = paymentMethods.reduce(
    (sum, pm) => sum + pm.amount,
    0,
  );
  const balanceRemaining = remainingBalance - totalPaymentAmount;

  const checkGiftCardBalance = async () => {
    if (!giftCardNumber) return;

    setCheckingGiftCard(true);
    try {
      const response = await apiClient.get(`/api/public/gift-cards/balance`, {
        params: { card_number: giftCardNumber },
      });
      const data = response.data;
      if (data.status !== "active") {
        showToast(`Gift card is ${data.status}`, "warning");
        setGiftCardBalance(null);
        return;
      }
      setGiftCardBalance(data.balance);
    } catch (error) {
      showToast("Failed to check gift card balance", "error");
      setGiftCardBalance(null);
    } finally {
      setCheckingGiftCard(false);
    }
  };

  const addPaymentMethod = () => {
    setPaymentMethods([...paymentMethods, { method: "cash", amount: 0 }]);
  };

  const removePaymentMethod = (index: number) => {
    setPaymentMethods(paymentMethods.filter((_, i) => i !== index));
  };

  const updatePaymentMethod = (
    index: number,
    field: keyof PaymentMethod,
    value: any,
  ) => {
    const updated = [...paymentMethods];
    updated[index] = { ...updated[index], [field]: value };

    // Reset gift card balance when changing method or card number
    if (
      field === "method" ||
      (field === "gift_card_code" && updated[index].method === "gift_card")
    ) {
      setGiftCardBalance(null);
      if (field === "gift_card_code") {
        setGiftCardNumber(value);
      }
    }

    setPaymentMethods(updated);
  };

  const handleCheckout = () => {
    if (balanceRemaining !== 0) {
      showToast("Payment amount must equal the remaining balance", "warning");
      return;
    }

    // Validate gift card payments
    for (const pm of paymentMethods) {
      if (pm.method === "gift_card") {
        if (!pm.gift_card_code) {
          showToast("Please enter gift card number", "warning");
          return;
        }
        if (giftCardBalance === null) {
          showToast("Please check gift card balance first", "warning");
          return;
        }
        if (pm.amount > giftCardBalance) {
          showToast(
            `Insufficient gift card balance. Available: ₦${giftCardBalance.toLocaleString()}`,
            "warning",
          );
          return;
        }
      }
    }

    checkoutMutation.mutate({
      booking_id: bookingId,
      payment_methods: paymentMethods,
    });
  };

  if (loadingBooking) {
    return (
      <div className="flex justify-center py-12">
        <Spinner />
      </div>
    );
  }

  if (!booking) {
    return (
      <Alert variant="error">
        <AlertTriangleIcon size={20} />
        <div>
          <h3 className="font-semibold">Booking not found</h3>
          <p className="text-sm">
            The booking you're looking for doesn't exist
          </p>
        </div>
      </Alert>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/dashboard/bookings")}
        >
          <ArrowLeftIcon size={20} />
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-foreground">Checkout</h1>
          <p className="text-muted-foreground">
            Process payment for booking #{booking.id.slice(0, 8)}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Payment Methods */}
        <div className="lg:col-span-2 space-y-6">
          {/* Booking Summary */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Booking Details
            </h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Client</span>
                <span className="font-medium text-foreground">
                  {booking.client?.name}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Service</span>
                <span className="font-medium text-foreground">
                  {booking.service?.name}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Stylist</span>
                <span className="font-medium text-foreground">
                  {booking.stylist?.name}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Date</span>
                <span className="font-medium text-foreground">
                  {new Date(booking.booking_date).toLocaleDateString()}
                </span>
              </div>
            </div>
          </Card>

          {/* Payment Methods */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-foreground">
                Payment Methods
              </h2>
              <Button size="sm" onClick={addPaymentMethod}>
                Add Method
              </Button>
            </div>

            <div className="space-y-4">
              {paymentMethods.map((pm, index) => (
                <div
                  key={index}
                  className="p-4 border border-[var(--border)] rounded-lg space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-foreground">
                      Payment Method {index + 1}
                    </span>
                    {paymentMethods.length > 1 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removePaymentMethod(index)}
                      >
                        Remove
                      </Button>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-foreground mb-1">
                        Method
                      </label>
                      <select
                        value={pm.method}
                        onChange={(e) =>
                          updatePaymentMethod(
                            index,
                            "method",
                            e.target.value as PaymentMethodType,
                          )
                        }
                        className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-background text-foreground"
                      >
                        <option value="cash">Cash</option>
                        <option value="card">Card</option>
                        <option value="transfer">Bank Transfer</option>
                        <option value="gift_card">Gift Card</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-foreground mb-1">
                        Amount
                      </label>
                      <Input
                        type="number"
                        value={pm.amount}
                        onChange={(e) =>
                          updatePaymentMethod(
                            index,
                            "amount",
                            parseFloat(e.target.value) || 0,
                          )
                        }
                        placeholder="0.00"
                      />
                    </div>
                  </div>

                  {pm.method === "transfer" && (
                    <div>
                      <label className="block text-sm font-medium text-foreground mb-1">
                        Reference Number
                      </label>
                      <Input
                        value={pm.reference || ""}
                        onChange={(e) =>
                          updatePaymentMethod(
                            index,
                            "reference",
                            e.target.value,
                          )
                        }
                        placeholder="Enter transfer reference"
                      />
                    </div>
                  )}

                  {pm.method === "gift_card" && (
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-foreground mb-1">
                          Gift Card Number
                        </label>
                        <div className="flex gap-2">
                          <Input
                            value={pm.gift_card_code || ""}
                            onChange={(e) => {
                              updatePaymentMethod(
                                index,
                                "gift_card_code",
                                e.target.value,
                              );
                              setGiftCardNumber(e.target.value);
                            }}
                            placeholder="GC-XXXXXXXXXXXX"
                          />
                          <Button
                            type="button"
                            onClick={checkGiftCardBalance}
                            disabled={!giftCardNumber || checkingGiftCard}
                            variant="outline"
                            size="sm"
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
                              ₦{giftCardBalance.toLocaleString()}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {pm.method === "card" && (
                    <div>
                      <label className="block text-sm font-medium text-foreground mb-1">
                        Payment Gateway
                      </label>
                      <select
                        value={selectedGateway}
                        onChange={(e) =>
                          setSelectedGateway(
                            e.target.value as "paystack" | "flutterwave",
                          )
                        }
                        className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-background text-foreground"
                      >
                        <option value="paystack">Paystack</option>
                        <option value="flutterwave">Flutterwave</option>
                      </select>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Right Column - Summary */}
        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Payment Summary
            </h2>

            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Service Total</span>
                <span className="font-medium text-foreground">
                  ₦{totalAmount.toLocaleString()}
                </span>
              </div>

              {depositPaid > 0 && (
                <div className="flex justify-between text-[var(--success)]">
                  <span>Deposit Paid</span>
                  <span>-₦{depositPaid.toLocaleString()}</span>
                </div>
              )}

              <div className="border-t border-[var(--border)] pt-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">
                    Remaining Balance
                  </span>
                  <span className="font-medium text-foreground">
                    ₦{remainingBalance.toLocaleString()}
                  </span>
                </div>
              </div>

              <div className="flex justify-between">
                <span className="text-muted-foreground">Payment Amount</span>
                <span className="font-medium text-foreground">
                  ₦{totalPaymentAmount.toLocaleString()}
                </span>
              </div>

              <div className="border-t border-[var(--border)] pt-3">
                <div className="flex justify-between text-lg">
                  <span className="font-semibold text-foreground">
                    Balance Due
                  </span>
                  <span
                    className={`font-bold ${
                      balanceRemaining === 0
                        ? "text-[var(--success)]"
                        : balanceRemaining < 0
                          ? "text-[var(--error)]"
                          : "text-foreground"
                    }`}
                  >
                    ₦{Math.abs(balanceRemaining).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>

            {balanceRemaining !== 0 && (
              <Alert variant="warning" className="mt-4">
                <AlertTriangleIcon size={20} />
                <div>
                  <p className="text-sm">
                    {balanceRemaining > 0
                      ? "Payment amount is less than balance"
                      : "Payment amount exceeds balance"}
                  </p>
                </div>
              </Alert>
            )}

            <Button
              fullWidth
              className="mt-6"
              onClick={handleCheckout}
              disabled={balanceRemaining !== 0 || checkoutMutation.isPending}
            >
              {checkoutMutation.isPending ? (
                <>
                  <Spinner size="sm" />
                  Processing...
                </>
              ) : (
                <>
                  <CheckCircleIcon size={20} />
                  Complete Payment
                </>
              )}
            </Button>
          </Card>

          {checkoutMutation.isError && (
            <Alert variant="error">
              <AlertTriangleIcon size={20} />
              <div>
                <h3 className="font-semibold">Payment Failed</h3>
                <p className="text-sm">
                  {checkoutMutation.error?.response?.data?.detail ||
                    "An error occurred"}
                </p>
              </div>
            </Alert>
          )}
        </div>
      </div>
    </div>
  );
}

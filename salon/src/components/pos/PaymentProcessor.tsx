import { useState } from "react";
import { usePOSStore } from "@/stores/pos";
import { useCheckout } from "@/hooks/useCheckout";
import { useInitializePOSPayment } from "@/hooks/usePayment";
import { useToast } from "@/components/ui/toast";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import TipHandler from "./TipHandler";
import SplitPayment from "./SplitPayment";
import QuickCheckout from "./QuickCheckout";

interface PaymentProcessorProps {
  customerId: string;
  staffId: string;
  paymentMethod: string;
  onClose: () => void;
}

export default function PaymentProcessor({
  customerId,
  staffId,
  paymentMethod: initialPaymentMethod,
  onClose,
}: PaymentProcessorProps) {
  const [paymentMethod, setPaymentMethod] =
    useState<string>(initialPaymentMethod);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string>();
  const [success, setSuccess] = useState(false);
  const [showTipHandler, setShowTipHandler] = useState(false);
  const [showSplitPayment, setShowSplitPayment] = useState(false);
  const [showQuickCheckout, setShowQuickCheckout] = useState(false);
  const [tipAmount, setTipAmount] = useState(0);
  const { mutate: checkout } = useCheckout();
  const { mutate: initializePOSPayment } = useInitializePOSPayment();
  const { showToast } = useToast();
  const { cartItems, cartTotal, cartSubtotal, setPaymentStatus, clearCart } =
    usePOSStore();

  const totalWithTip = cartTotal + tipAmount;

  const handlePayment = async () => {
    if (!customerId || !staffId || cartItems.length === 0) {
      setError("Missing required information");
      showToast({
        title: "Missing Information",
        description: "Customer, staff, and items are required",
        variant: "error",
      });
      return;
    }

    setIsProcessing(true);
    setError(undefined);

    try {
      if (paymentMethod === "cash") {
        // Cash payment - create transaction immediately with completed status
        const transactionItems = cartItems.map((item: any) => ({
          item_type: item.itemType || "service",
          item_id: item.itemId,
          item_name: item.itemName,
          quantity: item.quantity,
          unit_price: item.unitPrice,
          tax_rate: 0.1,
          discount_rate: 0,
        }));

        checkout(
          {
            customer_id: customerId,
            staff_id: staffId,
            items: transactionItems,
            payment_method: "cash",
          },
          {
            onSuccess: (transaction: any) => {
              // Generate receipt after cash payment
              fetch(`/api/v1/transactions/${transaction.id}/generate-receipt`, {
                method: "POST",
              })
                .then(() => {
                  setPaymentStatus("completed");
                  setSuccess(true);
                  showToast({
                    title: "Payment Completed",
                    description: `Cash payment of ₦${totalWithTip.toLocaleString("en-NG")} recorded`,
                    variant: "success",
                  });
                  setTimeout(() => {
                    clearCart();
                    onClose();
                  }, 2000);
                })
                .catch((err) => {
                  // Receipt generation failed but transaction was created
                  console.error("Receipt generation failed:", err);
                  setPaymentStatus("completed");
                  setSuccess(true);
                  showToast({
                    title: "Payment Completed",
                    description: `Cash payment recorded (receipt generation pending)`,
                    variant: "success",
                  });
                  setTimeout(() => {
                    clearCart();
                    onClose();
                  }, 2000);
                });
            },
            onError: (error: any) => {
              const errorMsg =
                error?.response?.data?.detail || "Failed to create transaction";
              setError(errorMsg);
              showToast({
                title: "Payment Failed",
                description: errorMsg,
                variant: "error",
              });
              setIsProcessing(false);
            },
          },
        );
      } else if (paymentMethod === "card" || paymentMethod === "mobile_money") {
        // Card/Mobile Money - create transaction FIRST, then initialize payment
        const transactionItems = cartItems.map((item: any) => ({
          item_type: item.itemType || "service",
          item_id: item.itemId,
          item_name: item.itemName,
          quantity: item.quantity,
          unit_price: item.unitPrice,
          tax_rate: 0.1,
          discount_rate: 0,
        }));

        // First, create the transaction
        checkout(
          {
            customer_id: customerId,
            staff_id: staffId,
            items: transactionItems,
            payment_method: paymentMethod,
          },
          {
            onSuccess: (transaction: any) => {
              // Transaction created successfully, now initialize payment
              const transactionId = transaction.id;

              initializePOSPayment(
                {
                  transactionId,
                  email: "staff@salon.local",
                  callbackUrl: `${window.location.origin}/pos`,
                },
                {
                  onSuccess: (paymentData: any) => {
                    if (paymentData.authorization_url) {
                      // Save transaction data to localStorage before redirecting
                      localStorage.setItem(
                        "posPaymentData",
                        JSON.stringify({
                          transactionId,
                          reference: paymentData.reference,
                          customerId,
                          staffId,
                          paymentMethod,
                          totalAmount: totalWithTip,
                        }),
                      );
                      showToast({
                        title: "Redirecting to Payment",
                        description: "Please complete payment on the next page",
                        variant: "default",
                      });
                      // Redirect to Paystack
                      window.location.href = paymentData.authorization_url;
                    } else {
                      setError("Failed to get payment authorization URL");
                      showToast({
                        title: "Payment Initialization Failed",
                        description: "Could not get payment authorization",
                        variant: "error",
                      });
                      setIsProcessing(false);
                    }
                  },
                  onError: (error: any) => {
                    const errorMsg =
                      error?.response?.data?.detail ||
                      "Failed to initialize payment";
                    setError(errorMsg);
                    showToast({
                      title: "Payment Initialization Failed",
                      description: errorMsg,
                      variant: "error",
                    });
                    setIsProcessing(false);
                  },
                },
              );
            },
            onError: (error: any) => {
              const errorMsg =
                error?.response?.data?.detail || "Failed to create transaction";
              setError(errorMsg);
              showToast({
                title: "Transaction Creation Failed",
                description: errorMsg,
                variant: "error",
              });
              setIsProcessing(false);
            },
          },
        );
      } else if (paymentMethod === "check") {
        // Check payment - create transaction with pending status
        const transactionItems = cartItems.map((item: any) => ({
          item_type: item.itemType || "service",
          item_id: item.itemId,
          item_name: item.itemName,
          quantity: item.quantity,
          unit_price: item.unitPrice,
          tax_rate: 0.1,
          discount_rate: 0,
        }));

        checkout(
          {
            customer_id: customerId,
            staff_id: staffId,
            items: transactionItems,
            payment_method: "check",
          },
          {
            onSuccess: (transaction: any) => {
              // Generate receipt after check payment
              fetch(`/api/v1/transactions/${transaction.id}/generate-receipt`, {
                method: "POST",
              })
                .then(() => {
                  setPaymentStatus("pending");
                  setSuccess(true);
                  showToast({
                    title: "Check Payment Recorded",
                    description: `Check payment of ₦${totalWithTip.toLocaleString("en-NG")} marked as pending`,
                    variant: "success",
                  });
                  setTimeout(() => {
                    clearCart();
                    onClose();
                  }, 2000);
                })
                .catch((err) => {
                  // Receipt generation failed but transaction was created
                  console.error("Receipt generation failed:", err);
                  setPaymentStatus("pending");
                  setSuccess(true);
                  showToast({
                    title: "Check Payment Recorded",
                    description: `Check payment recorded (receipt generation pending)`,
                    variant: "success",
                  });
                  setTimeout(() => {
                    clearCart();
                    onClose();
                  }, 2000);
                });
            },
            onError: (error: any) => {
              const errorMsg =
                error?.response?.data?.detail || "Failed to create transaction";
              setError(errorMsg);
              showToast({
                title: "Payment Failed",
                description: errorMsg,
                variant: "error",
              });
              setIsProcessing(false);
            },
          },
        );
      }
    } catch (err: any) {
      const errorMessage =
        err?.response?.data?.detail ||
        err?.message ||
        "Payment processing failed";
      setError(errorMessage);
      showToast({
        title: "Payment Error",
        description: errorMessage,
        variant: "error",
      });
      setIsProcessing(false);
    }
  };

  const handleTipChange = (amount: number) => {
    setTipAmount(amount);
  };

  return (
    <>
      {/* Overlay backdrop */}
      <div className="fixed inset-0 bg-black/50 z-40" onClick={onClose} />
      {/* Modal */}
      <Card className="p-4 md:p-6 border-2 border-primary fixed bottom-0 left-0 right-0 md:inset-auto md:bottom-6 md:right-6 md:max-w-md z-50 overflow-y-auto rounded-t-lg md:rounded-lg">
        <h3 className="text-base md:text-lg font-semibold mb-4 text-foreground">
          Payment Method
        </h3>

        {error && (
          <Alert variant="error" className="mb-4">
            {error}
          </Alert>
        )}
        {success && (
          <Alert variant="default" className="mb-4">
            <p>Payment processed successfully!</p>
          </Alert>
        )}

        {showTipHandler ? (
          <TipHandler
            subtotal={cartSubtotal}
            onTipChange={handleTipChange}
            onClose={() => setShowTipHandler(false)}
          />
        ) : showSplitPayment ? (
          <SplitPayment
            totalAmount={totalWithTip}
            onApply={() => {
              setShowSplitPayment(false);
              handlePayment();
            }}
            onCancel={() => setShowSplitPayment(false)}
          />
        ) : showQuickCheckout ? (
          <QuickCheckout
            total={totalWithTip}
            onCheckout={() => handlePayment()}
            isProcessing={isProcessing}
            onClose={() => setShowQuickCheckout(false)}
          />
        ) : (
          <>
            <RadioGroup value={paymentMethod} onValueChange={setPaymentMethod}>
              <div className="space-y-2 md:space-y-3">
                <div className="flex items-center space-x-2 p-2 md:p-3 border border-border rounded-lg hover:bg-muted">
                  <RadioGroupItem value="cash" id="cash" />
                  <Label htmlFor="cash" className="flex-1 cursor-pointer">
                    <span className="font-medium text-sm md:text-base text-foreground">
                      Cash
                    </span>
                    <p className="text-xs md:text-sm text-muted-foreground">
                      Pay with cash
                    </p>
                  </Label>
                </div>

                <div className="flex items-center space-x-2 p-2 md:p-3 border border-border rounded-lg hover:bg-muted">
                  <RadioGroupItem value="card" id="card" />
                  <Label htmlFor="card" className="flex-1 cursor-pointer">
                    <span className="font-medium text-sm md:text-base text-foreground">
                      Card (Paystack)
                    </span>
                    <p className="text-xs md:text-sm text-muted-foreground">
                      Pay with debit/credit card
                    </p>
                  </Label>
                </div>

                <div className="flex items-center space-x-2 p-2 md:p-3 border border-border rounded-lg hover:bg-muted">
                  <RadioGroupItem value="mobile_money" id="mobile_money" />
                  <Label
                    htmlFor="mobile_money"
                    className="flex-1 cursor-pointer"
                  >
                    <span className="font-medium text-sm md:text-base text-foreground">
                      Mobile Money
                    </span>
                    <p className="text-xs md:text-sm text-muted-foreground">
                      Pay with mobile money
                    </p>
                  </Label>
                </div>

                <div className="flex items-center space-x-2 p-2 md:p-3 border border-border rounded-lg hover:bg-muted">
                  <RadioGroupItem value="check" id="check" />
                  <Label htmlFor="check" className="flex-1 cursor-pointer">
                    <span className="font-medium text-sm md:text-base text-foreground">
                      Check
                    </span>
                    <p className="text-xs md:text-sm text-muted-foreground">
                      Pay with check
                    </p>
                  </Label>
                </div>
              </div>
            </RadioGroup>

            <div className="mt-4 md:mt-6 p-3 md:p-4 bg-muted rounded-lg">
              <p className="text-xs md:text-sm text-muted-foreground">
                Total Amount
              </p>
              <p className="text-xl md:text-2xl font-bold text-foreground">
                ₦
                {totalWithTip.toLocaleString("en-NG", {
                  maximumFractionDigits: 2,
                })}
              </p>
              {tipAmount > 0 && (
                <p className="text-xs md:text-sm text-green-600 mt-1">
                  Includes ₦
                  {tipAmount.toLocaleString("en-NG", {
                    maximumFractionDigits: 2,
                  })}{" "}
                  tip
                </p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-2 mt-4 md:mt-6">
              <Button
                variant="outline"
                onClick={() => setShowTipHandler(true)}
                className="text-xs md:text-sm"
              >
                Add Tip
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowSplitPayment(true)}
                className="text-xs md:text-sm"
              >
                Split Payment
              </Button>
            </div>

            <div className="flex gap-2 md:gap-3 mt-4 md:mt-6">
              <Button
                variant="outline"
                onClick={onClose}
                disabled={isProcessing}
                className="flex-1 text-sm md:text-base"
              >
                Cancel
              </Button>
              <Button
                onClick={handlePayment}
                disabled={isProcessing}
                className="flex-1 text-sm md:text-base"
              >
                {isProcessing ? (
                  <>
                    <Spinner className="w-4 h-4 mr-2" />
                    Processing...
                  </>
                ) : (
                  "Complete Payment"
                )}
              </Button>
            </div>

            <Button
              variant="ghost"
              onClick={() => setShowQuickCheckout(true)}
              className="w-full mt-2 text-xs md:text-sm"
            >
              Use Saved Payment Method
            </Button>
          </>
        )}
      </Card>
    </>
  );
}

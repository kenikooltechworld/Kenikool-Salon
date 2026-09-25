import { useState, useEffect } from "react";
import { Modal, ModalHeader, ModalTitle, ModalBody, ModalFooter } from "@/components/ui/modal";
import { usePOSStore } from "@/stores/pos";
import { useCheckout } from "@/hooks/useCheckout";
import { useInitializePOSPayment } from "@/hooks/usePayment";
import { useGenerateReceipt } from "@/hooks/useReceipt";
import { useToast } from "@/components/ui/toast";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import TipHandler from "./TipHandler";
import SplitPayment from "./SplitPayment";
import QuickCheckout from "./QuickCheckout";
import { generateSalonReference } from "@/lib/utils/reference";

interface PaymentProcessorProps {
  customerId: string;
  staffId: string;
  appointmentId?: string;
  paymentMethod: string;
  open: boolean;
  onClose: () => void;
}

export default function PaymentProcessor({
  customerId,
  staffId,
  appointmentId,
  paymentMethod: initialPaymentMethod,
  open,
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
  const { mutate: generateReceipt } = useGenerateReceipt();
  const { showToast } = useToast();
  const { cartItems, cartTotal, cartSubtotal, setPaymentStatus, clearCart } =
    usePOSStore();

  const totalWithTip = cartTotal + tipAmount;

  useEffect(() => {
    if (!open) {
      setIsProcessing(false);
      setError(undefined);
      setSuccess(false);
      setShowTipHandler(false);
      setShowSplitPayment(false);
      setShowQuickCheckout(false);
      setTipAmount(0);
    }
  }, [open]);

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
            appointment_id: appointmentId,
            items: transactionItems,
            payment_method: "cash",
          },
          {
            onSuccess: (transaction: any) => {
              generateReceipt(transaction.id, {
                onSuccess: () => {
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
                },
                onError: (err: any) => {
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
                },
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
            appointment_id: appointmentId,
            items: transactionItems,
            payment_method: paymentMethod,
          },
          {
            onSuccess: (transaction: any) => {
              const transactionId = transaction.id;

              initializePOSPayment(
                {
                  transactionId,
                  email: "staff@salon.local",
                  callbackUrl: `${window.location.origin}/pos`,
                  reference: generateSalonReference(),
                },
                {
                  onSuccess: (paymentData: any) => {
                    if (paymentData.authorizationUrl) {
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
                      window.location.href = paymentData.authorizationUrl;
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
            appointment_id: appointmentId,
            items: transactionItems,
            payment_method: "check",
          },
          {
            onSuccess: (transaction: any) => {
              generateReceipt(transaction.id, {
                onSuccess: () => {
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
                },
                onError: (err: any) => {
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
                },
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
    <Modal open={open} onClose={onClose} size="md">
      <ModalHeader className="text-center">
        <ModalTitle>Payment Method</ModalTitle>
      </ModalHeader>

      <ModalBody>
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
          </>
        )}
      </ModalBody>

      {!showTipHandler && !showSplitPayment && !showQuickCheckout && (
        <ModalFooter>
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isProcessing}
            className="text-sm md:text-base"
          >
            Cancel
          </Button>
          <Button
            onClick={handlePayment}
            disabled={isProcessing}
            className="text-sm md:text-base"
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
        </ModalFooter>
      )}

      {!showTipHandler && !showSplitPayment && !showQuickCheckout && (
        <div className="px-6 pb-6">
          <Button
            variant="ghost"
            onClick={() => setShowQuickCheckout(true)}
            className="w-full text-xs md:text-sm"
          >
            Use Saved Payment Method
          </Button>
        </div>
      )}
    </Modal>
  );
}

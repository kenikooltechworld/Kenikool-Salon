import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { CreditCardIcon } from "@/components/icons";
import {
  useInitializePayment,
  useVerifyPayment,
} from "@/lib/api/hooks/usePayments";

interface PaystackPaymentProps {
  bookingId: string;
  amount: number;
  email: string;
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export function PaystackPayment({
  bookingId,
  amount,
  email,
  onSuccess,
  onError,
}: PaystackPaymentProps) {
  const initializePayment = useInitializePayment({
    onSuccess: (data) => {
      // Redirect to Paystack payment page
      window.location.href = data.authorization_url;
    },
    onError: (error) => {
      onError?.(error.response?.data?.detail || "Failed to initialize payment");
    },
  });

  const verifyPayment = useVerifyPayment({
    onSuccess: () => {
      onSuccess?.();
    },
    onError: (error) => {
      onError?.(error.response?.data?.detail || "Payment verification failed");
    },
  });

  useEffect(() => {
    // Check for payment reference in URL (after redirect from Paystack)
    const urlParams = new URLSearchParams(window.location.search);
    const reference = urlParams.get("reference");

    if (reference) {
      verifyPayment.mutate(reference);
    }
  }, []);

  const handlePayment = () => {
    initializePayment.mutate({
      booking_id: bookingId,
      email,
      amount,
      gateway: "paystack",
    });
  };

  return (
    <Button
      fullWidth
      onClick={handlePayment}
      disabled={initializePayment.isPending || verifyPayment.isPending}
    >
      {initializePayment.isPending || verifyPayment.isPending ? (
        <>
          <Spinner size="sm" />
          Processing...
        </>
      ) : (
        <>
          <CreditCardIcon size={20} />
          Pay with Paystack
        </>
      )}
    </Button>
  );
}

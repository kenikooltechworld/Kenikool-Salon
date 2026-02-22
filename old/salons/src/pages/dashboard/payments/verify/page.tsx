import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  CheckCircleIcon,
  AlertTriangleIcon,
  HomeIcon,
} from "@/components/icons";
import { useVerifyPayment } from "@/lib/api/hooks/usePayments";

export default function PaymentVerificationPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [verificationStatus, setVerificationStatus] = useState<
    "verifying" | "success" | "failed"
  >("verifying");

  const verifyPayment = useVerifyPayment({
    onSuccess: () => {
      setVerificationStatus("success");
    },
    onError: () => {
      setVerificationStatus("failed");
    },
  });

  useEffect(() => {
    const reference =
      searchParams.get("reference") ||
      searchParams.get("tx_ref") ||
      searchParams.get("trxref");

    if (reference) {
      verifyPayment.mutate(reference);
    } else {
      setVerificationStatus("failed");
    }
  }, [searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="max-w-md w-full p-8">
        {verificationStatus === "verifying" && (
          <div className="text-center space-y-4">
            <Spinner size="lg" />
            <h2 className="text-xl font-semibold text-foreground">
              Verifying Payment
            </h2>
            <p className="text-muted-foreground">
              Please wait while we confirm your payment...
            </p>
          </div>
        )}

        {verificationStatus === "success" && (
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <div className="w-16 h-16 rounded-full bg-[var(--success)]/10 flex items-center justify-center">
                <CheckCircleIcon size={32} className="text-[var(--success)]" />
              </div>
            </div>
            <h2 className="text-xl font-semibold text-foreground">
              Payment Successful!
            </h2>
            <p className="text-muted-foreground">
              Your payment has been confirmed and processed successfully.
            </p>
            <div className="flex gap-3 pt-4">
              <Button
                fullWidth
                onClick={() => navigate("/dashboard/bookings")}
              >
                View Bookings
              </Button>
              <Button
                fullWidth
                variant="outline"
                onClick={() => navigate("/dashboard")}
              >
                <HomeIcon size={20} />
                Dashboard
              </Button>
            </div>
          </div>
        )}

        {verificationStatus === "failed" && (
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <div className="w-16 h-16 rounded-full bg-[var(--error)]/10 flex items-center justify-center">
                <AlertTriangleIcon size={32} className="text-[var(--error)]" />
              </div>
            </div>
            <h2 className="text-xl font-semibold text-foreground">
              Payment Verification Failed
            </h2>
            <p className="text-muted-foreground">
              We couldn't verify your payment. Please contact support if you
              were charged.
            </p>
            <Alert variant="error">
              <AlertTriangleIcon size={20} />
              <div>
                <p className="text-sm">
                  {verifyPayment.error?.response?.data?.detail ||
                    "Payment verification failed"}
                </p>
              </div>
            </Alert>
            <div className="flex gap-3 pt-4">
              <Button
                fullWidth
                onClick={() => navigate("/dashboard/bookings")}
              >
                Back to Bookings
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}

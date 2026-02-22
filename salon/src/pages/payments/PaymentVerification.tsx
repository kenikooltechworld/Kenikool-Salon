import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { CheckCircleIcon, XCircleIcon } from "@/components/icons";
import { useVerifyPayment } from "@/hooks/usePayments";

type PaymentStatus = "loading" | "success" | "failed" | "error";

export default function PaymentVerification() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<PaymentStatus>("loading");
  const [message, setMessage] = useState("");
  const [invoiceId, setInvoiceId] = useState<string | null>(null);

  const verifyPaymentMutation = useVerifyPayment();

  useEffect(() => {
    const verifyPayment = async () => {
      try {
        // Get reference from URL query params
        const reference = searchParams.get("reference");
        const invoiceIdParam = searchParams.get("invoice_id");

        if (!reference) {
          setStatus("error");
          setMessage("Payment reference not found in URL");
          return;
        }

        setInvoiceId(invoiceIdParam);

        // Verify payment with backend
        await verifyPaymentMutation.mutateAsync(reference);

        setStatus("success");
        setMessage("Payment verified successfully!");

        // Redirect to invoice after 3 seconds
        setTimeout(() => {
          if (invoiceIdParam) {
            navigate(`/invoices/${invoiceIdParam}`);
          } else {
            navigate("/invoices");
          }
        }, 3000);
      } catch (error: any) {
        console.error("Payment verification error:", error);
        setStatus("failed");
        setMessage(
          error?.response?.data?.detail ||
            "Payment verification failed. Please try again.",
        );
      }
    };

    verifyPayment();
  }, [searchParams, navigate, verifyPaymentMutation]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Payment Verification
          </h1>
          <p className="text-muted-foreground">
            Please wait while we verify your payment
          </p>
        </div>

        {/* Status Card */}
        <div className="bg-card border border-border rounded-lg p-8">
          {status === "loading" && (
            <div className="flex flex-col items-center gap-4">
              <Spinner size="lg" />
              <p className="text-muted-foreground text-center">
                Verifying your payment...
              </p>
            </div>
          )}

          {status === "success" && (
            <div className="flex flex-col items-center gap-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircleIcon size={32} className="text-green-600" />
              </div>
              <div className="text-center">
                <h2 className="text-xl font-semibold text-foreground mb-2">
                  Payment Successful!
                </h2>
                <p className="text-muted-foreground mb-4">{message}</p>
                <p className="text-sm text-muted-foreground">
                  Redirecting to invoice in 3 seconds...
                </p>
              </div>
            </div>
          )}

          {status === "failed" && (
            <div className="flex flex-col items-center gap-4">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                <XCircleIcon size={32} className="text-red-600" />
              </div>
              <div className="text-center">
                <h2 className="text-xl font-semibold text-foreground mb-2">
                  Payment Failed
                </h2>
                <Alert variant="error" className="mb-4">
                  {message}
                </Alert>
                <div className="flex gap-2 justify-center">
                  <Button
                    variant="outline"
                    onClick={() => navigate("/invoices")}
                  >
                    Back to Invoices
                  </Button>
                  <Button onClick={() => navigate(-1)}>Retry Payment</Button>
                </div>
              </div>
            </div>
          )}

          {status === "error" && (
            <div className="flex flex-col items-center gap-4">
              <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center">
                <XCircleIcon size={32} className="text-yellow-600" />
              </div>
              <div className="text-center">
                <h2 className="text-xl font-semibold text-foreground mb-2">
                  Error
                </h2>
                <Alert variant="error" className="mb-4">
                  {message}
                </Alert>
                <Button onClick={() => navigate("/invoices")}>
                  Back to Invoices
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-sm text-muted-foreground">
          <p>
            If you have any questions, please contact our support team at{" "}
            <a
              href="mailto:support@example.com"
              className="text-primary hover:underline"
            >
              support@example.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

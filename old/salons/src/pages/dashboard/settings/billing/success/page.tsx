import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { CheckCircleIcon, AlertTriangleIcon } from "@/components/icons";
import { apiClient } from "@/lib/api/client";

export default function SubscriptionSuccessPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const reference = searchParams.get("reference");

  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading"
  );
  const [message, setMessage] = useState("");
  const [planName, setPlanName] = useState("");

  useEffect(() => {
    if (!reference) {
      setStatus("error");
      setMessage("No payment reference found");
      return;
    }

    // Verify payment
    const verifyPayment = async () => {
      try {
        const response = await apiClient.post(
          `/api/subscriptions/verify/${reference}`
        );

        setStatus("success");
        setPlanName(response.data.plan_name || "");
        setMessage("Your subscription has been activated successfully!");
      } catch (error: any) {
        setStatus("error");
        setMessage(
          error.response?.data?.detail ||
            "Failed to verify payment. Please contact support."
        );
      }
    };

    verifyPayment();
  }, [reference]);

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="max-w-md w-full p-8">
        {status === "loading" && (
          <div className="text-center">
            <Spinner size="lg" className="mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-foreground mb-2">
              Verifying Payment
            </h2>
            <p className="text-muted-foreground">
              Please wait while we confirm your payment...
            </p>
          </div>
        )}

        {status === "success" && (
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircleIcon size={32} className="text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-foreground mb-2">
              Payment Successful!
            </h2>
            <p className="text-muted-foreground mb-6">{message}</p>
            {planName && (
              <p className="text-sm text-muted-foreground mb-6">
                You are now subscribed to the{" "}
                <span className="font-semibold">{planName}</span> plan
              </p>
            )}
            <div className="space-y-3">
              <Button
                fullWidth
                onClick={() => navigate("/dashboard/settings/billing")}
              >
                View Billing Details
              </Button>
              <Button
                fullWidth
                variant="outline"
                onClick={() => navigate("/dashboard")}
              >
                Go to Dashboard
              </Button>
            </div>
          </div>
        )}

        {status === "error" && (
          <div className="text-center">
            <div className="w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertTriangleIcon size={32} className="text-red-600" />
            </div>
            <h2 className="text-2xl font-bold text-foreground mb-2">
              Payment Failed
            </h2>
            <p className="text-muted-foreground mb-6">{message}</p>
            <div className="space-y-3">
              <Button
                fullWidth
                onClick={() => navigate("/dashboard/settings/billing")}
              >
                Try Again
              </Button>
              <Button
                fullWidth
                variant="outline"
                onClick={() => navigate("/dashboard")}
              >
                Go to Dashboard
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}

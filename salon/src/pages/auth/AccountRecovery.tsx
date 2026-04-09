import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { apiClient } from "@/lib/utils/api";

export default function AccountRecovery() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const recoverAccount = async () => {
      try {
        const token = searchParams.get("token");
        if (!token) {
          setError("Invalid recovery link. No token provided.");
          setIsLoading(false);
          return;
        }

        const response = await apiClient.post("/api/tenants/recover", {
          recovery_token: token,
        });

        if (response.data.success) {
          setSuccess(true);
          setTimeout(() => {
            navigate("/auth/login");
          }, 3000);
        } else {
          setError(response.data.detail || "Recovery failed");
        }
      } catch (err: any) {
        setError(
          err.response?.data?.detail ||
            err.message ||
            "Failed to recover account",
        );
      } finally {
        setIsLoading(false);
      }
    };

    recoverAccount();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 to-secondary/10 flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Account Recovery
          </h1>
          <p className="text-muted-foreground">
            Processing your account recovery...
          </p>
        </div>

        {isLoading && (
          <div className="flex justify-center py-8">
            <Spinner className="h-8 w-8" />
          </div>
        )}

        {success && (
          <Alert variant="success" className="mb-6">
            <AlertTitle>Success</AlertTitle>
            <AlertDescription>
              Your account has been recovered successfully. Redirecting to
              login...
            </AlertDescription>
          </Alert>
        )}

        {error && !isLoading && (
          <div className="space-y-4">
            <Alert variant="error">
              <AlertTitle>Recovery Failed</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>

            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                If your recovery link has expired, you can:
              </p>
              <Button
                onClick={() => navigate("/auth/login")}
                variant="outline"
                className="w-full"
              >
                Return to Login
              </Button>
              <Button
                onClick={() => navigate("/auth/forgot-password")}
                className="w-full"
              >
                Request New Recovery Link
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}

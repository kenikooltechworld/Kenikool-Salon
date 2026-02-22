import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiClient } from "@/lib/utils/api";

export default function MFAVerify() {
  const navigate = useNavigate();
  const [method, setMethod] = useState<"totp" | "sms" | "backup">("totp");
  const [code, setCode] = useState("");
  const [backupCode, setBackupCode] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [resendCountdown, setResendCountdown] = useState(0);

  const email = localStorage.getItem("mfaEmail");

  useEffect(() => {
    if (!email) {
      navigate("/auth/login");
    }
  }, [email, navigate]);

  useEffect(() => {
    if (resendCountdown <= 0) return;
    const timer = setTimeout(
      () => setResendCountdown(resendCountdown - 1),
      1000,
    );
    return () => clearTimeout(timer);
  }, [resendCountdown]);

  const handleVerify = async () => {
    setError("");

    if (method === "backup") {
      if (!backupCode) {
        setError("Please enter a backup code");
        return;
      }
    } else {
      if (code.length !== 6) {
        setError("Please enter a 6-digit code");
        return;
      }
    }

    setIsLoading(true);

    try {
      const payload =
        method === "backup"
          ? { email, backup_code: backupCode }
          : { email, method, code };

      await apiClient.post("/auth/mfa/verify", payload);

      // MFA verified, redirect to dashboard
      localStorage.removeItem("mfaEmail");
      navigate("/dashboard");
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Invalid code. Please try again.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendSMS = async () => {
    setError("");
    setIsLoading(true);

    try {
      await apiClient.post("/auth/mfa/resend-sms", { email });
      setCode("");
      setResendCountdown(60);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Failed to resend code. Please try again.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  if (!email) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 to-secondary/10 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">
              Verify Your Identity
            </h1>
            <p className="text-muted-foreground">
              Enter the code from your authentication method
            </p>
          </div>

          {error && (
            <Alert variant="error" className="mb-6">
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Tabs
            defaultValue={method}
            value={method}
            onValueChange={(v) => setMethod(v as any)}
          >
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="totp">Authenticator</TabsTrigger>
              <TabsTrigger value="sms">SMS</TabsTrigger>
              <TabsTrigger value="backup">Backup Code</TabsTrigger>
            </TabsList>

            <TabsContent value="totp" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="totp-code">6-Digit Code</Label>
                <Input
                  id="totp-code"
                  type="text"
                  placeholder="000000"
                  value={code}
                  onChange={(e) => setCode(e.target.value.slice(0, 6))}
                  disabled={isLoading}
                  maxLength={6}
                  inputMode="numeric"
                  autoFocus
                />
              </div>

              <Button
                onClick={handleVerify}
                disabled={isLoading || code.length !== 6}
                className="w-full"
              >
                {isLoading ? (
                  <>
                    <Spinner className="mr-2 h-4 w-4" />
                    Verifying...
                  </>
                ) : (
                  "Verify"
                )}
              </Button>
            </TabsContent>

            <TabsContent value="sms" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="sms-code">6-Digit Code from SMS</Label>
                <Input
                  id="sms-code"
                  type="text"
                  placeholder="000000"
                  value={code}
                  onChange={(e) => setCode(e.target.value.slice(0, 6))}
                  disabled={isLoading}
                  maxLength={6}
                  inputMode="numeric"
                  autoFocus
                />
              </div>

              <Button
                onClick={handleVerify}
                disabled={isLoading || code.length !== 6}
                className="w-full"
              >
                {isLoading ? (
                  <>
                    <Spinner className="mr-2 h-4 w-4" />
                    Verifying...
                  </>
                ) : (
                  "Verify"
                )}
              </Button>

              <Button
                onClick={handleResendSMS}
                variant="outline"
                disabled={resendCountdown > 0 || isLoading}
                className="w-full"
              >
                {resendCountdown > 0
                  ? `Resend in ${resendCountdown}s`
                  : "Resend Code"}
              </Button>
            </TabsContent>

            <TabsContent value="backup" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="backup-code">Backup Code</Label>
                <Input
                  id="backup-code"
                  type="text"
                  placeholder="XXXX-XXXX-XXXX"
                  value={backupCode}
                  onChange={(e) => setBackupCode(e.target.value.toUpperCase())}
                  disabled={isLoading}
                  autoFocus
                />
              </div>

              <Button
                onClick={handleVerify}
                disabled={isLoading || !backupCode}
                className="w-full"
              >
                {isLoading ? (
                  <>
                    <Spinner className="mr-2 h-4 w-4" />
                    Verifying...
                  </>
                ) : (
                  "Verify"
                )}
              </Button>
            </TabsContent>
          </Tabs>

          <div className="mt-6 pt-6 border-t border-border text-center">
            <Button
              variant="ghost"
              onClick={() => {
                localStorage.removeItem("mfaEmail");
                navigate("/auth/login");
              }}
              className="text-sm"
            >
              Back to Sign In
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}

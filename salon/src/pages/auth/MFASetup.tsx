import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiClient } from "@/lib/utils/api";

export default function MFASetup() {
  const navigate = useNavigate();
  const [method, setMethod] = useState<"totp" | "sms">("totp");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [qrCode, setQrCode] = useState("");
  const [secret, setSecret] = useState("");
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [verificationCode, setVerificationCode] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [step, setStep] = useState<"setup" | "verify" | "complete">("setup");

  const handleTOTPSetup = async () => {
    setError("");
    setIsLoading(true);

    try {
      const response = await apiClient.post("/auth/mfa/setup", {
        method: "totp",
      });

      setQrCode(response.data.qr_code);
      setSecret(response.data.secret);
      setStep("verify");
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Failed to setup MFA. Please try again.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSMSSetup = async () => {
    setError("");
    if (!phoneNumber) {
      setError("Please enter a phone number");
      return;
    }

    setIsLoading(true);

    try {
      await apiClient.post("/auth/mfa/setup", {
        method: "sms",
        phone_number: phoneNumber,
      });

      setStep("verify");
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Failed to setup MFA. Please try again.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerify = async () => {
    setError("");
    if (verificationCode.length !== 6) {
      setError("Please enter a 6-digit code");
      return;
    }

    setIsLoading(true);

    try {
      const response = await apiClient.post("/auth/mfa/verify-setup", {
        method,
        code: verificationCode,
      });

      setBackupCodes(response.data.backup_codes);
      setStep("complete");
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Invalid verification code. Please try again.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleComplete = () => {
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 to-secondary/10 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">
              Set Up Two-Factor Authentication
            </h1>
            <p className="text-muted-foreground">
              Secure your account with an additional verification step
            </p>
          </div>

          {error && (
            <Alert variant="error" className="mb-6">
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {step === "setup" && (
            <Tabs
              defaultValue={method}
              value={method}
              onValueChange={(v) => setMethod(v as any)}
            >
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="totp">Authenticator App</TabsTrigger>
                <TabsTrigger value="sms">SMS</TabsTrigger>
              </TabsList>

              <TabsContent value="totp" className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  Use an authenticator app like Google Authenticator or Authy
                </p>
                <Button
                  onClick={handleTOTPSetup}
                  disabled={isLoading}
                  className="w-full"
                >
                  {isLoading ? (
                    <>
                      <Spinner className="mr-2 h-4 w-4" />
                      Setting up...
                    </>
                  ) : (
                    "Continue with Authenticator App"
                  )}
                </Button>
              </TabsContent>

              <TabsContent value="sms" className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input
                    id="phone"
                    type="tel"
                    placeholder="+234 123 456 7890"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    disabled={isLoading}
                  />
                </div>
                <Button
                  onClick={handleSMSSetup}
                  disabled={isLoading || !phoneNumber}
                  className="w-full"
                >
                  {isLoading ? (
                    <>
                      <Spinner className="mr-2 h-4 w-4" />
                      Setting up...
                    </>
                  ) : (
                    "Continue with SMS"
                  )}
                </Button>
              </TabsContent>
            </Tabs>
          )}

          {step === "verify" && (
            <div className="space-y-4">
              {method === "totp" && qrCode && (
                <div className="space-y-4">
                  <div className="bg-white p-4 rounded-lg flex justify-center">
                    <img src={qrCode} alt="QR Code" className="w-48 h-48" />
                  </div>
                  <div className="space-y-2">
                    <Label>Secret Key (backup)</Label>
                    <div className="bg-muted p-3 rounded font-mono text-sm break-all">
                      {secret}
                    </div>
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="code">
                  {method === "totp"
                    ? "Enter 6-digit code from your app"
                    : "Enter 6-digit code from SMS"}
                </Label>
                <Input
                  id="code"
                  type="text"
                  placeholder="000000"
                  value={verificationCode}
                  onChange={(e) =>
                    setVerificationCode(e.target.value.slice(0, 6))
                  }
                  disabled={isLoading}
                  maxLength={6}
                  inputMode="numeric"
                />
              </div>

              <Button
                onClick={handleVerify}
                disabled={isLoading || verificationCode.length !== 6}
                className="w-full"
              >
                {isLoading ? (
                  <>
                    <Spinner className="mr-2 h-4 w-4" />
                    Verifying...
                  </>
                ) : (
                  "Verify & Continue"
                )}
              </Button>
            </div>
          )}

          {step === "complete" && (
            <div className="space-y-4">
              <Alert variant="success">
                <AlertTitle>Setup Complete!</AlertTitle>
                <AlertDescription>
                  Two-factor authentication is now enabled on your account.
                </AlertDescription>
              </Alert>

              <div className="space-y-2">
                <Label>Backup Codes</Label>
                <p className="text-sm text-muted-foreground">
                  Save these codes in a safe place. You can use them to access
                  your account if you lose access to your authentication method.
                </p>
                <div className="bg-muted p-4 rounded space-y-2 max-h-48 overflow-y-auto">
                  {backupCodes.map((code, idx) => (
                    <div key={idx} className="font-mono text-sm">
                      {code}
                    </div>
                  ))}
                </div>
              </div>

              <Button onClick={handleComplete} className="w-full">
                Go to Dashboard
              </Button>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import {
  CheckIcon,
  AlertTriangleIcon,
  ShieldIcon,
  CopyIcon,
} from "@/components/icons";
import {
  useSetup2FA,
  useVerify2FA,
  useDisable2FA,
} from "@/lib/api/hooks/useSettings";

interface TwoFactorSetupWizardProps {
  is2FAEnabled?: boolean;
}

export function TwoFactorSetupWizard({
  is2FAEnabled = false,
}: TwoFactorSetupWizardProps) {
  const [step, setStep] = useState<"idle" | "setup" | "verify" | "backup">(
    "idle"
  );
  const [setupData, setSetupData] = useState<{
    secret?: string;
    qr_code_url?: string;
    backup_codes?: string[];
  }>({});
  const [verificationCode, setVerificationCode] = useState("");
  const [disablePassword, setDisablePassword] = useState("");
  const [disableCode, setDisableCode] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const setup2FAMutation = useSetup2FA({
    onSuccess: (data) => {
      setSetupData(data);
      setStep("verify");
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to setup 2FA"
      );
    },
  });

  const verify2FAMutation = useVerify2FA({
    onSuccess: () => {
      setStep("backup");
      setSuccessMessage("2FA enabled successfully!");
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Invalid verification code"
      );
    },
  });

  const disable2FAMutation = useDisable2FA({
    onSuccess: () => {
      setSuccessMessage("2FA disabled successfully!");
      setStep("idle");
      setDisablePassword("");
      setDisableCode("");
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to disable 2FA"
      );
    },
  });

  const handleStartSetup = () => {
    setErrorMessage("");
    setSuccessMessage("");
    setup2FAMutation.mutate();
  };

  const handleVerify = () => {
    if (!verificationCode || verificationCode.length !== 6) {
      setErrorMessage("Verification code must be 6 digits");
      return;
    }
    verify2FAMutation.mutate({ code: verificationCode });
  };

  const handleDisable = () => {
    if (!disablePassword) {
      setErrorMessage("Password is required");
      return;
    }
    if (!disableCode || disableCode.length !== 6) {
      setErrorMessage("Verification code must be 6 digits");
      return;
    }
    disable2FAMutation.mutate({
      password: disablePassword,
      code: disableCode,
    });
  };

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-foreground">
            Two-Factor Authentication
          </h2>
          <p className="text-sm text-muted-foreground">
            Add an extra layer of security to your account
          </p>
        </div>
        {is2FAEnabled && step === "idle" && (
          <Button
            variant="destructive"
            onClick={() => setStep("disable")}
          >
            Disable 2FA
          </Button>
        )}
        {!is2FAEnabled && step === "idle" && (
          <Button onClick={handleStartSetup}>Enable 2FA</Button>
        )}
      </div>

      {successMessage && (
        <Alert variant="success" className="mb-4">
          <CheckIcon size={20} />
          <p>{successMessage}</p>
        </Alert>
      )}

      {errorMessage && (
        <Alert variant="error" className="mb-4">
          <AlertTriangleIcon size={20} />
          <p>{errorMessage}</p>
        </Alert>
      )}

      {/* Setup Step - QR Code */}
      {step === "setup" && setupData.qr_code_url && (
        <div className="space-y-4">
          <div className="bg-muted p-4 rounded-lg">
            <p className="text-sm font-medium text-foreground mb-3">
              Step 1: Scan QR Code
            </p>
            <p className="text-sm text-muted-foreground mb-4">
              Use an authenticator app (Google Authenticator, Authy, Microsoft
              Authenticator) to scan this QR code:
            </p>
            <div className="flex justify-center bg-white p-4 rounded">
              <img
                src={setupData.qr_code_url}
                alt="2FA QR Code"
                className="w-48 h-48"
              />
            </div>
            <p className="text-xs text-muted-foreground mt-4">
              Can't scan? Enter this code manually:
            </p>
            <code className="block bg-background p-2 rounded mt-2 text-xs font-mono break-all">
              {setupData.secret}
            </code>
          </div>
          <Button
            onClick={() => setStep("verify")}
            className="w-full"
          >
            Next: Verify Code
          </Button>
        </div>
      )}

      {/* Verify Step */}
      {step === "verify" && (
        <div className="space-y-4">
          <div className="bg-muted p-4 rounded-lg">
            <p className="text-sm font-medium text-foreground mb-3">
              Step 2: Verify Code
            </p>
            <p className="text-sm text-muted-foreground mb-4">
              Enter the 6-digit code from your authenticator app:
            </p>
            <Input
              type="text"
              maxLength={6}
              placeholder="000000"
              value={verificationCode}
              onChange={(e) =>
                setVerificationCode(e.target.value.replace(/\D/g, ""))
              }
              disabled={verify2FAMutation.isPending}
              className="text-center text-2xl tracking-widest"
            />
          </div>
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => {
                setStep("setup");
                setVerificationCode("");
              }}
              disabled={verify2FAMutation.isPending}
              className="flex-1"
            >
              Back
            </Button>
            <Button
              onClick={handleVerify}
              disabled={verify2FAMutation.isPending}
              className="flex-1"
            >
              {verify2FAMutation.isPending ? (
                <>
                  <Spinner size="sm" />
                  Verifying...
                </>
              ) : (
                "Verify"
              )}
            </Button>
          </div>
        </div>
      )}

      {/* Backup Codes Step */}
      {step === "backup" && setupData.backup_codes && (
        <div className="space-y-4">
          <div className="bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800 p-4 rounded-lg">
            <p className="text-sm font-medium text-yellow-900 dark:text-yellow-100 mb-2">
              ⚠️ Save Your Backup Codes
            </p>
            <p className="text-sm text-yellow-800 dark:text-yellow-200 mb-4">
              Save these codes in a safe place. You can use them to access your
              account if you lose access to your authenticator app.
            </p>
          </div>

          <div className="bg-muted p-4 rounded-lg space-y-2">
            {setupData.backup_codes.map((code, index) => (
              <div
                key={index}
                className="flex items-center justify-between bg-background p-3 rounded"
              >
                <code className="font-mono text-sm">{code}</code>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => copyToClipboard(code, index)}
                >
                  {copiedIndex === index ? (
                    <CheckIcon size={16} className="text-green-600" />
                  ) : (
                    <CopyIcon size={16} />
                  )}
                </Button>
              </div>
            ))}
          </div>

          <Button onClick={() => setStep("idle")} className="w-full">
            Done
          </Button>
        </div>
      )}

      {/* Disable 2FA Step */}
      {step === "disable" && (
        <div className="space-y-4">
          <Alert variant="warning">
            <AlertTriangleIcon size={20} />
            <p>
              Disabling 2FA will reduce your account security. You'll need to
              provide your password and current 2FA code to confirm.
            </p>
          </Alert>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Password *
            </label>
            <Input
              type="password"
              value={disablePassword}
              onChange={(e) => setDisablePassword(e.target.value)}
              placeholder="Enter your password"
              disabled={disable2FAMutation.isPending}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              2FA Code *
            </label>
            <Input
              type="text"
              maxLength={6}
              placeholder="000000"
              value={disableCode}
              onChange={(e) =>
                setDisableCode(e.target.value.replace(/\D/g, ""))
              }
              disabled={disable2FAMutation.isPending}
              className="text-center text-2xl tracking-widest"
            />
          </div>

          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => {
                setStep("idle");
                setDisablePassword("");
                setDisableCode("");
              }}
              disabled={disable2FAMutation.isPending}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDisable}
              disabled={disable2FAMutation.isPending}
              className="flex-1"
            >
              {disable2FAMutation.isPending ? (
                <>
                  <Spinner size="sm" />
                  Disabling...
                </>
              ) : (
                "Disable 2FA"
              )}
            </Button>
          </div>
        </div>
      )}

      {/* Status Display */}
      {step === "idle" && (
        <div className="bg-muted p-4 rounded-lg">
          <div className="flex items-center gap-3">
            <ShieldIcon
              size={24}
              className={
                is2FAEnabled ? "text-green-600" : "text-muted-foreground"
              }
            />
            <div>
              <p className="text-sm font-medium text-foreground">
                {is2FAEnabled ? "2FA Enabled" : "2FA Disabled"}
              </p>
              <p className="text-xs text-muted-foreground">
                {is2FAEnabled
                  ? "Your account is protected with two-factor authentication"
                  : "Enable 2FA to add an extra layer of security"}
              </p>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}

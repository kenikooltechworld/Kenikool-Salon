import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import {
  CheckIcon,
  AlertTriangleIcon,
  PhoneIcon,
  RefreshCwIcon,
} from "@/components/icons";
import {
  useVerifyPhone,
  useConfirmPhoneVerification,
} from "@/lib/api/hooks/useSettings";

interface PhoneVerificationFlowProps {
  isPhoneVerified?: boolean;
  currentPhone?: string;
}

export function PhoneVerificationFlow({
  isPhoneVerified = false,
  currentPhone,
}: PhoneVerificationFlowProps) {
  const [step, setStep] = useState<"idle" | "input" | "verify">("idle");
  const [phoneNumber, setPhoneNumber] = useState(currentPhone || "");
  const [verificationCode, setVerificationCode] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const verifyPhoneMutation = useVerifyPhone({
    onSuccess: () => {
      setStep("verify");
      setSuccessMessage("Verification code sent to your phone");
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to send verification code"
      );
    },
  });

  const confirmPhoneMutation = useConfirmPhoneVerification({
    onSuccess: () => {
      setSuccessMessage("Phone number verified successfully!");
      setStep("idle");
      setPhoneNumber("");
      setVerificationCode("");
      setTimeout(() => setSuccessMessage(""), 3000);
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Invalid verification code"
      );
    },
  });

  const handleVerifyPhone = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");

    if (!phoneNumber) {
      setErrorMessage("Phone number is required");
      return;
    }

    // Basic phone validation (Nigerian format)
    const phoneRegex = /^(\+234|0)[0-9]{10}$/;
    if (!phoneRegex.test(phoneNumber.replace(/\s/g, ""))) {
      setErrorMessage("Please enter a valid Nigerian phone number");
      return;
    }

    verifyPhoneMutation.mutate({ phone_number: phoneNumber });
  };

  const handleConfirmPhone = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");

    if (!verificationCode) {
      setErrorMessage("Verification code is required");
      return;
    }

    if (verificationCode.length !== 6) {
      setErrorMessage("Verification code must be 6 digits");
      return;
    }

    confirmPhoneMutation.mutate({ code: verificationCode });
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-foreground">
          Phone Number
        </h2>
        {isPhoneVerified && (
          <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-100 text-xs rounded-full font-medium">
            ✓ Verified
          </span>
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

      {step === "idle" && (
        <div className="space-y-4">
          {currentPhone && (
            <div className="bg-muted p-4 rounded-lg">
              <p className="text-sm font-medium text-foreground mb-1">
                Current Phone
              </p>
              <p className="text-sm text-muted-foreground">{currentPhone}</p>
            </div>
          )}

          <Button
            onClick={() => setStep("input")}
            className="w-full"
          >
            {currentPhone ? "Change Phone Number" : "Add Phone Number"}
          </Button>
        </div>
      )}

      {step === "input" && (
        <form onSubmit={handleVerifyPhone} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              <PhoneIcon size={16} className="inline mr-2" />
              Phone Number *
            </label>
            <Input
              type="tel"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              placeholder="+234 (0) 123 456 7890"
              disabled={verifyPhoneMutation.isPending}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Nigerian phone numbers only (e.g., +234 or 0)
            </p>
          </div>

          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setStep("idle");
                setPhoneNumber(currentPhone || "");
                setErrorMessage("");
              }}
              disabled={verifyPhoneMutation.isPending}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={verifyPhoneMutation.isPending}
              className="flex-1"
            >
              {verifyPhoneMutation.isPending ? (
                <>
                  <Spinner size="sm" />
                  Sending...
                </>
              ) : (
                "Send Code"
              )}
            </Button>
          </div>
        </form>
      )}

      {step === "verify" && (
        <form onSubmit={handleConfirmPhone} className="space-y-4">
          <Alert variant="info">
            <CheckIcon size={20} />
            <p>
              We've sent a verification code to <strong>{phoneNumber}</strong>
            </p>
          </Alert>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Verification Code *
            </label>
            <Input
              type="text"
              maxLength={6}
              value={verificationCode}
              onChange={(e) =>
                setVerificationCode(e.target.value.replace(/\D/g, ""))
              }
              placeholder="000000"
              disabled={confirmPhoneMutation.isPending}
              className="text-center text-2xl tracking-widest"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Check your SMS for the 6-digit code
            </p>
          </div>

          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setStep("input");
                setVerificationCode("");
                setErrorMessage("");
              }}
              disabled={confirmPhoneMutation.isPending}
              className="flex-1"
            >
              Back
            </Button>
            <Button
              type="submit"
              disabled={confirmPhoneMutation.isPending}
              className="flex-1"
            >
              {confirmPhoneMutation.isPending ? (
                <>
                  <Spinner size="sm" />
                  Verifying...
                </>
              ) : (
                "Verify"
              )}
            </Button>
          </div>

          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => verifyPhoneMutation.mutate({ phone_number: phoneNumber })}
            disabled={verifyPhoneMutation.isPending}
            className="w-full"
          >
            <RefreshCwIcon size={16} className="mr-2" />
            Resend Code
          </Button>
        </form>
      )}
    </Card>
  );
}

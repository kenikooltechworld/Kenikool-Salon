import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import {
  CheckIcon,
  AlertTriangleIcon,
  MailIcon,
  RefreshCwIcon,
} from "@/components/icons";
import {
  useChangeEmail,
  useVerifyNewEmail,
} from "@/lib/api/hooks/useSettings";

interface EmailChangeFlowProps {
  currentEmail: string;
}

export function EmailChangeFlow({ currentEmail }: EmailChangeFlowProps) {
  const [step, setStep] = useState<"idle" | "change" | "verify">("idle");
  const [newEmail, setNewEmail] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const changeEmailMutation = useChangeEmail({
    onSuccess: () => {
      setStep("verify");
      setSuccessMessage("Verification email sent to your new email address");
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to change email"
      );
    },
  });

  const verifyEmailMutation = useVerifyNewEmail({
    onSuccess: () => {
      setSuccessMessage("Email changed successfully!");
      setStep("idle");
      setNewEmail("");
      setVerificationCode("");
      setTimeout(() => setSuccessMessage(""), 3000);
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Invalid verification code"
      );
    },
  });

  const handleChangeEmail = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");

    if (!newEmail) {
      setErrorMessage("New email is required");
      return;
    }

    if (newEmail === currentEmail) {
      setErrorMessage("New email must be different from current email");
      return;
    }

    changeEmailMutation.mutate({ new_email: newEmail });
  };

  const handleVerifyEmail = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");

    if (!verificationCode) {
      setErrorMessage("Verification code is required");
      return;
    }

    verifyEmailMutation.mutate({ token: verificationCode });
  };

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-foreground mb-6">
        Email Address
      </h2>

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
          <div className="bg-muted p-4 rounded-lg">
            <p className="text-sm font-medium text-foreground mb-1">
              Current Email
            </p>
            <p className="text-sm text-muted-foreground">{currentEmail}</p>
          </div>

          <Button
            onClick={() => setStep("change")}
            className="w-full"
          >
            Change Email
          </Button>
        </div>
      )}

      {step === "change" && (
        <form onSubmit={handleChangeEmail} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              <MailIcon size={16} className="inline mr-2" />
              New Email Address *
            </label>
            <Input
              type="email"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              placeholder="Enter new email address"
              disabled={changeEmailMutation.isPending}
            />
          </div>

          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setStep("idle");
                setNewEmail("");
                setErrorMessage("");
              }}
              disabled={changeEmailMutation.isPending}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={changeEmailMutation.isPending}
              className="flex-1"
            >
              {changeEmailMutation.isPending ? (
                <>
                  <Spinner size="sm" />
                  Sending...
                </>
              ) : (
                "Send Verification Code"
              )}
            </Button>
          </div>
        </form>
      )}

      {step === "verify" && (
        <form onSubmit={handleVerifyEmail} className="space-y-4">
          <Alert variant="info">
            <CheckIcon size={20} />
            <p>
              We've sent a verification code to <strong>{newEmail}</strong>
            </p>
          </Alert>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Verification Code *
            </label>
            <Input
              type="text"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
              placeholder="Enter verification code"
              disabled={verifyEmailMutation.isPending}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Check your email for the verification code
            </p>
          </div>

          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setStep("change");
                setVerificationCode("");
                setErrorMessage("");
              }}
              disabled={verifyEmailMutation.isPending}
              className="flex-1"
            >
              Back
            </Button>
            <Button
              type="submit"
              disabled={verifyEmailMutation.isPending}
              className="flex-1"
            >
              {verifyEmailMutation.isPending ? (
                <>
                  <Spinner size="sm" />
                  Verifying...
                </>
              ) : (
                "Verify Email"
              )}
            </Button>
          </div>

          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => changeEmailMutation.mutate({ new_email: newEmail })}
            disabled={changeEmailMutation.isPending}
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

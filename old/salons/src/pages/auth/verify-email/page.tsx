import { useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";
import { useVerifyEmail, useResendVerification } from "@/lib/api/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const email = searchParams.get("email") || "";
  const [code, setCode] = useState("");
  const [success, setSuccess] = useState(false);

  const { mutate: verifyEmail, isPending: verifying } = useVerifyEmail({
    onSuccess: (data: { message?: string }) => {
      setSuccess(true);
      showToast({
        title: "Email Verified!",
        description:
          data.message || "Your email has been verified successfully",
        variant: "success",
      });
      // Redirect to login after 2 seconds
      setTimeout(() => {
        navigate("/login");
      }, 2000);
    },
    onError: (error: {
      response?: { data?: { detail?: string; message?: string } };
      message?: string;
    }) => {
      const errorMessage =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        "Email verification failed";
      showToast({
        title: "Verification Failed",
        description: errorMessage,
        variant: "error",
      });
    },
  });

  const { mutate: resendVerification, isPending: resending } =
    useResendVerification({
      onSuccess: (data: { message?: string }) => {
        showToast({
          title: "Code Sent!",
          description: data.message || "Verification code sent successfully",
          variant: "success",
        });
      },
      onError: (error: {
        response?: { data?: { message?: string } };
        message?: string;
      }) => {
        const errorMessage =
          error.response?.data?.message ||
          error.message ||
          "Failed to send code";
        showToast({
          title: "Failed to Send Code",
          description: errorMessage,
          variant: "error",
        });
      },
    });

  const handleVerify = () => {
    if (code.length !== 6) {
      showToast({
        title: "Invalid Code",
        description: "Please enter a 6-digit code",
        variant: "error",
      });
      return;
    }
    verifyEmail({ code });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md p-8">
        {/* Success state */}
        {success && (
          <div className="text-center">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-10 h-10 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <h1 className="text-3xl font-bold text-foreground mb-2">
              Email Verified!
            </h1>
            <p className="text-muted-foreground mb-6">
              Your email has been verified successfully. Redirecting to login...
            </p>
            <Link
              to="/login"
              className="text-primary font-medium hover:underline"
            >
              Go to Login
            </Link>
          </div>
        )}

        {/* Verification code input */}
        {!success && (
          <>
            <div className="text-center mb-8">
              <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-10 h-10 text-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <h1 className="text-3xl font-bold text-foreground mb-2">
                Verify Your Email
              </h1>
              <p className="text-muted-foreground mb-4">
                We&apos;ve sent a verification code to
              </p>
              <p className="text-lg font-semibold text-foreground">{email}</p>
            </div>

            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Verification Code
                </label>
                <input
                  type="text"
                  maxLength={6}
                  placeholder="000000"
                  value={code}
                  onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
                  className="w-full px-4 py-2 text-center text-2xl font-bold tracking-widest border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <p className="text-xs text-muted-foreground mt-2">
                  Enter the 6-digit code from your email
                </p>
              </div>

              <Button
                onClick={handleVerify}
                fullWidth
                loading={verifying}
                disabled={code.length !== 6}
              >
                Verify Code
              </Button>

              <p className="text-sm text-muted-foreground text-center">
                Didn&apos;t receive the code?
              </p>

              <Button
                onClick={() => resendVerification({ email })}
                variant="outline"
                fullWidth
                loading={resending}
              >
                Resend Code
              </Button>
            </div>

            <div className="text-center space-y-3">
              <p className="text-sm text-muted-foreground">
                Wrong email address?{" "}
                <Link
                  to="/register"
                  className="text-primary font-medium hover:underline"
                >
                  Register again
                </Link>
              </p>
              <p className="text-sm text-muted-foreground">
                Need help?{" "}
                <Link
                  to="/contact"
                  className="text-primary font-medium hover:underline"
                >
                  Contact support
                </Link>
              </p>
            </div>
          </>
        )}
      </Card>
    </div>
  );
}

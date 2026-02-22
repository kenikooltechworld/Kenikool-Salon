import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Alert } from "@/components/ui/alert";
import { useToast } from "@/components/ui/toast";
import { useResendVerification } from "@/lib/api/hooks/useAuth";

export default function ResendVerificationPage() {
  const [searchParams] = useSearchParams();
  const { showToast } = useToast();
  const emailParam = searchParams.get("email") || "";
  const [email, setEmail] = useState(emailParam);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const { mutate: resendVerification, isPending: loading } =
    useResendVerification({
      onSuccess: (data) => {
        setSuccess(true);
        setError("");
        showToast({
          title: "Email Sent!",
          description: data.message,
          variant: "success",
        });
      },
      onError: (error) => {
        const errorMessage =
          error.response?.data?.message ||
          error.message ||
          "Failed to send email";
        setError(errorMessage);
        showToast({
          title: "Failed to Send Email",
          description: errorMessage,
          variant: "error",
        });
      },
    });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess(false);

    if (!email) {
      setError("Please enter your email address");
      return;
    }

    resendVerification({ email });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-primary"
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
          <p className="text-muted-foreground">
            Enter your email address to receive a new verification link
          </p>
        </div>

        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

        {success && (
          <Alert variant="success" className="mb-6">
            <div className="space-y-2">
              <p className="font-medium">Verification email sent!</p>
              <p className="text-sm">
                Please check your inbox and click the verification link.
                Don&apos;t forget to check your spam folder.
              </p>
            </div>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <Label htmlFor="email" required>
              Email Address
            </Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              disabled={loading}
              className="mt-2"
            />
          </div>

          <Button type="submit" fullWidth loading={loading}>
            {success ? "Resend Verification Email" : "Send Verification Email"}
          </Button>
        </form>

        <div className="mt-6 space-y-3 text-center">
          <p className="text-sm text-muted-foreground">
            Already verified?{" "}
            <Link
              to="/login"
              className="text-primary font-medium hover:underline"
            >
              Sign in
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
      </Card>
    </div>
  );
}

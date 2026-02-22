import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Alert } from "@/components/ui/alert";
import { useToast } from "@/components/ui/toast";
import { ArrowLeftIcon } from "@/components/icons";
import { useForgotPassword } from "@/lib/api/hooks/useAuth";

export default function ForgotPasswordPage() {
  const { showToast } = useToast();
  const [email, setEmail] = useState("");
  const [success, setSuccess] = useState(false);

  const { mutate: forgotPassword, isPending: loading } = useForgotPassword({
    onSuccess: (data) => {
      setSuccess(true);
      showToast({
        title: "Email Sent!",
        description:
          data.message || "Check your inbox for password reset instructions",
        variant: "success",
      });
    },
    onError: (error) => {
      const errorMessage =
        error.response?.data?.message ||
        error.message ||
        "Failed to send reset email";
      showToast({
        title: "Failed to Send Email",
        description: errorMessage,
        variant: "error",
      });
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email) {
      showToast({
        title: "Email Required",
        description: "Please enter your email address",
        variant: "warning",
      });
      return;
    }

    forgotPassword({ email });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--background)] p-4">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-[var(--foreground)] mb-2">
            Forgot Password?
          </h1>
          <p className="text-[var(--muted-foreground)]">
            Enter your email and we'll send you reset instructions
          </p>
        </div>

        {success ? (
          <Alert variant="success" className="mb-6">
            <div className="space-y-2">
              <p className="font-semibold">Check your email</p>
              <p className="text-sm">
                We&apos;ve sent password reset instructions to {email}
              </p>
            </div>
          </Alert>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
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
              Send Reset Link
            </Button>
          </form>
        )}

        <div className="mt-6 text-center">
          <Link
            to="/login"
            className="inline-flex items-center gap-2 text-sm text-[var(--primary)] hover:underline"
          >
            <ArrowLeftIcon size={16} />
            Back to login
          </Link>
        </div>
      </Card>
    </div>
  );
}

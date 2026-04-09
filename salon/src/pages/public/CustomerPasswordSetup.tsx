import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiClient } from "@/lib/utils/api";
import { useToast } from "@/components/ui/toast";
import { PasswordStrengthIndicator } from "@/components/auth/PasswordStrengthIndicator";

export default function CustomerPasswordSetup() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const token = searchParams.get("token");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token) {
      showToast({
        title: "Invalid Link",
        description: "The setup link is invalid or missing.",
        variant: "error",
      });
      return;
    }

    if (password !== confirmPassword) {
      showToast({
        title: "Passwords Don't Match",
        description: "Please make sure both passwords match.",
        variant: "error",
      });
      return;
    }

    if (password.length < 8) {
      showToast({
        title: "Password Too Short",
        description: "Password must be at least 8 characters long.",
        variant: "error",
      });
      return;
    }

    setIsLoading(true);

    try {
      const { data } = await apiClient.post(
        "/public/customer-auth/setup-password",
        {
          token,
          password,
        },
      );

      // Store the access token
      localStorage.setItem("customer_token", data.access_token);

      showToast({
        title: "Success!",
        description:
          "Your password has been set up. Welcome to the customer portal!",
        variant: "success",
      });

      // Redirect to customer portal after a short delay
      setTimeout(() => navigate("/customer/portal"), 1500);
    } catch (error: any) {
      showToast({
        title: "Setup Failed",
        description:
          error.response?.data?.detail ||
          "Failed to set up password. The link may have expired.",
        variant: "error",
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <Card className="w-full max-w-md p-6">
          <h1 className="text-2xl font-bold text-center mb-4">Invalid Link</h1>
          <p className="text-center text-muted-foreground">
            The password setup link is invalid or missing. Please contact the
            business for a new invitation.
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md p-6">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold mb-2">Set Up Your Password</h1>
          <p className="text-muted-foreground">
            Create a password to access your customer portal
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              minLength={8}
            />
            <PasswordStrengthIndicator password={password} />
          </div>

          <div>
            <Label htmlFor="confirmPassword">Confirm Password</Label>
            <Input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm your password"
              required
              minLength={8}
            />
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Setting Up..." : "Set Up Password"}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-muted-foreground">
            Already have an account?{" "}
            <a
              href="/customer/login"
              className="text-primary hover:underline font-medium"
            >
              Sign in
            </a>
          </p>
        </div>
      </Card>
    </div>
  );
}

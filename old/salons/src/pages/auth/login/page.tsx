import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useLogin } from "@/lib/api/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Alert } from "@/components/ui/alert";
import { useToast } from "@/components/ui/toast";
import { EyeIcon, EyeOffIcon } from "@/components/icons";

export default function LoginPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState("");

  const { mutate: login, isPending: loading } = useLogin({
    onSuccess: (data) => {
      // Tokens are now stored as httpOnly cookies by the backend
      // No need to store them in localStorage
      console.log("✅ Login successful - user:", data.user.email);

      showToast({
        title: "Welcome back!",
        description: `Logged in as ${data.user.email}`,
        variant: "success",
      });

      // Redirect to dashboard after a short delay
      setTimeout(() => {
        // Check if user needs onboarding (new user)
        // For now, redirect to dashboard - onboarding can be triggered from there
        navigate("/dashboard");
      }, 500);
    },
    onError: (error) => {
      const errorMessage =
        error.response?.data?.message || error.message || "Login failed";
      setError(errorMessage);
      showToast({
        title: "Login Failed",
        description: errorMessage,
        variant: "error",
      });
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("=== LOGIN FORM SUBMITTED ===");
    console.log("Email:", email);
    console.log("Password:", password ? "***" : "(empty)");
    setError("");

    if (!email || !password) {
      console.log("ERROR: Missing email or password");
      setError("Please in all fields");
      showToast({
        title: "Missing Information",
        description: "Please in all fields",
        variant: "warning",
      });
      return;
    }

    // Show loading toast
    showToast({
      title: "Signing In...",
      description: "Please wait",
      variant: "info",
    });

    console.log("Calling login API...");
    login({ email, password });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--background)] p-4">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-[var(--foreground)] mb-2">
            Welcome Back
          </h1>
          <p className="text-[var(--muted-foreground)]">
            Sign in to your salon dashboard
          </p>
        </div>

        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

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

          <div>
            <Label htmlFor="password" required>
              Password
            </Label>
            <div className="relative mt-2">
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                disabled={loading}
                className="pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors cursor-pointer"
                tabIndex={-1}
              >
                {showPassword ? (
                  <EyeOffIcon className="w-5 h-5" />
                ) : (
                  <EyeIcon className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="rounded border-[var(--border)] cursor-pointer"
              />
              <span className="text-[var(--muted-foreground)]">
                Remember me
              </span>
            </label>
            <Link
              to="/forgot-password"
              className="text-sm text-[var(--primary)] hover:underline"
            >
              Forgot password?
            </Link>
          </div>

          <Button type="submit" fullWidth loading={loading}>
            Sign In
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-[var(--muted-foreground)]">
            Don&apos;t have an account?{" "}
            <Link
              to="/register"
              className="text-[var(--primary)] font-medium hover:underline"
            >
              Sign up
            </Link>
          </p>
        </div>
      </Card>
    </div>
  );
}

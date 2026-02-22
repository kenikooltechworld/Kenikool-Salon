import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface AccountRegistrationProps {
  onSuccess?: (userId: string) => void;
  onCancel?: () => void;
  prefilledEmail?: string;
  prefilledName?: string;
}

export function AccountRegistration({
  onSuccess,
  onCancel,
  prefilledEmail,
  prefilledName,
}: AccountRegistrationProps) {
  const { toast } = useToast();
  const [step, setStep] = useState<"info" | "password" | "verify">("info");
  const [email, setEmail] = useState(prefilledEmail || "");
  const [fullName, setFullName] = useState(prefilledName || "");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [passwordStrength, setPasswordStrength] = useState(0);

  const registerMutation = useMutation({
    mutationFn: async () => {
      if (password !== confirmPassword) {
        throw new Error("Passwords do not match");
      }

      if (password.length < 8) {
        throw new Error("Password must be at least 8 characters");
      }

      const response = await apiClient.post("/api/auth/register", {
        email: email,
        password: password,
        full_name: fullName,
      });

      return response.data;
    },
    onSuccess: (data) => {
      toast("Account created! Check your email for verification.", "success");
      setStep("verify");
    },
    onError: (error: any) => {
      toast(
        error.message || error.response?.data?.detail || "Registration failed",
        "error"
      );
    },
  });

  const verifyEmailMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post("/api/auth/verify-email", {
        token: verificationCode,
      });
      return response.data;
    },
    onSuccess: (data) => {
      toast("Email verified successfully!", "success");
      onSuccess?.(data.user.id);
    },
    onError: (error: any) => {
      toast(
        error.response?.data?.detail || "Verification failed",
        "error"
      );
    },
  });

  const calculatePasswordStrength = (pwd: string) => {
    let strength = 0;
    if (pwd.length >= 8) strength++;
    if (pwd.length >= 12) strength++;
    if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength++;
    if (/\d/.test(pwd)) strength++;
    if (/[^a-zA-Z\d]/.test(pwd)) strength++;
    setPasswordStrength(strength);
  };

  const handlePasswordChange = (pwd: string) => {
    setPassword(pwd);
    calculatePasswordStrength(pwd);
  };

  const handleRegister = async () => {
    if (!email || !fullName) {
      toast("Please fill in all fields", "error");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      toast("Please enter a valid email", "error");
      return;
    }

    await registerMutation.mutateAsync();
  };

  const handleVerify = async () => {
    if (!verificationCode.trim()) {
      toast("Please enter the verification code", "error");
      return;
    }

    await verifyEmailMutation.mutateAsync();
  };

  return (
    <div className="space-y-6">
      {/* Step 1: Account Information */}
      {step === "info" && (
        <Card>
          <CardHeader>
            <CardTitle>Create Your Account</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label required>Full Name</Label>
              <Input
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Enter your full name"
                className="mt-1"
              />
            </div>

            <div>
              <Label required>Email Address</Label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                className="mt-1"
              />
            </div>

            <div className="flex gap-2 pt-4">
              {onCancel && (
                <Button onClick={onCancel} variant="outline" className="flex-1">
                  Cancel
                </Button>
              )}
              <Button
                onClick={() => setStep("password")}
                className="flex-1"
                disabled={!email || !fullName}
              >
                Next
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Password */}
      {step === "password" && (
        <Card>
          <CardHeader>
            <CardTitle>Set Your Password</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label required>Password</Label>
              <Input
                type="password"
                value={password}
                onChange={(e) => handlePasswordChange(e.target.value)}
                placeholder="At least 8 characters"
                className="mt-1"
              />
              <div className="mt-2 space-y-1">
                <div className="flex gap-1">
                  {[...Array(5)].map((_, i) => (
                    <div
                      key={i}
                      className={`h-1 flex-1 rounded ${
                        i < passwordStrength
                          ? "bg-green-500"
                          : "bg-[var(--muted)]"
                      }`}
                    />
                  ))}
                </div>
                <p className="text-xs text-[var(--muted-foreground)]">
                  {passwordStrength === 0 && "Very weak"}
                  {passwordStrength === 1 && "Weak"}
                  {passwordStrength === 2 && "Fair"}
                  {passwordStrength === 3 && "Good"}
                  {passwordStrength === 4 && "Strong"}
                  {passwordStrength === 5 && "Very strong"}
                </p>
              </div>
            </div>

            <div>
              <Label required>Confirm Password</Label>
              <Input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter your password"
                className="mt-1"
              />
              {password && confirmPassword && password !== confirmPassword && (
                <p className="text-xs text-red-600 mt-1">
                  Passwords do not match
                </p>
              )}
            </div>

            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-xs text-blue-900">
                Password requirements:
              </p>
              <ul className="text-xs text-blue-800 mt-1 space-y-1">
                <li>✓ At least 8 characters</li>
                <li>✓ Mix of uppercase and lowercase letters</li>
                <li>✓ At least one number</li>
                <li>✓ At least one special character</li>
              </ul>
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                onClick={() => setStep("info")}
                variant="outline"
                className="flex-1"
              >
                Back
              </Button>
              <Button
                onClick={handleRegister}
                className="flex-1"
                disabled={
                  registerMutation.isPending ||
                  !password ||
                  !confirmPassword ||
                  password !== confirmPassword
                }
              >
                {registerMutation.isPending ? "Creating..." : "Create Account"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Email Verification */}
      {step === "verify" && (
        <Card>
          <CardHeader>
            <CardTitle>Verify Your Email</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-900">
                We've sent a verification code to <strong>{email}</strong>
              </p>
              <p className="text-sm text-blue-800 mt-2">
                Check your email and enter the code below.
              </p>
            </div>

            <div>
              <Label required>Verification Code</Label>
              <Input
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                placeholder="Enter 6-digit code"
                className="mt-1"
                maxLength={6}
              />
            </div>

            <Button
              onClick={handleVerify}
              className="w-full"
              disabled={
                verifyEmailMutation.isPending || !verificationCode.trim()
              }
            >
              {verifyEmailMutation.isPending ? "Verifying..." : "Verify Email"}
            </Button>

            <p className="text-xs text-[var(--muted-foreground)] text-center">
              Didn't receive the code?{" "}
              <button className="text-[var(--primary)] hover:underline">
                Resend
              </button>
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

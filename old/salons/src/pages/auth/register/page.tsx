import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useRegister } from "@/lib/api/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Alert } from "@/components/ui/alert";
import { useToast } from "@/components/ui/toast";
import { EyeIcon, EyeOffIcon } from "@/components/icons";

export default function RegisterPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    businessName: "",
    ownerName: "",
    phone: "",
    address: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [salonNameError, setSalonNameError] = useState("");

  const { mutate: register, isPending: loading } = useRegister({
    onSuccess: async (data) => {
      console.log("=== REGISTRATION COMPLETED ===");
      console.log("Response data:", data);
      // Tokens are already stored by the hook

      // Store user data
      localStorage.setItem("user", JSON.stringify(data.user));

      showToast({
        title: "Account Created!",
        description: "Please check your email to verify your account",
        variant: "success",
      });

      // Redirect to verification pending page
      navigate(`/verify-email?email=${encodeURIComponent(formData.email)}`);
    },
    onError: (error) => {
      console.error("=== REGISTRATION ERROR ===");
      console.error("Error message:", error.message);
      console.error("Error response:", error.response);
      console.error("Full error object:", JSON.stringify(error, null, 2));

      const errorMessage =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        "Registration failed";

      // Check if this is an unverified email error
      if (errorMessage.startsWith("UNVERIFIED_EMAIL:")) {
        const cleanMessage = errorMessage.replace("UNVERIFIED_EMAIL:", "");
        showToast({
          title: "Email Not Verified",
          description: cleanMessage,
          variant: "warning",
        });
        // Redirect to resend verification page with email
        navigate(
          `/resend-verification?email=${encodeURIComponent(formData.email)}`,
        );
        return;
      }

      setError(errorMessage);
      showToast({
        title: "Registration Failed",
        description: errorMessage,
        variant: "error",
      });
    },
  });

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    // Clear salon name error when user types
    if (field === "businessName") {
      setSalonNameError("");
    }

    // Calculate password strength
    if (field === "password") {
      let strength = 0;
      if (value.length >= 8) strength++;
      if (/[a-z]/.test(value) && /[A-Z]/.test(value)) strength++;
      if (/\d/.test(value)) strength++;
      if (/[^a-zA-Z0-9]/.test(value)) strength++;
      setPasswordStrength(strength);
    }
  };

  const validateForm = () => {
    if (
      !formData.email ||
      !formData.password ||
      !formData.businessName ||
      !formData.ownerName ||
      !formData.phone
    ) {
      setError("Please in all required fields");
      return false;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return false;
    }

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters");
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSalonNameError("");

    if (!validateForm()) return;

    console.log("=== FRONTEND REGISTRATION START ===");
    console.log("Form data:", {
      salon_name: formData.businessName,
      owner_name: formData.ownerName,
      email: formData.email,
      phone: formData.phone,
      address: formData.address || undefined,
    });

    try {
      console.log("Calling register API...");
      register({
        salon_name: formData.businessName,
        owner_name: formData.ownerName,
        email: formData.email,
        phone: formData.phone,
        password: formData.password,
        address: formData.address || undefined,
      });
      console.log("=== FRONTEND REGISTRATION SUCCESS ===");
    } catch (err) {
      console.error("=== FRONTEND REGISTRATION ERROR ===");
      console.error("Error details:", err);
      // Error is already handled by the mutation's onError callback
      // But we can also check if it's a salon name error and show it specifically
      const errorMessage =
        err instanceof Error ? err.message : "An error occurred";
      if (errorMessage.toLowerCase().includes("salon name")) {
        setSalonNameError(errorMessage);
      }
    }
  };

  const strengthColors = ["#ef4444", "#f59e0b", "#eab308", "#22c55e"];
  const strengthLabels = ["Weak", "Fair", "Good", "Strong"];

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--background)] p-4">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-[var(--foreground)] mb-2">
            Create Your Account
          </h1>
          <p className="text-[var(--muted-foreground)]">
            Start managing your salon today
          </p>
        </div>

        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <Label htmlFor="businessName" required>
              Salon Name
            </Label>
            <Input
              id="businessName"
              type="text"
              value={formData.businessName}
              onChange={(e) => handleChange("businessName", e.target.value)}
              placeholder="Your Salon Name"
              disabled={loading}
              className="mt-2"
            />
            {salonNameError && (
              <p className="text-xs text-[var(--error)] mt-1">
                {salonNameError}
              </p>
            )}
            <p className="text-xs text-[var(--muted-foreground)] mt-1">
              Choose a unique name for your salon. If you have multiple
              locations, include the area (e.g., &quot;Beauty Salon -
              Lekki&quot;)
            </p>
          </div>

          <div>
            <Label htmlFor="ownerName" required>
              Owner Name
            </Label>
            <Input
              id="ownerName"
              type="text"
              value={formData.ownerName}
              onChange={(e) => handleChange("ownerName", e.target.value)}
              placeholder="Your Full Name"
              disabled={loading}
              className="mt-2"
            />
          </div>

          <div>
            <Label htmlFor="phone" required>
              Phone Number
            </Label>
            <Input
              id="phone"
              type="tel"
              value={formData.phone}
              onChange={(e) => handleChange("phone", e.target.value)}
              placeholder="+234 800 000 0000"
              disabled={loading}
              className="mt-2"
            />
          </div>

          <div>
            <Label htmlFor="email" required>
              Email Address
            </Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => handleChange("email", e.target.value)}
              placeholder="you@example.com"
              disabled={loading}
              className="mt-2"
            />
          </div>

          <div>
            <Label htmlFor="address">Address</Label>
            <Input
              id="address"
              type="text"
              value={formData.address}
              onChange={(e) => handleChange("address", e.target.value)}
              placeholder="123 Main Street, Lagos"
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
                value={formData.password}
                onChange={(e) => handleChange("password", e.target.value)}
                placeholder="Create a strong password"
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
            {formData.password && (
              <div className="mt-2">
                <div className="flex gap-1 mb-1">
                  {[0, 1, 2, 3].map((i) => (
                    <div
                      key={i}
                      className="h-1 flex-1 rounded-full transition-colors"
                      style={{
                        backgroundColor:
                          i < passwordStrength
                            ? strengthColors[passwordStrength - 1]
                            : "var(--muted)",
                      }}
                    />
                  ))}
                </div>
                <p className="text-xs text-[var(--muted-foreground)]">
                  Password strength:{" "}
                  <span
                    style={{
                      color:
                        passwordStrength > 0
                          ? strengthColors[passwordStrength - 1]
                          : "inherit",
                    }}
                  >
                    {passwordStrength > 0
                      ? strengthLabels[passwordStrength - 1]
                      : "Too short"}
                  </span>
                </p>
              </div>
            )}
          </div>

          <div>
            <Label htmlFor="confirmPassword" required>
              Confirm Password
            </Label>
            <div className="relative mt-2">
              <Input
                id="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                value={formData.confirmPassword}
                onChange={(e) =>
                  handleChange("confirmPassword", e.target.value)
                }
                placeholder="Re-enter your password"
                disabled={loading}
                className="pr-10"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors cursor-pointer"
                tabIndex={-1}
              >
                {showConfirmPassword ? (
                  <EyeOffIcon className="w-5 h-5" />
                ) : (
                  <EyeIcon className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>

          <div className="flex items-start gap-2">
            <input
              type="checkbox"
              required
              className="mt-1 rounded border-[var(--border)]"
            />
            <p className="text-xs text-[var(--muted-foreground)]">
              I agree to the{" "}
              <Link
                to="/terms"
                className="text-[var(--primary)] hover:underline"
              >
                Terms of Service
              </Link>{" "}
              and{" "}
              <Link
                to="/privacy"
                className="text-[var(--primary)] hover:underline"
              >
                Privacy Policy
              </Link>
            </p>
          </div>

          <Button type="submit" fullWidth loading={loading}>
            Create Account
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-[var(--muted-foreground)]">
            Already have an account?{" "}
            <Link
              to="/login"
              className="text-[var(--primary)] font-medium hover:underline"
            >
              Sign in
            </Link>
          </p>
        </div>
      </Card>
    </div>
  );
}

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import {
  isValidEmail,
  isValidPhone,
  isStrongPassword,
} from "@/lib/utils/validation";
import type { RegistrationData } from "@/hooks/useRegistration";

interface RegistrationFormProps {
  onSubmit: (data: RegistrationData) => Promise<void>;
  isLoading?: boolean;
  error?: string;
}

export function RegistrationForm({
  onSubmit,
  isLoading = false,
  error,
}: RegistrationFormProps) {
  const [formData, setFormData] = useState<RegistrationData>({
    salon_name: "",
    owner_name: "",
    email: "",
    phone: "",
    password: "",
    address: "",
    bank_account: "",
    referral_code: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [passwordStrength, setPasswordStrength] = useState<{
    score: number;
    message: string;
  }>({ score: 0, message: "" });

  const validateField = (name: string, value: string): string | null => {
    switch (name) {
      case "email":
        if (!value) return "Email is required";
        if (!isValidEmail(value)) return "Invalid email format";
        return null;

      case "phone":
        if (!value) return "Phone is required";
        if (!isValidPhone(value)) return "Invalid phone format";
        return null;

      case "salon_name":
        if (!value) return "Salon name is required";
        if (value.length < 3) return "Salon name must be at least 3 characters";
        if (value.length > 255)
          return "Salon name must be less than 255 characters";
        return null;

      case "owner_name":
        if (!value) return "Owner name is required";
        if (value.length < 2) return "Owner name must be at least 2 characters";
        if (value.length > 100)
          return "Owner name must be less than 100 characters";
        return null;

      case "password":
        if (!value) return "Password is required";
        if (!isStrongPassword(value)) {
          return "Password must be at least 8 characters with uppercase, lowercase, number, and special character";
        }
        return null;

      case "address":
        if (!value) return "Address is required";
        if (value.length < 5) return "Address must be at least 5 characters";
        if (value.length > 500)
          return "Address must be less than 500 characters";
        return null;

      case "bank_account":
        if (value && (value.length < 10 || value.length > 50)) {
          return "Bank account must be 10-50 characters";
        }
        return null;

      case "referral_code":
        if (value && !/^[a-zA-Z0-9]+$/.test(value)) {
          return "Referral code must be alphanumeric";
        }
        return null;

      default:
        return null;
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Validate field
    const error = validateField(name, value);
    setErrors((prev) => {
      if (error) {
        return { ...prev, [name]: error };
      } else {
        const { [name]: _, ...rest } = prev;
        return rest;
      }
    });

    // Check password strength
    if (name === "password") {
      const strength = calculatePasswordStrength(value);
      setPasswordStrength(strength);
    }
  };

  const calculatePasswordStrength = (
    password: string,
  ): { score: number; message: string } => {
    let score = 0;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[a-z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) score++;

    const messages = [
      "Very weak",
      "Weak",
      "Fair",
      "Good",
      "Strong",
      "Very strong",
    ];
    return { score, message: messages[score] || "Very weak" };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate all fields
    const newErrors: Record<string, string> = {};
    Object.entries(formData).forEach(([key, value]) => {
      if (key !== "bank_account" && key !== "referral_code") {
        const error = validateField(key, value);
        if (error) newErrors[key] = error;
      } else {
        const error = validateField(key, value || "");
        if (error) newErrors[key] = error;
      }
    });

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      await onSubmit(formData);
    } catch (err) {
      // Error is handled by parent component
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <Alert variant="error">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Salon Name */}
        <div className="space-y-2">
          <Label htmlFor="salon_name">Salon Name *</Label>
          <Input
            id="salon_name"
            name="salon_name"
            value={formData.salon_name}
            onChange={handleChange}
            placeholder="Enter your salon name"
            disabled={isLoading}
            className={errors.salon_name ? "border-red-500" : ""}
          />
          {errors.salon_name && (
            <p className="text-sm text-red-500">{errors.salon_name}</p>
          )}
        </div>

        {/* Owner Name */}
        <div className="space-y-2">
          <Label htmlFor="owner_name">Owner Name *</Label>
          <Input
            id="owner_name"
            name="owner_name"
            value={formData.owner_name}
            onChange={handleChange}
            placeholder="Enter your full name"
            disabled={isLoading}
            className={errors.owner_name ? "border-red-500" : ""}
          />
          {errors.owner_name && (
            <p className="text-sm text-red-500">{errors.owner_name}</p>
          )}
        </div>

        {/* Email */}
        <div className="space-y-2">
          <Label htmlFor="email">Email *</Label>
          <Input
            id="email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="your@email.com"
            disabled={isLoading}
            className={errors.email ? "border-red-500" : ""}
          />
          {errors.email && (
            <p className="text-sm text-red-500">{errors.email}</p>
          )}
        </div>

        {/* Phone */}
        <div className="space-y-2">
          <Label htmlFor="phone">Phone *</Label>
          <Input
            id="phone"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            placeholder="+234 123 456 7890"
            disabled={isLoading}
            className={errors.phone ? "border-red-500" : ""}
          />
          {errors.phone && (
            <p className="text-sm text-red-500">{errors.phone}</p>
          )}
        </div>

        {/* Password */}
        <div className="space-y-2">
          <Label htmlFor="password">Password *</Label>
          <Input
            id="password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Min 8 chars, uppercase, lowercase, number, special char"
            disabled={isLoading}
            className={errors.password ? "border-red-500" : ""}
          />
          {formData.password && (
            <div className="flex items-center gap-2">
              <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    passwordStrength.score <= 2
                      ? "bg-red-500"
                      : passwordStrength.score <= 4
                        ? "bg-yellow-500"
                        : "bg-green-500"
                  }`}
                  style={{
                    width: `${(passwordStrength.score / 6) * 100}%`,
                  }}
                />
              </div>
              <span className="text-xs text-gray-600">
                {passwordStrength.message}
              </span>
            </div>
          )}
          {errors.password && (
            <p className="text-sm text-red-500">{errors.password}</p>
          )}
        </div>
      </div>

      {/* Address */}
      <div className="space-y-2">
        <Label htmlFor="address">Address *</Label>
        <Textarea
          id="address"
          name="address"
          value={formData.address}
          onChange={handleChange}
          placeholder="Enter your salon address"
          disabled={isLoading}
          className={errors.address ? "border-red-500" : ""}
          rows={3}
        />
        {errors.address && (
          <p className="text-sm text-red-500">{errors.address}</p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Bank Account (Optional) */}
        <div className="space-y-2">
          <Label htmlFor="bank_account">Bank Account (Optional)</Label>
          <Input
            id="bank_account"
            name="bank_account"
            value={formData.bank_account}
            onChange={handleChange}
            placeholder="Bank account number"
            disabled={isLoading}
            className={errors.bank_account ? "border-red-500" : ""}
          />
          {errors.bank_account && (
            <p className="text-sm text-red-500">{errors.bank_account}</p>
          )}
        </div>

        {/* Referral Code (Optional) */}
        <div className="space-y-2">
          <Label htmlFor="referral_code">Referral Code (Optional)</Label>
          <Input
            id="referral_code"
            name="referral_code"
            value={formData.referral_code}
            onChange={handleChange}
            placeholder="If you have a referral code"
            disabled={isLoading}
            className={errors.referral_code ? "border-red-500" : ""}
          />
          {errors.referral_code && (
            <p className="text-sm text-red-500">{errors.referral_code}</p>
          )}
        </div>
      </div>

      {/* Submit Button */}
      <Button
        type="submit"
        variant="primary"
        size="lg"
        disabled={isLoading || Object.keys(errors).length > 0}
        className="w-full"
      >
        {isLoading ? (
          <>
            <Spinner className="mr-2 h-4 w-4" />
            Creating Account...
          </>
        ) : (
          "Create Account"
        )}
      </Button>
    </form>
  );
}

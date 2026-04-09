import { useState } from "react";
import { motion } from "motion/react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { PasswordStrengthIndicator } from "@/components/auth/PasswordStrengthIndicator";
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
  const [formData, setFormData] = useState<
    RegistrationData & { showPassword?: boolean }
  >({
    salon_name: "",
    owner_name: "",
    email: "",
    phone: "",
    password: "",
    address: "",
    bank_account: "",
    referral_code: "",
    showPassword: false,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

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

      {/* Salon Name */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0 }}
      >
        <div className="space-y-2">
          <Label htmlFor="salon_name">Salon Name *</Label>
          <Input
            id="salon_name"
            name="salon_name"
            value={formData.salon_name}
            onChange={handleChange}
            placeholder="Enter your salon name"
            disabled={isLoading}
            className={`w-full ${errors.salon_name ? "border-destructive" : ""}`}
          />
          {errors.salon_name && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              <p className="text-sm" style={{ color: "var(--destructive)" }}>
                {errors.salon_name}
              </p>
            </motion.div>
          )}
        </div>
      </motion.div>

      {/* Owner Name */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.05 }}
      >
        <div className="space-y-2">
          <Label htmlFor="owner_name">Owner Name *</Label>
          <Input
            id="owner_name"
            name="owner_name"
            value={formData.owner_name}
            onChange={handleChange}
            placeholder="Enter your full name"
            disabled={isLoading}
            className={`w-full ${errors.owner_name ? "border-destructive" : ""}`}
          />
          {errors.owner_name && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              <p className="text-sm" style={{ color: "var(--destructive)" }}>
                {errors.owner_name}
              </p>
            </motion.div>
          )}
        </div>
      </motion.div>

      {/* Email */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
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
            className={`w-full ${errors.email ? "border-destructive" : ""}`}
          />
          {errors.email && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              <p className="text-sm" style={{ color: "var(--destructive)" }}>
                {errors.email}
              </p>
            </motion.div>
          )}
        </div>
      </motion.div>

      {/* Phone */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.15 }}
      >
        <div className="space-y-2">
          <Label htmlFor="phone">Phone *</Label>
          <Input
            id="phone"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            placeholder="+234 123 456 7890"
            disabled={isLoading}
            className={`w-full ${errors.phone ? "border-destructive" : ""}`}
          />
          {errors.phone && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              <p className="text-sm" style={{ color: "var(--destructive)" }}>
                {errors.phone}
              </p>
            </motion.div>
          )}
        </div>
      </motion.div>

      {/* Password */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.2 }}
      >
        <div className="space-y-2">
          <Label htmlFor="password">Password *</Label>
          <div className="relative">
            <Input
              id="password"
              name="password"
              type={
                formData.password && (formData as any).showPassword
                  ? "text"
                  : "password"
              }
              value={formData.password}
              onChange={handleChange}
              placeholder="Min 8 chars, uppercase, lowercase, number, special char"
              disabled={isLoading}
              className={`w-full pr-10 ${errors.password ? "border-destructive" : ""}`}
            />
            {formData.password && (
              <button
                type="button"
                onClick={() => {
                  setFormData((prev: any) => ({
                    ...prev,
                    showPassword: !prev.showPassword,
                  }));
                }}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                disabled={isLoading}
              >
                {(formData as any).showPassword ? (
                  <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                    <path
                      fillRule="evenodd"
                      d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                ) : (
                  <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z"
                      clipRule="evenodd"
                    />
                    <path d="M15.171 13.576l1.414 1.414A10.025 10.025 0 0019.542 10c-1.274-4.057-5.064-7-9.542-7a9.96 9.96 0 00-5.084 1.368l1.433 1.433C5.124 3.936 7.403 3 10 3c4.478 0 8.268 2.943 9.542 7a9.958 9.958 0 01-1.371 2.576z" />
                  </svg>
                )}
              </button>
            )}
          </div>
          {formData.password && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <PasswordStrengthIndicator
                password={formData.password}
                showRequirements={true}
              />
            </motion.div>
          )}
          {errors.password && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              <p className="text-sm" style={{ color: "var(--destructive)" }}>
                {errors.password}
              </p>
            </motion.div>
          )}
        </div>
      </motion.div>

      {/* Address */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.25 }}
      >
        <div className="space-y-2">
          <Label htmlFor="address">Address *</Label>
          <Textarea
            id="address"
            name="address"
            value={formData.address}
            onChange={handleChange}
            placeholder="Enter your salon address"
            disabled={isLoading}
            className={`w-full ${errors.address ? "border-destructive text-destructive" : ""}`}
            rows={3}
          />
          {errors.address && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              <p className="text-sm text-destructive">{errors.address}</p>
            </motion.div>
          )}
        </div>
      </motion.div>

      <div className="grid grid-cols-1 gap-4">
        {/* Bank Account (Optional) */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <div className="space-y-2">
            <Label htmlFor="bank_account">Bank Account (Optional)</Label>
            <Input
              id="bank_account"
              name="bank_account"
              value={formData.bank_account}
              onChange={handleChange}
              placeholder="Bank account number"
              disabled={isLoading}
              className={`w-full ${errors.bank_account ? "border-destructive" : ""}`}
            />
            {errors.bank_account && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.2 }}
              >
                <p className="text-sm" style={{ color: "var(--destructive)" }}>
                  {errors.bank_account}
                </p>
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Referral Code (Optional) */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.35 }}
        >
          <div className="space-y-2">
            <Label htmlFor="referral_code">Referral Code (Optional)</Label>
            <Input
              id="referral_code"
              name="referral_code"
              value={formData.referral_code}
              onChange={handleChange}
              placeholder="If you have a referral code"
              disabled={isLoading}
              className={`w-full ${errors.referral_code ? "border-destructive" : ""}`}
            />
            {errors.referral_code && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.2 }}
              >
                <p className="text-sm" style={{ color: "var(--destructive)" }}>
                  {errors.referral_code}
                </p>
              </motion.div>
            )}
          </div>
        </motion.div>
      </div>

      {/* Submit Button */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.4 }}
      >
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
      </motion.div>
    </form>
  );
}
